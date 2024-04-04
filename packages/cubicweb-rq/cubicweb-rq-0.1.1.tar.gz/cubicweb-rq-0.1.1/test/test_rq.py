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
"""cubicweb-rq tests for RQ tasks"""
import logging
import fakeredis
import rq

import rq.job
from cubicweb.devtools.testlib import CubicWebTC

from cubicweb_rq.rq import work, rqjob


@rqjob
def rq_task(cnx, success=False):
    logger = logging.getLogger("rq.task")
    for level in ("debug", "info", "warning", "error", "critical"):
        getattr(logger, level)(level)
    try:
        raise RuntimeError("catched")
    except Exception:
        logger.exception("unexpected")
    if success:
        return 42
    else:
        raise ValueError("uncatched")


class RQTaskTC(CubicWebTC):
    def setUp(self):
        super(RQTaskTC, self).setUp()
        self.fakeredis = fakeredis.FakeStrictRedis()

    def assertDateAlmostEqual(self, d1, d2, epsilon=0.1):
        dt = d1 - d2
        self.assertLessEqual(
            abs(dt.total_seconds()),
            epsilon,
            "%s and %s are not almost equal" % (d1, d2),
        )

    def test_success(self):
        with self.admin_access.cnx() as cnx, rq.Connection(self.fakeredis):
            task = cnx.create_entity("RqTask", name="import_something")
            job = task.cw_adapt_to("IRqJob")
            job.enqueue(rq_task, success=True)
            cnx.commit()
            self.assertEqual(job.status, "queued")
            work(cnx, burst=True, worker_class=rq.worker.SimpleWorker)
            job.refresh()
            self.assertEqual(job.status, "finished")
            self.assertEqual(job.result, 42)
            log = job.log
            for expected in (
                "debug",
                "info",
                "warning",
                "error",
                "critical",
                "unexpected",
                "RuntimeError: catched",
            ):
                self.assertIn(expected, log)
            task = cnx.entity_from_eid(task.eid)
            self.assertEqual(task.status, job.status)
            for attr in ("enqueued_at", "started_at"):
                self.assertDateAlmostEqual(getattr(task, attr), getattr(job, attr))
            self.assertEqual(task.log.read(), log.encode("utf-8"))

    def test_failure(self):
        with self.admin_access.cnx() as cnx, rq.Connection(self.fakeredis):
            task = cnx.create_entity("RqTask", name="import_something")
            job = task.cw_adapt_to("IRqJob")
            job.enqueue(rq_task, success=False)
            cnx.commit()
            self.assertEqual(job.status, "queued")
            work(cnx, burst=True, worker_class=rq.worker.SimpleWorker)
            job.refresh()
            self.assertEqual(job.status, "failed")
            self.assertEqual(job.result, None)
            log = job.log
            for expected in (
                "debug",
                "info",
                "warning",
                "error",
                "critical",
                "unexpected",
                "RuntimeError: catched",
                "ValueError: uncatched",
            ):
                self.assertIn(expected, log)
            task = cnx.entity_from_eid(task.eid)
            self.assertEqual(task.status, job.status)
            for attr in ("enqueued_at", "started_at"):
                self.assertDateAlmostEqual(getattr(job, attr), getattr(task, attr))
            self.assertEqual(task.log.read(), log.encode("utf-8"))
