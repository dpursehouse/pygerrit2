""" Gerrit event stream interface.

Class to listen to the Gerrit event stream and dispatch events.

"""

import json
import logging

from pygerrit.error import GerritError
from pygerrit.events import GerritEventFactory


class GerritStreamError(Exception):

    """ Raised when an error occurs while reading the Gerrit events stream. """

    pass


class GerritStream(object):

    """ Gerrit events stream handler. """

    def __init__(self):
        self.listeners = []

    def attach(self, listener):
        """ Attach the `listener` to the list of listeners.

        Raise GerritStreamError if the listener does not match the
        expected signature, or if its event handler is not callable.

        """
        if not hasattr(listener, "on_gerrit_event"):
            raise GerritStreamError("Listener must have `on_gerrit_event` "
                                    "event handler method")
        if not callable(listener.on_gerrit_event):
            raise GerritStreamError("`on_gerrit_event` must be callable")
        if not listener.on_gerrit_event.func_code.co_argcount == 2:
            raise GerritStreamError("`on_gerrit_event` must take 1 arg")
        if not listener in self.listeners:
            self.listeners.append(listener)

    def detach(self, listener):
        """ Remove the `listener` from the list of listeners. """
        if listener in self.listeners:
            try:
                self.listeners.remove(listener)
            except ValueError:
                pass

    def stream(self, inputstream):
        """ Read lines of JSON data from `inputstream` and dispatch events.

        For each line read from `inputstream`, until EOF, parse the line as
        JSON data, instantiate the corresponding GerritEvent, and dispatch it
        to the listeners.

        Raise GerritStreamError on any errors.

        """
        try:
            while 1:
                line = inputstream.readline()
                if not line:
                    break
                json_data = json.loads(line)
                try:
                    event = GerritEventFactory.create(json_data)
                    for listener in self.listeners:
                        listener.on_gerrit_event(event)
                except GerritError, e:
                    logging.error("Unable to dispatch event: %s", e)
        except IOError, e:
            raise GerritStreamError("Error reading event stream: %s" % e)
        except ValueError, e:
            raise GerritStreamError("Invalid JSON data in event stream: %s" % e)
