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

""" Gerrit event stream interface.

Class to listen to the Gerrit event stream and dispatch events.

"""

from threading import Thread, Event

from .events import ErrorEvent


class GerritStream(Thread):

    """ Gerrit events stream handler. """

    def __init__(self, gerrit, ssh_client):
        Thread.__init__(self)
        self.daemon = True
        self._gerrit = gerrit
        self._ssh_client = ssh_client
        self._stop = Event()

    def stop(self):
        """ Stop the thread. """
        self._stop.set()

    def _error_event(self, error):
        """ Dispatch `error` to the Gerrit client. """
        self._gerrit.put_event(ErrorEvent.error_json(error))

    def run(self):
        """ Listen to the stream and send events to the client. """
        channel = self._ssh_client.get_transport().open_session()
        channel.exec_command("gerrit stream-events")
        stdout = channel.makefile()
        stderr = channel.makefile_stderr()
        while not self._stop.is_set():
            try:
                if channel.exit_status_ready():
                    if channel.recv_stderr_ready():
                        error = stderr.readline().strip()
                    else:
                        error = "Remote server connection closed"
                    self._error_event(error)
                    self._stop.set()
                else:
                    data = stdout.readline()
                    self._gerrit.put_event(data)
            except Exception as e:  # pylint: disable=W0703
                self._error_event(repr(e))
                self._stop.set()
