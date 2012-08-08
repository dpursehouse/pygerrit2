#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Unit tests for the event factory. """

import unittest

from pygerrit.events import GerritEventFactory


class TestGerritEventFactory(unittest.TestCase):

    """ Test that the event factory behaves properly. """

    def test_singleton(self):
        """ Test that the event factory is a singleton. """
        factory1 = GerritEventFactory()
        factory2 = GerritEventFactory()
        self.assertEquals(factory1, factory2)


if __name__ == '__main__':
    unittest.main()
