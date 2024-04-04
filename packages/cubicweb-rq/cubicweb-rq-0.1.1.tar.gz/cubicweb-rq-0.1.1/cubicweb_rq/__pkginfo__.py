"""cubicweb-rq application packaging information"""

modname = "cubicweb_rq"
distname = "cubicweb-rq"

numversion = (0, 1, 1)
version = ".".join(str(num) for num in numversion)

license = "LGPL"
author = "LOGILAB S.A. (Paris, FRANCE)"
author_email = "contact@logilab.fr"
description = "Cube for starting RqJobs on a Rq worker"
web = "https://forge.extranet.logilab.fr/cubicweb/cubes/rq"

__depends__ = {
    "cubicweb": ">= 4.5.2, < 5.0.0",
    "pyramid-session-redis": ">=1.6.3,<2.0.0",
    "rq": "<2.0.0",
}
__recommends__ = {}

classifiers = [
    "Environment :: Web Environment",
    "Framework :: CubicWeb",
    "Programming Language :: Python :: 3",
    "Programming Language :: JavaScript",
]
