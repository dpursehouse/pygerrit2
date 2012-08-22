""" Gerrit client interface. """

from Queue import Queue, Empty, Full

from pygerrit.error import GerritError
from pygerrit.events import GerritEventFactory


class GerritClient(object):

    """ Gerrit client interface. """

    def __init__(self, host):
        self._factory = GerritEventFactory()
        self._host = host
        self._events = Queue()

    def get_event(self, block=True, timeout=None):
        """ Get the next event from the queue.

        Return a `GerritEvent` instance, or None if:
         - `block` was False and there is no event available in the queue, or
         - `block` was True and no event was available within the time
        specified by `timeout`.

        """
        try:
            return self._events.get(block, timeout)
        except Empty:
            return None

    def put_event(self, json_data):
        """ Create event from `json_data` and add it to the queue.

        Raise GerritError if the queue is full, or the factory could not
        create the event.

        """
        try:
            event = self._factory.create(json_data)
            self._events.put(event)
        except Full:
            raise GerritError("Unable to add event: queue is full")
