"""cubicweb-rq application package

Cube for starting RqJobs on a Rq worker
"""

from sched import scheduler

from cubicweb import repoapi
from cubicweb.cwconfig import CubicWebConfiguration
from cubicweb.cwctl import init_cmdline_log_threshold
from cubicweb.server.repository import Repository


def admincnx(appid, loglevel=None):
    config = CubicWebConfiguration.config_for(appid)
    config["connections-pool-min-size"] = 2

    login = config.default_admin_config["login"]
    password = config.default_admin_config["password"]

    if loglevel is not None:
        init_cmdline_log_threshold(config, loglevel)

    repo = Repository(config, scheduler=scheduler())
    repo.bootstrap()
    return repoapi.connect(repo, login, password=password)
