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

import re
import unittest

from mock import patch
from pygerrit2 import GerritReviewMessageFormatter, GerritReview
from pygerrit2 import HTTPBasicAuthFromNetrc, HTTPDigestAuthFromNetrc, Anonymous
from pygerrit2 import GerritRestAPI

EXPECTED_TEST_CASE_FIELDS = ["header", "footer", "paragraphs", "result"]


TEST_CASES = [
    {"header": None, "footer": None, "paragraphs": [], "result": ""},
    {"header": "Header", "footer": "Footer", "paragraphs": [], "result": ""},
    {"header": None, "footer": None, "paragraphs": ["Test"], "result": "Test"},
    {
        "header": None,
        "footer": None,
        "paragraphs": ["Test", "Test"],
        "result": "Test\n\nTest",
    },
    {
        "header": "Header",
        "footer": None,
        "paragraphs": ["Test"],
        "result": "Header\n\nTest",
    },
    {
        "header": "Header",
        "footer": None,
        "paragraphs": ["Test", "Test"],
        "result": "Header\n\nTest\n\nTest",
    },
    {
        "header": "Header",
        "footer": "Footer",
        "paragraphs": ["Test", "Test"],
        "result": "Header\n\nTest\n\nTest\n\nFooter",
    },
    {
        "header": "Header",
        "footer": "Footer",
        "paragraphs": [["One"]],
        "result": "Header\n\n* One\n\nFooter",
    },
    {
        "header": "Header",
        "footer": "Footer",
        "paragraphs": [["One", "Two"]],
        "result": "Header\n\n* One\n* Two\n\nFooter",
    },
    {
        "header": "Header",
        "footer": "Footer",
        "paragraphs": ["Test", ["One"], "Test"],
        "result": "Header\n\nTest\n\n* One\n\nTest\n\nFooter",
    },
    {
        "header": "Header",
        "footer": "Footer",
        "paragraphs": ["Test", ["One", "Two"], "Test"],
        "result": "Header\n\nTest\n\n* One\n* Two\n\nTest\n\nFooter",
    },
    {
        "header": "Header",
        "footer": "Footer",
        "paragraphs": ["Test", "Test", ["One"]],
        "result": "Header\n\nTest\n\nTest\n\n* One\n\nFooter",
    },
    {
        "header": None,
        "footer": None,
        "paragraphs": [["* One", "* Two"]],
        "result": "* One\n* Two",
    },
    {
        "header": None,
        "footer": None,
        "paragraphs": [["*    One  ", "    * Two  "]],
        "result": "* One\n* Two",
    },
    {"header": None, "footer": None, "paragraphs": [["*", "*"]], "result": ""},
    {"header": None, "footer": None, "paragraphs": [["", ""]], "result": ""},
    {"header": None, "footer": None, "paragraphs": [["  ", "  "]], "result": ""},
    {
        "header": None,
        "footer": None,
        "paragraphs": [["* One", "  ", "* Two"]],
        "result": "* One\n* Two",
    },
]


class TestGerritReviewMessageFormatter(unittest.TestCase):
    """Test that the GerritReviewMessageFormatter class behaves properly."""

    def _check_test_case_fields(self, test_case, i):
        for field in EXPECTED_TEST_CASE_FIELDS:
            self.assertTrue(
                field in test_case,
                "field '%s' not present in test case #%d" % (field, i),
            )
        self.assertTrue(
            isinstance(test_case["paragraphs"], list),
            "'paragraphs' field is not a list in test case #%d" % i,
        )

    def test_is_empty(self):
        """Test if message is empty for missing header and footer."""
        fmt = GerritReviewMessageFormatter(header=None, footer=None)
        self.assertTrue(fmt.is_empty())
        fmt.append(["test"])
        self.assertFalse(fmt.is_empty())

    def test_message_formatting(self):
        """Test message formatter for different test cases."""
        for i, test_case in enumerate(TEST_CASES):
            self._check_test_case_fields(test_case, i)
            fmt = GerritReviewMessageFormatter(
                header=test_case["header"], footer=test_case["footer"]
            )
            for paragraph in test_case["paragraphs"]:
                fmt.append(paragraph)
            msg = fmt.format()
            self.assertEqual(
                msg,
                test_case["result"],
                "Formatted message does not match expected "
                "result in test case #%d:\n[%s]" % (i, msg),
            )


class TestGerritReview(unittest.TestCase):
    """Test that the GerritReview class behaves properly."""

    def test_str(self):
        """Test for str function."""
        obj = GerritReview()
        self.assertEqual(str(obj), "{}")

        obj2 = GerritReview(labels={"Verified": 1, "Code-Review": -1})
        self.assertEqual(str(obj2), '{"labels": {"Code-Review": -1, "Verified": 1}}')

        obj3 = GerritReview(
            comments=[{"filename": "Makefile", "line": 10, "message": "test"}]
        )
        self.assertEqual(
            str(obj3), '{"comments": {"Makefile": [{"line": 10, "message": "test"}]}}'
        )

        obj4 = GerritReview(
            labels={"Verified": 1, "Code-Review": -1},
            comments=[{"filename": "Makefile", "line": 10, "message": "test"}],
        )
        self.assertEqual(
            str(obj4),
            '{"comments": {"Makefile": [{"line": 10, "message": "test"}]},'
            ' "labels": {"Code-Review": -1, "Verified": 1}}',
        )

        obj5 = GerritReview(
            comments=[
                {"filename": "Makefile", "line": 15, "message": "test"},
                {"filename": "Make", "line": 10, "message": "test1"},
            ]
        )
        self.assertEqual(
            str(obj5),
            '{"comments": {"Make": [{"line": 10, "message": "test1"}],'
            ' "Makefile": [{"line": 15, "message": "test"}]}}',
        )


class TestNetrcAuth(unittest.TestCase):
    """Test that netrc authentication works."""

    def test_basic_auth_from_netrc(self):
        """Test that the HTTP basic auth is taken from netrc."""
        with patch("pygerrit2.rest.auth._get_netrc_auth") as mock_netrc:
            mock_netrc.return_value = ("netrcuser", "netrcpass")
            auth = HTTPBasicAuthFromNetrc(url="http://review.example.com")
            assert auth.username == "netrcuser"
            assert auth.password == "netrcpass"

    def test_digest_auth_from_netrc(self):
        """Test that the HTTP digest auth is taken from netrc."""
        with patch("pygerrit2.rest.auth._get_netrc_auth") as mock_netrc:
            mock_netrc.return_value = ("netrcuser", "netrcpass")
            auth = HTTPDigestAuthFromNetrc(url="http://review.example.com")
            assert auth.username == "netrcuser"
            assert auth.password == "netrcpass"

    def test_basic_auth_from_netrc_fails(self):
        """Test that an exception is raised when credentials are not found."""
        with self.assertRaises(ValueError) as exc:
            HTTPBasicAuthFromNetrc(url="http://review.example.com")
        assert str(exc.exception) == "netrc missing or no credentials found in netrc"

    def test_digest_auth_from_netrc_fails(self):
        """Test that an exception is raised when credentials are not found."""
        with self.assertRaises(ValueError) as exc:
            HTTPDigestAuthFromNetrc(url="http://review.example.com")
        assert str(exc.exception) == "netrc missing or no credentials found in netrc"

    def test_default_to_basic_auth_from_netrc(self):
        """Test auth defaults to HTTP basic from netrc when not specified."""
        with patch("pygerrit2.rest.auth._get_netrc_auth") as mock_netrc:
            mock_netrc.return_value = ("netrcuser", "netrcpass")
            api = GerritRestAPI(url="http://review.example.com")
            assert isinstance(api.auth, HTTPBasicAuthFromNetrc)
            assert api.url.endswith("/a/")

    def test_default_to_no_auth_when_not_in_netrc(self):
        """Test auth defaults to none when not specified and not in netrc."""
        with patch("pygerrit2.rest.auth._get_netrc_auth") as mock_netrc:
            mock_netrc.return_value = None
            api = GerritRestAPI(url="http://review.example.com")
            assert api.auth is None
            assert not api.url.endswith("/a/")

    def test_invalid_auth_type(self):
        """Test that an exception is raised for invalid auth type."""
        with self.assertRaises(ValueError) as exc:
            GerritRestAPI(url="http://review.example.com", auth="foo")
        assert re.search(r"Invalid auth type", str(exc.exception))

    def test_explicit_anonymous_with_netrc(self):
        """Test explicit anonymous access when credentials are in netrc."""
        with patch("pygerrit2.rest.auth._get_netrc_auth") as mock_netrc:
            mock_netrc.return_value = ("netrcuser", "netrcpass")
            auth = Anonymous()
            api = GerritRestAPI(url="http://review.example.com", auth=auth)
            assert api.auth is None
            assert not api.url.endswith("/a/")

    def test_explicit_anonymous_without_netrc(self):
        """Test explicit anonymous access when credentials are not in netrc."""
        with patch("pygerrit2.rest.auth._get_netrc_auth") as mock_netrc:
            mock_netrc.return_value = None
            auth = Anonymous()
            api = GerritRestAPI(url="http://review.example.com", auth=auth)
            assert api.auth is None
            assert not api.url.endswith("/a/")


class TestKwargsTranslation(unittest.TestCase):
    """Test that kwargs translation works."""

    def test_data_and_json(self):
        """Test that `json` and `data` cannot be used at the same time."""
        api = GerritRestAPI(url="http://review.example.com")
        with self.assertRaises(ValueError) as exc:
            api.translate_kwargs(data="d", json="j")
        assert re.search(r"Cannot use data and json together", str(exc.exception))

    def test_data_as_dict_converts_to_json_and_header_added(self):
        """Test that `data` dict is converted to `json`.

        Also test that a Content-Type header is added.
        """
        api = GerritRestAPI(url="http://review.example.com")
        data = {"a": "a"}
        result = api.translate_kwargs(data=data)
        assert "json" in result
        assert "data" not in result
        assert "headers" in result
        headers = result["headers"]
        assert "Content-Type" in headers
        assert result["json"] == {"a": "a"}
        assert headers["Content-Type"] == "application/json;charset=UTF-8"

    def test_json_is_unchanged_and_header_added(self):
        """Test that `json` is unchanged and a Content-Type header is added."""
        api = GerritRestAPI(url="http://review.example.com")
        json = {"a": "a"}
        result = api.translate_kwargs(json=json)
        assert "json" in result
        assert "data" not in result
        assert "headers" in result
        headers = result["headers"]
        assert "Content-Type" in headers
        assert result["json"] == {"a": "a"}
        assert headers["Content-Type"] == "application/json;charset=UTF-8"

    def test_json_no_side_effect_on_subsequent_call(self):
        """Test that subsequent call is not polluted with results of previous.

        If the translate_kwargs method is called, resulting in the content-type
        header being added, the header should not also be added on a subsequent
        call that does not need it.
        """
        api = GerritRestAPI(url="http://review.example.com")
        json = {"a": "a"}
        result = api.translate_kwargs(json=json)
        assert "json" in result
        assert "data" not in result
        assert "headers" in result
        headers = result["headers"]
        assert "Content-Type" in headers
        assert result["json"] == {"a": "a"}
        assert headers["Content-Type"] == "application/json;charset=UTF-8"
        kwargs = {"a": "a", "b": "b"}
        result = api.translate_kwargs(**kwargs)
        assert "json" not in result
        assert "data" not in result
        assert "a" in result
        assert "b" in result
        assert "headers" in result
        headers = result["headers"]
        assert "Content-Type" not in headers

    def test_kwargs_unchanged_when_no_data_or_json(self):
        """Test that `json` or `data` are not added when not passed."""
        api = GerritRestAPI(url="http://review.example.com")
        kwargs = {"a": "a", "b": "b"}
        result = api.translate_kwargs(**kwargs)
        assert "json" not in result
        assert "data" not in result
        assert "a" in result
        assert "b" in result
        assert "headers" in result
        headers = result["headers"]
        assert "Content-Type" not in headers

    def test_data_as_string_is_unchanged(self):
        """Test that `data` is unchanged when passed as a string."""
        api = GerritRestAPI(url="http://review.example.com")
        kwargs = {"data": "Content with non base64 valid chars åäö"}
        result = api.translate_kwargs(**kwargs)
        assert "json" not in result
        assert "data" in result
        assert result["data"] == "Content with non base64 valid chars åäö"
        assert "headers" in result
        headers = result["headers"]
        assert "Content-Type" not in headers


if __name__ == "__main__":
    unittest.main()
