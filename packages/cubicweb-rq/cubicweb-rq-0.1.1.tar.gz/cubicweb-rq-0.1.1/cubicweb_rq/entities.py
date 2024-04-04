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

"""cubicweb-rq entity's classes"""

import rq

from datetime import datetime

from cubicweb import Binary

from cubicweb.predicates import is_instance

from cubicweb.server.hook import DataOperationMixIn, Operation

from cubicweb.entity import EntityAdapter
from cubicweb.entities import AnyEntity

from cubicweb_rq.ccplugin import get_rq_redis_connection


class RqTask(AnyEntity):
    __regid__ = "RqTask"

    def dc_title(self):
        return "{} ({})".format(self.title, self.name)


class StartRqTaskOp(DataOperationMixIn, Operation):
    def postcommit_event(self):
        # use connection if it exists (e.g. one created by FakeRedis), else create new connection
        # the demo does not seem to connect automatically to the redis instance, so we need
        # to manually create it
        connection = rq.connections.get_current_connection()
        if not connection:
            appid = self.cnx.repo.config.appid
            connection = get_rq_redis_connection(appid)

        queue = rq.Queue(connection=connection)
        for args, kwargs in self.cnx.transaction_data.get("rq_tasks", []):
            kwargs.setdefault("job_timeout", "12h")
            queue.enqueue(*args, **kwargs)


class IRqJob(EntityAdapter):
    """provide a proxy from an entity to rq Job"""

    __regid__ = "IRqJob"
    END_STATUSES = (rq.job.JobStatus.FINISHED, rq.job.JobStatus.FAILED)

    def __init__(self, *args, **kwargs):
        super(IRqJob, self).__init__(*args, **kwargs)
        self._job = None

    @property
    def id(self):
        return str(self.entity.eid)

    def enqueue(self, *args, **kwargs):
        assert "job_id" not in kwargs, "job_id is a reserved kwarg"
        kwargs["job_id"] = self.id
        self._cw.transaction_data.setdefault("rq_tasks", []).append((args, kwargs))
        # Operation want a cnx not a request
        cnx = getattr(self._cw, "cnx", self._cw)
        StartRqTaskOp.get_instance(cnx).add_data(self.entity.eid)

    def get_job(self):
        if self._job is None:
            try:
                self._job = rq.job.Job.fetch(self.id)
            except rq.job.NoSuchJobError as err:
                self.warning(
                    f"failed to get job #{self.id} from redis, mocking one: {err}"
                )
                return rq.job.Job.create(self.id)
            except rq.connections.NoRedisConnectionException as err:
                self.warning(
                    f"failed to get job #{self.id} from redis, mocking one: {err}"
                )
                return rq.job.Job.create(self.id)
        return self._job

    def refresh(self):
        self._job = None

    @property
    def progress(self):
        if self.status in self.END_STATUSES:
            return 1.0
        meta = self.get_job().meta
        return meta.get("progress", 0.0)

    @property
    def log(self):
        key = "rq:job:{0}:log".format(self.id)
        connection = self.get_job().connection
        content = connection.get(key) or b""
        content = content.decode("utf-8")
        return content

    def handle_finished(self):
        pass

    def __getattr__(self, attr):
        return getattr(self.get_job(), attr)


class RqTaskJob(IRqJob):
    __select__ = IRqJob.__select__ & is_instance("RqTask")

    def handle_failure(self, *exc_info):
        update = dict(
            log=Binary(self.log.encode("utf-8")),
            status=rq.job.JobStatus.FAILED.value,
        )
        for attr in ("enqueued_at", "started_at"):
            update[attr] = getattr(self, attr)
        # XXX for some reason ended_at is never available put an approximate end date
        update["ended_at"] = self.ended_at if self.ended_at else datetime.now()
        self.entity.cw_set(**update)

    def handle_finished(self):
        update = {"log": Binary(self.log.encode("utf-8"))}
        for attr in ("enqueued_at", "started_at"):
            update[attr] = getattr(self, attr)
        # XXX for some reason ended_at is never available put an approximate end date
        update["ended_at"] = self.ended_at if self.ended_at else datetime.now()
        update["status"] = rq.job.JobStatus.FINISHED.value
        self.entity.cw_set(**update)

    def is_finished(self):
        return self.entity.status in self.END_STATUSES

    def get_job(self):
        if self.is_finished():
            return self.entity
        return super(RqTaskJob, self).get_job()

    @property
    def status(self):
        if self.is_finished():
            return self.entity.status
        return self.get_status()

    @property
    def log(self):
        if self.is_finished():
            return self.entity.log.read().decode("utf-8")
        return super(RqTaskJob, self).log
