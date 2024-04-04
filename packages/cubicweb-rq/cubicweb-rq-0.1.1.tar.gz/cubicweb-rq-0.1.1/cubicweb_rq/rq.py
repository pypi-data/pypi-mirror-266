# -*- coding: utf-8 -*-
# copyright 2023 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact https://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

from functools import wraps
from contextlib import contextmanager
import sys
import logging

import rq
from rq.logutils import ColorizingStreamHandler
from rq.contrib.sentry import register_sentry

from cubicweb.cwconfig import CubicWebConfiguration

from cubicweb_rq import admincnx as orig_admincnx


@contextmanager
def admincnx(appid_or_cnx, loglevel=None):
    if isinstance(appid_or_cnx, str):
        with orig_admincnx(appid_or_cnx, loglevel) as cnx:
            yield cnx
    else:
        assert (
            appid_or_cnx.vreg.config.mode == "test"
        ), "expected to be a connection only in test mode"
        yield appid_or_cnx


def rqjob(task):
    @wraps(task)
    def task_wrapper(appid, *args, **kwargs):
        job = rq.get_current_job()
        with admincnx(appid, loglevel="warning") as cnx:
            rqtask = cnx.find("RqTask", eid=int(job.id)).one()
            irqjob = rqtask.cw_adapt_to("IRqJob")
            try:
                result = task(cnx, *args, **kwargs)
            except Exception:
                logging.getLogger("rq.task").exception("An error has occurred.")
                cnx.rollback()
                irqjob.handle_failure(*sys.exc_info())
                cnx.commit()
                raise
            else:
                irqjob.handle_finished()
                cnx.commit()
        return result

    return task_wrapper


class RedisHandler(logging.Handler):
    def emit(self, record):
        job = rq.get_current_job()
        if job is not None:
            key = "rq:job:{0}:log".format(job.id)
            pipe = job.connection.pipeline()
            msg = self.format(record)
            if isinstance(msg, str):
                msg = msg.encode("utf-8")
            pipe.append(key, msg)
            # keep RQ logs 24h in case of non-default timeout
            pipe.expire(key, 86400)
            pipe.execute()


def update_progress(job, progress_value):
    job.meta["progress"] = progress_value
    job.save_meta()
    return progress_value


def config_from_appid(appid_or_cnx):
    if isinstance(appid_or_cnx, str):
        return CubicWebConfiguration.config_for(appid_or_cnx)
    assert (
        appid_or_cnx.vreg.config.mode == "test"
    ), "expected to be a connection only in test mode"
    return appid_or_cnx.vreg.config


def work(appid, burst=False, worker_class=rq.Worker):
    logger = logging.getLogger("rq.worker")
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter(fmt="%(asctime)s %(message)s", datefmt="%H:%M:%S")
        handler = ColorizingStreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    task_logger = logging.getLogger("rq.task")
    task_logger.setLevel(logging.DEBUG)
    handler = RedisHandler()
    handler.setFormatter(
        logging.Formatter(
            fmt="%(levelname)s %(asctime)s %(module)s %(process)d %(message)s\n"
        )
    )
    task_logger.addHandler(handler)

    class Job(rq.job.Job):
        @property
        def args(self):
            return (appid,) + super(Job, self).args

    cwconfig = config_from_appid(appid)
    worker = worker_class("default", job_class=Job)
    sentry_dsn = cwconfig.get("sentry-dsn")
    if sentry_dsn:
        register_sentry(sentry_dsn)
    worker.work(burst=burst)
