""" Gerrit event stream interface.

Class to listen to the Gerrit event stream and dispatch events.

"""

import json
from select import poll, POLLIN
from threading import Thread, Event

from pygerrit.ssh import GerritSSHClient
from pygerrit.error import GerritError
from pygerrit.events import GerritEvent, GerritEventFactory


@GerritEventFactory.register("gerrit-stream-error")
class GerritStreamErrorEvent(GerritEvent):

    """ Represents an error when handling the gerrit event stream """

    def __init__(self, json_data):
        super(GerritStreamErrorEvent, self).__init__()
        self.error = json_data["error"]


class GerritStream(Thread):

    """ Gerrit events stream handler. """

    def __init__(self, gerrit, host):
        Thread.__init__(self)
        self.daemon = True
        self._gerrit = gerrit
        self._host = host
        self._stop = Event()

    def stop(self):
        """ Stop the thread. """
        self._stop.set()

    def run(self):
        """ Listen to the stream and send events to the client. """
        try:
            client = GerritSSHClient(self._host)
            _stdin, stdout, _stderr = client.run_gerrit_command("stream-events")
            p = poll()
            p.register(stdout.channel)
            while not self._stop.is_set():
                data = p.poll()
                for (fd, event) in data:
                    if fd == stdout.channel.fileno():
                        if event == POLLIN:
                            line = stdout.readline()
                            json_data = json.loads(line)
                            self._gerrit.put_event(json_data)
        except GerritError, e:
            error = json.loads('{"type":"gerrit-stream-error",'
                               '"error":"%s"}' % str(e))
            self._gerrit.put_event(error)
