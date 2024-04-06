.. Nogi documentation master file, created by
   sphinx-quickstart on Thu Mar 21 15:56:55 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Nogi's docs!
=======================

Toogleable events auditor for Python apps.


Live monitor Python events and user defined custome events in running
Python applications.

Nogi allow you to audit your code without adding debug tracing and invasive
prints. Just instantiate Nogi in your code and then send a signal to your
running app to start auditing it.

Nogi allow you to enable and disable audit without restarting your application
and so without loosing the context that you want to observe, by example a
occuring bug.

See the example below.

Install
-------

.. code::

    $ pip install nogi

Usages
------

Simply instanciate ``Nogi`` at the begining of your code:

.. code::

    Nogi()

Example
-------

Here is a concret example (see examples/sample.py):

.. code::

    # sample.py
    import requests
    import time

    from nogi import Nogi

    Nogi()

    def main():
        for i in range(1000):
            r = requests.get(
                "https://en.wikipedia.org/wiki/Python_(programming_language)")
            print(r.status_code)
            time.sleep(1)

    if __name__ == "__main__":
        main()

Run the previous code:

.. code::

    $ python examples/sample.py
    200
    200
    ...
    200
    ...

Then enable the audit by sending the ``SIGUSR1`` to the process previously
launched:

.. code::

    $ ps ax | grep python | grep sample # to retrieve the process id (pid)
    $ kill -SIGUSR1 <pid>

We are now able to collect events by running the Nogi client:

.. code::

    $ nogi
    Starting the audit listener
    Audit client listening...
    event: socket.getaddrinfo
    data: ('en.wikipedia.org', 443, 0, 1, 0)
    event: socket.__new__
    data: (<socket.socket fd=-1, family=0, type=0, proto=0>, 2, 1, 6)
    event: socket.connect
    data: (<socket.socket fd=4, family=2, type=1, proto=6, laddr=('0.0.0.0', 0)>, ('185.15.58.224', 443))
    event: http.client.connect
    data: (<urllib3.connection.HTTPSConnection object at 0x7f0b48fafbf0>, 'en.wikipedia.org', 443)
    event: socket.__new__
    data: (<ssl.SSLSocket fd=-1, family=0, type=0, proto=0>, 2, 1, 6)
    event: http.client.send
    data: (<urllib3.connection.HTTPSConnection object at 0x7f0b48fafbf0>, b'GET /wiki/Python_(programming_language) HTTP/1.1\r\nHost: en.wikipedia.org\r\nUser-Agent: python-requests/2.31.0\r\nAccept-Encoding: gzip, deflate\r\nAccept: */*\r\nConnection: keep-alive\r\n\r\n')
    ...

When you want to terminate your audit, simply send the ``SIGUSR2`` signal
to the same process id (pid) to stop forwarding events.

.. code::

    $ kill -SIGUSR2 <pid>

What Nogi stands for?
---------------------

Nogi, pronounced as "no gi".

The Gi is the traditional martial arts uniform, the kimono.
The Gi is usually what’s pictured when someone thinks of martial arts.

No Gi in martial arts means that its practice is done without the Gi,
without the kimono, that is usually worn in martial arts.
Ones can also call it grappling.

No Gi allows for more realistic scenarios as the grips used vs opponents
include the wrist, ankles, necks, and additional limbs.

Since they don't use the traditional Gi uniform, they aren't able to use the
Gi as an extra 'weapon' to set up submissions or even execute submissions
using them.

The No Gi is thought to more likely resemble street fighting as the
perpetrators usually will not be wearing uniforms.

For more details about details about "no gi" in martial arts context please
take a look to `this blog article <https://martialartsinsider.com/blogs/bjj/no-gi-bjj>`_.

Debugging running apps is like street fight. Bugs always appears when no one
expects it. Developers are never prepared to fight them. Bugs bully operators
and teams. Only developers with self defense skills can defeat their
opponents.

Nogi don't need extra 'weapon' to catch things happening in your application
at runtime. Nogi is based on the backbone of your Python runtime, CPython
itself. Nogi interact directly with the low level of your app to catch events
to audit.

Why Nogi?
---------

Nogi could be, in some ways, compared to Userland Statically Defined Tracing
(USDT, `see this article for more details about USDT
<https://docs.openvswitch.org/en/latest/topics/usdt-probes/>`_).

After weeks of studies and researches about USDT, I found that CPython
ecosystem is a bit poor concerning them.

I wrote several related debug notes:
* http://herve.beraud.io/debug/sections/python/python.html
* http://herve.beraud.io/debug/sections/network.html
* http://herve.beraud.io/debug/sections/python/eventlet.html

But I was thinking using the audit hook feature from the CPython stdlib to
extend the debug capabilities of the python developers world.

Almost all debug solutions at the Python level require restarting the running
process to attach debugger or debug things. But process restart make us loosing
the context of bugs. That's annoying and not really useful.

Nogi was thoughts to avoid loosing bug context.

Of course, Nogi does not have the ambition to replace eBPF, BCC, USDT, strace,
stat, lsof, perf, etc... all these tools are more powerful and well far more
documented, but in some case, Nogi could be a good addition, especially
if you start placing custom audit in your apps:

.. code::

   sys.audit('my-event', 'foo', 'bar', 123)

Then Nogi will allow you to subscribe to your custom events. No extra prints
or debugger trace points are required.

Nogi should be used in conjunction of the classic Linux debug/trace commands.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   reference/api/modules


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
