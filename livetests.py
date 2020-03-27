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
from pygerrit2 import GerritRestAPI, GerritReview, HTTPBasicAuth, Anonymous
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready


TEST_TOPIC = "test-topic"


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


@pytest.fixture(
    scope="module", params=["2.14.20", "2.15.18", "2.16.17", "3.0.8", "3.1.3"]
)
def gerrit_api(request):
    """Create a Gerrit container for the given version and return an API."""
    with GerritContainer(request.param) as gerrit:
        port = gerrit.get_exposed_port(8080)
        url = "http://localhost:%s" % port
        api = GerritRestAPI(url=url, auth=Anonymous())
        _initialize(api)
        auth = HTTPBasicAuth("admin", "secret")
        api = GerritRestAPI(url=url, auth=auth)
        yield api


class TestGerritAgainstLiveServer(object):
    """Run tests against a live server."""

    def _get_test_change(self, gerrit_api, topic=TEST_TOPIC):
        results = gerrit_api.get("/changes/?q=topic:" + topic)
        assert len(results) == 1
        return results[0]

    def test_put_with_json_dict(self, gerrit_api):
        """Test a PUT request passing data as a dict to `json`.

        Tests that the PUT request works as expected when data is passed
        via the `json` argument as a `dict`.

        Creates the test project which is used by subsequent tests.
        """
        projectinput = {"create_empty_commit": "true"}
        gerrit_api.put("/projects/test-project", json=projectinput)
        gerrit_api.get("/projects/test-project")

    def test_put_with_data_dict(self, gerrit_api):
        """Test a PUT request passing data as a dict to `data`.

        Tests that the PUT request works as expected when data is passed
        via the `data` argument as a `dict`.
        """
        description = {"description": "New Description"}
        gerrit_api.put("/projects/test-project/description", data=description)
        project = gerrit_api.get("/projects/test-project")
        assert project["description"] == "New Description"

    def test_post_with_data_dict_and_no_data(self, gerrit_api):
        """Test a POST request passing data as a dict to `data`.

        Tests that the POST request works as expected when data is passed
        via the `data` argument as a `dict`.
        """
        changeinput = {
            "project": "test-project",
            "subject": "subject",
            "branch": "master",
            "topic": "post-with-data",
        }
        result = gerrit_api.post("/changes/", data=changeinput)
        change = self._get_test_change(gerrit_api, "post-with-data")
        assert change["id"] == result["id"]

        # Subsequent post without data or json should not have the Content-Type
        # json header, and should succeed.
        result = gerrit_api.post("/changes/" + change["id"] + "/abandon")
        assert result["status"] == "ABANDONED"

    def test_post_with_json_dict(self, gerrit_api):
        """Test a POST request passing data as a dict to `json`.

        Tests that the POST request works as expected when data is passed
        via the `json` argument as a `dict`.

        Creates the change which is used by subsequent tests.
        """
        changeinput = {
            "project": "test-project",
            "subject": "subject",
            "branch": "master",
            "topic": TEST_TOPIC,
        }
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
        gerrit_api.put(
            "/changes/" + change_id + "/edit/foo",
            data="Content with non base64 valid chars åäö",
        )

    def test_put_json_content(self, gerrit_api):
        """Test a PUT request with a json file content (issue #54)."""
        change_id = self._get_test_change(gerrit_api)["id"]
        content = """{"foo" : "bar"}"""
        gerrit_api.put("/changes/" + change_id + "/edit/file.json", data=content)

    def test_get_base64_data(self, gerrit_api):
        """Test a GET request on an API that returns base64 encoded response.

        Tests that the headers can be overridden on the GET call, resulting
        in the data being returned as text/plain, and that the content of the
        response can be base64 decoded.
        """
        change_id = self._get_test_change(gerrit_api)["id"]
        response = gerrit_api.get(
            "/changes/" + change_id + "/edit/foo", headers={"Accept": "text/plain"}
        )

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
        review.set_tag("a_test_tag")
        gerrit_api.review(change_id, "current", review)


if __name__ == "__main__":
    unittest.main()
