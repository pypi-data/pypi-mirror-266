rq
=============================================================

Cube for starting RqJobs on a Rq worker

Installation
------------

Open the project in a terminal and run::

    pip install -e .

This will install the cube in your active virtual environment
as ``cubicweb-rq``.

The following sections indicate additional steps when you
install this cube as a dependency or as an instance.

As a dependency
~~~~~~~~~~~~~~~

If you plan to use this cube as a dependency for your own cube,
add it to your ``__pkginfo__.py`` as follows::

    __depends__ = {
        # ... Your previous dependencies
        "cubicweb-rq": None,
    }

If the target cube is already used as an instance, you need to migrate it
with the help of its python shell (replace ``YOUR_INSTANCE_NAME`` by your instance name)::

    cubicweb-ctl shell YOUR_INSTANCE_NAME

In the python prompt, enter the following command::

    add_cube("rq")

Press ``Ctrl-D`` then restart your instance.
The cube should now be available in your instance.

As an instance
~~~~~~~~~~~~~~

If you plan to use this cube directly as an instance, create and start
your instance with the following commands (replace ``cubicweb-instance``
by the name of your choice)::

    cubicweb-ctl create rq cubicweb-instance
    cubicweb-ctl start -D cubicweb-instance


Learn More
----------

Visit the `official documentation <https://cubicweb.readthedocs.io/en/4.5.2>`_
to learn more about CubicWeb.



Launch a worker
---------------

Have redis installed and running on your machine.

::

    $ sudo apt-get install redis-server
    $ sudo system-ctl start redis

In your `~/etc/cubicweb.d/cubicweb-instance/pyramid.ini` file,
add the following lines

::

    redis.sessions.timeout = 1200
    redis.sessions.secret = stuff
    redis.sessions.prefix = cubicweb-instance:
    redis.sessions.url = redis://localhost:6379/0
    rq.redis_url = redis://localhost:6379/0


Launch a worker with the following command line (replace ``cubicweb-instance``
with the name of your cubicweb instance)::

    cubicweb-ctl rq-worker cubicweb-instance

