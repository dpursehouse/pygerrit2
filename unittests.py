#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

"""Unit tests for the Pygerrit2 helper methods."""

import unittest

from mock import patch
from pygerrit2 import GerritReviewMessageFormatter, GerritReview
from pygerrit2 import HTTPBasicAuthFromNetrc, HTTPDigestAuthFromNetrc
from pygerrit2.rest import _merge_dict

EXPECTED_TEST_CASE_FIELDS = ['header', 'footer', 'paragraphs', 'result']


TEST_CASES = [
    {'header': None,
     'footer': None,
     'paragraphs': [],
     'result': ""},
    {'header': "Header",
     'footer': "Footer",
     'paragraphs': [],
     'result': ""},
    {'header': None,
     'footer': None,
     'paragraphs': ["Test"],
     'result': "Test"},
    {'header': None,
     'footer': None,
     'paragraphs': ["Test", "Test"],
     'result': "Test\n\nTest"},
    {'header': "Header",
     'footer': None,
     'paragraphs': ["Test"],
     'result': "Header\n\nTest"},
    {'header': "Header",
     'footer': None,
     'paragraphs': ["Test", "Test"],
     'result': "Header\n\nTest\n\nTest"},
    {'header': "Header",
     'footer': "Footer",
     'paragraphs': ["Test", "Test"],
     'result': "Header\n\nTest\n\nTest\n\nFooter"},
    {'header': "Header",
     'footer': "Footer",
     'paragraphs': [["One"]],
     'result': "Header\n\n* One\n\nFooter"},
    {'header': "Header",
     'footer': "Footer",
     'paragraphs': [["One", "Two"]],
     'result': "Header\n\n* One\n* Two\n\nFooter"},
    {'header': "Header",
     'footer': "Footer",
     'paragraphs': ["Test", ["One"], "Test"],
     'result': "Header\n\nTest\n\n* One\n\nTest\n\nFooter"},
    {'header': "Header",
     'footer': "Footer",
     'paragraphs': ["Test", ["One", "Two"], "Test"],
     'result': "Header\n\nTest\n\n* One\n* Two\n\nTest\n\nFooter"},
    {'header': "Header",
     'footer': "Footer",
     'paragraphs': ["Test", "Test", ["One"]],
     'result': "Header\n\nTest\n\nTest\n\n* One\n\nFooter"},
    {'header': None,
     'footer': None,
     'paragraphs': [["* One", "* Two"]],
     'result': "* One\n* Two"},
    {'header': None,
     'footer': None,
     'paragraphs': [["*    One  ", "    * Two  "]],
     'result': "* One\n* Two"},
    {'header': None,
     'footer': None,
     'paragraphs': [["*", "*"]],
     'result': ""},
    {'header': None,
     'footer': None,
     'paragraphs': [["", ""]],
     'result': ""},
    {'header': None,
     'footer': None,
     'paragraphs': [["  ", "  "]],
     'result': ""},
    {'header': None,
     'footer': None,
     'paragraphs': [["* One", "  ", "* Two"]],
     'result': "* One\n* Two"}]


class TestMergeDict(unittest.TestCase):
    """Tests for the `_merge_dict` method."""

    def test_merge_into_empty_dict(self):
        """Test merging into an empty dict."""
        dct = {}
        _merge_dict(dct, {'a': 1, 'b': 2})
        self.assertEqual(dct, {'a': 1, 'b': 2})

    def test_merge_flat(self):
        """Test merging a flat dict."""
        dct = {'c': 3}
        _merge_dict(dct, {'a': 1, 'b': 2})
        self.assertEqual(dct, {'a': 1, 'b': 2, 'c': 3})

    def test_merge_with_override(self):
        """Test merging a dict and overriding values."""
        dct = {'a': 1}
        _merge_dict(dct, {'a': 0, 'b': 2})
        self.assertEqual(dct, {'a': 0, 'b': 2})

    def test_merge_two_levels(self):
        """Test merging a dict with two levels."""
        dct = {
            'a': {
                'A': 1,
                'AA': 2,
            },
            'b': {
                'B': 1,
                'BB': 2,
            },
        }
        overrides = {
            'a': {
                'AAA': 3,
            },
            'b': {
                'BBB': 3,
            },
        }
        _merge_dict(dct, overrides)
        self.assertEqual(
            dct,
            {
                'a': {
                    'A': 1,
                    'AA': 2,
                    'AAA': 3,
                },
                'b': {
                    'B': 1,
                    'BB': 2,
                    'BBB': 3,
                },
            }
        )


class TestGerritReviewMessageFormatter(unittest.TestCase):
    """Test that the GerritReviewMessageFormatter class behaves properly."""

    def _check_test_case_fields(self, test_case, i):
        for field in EXPECTED_TEST_CASE_FIELDS:
            self.assertTrue(field in test_case,
                            "field '%s' not present in test case #%d" %
                            (field, i))
        self.assertTrue(
            isinstance(test_case['paragraphs'], list),
            "'paragraphs' field is not a list in test case #%d" % i)

    def test_is_empty(self):
        """Test if message is empty for missing header and footer."""
        fmt = GerritReviewMessageFormatter(header=None, footer=None)
        self.assertTrue(fmt.is_empty())
        fmt.append(['test'])
        self.assertFalse(fmt.is_empty())

    def test_message_formatting(self):
        """Test message formatter for different test cases."""
        for i, test_case in enumerate(TEST_CASES):
            self._check_test_case_fields(test_case, i)
            fmt = GerritReviewMessageFormatter(header=test_case['header'],
                                               footer=test_case['footer'])
            for paragraph in test_case['paragraphs']:
                fmt.append(paragraph)
            msg = fmt.format()
            self.assertEqual(msg, test_case['result'],
                             "Formatted message does not match expected "
                             "result in test case #%d:\n[%s]" % (i, msg))


class TestGerritReview(unittest.TestCase):
    """Test that the GerritReview class behaves properly."""

    def test_str(self):
        """Test for str function."""
        obj = GerritReview()
        self.assertEqual(str(obj), '{}')

        obj2 = GerritReview(labels={'Verified': 1, 'Code-Review': -1})
        self.assertEqual(
            str(obj2),
            '{"labels": {"Code-Review": -1, "Verified": 1}}')

        obj3 = GerritReview(comments=[{'filename': 'Makefile',
                                       'line': 10, 'message': 'test'}])
        self.assertEqual(
            str(obj3),
            '{"comments": {"Makefile": [{"line": 10, "message": "test"}]}}')

        obj4 = GerritReview(labels={'Verified': 1, 'Code-Review': -1},
                            comments=[{'filename': 'Makefile', 'line': 10,
                                       'message': 'test'}])
        self.assertEqual(
            str(obj4),
            '{"comments": {"Makefile": [{"line": 10, "message": "test"}]},'
            ' "labels": {"Code-Review": -1, "Verified": 1}}')

        obj5 = GerritReview(comments=[
            {'filename': 'Makefile', 'line': 15, 'message': 'test'},
            {'filename': 'Make', 'line': 10, 'message': 'test1'}
        ])
        self.assertEqual(
            str(obj5),
            '{"comments": {"Make": [{"line": 10, "message": "test1"}],'
            ' "Makefile": [{"line": 15, "message": "test"}]}}')


class TestNetrcAuth(unittest.TestCase):
    """Test that netrc authentication works."""

    def test_basic_auth_from_netrc(self):
        """Test that the HTTP basic auth is taken from netrc."""
        with patch('pygerrit2.rest.auth._get_netrc_auth') as mock_netrc:
            mock_netrc.return_value = ("netrcuser", "netrcpass")
            auth = HTTPBasicAuthFromNetrc(url="http://review.example.com")
            assert auth.username == "netrcuser"
            assert auth.password == "netrcpass"

    def test_digest_auth_from_netrc(self):
        """Test that the HTTP digest auth is taken from netrc."""
        with patch('pygerrit2.rest.auth._get_netrc_auth') as mock_netrc:
            mock_netrc.return_value = ("netrcuser", "netrcpass")
            auth = HTTPDigestAuthFromNetrc(url="http://review.example.com")
            assert auth.username == "netrcuser"
            assert auth.password == "netrcpass"

    def test_basic_auth_from_netrc_fails(self):
        """Test that an exception is raised when credentials are not found."""
        with self.assertRaises(ValueError) as exc:
            HTTPBasicAuthFromNetrc(url="http://review.example.com")
        assert str(exc.exception) == \
            "netrc missing or no credentials found in netrc"

    def test_digest_auth_from_netrc_fails(self):
        """Test that an exception is raised when credentials are not found."""
        with self.assertRaises(ValueError) as exc:
            HTTPDigestAuthFromNetrc(url="http://review.example.com")
        assert str(exc.exception) == \
            "netrc missing or no credentials found in netrc"


if __name__ == '__main__':
    unittest.main()
