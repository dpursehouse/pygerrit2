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

import pytest
import unittest
from pygerrit2.rest import GerritRestAPI, GerritReview
from requests.auth import HTTPBasicAuth
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready


class GerritContainer(DockerContainer):
    """Gerrit container."""

    def __init__(self, version):
        """Construct a GerritContainer with the given version."""
        super(GerritContainer, self).__init__(
            "gerritcodereview/gerrit:" + version)
        self.with_exposed_ports(8080)


@wait_container_is_ready()
def _connect(api):
    api.get("")


@pytest.fixture(scope="module", params=["2.14.8", "2.15.2"])
def gerrit_api(request):
    """Create a Gerrit container for the given version and return an API."""
    with GerritContainer(request.param) as gerrit:
        port = gerrit.get_exposed_port(8080)
        url = "http://localhost:%s" % port
        auth = HTTPBasicAuth("admin", "secret")
        api = GerritRestAPI(url=url, auth=auth)
        _connect(api)
        yield api


def test_live_server(gerrit_api):
    """Run the tests."""
    # Create the project
    projectinput = {"create_empty_commit": "true"}
    gerrit_api.put("/projects/test-project", json=projectinput)

    # Post with content as dict
    changeinput = {"project": "test-project",
                   "subject": "subject",
                   "branch": "master",
                   "topic": "topic"}
    change = gerrit_api.post("/changes/", json=changeinput)
    change_id = change["id"]

    # Get
    gerrit_api.get("/changes/" + change_id)

    # Put with content as string
    gerrit_api.put("/changes/" + change_id + "/edit/foo", data="content")

    # Put with no content
    gerrit_api.put("/changes/" + change_id + "/edit/foo")

    # Review by API
    rev = GerritReview()
    rev.set_message("Review from live test")
    rev.add_labels({"Code-Review": 1})
    gerrit_api.review(change_id, "current", rev)


if __name__ == '__main__':
    unittest.main()
