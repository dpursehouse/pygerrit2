#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from gerrit_stream import GerritStream, GerritStreamError


class ListenerWithNoHandler():
    """ Dummy listener class with no event handler.
    """
    def __init__(self):
        pass


class ListenerWithInvalidHandler():
    """ Dummy listener class with invalid event handler.
    """
    def __init__(self):
        pass

    def on_gerrit_event(self):
        pass


class ListenerWithValidHandler():
    """ Dummy listener class.
    """
    def __init__(self):
        pass

    def on_gerrit_event(self, event):
        pass


class TestGerritStream(unittest.TestCase):
    """ Test that the GerritStream class behaves correctly.
    """

    def test_listener_no_handler(self):
        """ Test that an exception is raised if a listener is
        attached without an event handler method.
        """
        g = GerritStream()
        l = ListenerWithNoHandler()
        self.assertRaises(GerritStreamError, g.attach, l)

    def test_listener_invalid_handler(self):
        """ Test that an exception is raised if a listener is
        attached with an invalid event handler method.
        """
        g = GerritStream()
        l = ListenerWithInvalidHandler()
        self.assertRaises(GerritStreamError, g.attach, l)

    def test_listener_valid_handler(self):
        """ Test that a valid listener can be added.
        """
        g = GerritStream()
        l = ListenerWithValidHandler()
        self.assertEquals(len(g.listeners), 0)
        g.attach(l)
        self.assertEquals(len(g.listeners), 1)
        self.assertEquals(g.listeners[0], l)

    def test_add_same_listener_multiple_times(self):
        """ Test that the same listener will only be added once.
        """
        g = GerritStream()
        l = ListenerWithValidHandler()
        self.assertEquals(len(g.listeners), 0)
        g.attach(l)
        self.assertEquals(len(g.listeners), 1)
        self.assertEquals(g.listeners[0], l)
        g.attach(l)
        self.assertEquals(len(g.listeners), 1)
        self.assertEquals(g.listeners[0], l)

    def test_add_multiple_listeners(self):
        """ Test that multiple listeners can be added.
        """
        g = GerritStream()
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
        """ Test that a listener can be detached.
        """
        g = GerritStream()
        l = ListenerWithValidHandler()
        self.assertEquals(len(g.listeners), 0)
        g.attach(l)
        self.assertEquals(len(g.listeners), 1)
        self.assertEquals(g.listeners[0], l)
        g.detach(l)
        self.assertEquals(len(g.listeners), 0)

    def test_detach_not_attached_listener(self):
        """ Test that the class behaves correctly if a not-attached
        listener is detached.
        """
        g = GerritStream()
        l = ListenerWithValidHandler()
        self.assertEquals(len(g.listeners), 0)
        g.detach(l)
        self.assertEquals(len(g.listeners), 0)

if __name__ == '__main__':
    unittest.main()
