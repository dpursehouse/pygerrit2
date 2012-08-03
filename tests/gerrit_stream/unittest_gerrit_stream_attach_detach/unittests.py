#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Unit tests for the stream attach/detach functionality. """

from StringIO import StringIO
import unittest

from pygerrit.stream import GerritStream, GerritStreamError


class ListenerWithNoHandler():

    """ Dummy listener class with no event handler. """

    def __init__(self):
        pass


class ListenerWithInvalidHandler():

    """ Dummy listener class with invalid event handler. """

    def __init__(self):
        pass

    def on_gerrit_event(self):
        pass


class ListenerWithInvalidHandlerNotCallable():

    """ Dummy listener class with event handler that is not callable. """

    on_gerrit_event = "this is a string"

    def __init__(self):
        pass


class ListenerWithValidHandler():

    """ Dummy listener class. """

    def __init__(self):
        pass

    def on_gerrit_event(self, event):
        pass


class TestGerritStreamAttachDetach(unittest.TestCase):

    """ Test that the attach and detach methods behave correctly. """

    def test_listener_no_handler(self):
        """ Listener without event handler.

        Test that an exception is raised if a listener is attached without
        an event handler method.

        """
        g = GerritStream(StringIO("Dummy stream"))
        l = ListenerWithNoHandler()
        self.assertRaises(GerritStreamError, g.attach, l)

    def test_listener_invalid_handler(self):
        """ Listener with invalid handler method.

        Test that an exception is raised if a listener is attached with an
        invalid event handler method (does not have correct signature).

        """
        g = GerritStream(StringIO("Dummy stream"))
        l = ListenerWithInvalidHandler()
        self.assertRaises(GerritStreamError, g.attach, l)

    def test_listener_non_callable_handler(self):
        """ Listener with non-callable handler.

        Test that an exception is raised if a listener with non-callable
        event handler is added.

        """
        g = GerritStream(StringIO("Dummy stream"))
        l = ListenerWithInvalidHandlerNotCallable()
        self.assertRaises(GerritStreamError, g.attach, l)

    def test_listener_valid_handler(self):
        """ Test that a valid listener can be added. """
        g = GerritStream(StringIO("Dummy stream"))
        l = ListenerWithValidHandler()
        self.assertEquals(len(g.listeners), 0)
        g.attach(l)
        self.assertEquals(len(g.listeners), 1)
        self.assertEquals(g.listeners[0], l)

    def test_add_same_listener_multiple_times(self):
        """ Test that the same listener will only be added once. """
        g = GerritStream(StringIO("Dummy stream"))
        l = ListenerWithValidHandler()
        self.assertEquals(len(g.listeners), 0)
        g.attach(l)
        self.assertEquals(len(g.listeners), 1)
        self.assertEquals(g.listeners[0], l)
        g.attach(l)
        self.assertEquals(len(g.listeners), 1)
        self.assertEquals(g.listeners[0], l)

    def test_add_multiple_listeners(self):
        """ Test that multiple listeners can be added. """
        g = GerritStream(StringIO("Dummy stream"))
        l = ListenerWithValidHandler()
        self.assertEquals(len(g.listeners), 0)
        g.attach(l)
        self.assertEquals(len(g.listeners), 1)
        self.assertEquals(g.listeners[0], l)
        l2 = ListenerWithValidHandler()
        g.attach(l2)
        self.assertEquals(len(g.listeners), 2)
        self.assertEquals(g.listeners[0], l)
        self.assertEquals(g.listeners[1], l2)

    def test_detach_listener(self):
        """ Test that a listener can be detached. """
        g = GerritStream(StringIO("Dummy stream"))
        l = ListenerWithValidHandler()
        self.assertEquals(len(g.listeners), 0)
        g.attach(l)
        self.assertEquals(len(g.listeners), 1)
        self.assertEquals(g.listeners[0], l)
        g.detach(l)
        self.assertEquals(len(g.listeners), 0)

    def test_detach_not_attached_listener(self):
        """ Detach non-attached listener.

        Test that the class behaves correctly if a not-attached
        listener is detached.

        """
        g = GerritStream(StringIO("Dummy stream"))
        l = ListenerWithValidHandler()
        self.assertEquals(len(g.listeners), 0)
        g.detach(l)
        self.assertEquals(len(g.listeners), 0)

    def test_stream_without_read_method(self):
        """ Create stream with input that does not have read() method.

        Test that the class raises an exception when trying to stream
        from an input that does not have a read() method.

        """
        g = GerritStream("String does not have read()")
        self.assertRaises(GerritStreamError, g.read)

if __name__ == '__main__':
    unittest.main()
