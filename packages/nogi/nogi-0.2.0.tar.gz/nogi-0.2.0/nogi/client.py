import argparse
import re
import textwrap

import zmq

from nogi import DEFAULT_DELIMITER, DEFAULT_HOST, DEFAULT_PORT


class NogiClient:
    def __init__(
        self, host=DEFAULT_HOST, port=DEFAULT_PORT, events=["."], handler=None
    ):
        """Default Nogi client.

        This client is a convenience client. It will allow user
        to connect to the default handler and then to subscribe
        to emitted events.

        This client simply print the catched events and their arguments
        onto the stdout.
        """
        print("Starting the audit listener")
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect(f"tcp://{host}:{port}")
        self.socket.subscribe("")
        self._configure_monitored_events(events)
        self.used_handler = self.handler
        if handler:
            self.used_handler = handler
        self.run()

    def _configure_monitored_events(self, events):
        self.monitored_events = []
        for event in events:
            self.monitored_events.append(re.compile(event))

    def handler(self, event, data):
        """Defaut event handler.

        Display events and arguments onto the stdout.
        """
        print(f"event: {event}")
        print(f"data: {data}")

    def run(self):
        """This method create a zmq subscribe socket that listen for
        forwarded events.

        Received events are filtered to only capture the events specified by
        user.
        """
        running = True
        print("Audit client listening...")
        while running:
            try:
                string = self.socket.recv_string()
                event, data = string.split(DEFAULT_DELIMITER)
                for monitored_event in self.monitored_events:
                    if monitored_event.match(event):
                        self.used_handler(event, data)
            except KeyboardInterrupt:
                print("Stopping client...")
                running = False
        self.close()

    def close(self):
        """Closing the client."""
        print("Closing the client...")
        self.socket.close()
        print("Client properly terminated")

    def __del__(self):
        self.close()


def client():
    """Convenience function to launch the Nogi client"""
    epilog = textwrap.dedent(
        """
        See the Nogi documentation to see how to configure the socket
        of the process that you want to audit.

        This client exclusively rely on socket communication to monitor
        events.

        Feel free to submit a pull request to introduce new
        ways to monitor events.
    """
    )
    parser = argparse.ArgumentParser(
        description="Subscribe to audit from a running process", epilog=epilog
    )
    parser.add_argument(
        "--host",
        type=str,
        default=DEFAULT_HOST,
        help="Remote host to audit",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=str,
        default=DEFAULT_PORT,
        help="Remote port to connect",
    )
    parser.add_argument(
        "-e",
        "--events",
        type=str,
        nargs="*",
        default=["."],
        help="""
            Select the events to monitor. By default all events are monitored
        """,
    )
    args = parser.parse_args()
    NogiClient(args.host, args.port)
