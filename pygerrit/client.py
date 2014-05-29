# The MIT License
#
# Copyright 2012 Sony Mobile Communications. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

""" Gerrit client interface. """

from json import JSONDecoder
from Queue import Queue, Empty, Full

from . import escape_string
from .error import GerritError
from .events import GerritEventFactory
from .models import Change
from .ssh import GerritSSHClient
from .stream import GerritStream


class GerritClient(object):

    """ Gerrit client interface. """

    def __init__(self, host, username=None, port=None):
        self._factory = GerritEventFactory()
        self._events = Queue()
        self._stream = None
        self._ssh_client = GerritSSHClient(host, username=username, port=port)

    def gerrit_version(self):
        """ Return the version of Gerrit that is connected to. """
        return self._ssh_client.get_remote_version()

    def gerrit_info(self):
        """ Return the username, and version of Gerrit that is connected to. """
        return self._ssh_client.get_remote_info()

    def run_command(self, command):
        """ Run the command.  Return the result. """
        if not isinstance(command, basestring):
            raise ValueError("command must be a string")
        return self._ssh_client.run_gerrit_command(command)

    def query(self, term):
        """ Run `gerrit query` with the given `term`.

        Return a list of results as `Change` objects.

        Raise `ValueError` if `term` is not a string.

        """
        results = []
        command = ["query", "--current-patch-set", "--all-approvals",
                   "--format JSON", "--commit-message"]

        if not isinstance(term, basestring):
            raise ValueError("term must be a string")

        command.append(escape_string(term))
        result = self._ssh_client.run_gerrit_command(" ".join(command))
        decoder = JSONDecoder()
        for line in result.stdout.read().splitlines():
            # Gerrit's response to the query command contains one or more
            # lines of JSON-encoded strings.  The last one is a status
            # dictionary containing the key "type" whose value indicates
            # whether or not the operation was successful.
            # According to http://goo.gl/h13HD it should be safe to use the
            # presence of the "type" key to determine whether the dictionary
            # represents a change or if it's the query status indicator.
            try:
                data = decoder.decode(line)
            except ValueError as err:
                raise GerritError("Query returned invalid data: %s", err)
            if "type" in data and data["type"] == "error":
                raise GerritError("Query error: %s" % data["message"])
            elif "project" in data:
                results.append(Change(data))
        return results

    def start_event_stream(self):
        """ Start streaming events from `gerrit stream-events`. """
        if not self._stream:
            self._stream = GerritStream(self, ssh_client=self._ssh_client)
            self._stream.start()

    def stop_event_stream(self):
        """ Stop streaming events from `gerrit stream-events`."""
        if self._stream:
            self._stream.stop()
            self._stream.join()
            self._stream = None
            with self._events.mutex:
                self._events.queue.clear()

    def get_event(self, block=True, timeout=None):
        """ Get the next event from the queue.

        Return a `GerritEvent` instance, or None if:
         - `block` is False and there is no event available in the queue, or
         - `block` is True and no event is available within the time
           specified by `timeout`.

        """
        try:
            return self._events.get(block, timeout)
        except Empty:
            return None

    def put_event(self, data):
        """ Create event from `data` and add it to the queue.

        Raise GerritError if the queue is full, or the factory could not
        create the event.

        """
        try:
            event = self._factory.create(data)
            self._events.put(event)
        except Full:
            raise GerritError("Unable to add event: queue is full")
