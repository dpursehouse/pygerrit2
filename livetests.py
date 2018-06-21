#!/usr/bin/env python
# -*- coding: utf-8 -*-

# The MIT License
#
# Copyright 2018 David Pursehouse. All rights reserved.
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

"""Live server tests."""

import base64
import pytest
import unittest
from pygerrit2 import GerritRestAPI, GerritReview, HTTPBasicAuth, \
    HTTPDigestAuth
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready


class GerritContainer(DockerContainer):
    """Gerrit container."""

    def __init__(self, version):
        """Construct a GerritContainer with the given version."""
        image = "gerritcodereview/gerrit:" + version
        super(GerritContainer, self).__init__(image)
        self.with_exposed_ports(8080)


@wait_container_is_ready()
def _initialize(api):
    api.get("/changes/")


@pytest.fixture(scope="module", params=["2.13.11", "2.14.9", "2.15.2"])
def gerrit_api(request):
    """Create a Gerrit container for the given version and return an API."""
    with GerritContainer(request.param) as gerrit:
        port = gerrit.get_exposed_port(8080)
        url = "http://localhost:%s" % port
        if request.param == "2.13.11":
            auth = HTTPDigestAuth("admin", "secret")
        else:
            auth = HTTPBasicAuth("admin", "secret")
        api = GerritRestAPI(url=url, auth=auth)
        _initialize(api)
        yield api


class TestGerritAgainstLiveServer(object):
    """Run tests against a live server."""

    TEST_TOPIC = "test-topic"

    def _get_test_change(self, gerrit_api):
        results = gerrit_api.get("/changes/?q=topic:" + self.TEST_TOPIC)
        assert len(results) == 1
        return results[0]

    def test_put_with_json_dict(self, gerrit_api):
        """Test a PUT request passing data as a dict to `json`.

        Tests that the PUT request works as expected when data is passed
        via the `json` argument as a `dict`.

        Creates the test project which is used by subsequent tests.

        """
        # Creates the project which will be used by subsequent tests
        projectinput = {"create_empty_commit": "true"}
        gerrit_api.put("/projects/test-project", json=projectinput)
        gerrit_api.get("/projects/test-project")

    def test_post_with_json_dict(self, gerrit_api):
        """Test a POST request passing data as a dict to `json`.

        Tests that the POST request works as expected when data is passed
        via the `json` argument as a `dict`.

        Creates the change which is used by subsequent tests.
        """
        # Creates the change which will be used by subsequent tests
        changeinput = {"project": "test-project",
                       "subject": "subject",
                       "branch": "master",
                       "topic": self.TEST_TOPIC}
        result = gerrit_api.post("/changes/", json=changeinput)
        change = self._get_test_change(gerrit_api)
        assert change["id"] == result["id"]

    def test_put_with_data_as_string(self, gerrit_api):
        """Test a PUT request passing data as a string to `data`.

        Tests that the PUT request works as expected when data is passed
        via the `data` parameter as a string.

        Creates a change edit that is checked in the subsequent test.
        """
        change_id = self._get_test_change(gerrit_api)["id"]
        gerrit_api.put("/changes/" + change_id + "/edit/foo",
                       data="Content with non base64 valid chars åäö")

    def test_get_base64_data(self, gerrit_api):
        """Test a GET request on an API that returns base64 encoded response.

        Tests that the headers can be overridden on the GET call, resulting
        in the data being returned as text/plain, and that the content of the
        response can be base64 decoded.
        """
        change_id = self._get_test_change(gerrit_api)["id"]
        response = gerrit_api.get("/changes/" + change_id + "/edit/foo",
                                  headers={'Accept': 'text/plain'})

        # Will raise binascii.Error if content is not properly encoded
        base64.b64decode(response)

    def test_get_patch_zip(self, gerrit_api):
        """Test a GET request to get a patch file (issue #19)."""
        change_id = self._get_test_change(gerrit_api)["id"]
        gerrit_api.get("/changes/" + change_id + "/revisions/current/patch?zip")

    def test_put_with_no_content(self, gerrit_api):
        """Test a PUT request with no content."""
        change_id = self._get_test_change(gerrit_api)["id"]
        gerrit_api.put("/changes/" + change_id + "/edit/foo")

    def test_review(self, gerrit_api):
        """Test that a review can be posted by the review API."""
        change_id = self._get_test_change(gerrit_api)["id"]
        review = GerritReview()
        review.set_message("Review from live test")
        review.add_labels({"Code-Review": 1})
        gerrit_api.review(change_id, "current", review)


if __name__ == '__main__':
    unittest.main()
