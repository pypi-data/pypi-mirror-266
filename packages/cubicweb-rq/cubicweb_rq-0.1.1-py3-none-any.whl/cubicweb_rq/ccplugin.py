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

import redis
import rq


from cubicweb import ConfigurationError
from cubicweb.toolsutils import Command
from cubicweb.pyramid import settings_from_cwconfig

from cubicweb.cwconfig import CubicWebConfiguration as cwcfg

from cubicweb.cwctl import CWCTL

from cubicweb_rq.rq import work


def get_rq_redis_connection(appid):
    settings = settings_from_cwconfig(cwcfg.config_for(appid))
    redis_url = settings.get("rq.redis_url")
    if redis_url is None:
        raise ConfigurationError(
            "could not start rq: `rq.redis_url` is missing from pyramid.ini file"
        )
    return redis.StrictRedis.from_url(redis_url)


@CWCTL.register
class RqWorker(Command):
    """run a python-rq worker for instance"""

    arguments = "<instance>"
    name = "rq-worker"
    max_args = None
    min_args = 1

    def run(self, args):
        appid = args.pop()
        connection = get_rq_redis_connection(appid)
        with rq.Connection(connection):
            work(appid)
