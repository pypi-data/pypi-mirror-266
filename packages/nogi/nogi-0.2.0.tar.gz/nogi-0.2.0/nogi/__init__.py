import logging
import queue
import signal
import socket
import sys
import threading

import zmq

log = logging.getLogger(__name__)

DEFAULT_HOST = "*"
DEFAULT_PORT = 5556
DEFAULT_DELIMITER = "$$-$$"
STOP_NOGI_SERVER_SEQUENCE = "$$!!STOP_NOGI_SERVER_SEQUENCE!!$$"


class Nogi:
    """Provides high-level functionality for initialize the event audit.

    The :class:`Nogi` object automatically configure mechanismes that
    allow enable and disable auditing by sending signals to the process
    you want to inspect.

    By instanciate this class, two kind of signal are binds to the
    running process. The first one is the ``SIGUSR1`` signal, which
    is the signal who will trigger the audit. The second one is the
    ``SIGUSR2`` signal who should be used to disable the running audit.

    Nogi allow you to provide a custom event handler. The default
    event handler trigger a python thread which receive the catched
    events and then publish them on `PUB zmq socket
    <https://pyzmq.readthedocs.io/en/v22.1.0/logging.html?highlight=pub%20sub#pub-sub-and-topics>`_.

    By default this socket listen on localhost:5556 and each new
    intercepted event will be forwarded over it. The event name correspond
    to the publication topic, allowing users to subscribe only to specific
    events.

    When the audit handler is closed, then the socket is also closed.

    Users are allowed to customize the way they want to handle signals
    and the way they want to catch events.

    A convenience socket is provided by default, but this one can be
    disabled if needed.

    For more details about Python audits please take a look at
    the `Audit events table
    <https://docs.python.org/3/library/audit_events.html#audit-events>`_
    """

    def __init__(
        self,
        host=DEFAULT_HOST,
        port=DEFAULT_PORT,
        handler=None,
        socket=True,
        audit=None,
    ):
        self.host = host
        self.port = port
        if not handler:
            self.handler = self.serve
        else:
            log.info("Using a custom handler: {handler.__name__}")
            self.handler = handler
        if not audit:
            self.audit_hook = self.audit
        else:
            log.info("Using a custom audit hook: {audit.__name__}")
            self.audit_hook = audit
        self.socket = socket
        self.q = queue.Queue()
        self.hooked = False
        self.running = False
        signal.signal(signal.SIGUSR1, self.start)
        signal.signal(signal.SIGUSR2, self.stop)

    def audit(self, event, args):
        """Default audit hook.

        This hook puts all received events, and their arguments into
        a python queue. The default handler will consume the elements puts
        in that queue.

        .. warning::
            Only the thread which instanciate Nogi will be audited. Meaning
            that if you instanciate Nogi at the beginning of our process
            then you will surely audit the main python thread, not the
            events ran in the sub threads you launched.
        """
        if not self.running:
            return
        self.q.put((event, str(args)))

    def serve(self):
        """Default handler that publish received events on a zmq socket.

        When an event is consumed by this handler, it is automatically
        removed from the queue.

        This handler is executed in a dedicated thread to not block the
        main process.
        """
        log.debug("Starting the default audit server")
        serving = True
        while serving:
            try:
                topic, data = self.q.get()
            except queue.Empty:
                continue
            if topic == STOP_NOGI_SERVER_SEQUENCE:
                serving = False
                continue
            self.publisher.send_string(f"{topic}{DEFAULT_DELIMITER}{data}")
            self.q.task_done()

    def _setup_publisher(self):
        if not self.socket and self.handler == self.serve:
            raise RuntimeError(
                """
                It's not possible to disable the socket if you use the default
                handler. The default handler rely on the internal socket.
                You see this message because you disabled the internal socket
                and in parallel you use the default handler.
                To fix this problem either:
                    1) enable the internal socket
                    2) provide a customer handler that do not rely on
                       the internal socket.
                Further details are available at:
                https://nogi.readthedocs.org/configuration
            """
            )
        if self.socket:
            self.context = zmq.Context()
            self.publisher = self.context.socket(zmq.PUB)
            self.publisher.bind(f"tcp://{self.host}:{self.port}")

    def start(self, sig, frame):
        """Starting the audit.

        This method is bind on the ``SIGUSR1``, so if this signal is emitted
        this method will be automatically called and then will ran the audit.

        Will using the configured handler and audit hook. If not provided
        it will start with the default conveniences.
        """
        log.info("Signal received - starting the audit")
        if self.running:
            log.warning("audit is already running")
            return
        self._setup_publisher()
        threading.Thread(target=self.handler).start()
        if not self.hooked:
            log.info("Setting the audit hook")
            sys.addaudithook(self.audit_hook)
            self.hooked = True
        else:
            log.info("Audit hook already set, ignoring...")
        self.running = True

    def stop(self, sig, frame):
        """Stopping the audit.

        The ``SIGUSR2`` is bind to this method. If this signal is sent to
        the process, then this method will be called and so, the audit
        will be terminated.
        """
        if not self.running:
            log.info("audit already disabled...")
            return
        log.info("Stopping the audit server")
        self.q.put({STOP_NOGI_SERVER_SEQUENCE, "_"})
        self.running = False
        if self.socket:
            self.publisher.close()
        with self.q.mutex:
            self.q.queue.clear()
        self.q.join()

    def __del__(self):
        self.stop(None, None)
