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

""" Unit tests for the Gerrit event stream handler and event objects. """

import json
import os
import unittest

from pygerrit.events import PatchsetCreatedEvent, \
    RefUpdatedEvent, ChangeMergedEvent, CommentAddedEvent, \
    ChangeAbandonedEvent, ChangeRestoredEvent, \
    DraftPublishedEvent, GerritEventFactory, GerritEvent, UnhandledEvent, \
    ErrorEvent, MergeFailedEvent, ReviewerAddedEvent, TopicChangedEvent
from pygerrit.client import GerritClient


@GerritEventFactory.register("user-defined-event")
class UserDefinedEvent(GerritEvent):

    """ Dummy event class to test event registration. """

    def __init__(self, json_data):
        super(UserDefinedEvent, self).__init__(json_data)
        self.title = json_data['title']
        self.description = json_data['description']


def _create_event(name, gerrit):
    """ Create a new event.

    Read the contents of the file specified by `name` and load as JSON
    data, then add as an event in the `gerrit` client.

    """
    testfile = open(os.path.join("testdata", name + ".txt"))
    data = testfile.read().replace("\n", "")
    gerrit.put_event(data)
    return data


class TestGerritEvents(unittest.TestCase):
    def setUp(self):
        self.gerrit = GerritClient("review")

    def test_patchset_created(self):
        _create_event("patchset-created-event", self.gerrit)
        event = self.gerrit.get_event(False)
        self.assertTrue(isinstance(event, PatchsetCreatedEvent))
        self.assertEquals(event.name, "patchset-created")
        self.assertEquals(event.change.project, "project-name")
        self.assertEquals(event.change.branch, "branch-name")
        self.assertEquals(event.change.topic, "topic-name")
        self.assertEquals(event.change.change_id,
                          "Ideadbeefdeadbeefdeadbeefdeadbeefdeadbeef")
        self.assertEquals(event.change.number, "123456")
        self.assertEquals(event.change.subject, "Commit message subject")
        self.assertEquals(event.change.url, "http://review.example.com/123456")
        self.assertEquals(event.change.owner.name, "Owner Name")
        self.assertEquals(event.change.owner.email, "owner@example.com")
        self.assertEquals(event.patchset.number, "4")
        self.assertEquals(event.patchset.revision,
                          "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef")
        self.assertEquals(event.patchset.ref, "refs/changes/56/123456/4")
        self.assertEquals(event.patchset.uploader.name, "Uploader Name")
        self.assertEquals(event.patchset.uploader.email, "uploader@example.com")
        self.assertEquals(event.uploader.name, "Uploader Name")
        self.assertEquals(event.uploader.email, "uploader@example.com")

    def test_draft_published(self):
        _create_event("draft-published-event", self.gerrit)
        event = self.gerrit.get_event(False)
        self.assertTrue(isinstance(event, DraftPublishedEvent))
        self.assertEquals(event.name, "draft-published")
        self.assertEquals(event.change.project, "project-name")
        self.assertEquals(event.change.branch, "branch-name")
        self.assertEquals(event.change.topic, "topic-name")
        self.assertEquals(event.change.change_id,
                          "Ideadbeefdeadbeefdeadbeefdeadbeefdeadbeef")
        self.assertEquals(event.change.number, "123456")
        self.assertEquals(event.change.subject, "Commit message subject")
        self.assertEquals(event.change.url, "http://review.example.com/123456")
        self.assertEquals(event.change.owner.name, "Owner Name")
        self.assertEquals(event.change.owner.email, "owner@example.com")
        self.assertEquals(event.patchset.number, "4")
        self.assertEquals(event.patchset.revision,
                          "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef")
        self.assertEquals(event.patchset.ref, "refs/changes/56/123456/4")
        self.assertEquals(event.patchset.uploader.name, "Uploader Name")
        self.assertEquals(event.patchset.uploader.email, "uploader@example.com")
        self.assertEquals(event.uploader.name, "Uploader Name")
        self.assertEquals(event.uploader.email, "uploader@example.com")

    def test_ref_updated(self):
        _create_event("ref-updated-event", self.gerrit)
        event = self.gerrit.get_event(False)
        self.assertTrue(isinstance(event, RefUpdatedEvent))
        self.assertEquals(event.name, "ref-updated")
        self.assertEquals(event.ref_update.project, "project-name")
        self.assertEquals(event.ref_update.oldrev,
                          "0000000000000000000000000000000000000000")
        self.assertEquals(event.ref_update.newrev,
                          "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef")
        self.assertEquals(event.ref_update.refname, "refs/tags/refname")
        self.assertEquals(event.submitter.name, "Submitter Name")
        self.assertEquals(event.submitter.email, "submitter@example.com")

    def test_change_merged(self):
        _create_event("change-merged-event", self.gerrit)
        event = self.gerrit.get_event(False)
        self.assertTrue(isinstance(event, ChangeMergedEvent))
        self.assertEquals(event.name, "change-merged")
        self.assertEquals(event.change.project, "project-name")
        self.assertEquals(event.change.branch, "branch-name")
        self.assertEquals(event.change.topic, "topic-name")
        self.assertEquals(event.change.change_id,
                          "Ideadbeefdeadbeefdeadbeefdeadbeefdeadbeef")
        self.assertEquals(event.change.number, "123456")
        self.assertEquals(event.change.subject, "Commit message subject")
        self.assertEquals(event.change.url, "http://review.example.com/123456")
        self.assertEquals(event.change.owner.name, "Owner Name")
        self.assertEquals(event.change.owner.email, "owner@example.com")
        self.assertEquals(event.patchset.number, "4")
        self.assertEquals(event.patchset.revision,
                          "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef")
        self.assertEquals(event.patchset.ref, "refs/changes/56/123456/4")
        self.assertEquals(event.patchset.uploader.name, "Uploader Name")
        self.assertEquals(event.patchset.uploader.email, "uploader@example.com")
        self.assertEquals(event.submitter.name, "Submitter Name")
        self.assertEquals(event.submitter.email, "submitter@example.com")

    def test_merge_failed(self):
        _create_event("merge-failed-event", self.gerrit)
        event = self.gerrit.get_event(False)
        self.assertTrue(isinstance(event, MergeFailedEvent))
        self.assertEquals(event.name, "merge-failed")
        self.assertEquals(event.change.project, "project-name")
        self.assertEquals(event.change.branch, "branch-name")
        self.assertEquals(event.change.topic, "topic-name")
        self.assertEquals(event.change.change_id,
                          "Ideadbeefdeadbeefdeadbeefdeadbeefdeadbeef")
        self.assertEquals(event.change.number, "123456")
        self.assertEquals(event.change.subject, "Commit message subject")
        self.assertEquals(event.change.url, "http://review.example.com/123456")
        self.assertEquals(event.change.owner.name, "Owner Name")
        self.assertEquals(event.change.owner.email, "owner@example.com")
        self.assertEquals(event.patchset.number, "4")
        self.assertEquals(event.patchset.revision,
                          "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef")
        self.assertEquals(event.patchset.ref, "refs/changes/56/123456/4")
        self.assertEquals(event.patchset.uploader.name, "Uploader Name")
        self.assertEquals(event.patchset.uploader.email, "uploader@example.com")
        self.assertEquals(event.submitter.name, "Submitter Name")
        self.assertEquals(event.submitter.email, "submitter@example.com")
        self.assertEquals(event.reason, "Merge failed reason")

    def test_comment_added(self):
        _create_event("comment-added-event", self.gerrit)
        event = self.gerrit.get_event(False)
        self.assertTrue(isinstance(event, CommentAddedEvent))
        self.assertEquals(event.name, "comment-added")
        self.assertEquals(event.change.project, "project-name")
        self.assertEquals(event.change.branch, "branch-name")
        self.assertEquals(event.change.topic, "topic-name")
        self.assertEquals(event.change.change_id,
                          "Ideadbeefdeadbeefdeadbeefdeadbeefdeadbeef")
        self.assertEquals(event.change.number, "123456")
        self.assertEquals(event.change.subject, "Commit message subject")
        self.assertEquals(event.change.url, "http://review.example.com/123456")
        self.assertEquals(event.change.owner.name, "Owner Name")
        self.assertEquals(event.change.owner.email, "owner@example.com")
        self.assertEquals(event.patchset.number, "4")
        self.assertEquals(event.patchset.revision,
                          "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef")
        self.assertEquals(event.patchset.ref, "refs/changes/56/123456/4")
        self.assertEquals(event.patchset.uploader.name, "Uploader Name")
        self.assertEquals(event.patchset.uploader.email, "uploader@example.com")
        self.assertEquals(len(event.approvals), 2)
        self.assertEquals(event.approvals[0].category, "CRVW")
        self.assertEquals(event.approvals[0].description, "Code Review")
        self.assertEquals(event.approvals[0].value, "1")
        self.assertEquals(event.approvals[1].category, "VRIF")
        self.assertEquals(event.approvals[1].description, "Verified")
        self.assertEquals(event.approvals[1].value, "1")
        self.assertEquals(event.author.name, "Author Name")
        self.assertEquals(event.author.email, "author@example.com")

    def test_reviewer_added(self):
        _create_event("reviewer-added-event", self.gerrit)
        event = self.gerrit.get_event(False)
        self.assertTrue(isinstance(event, ReviewerAddedEvent))
        self.assertEquals(event.name, "reviewer-added")
        self.assertEquals(event.change.project, "project-name")
        self.assertEquals(event.change.branch, "branch-name")
        self.assertEquals(event.change.topic, "topic-name")
        self.assertEquals(event.change.change_id,
                          "Ideadbeefdeadbeefdeadbeefdeadbeefdeadbeef")
        self.assertEquals(event.change.number, "123456")
        self.assertEquals(event.change.subject, "Commit message subject")
        self.assertEquals(event.change.url, "http://review.example.com/123456")
        self.assertEquals(event.change.owner.name, "Owner Name")
        self.assertEquals(event.change.owner.email, "owner@example.com")
        self.assertEquals(event.patchset.number, "4")
        self.assertEquals(event.patchset.revision,
                          "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef")
        self.assertEquals(event.patchset.ref, "refs/changes/56/123456/4")
        self.assertEquals(event.patchset.uploader.name, "Uploader Name")
        self.assertEquals(event.patchset.uploader.email, "uploader@example.com")
        self.assertEquals(event.reviewer.name, "Reviewer Name")
        self.assertEquals(event.reviewer.email, "reviewer@example.com")

    def test_change_abandoned(self):
        _create_event("change-abandoned-event", self.gerrit)
        event = self.gerrit.get_event(False)
        self.assertTrue(isinstance(event, ChangeAbandonedEvent))
        self.assertEquals(event.name, "change-abandoned")
        self.assertEquals(event.change.project, "project-name")
        self.assertEquals(event.change.branch, "branch-name")
        self.assertEquals(event.change.topic, "topic-name")
        self.assertEquals(event.change.change_id,
                          "Ideadbeefdeadbeefdeadbeefdeadbeefdeadbeef")
        self.assertEquals(event.change.number, "123456")
        self.assertEquals(event.change.subject, "Commit message subject")
        self.assertEquals(event.change.url, "http://review.example.com/123456")
        self.assertEquals(event.change.owner.name, "Owner Name")
        self.assertEquals(event.change.owner.email, "owner@example.com")
        self.assertEquals(event.abandoner.name, "Abandoner Name")
        self.assertEquals(event.abandoner.email, "abandoner@example.com")
        self.assertEquals(event.reason, "Abandon reason")

    def test_change_restored(self):
        _create_event("change-restored-event", self.gerrit)
        event = self.gerrit.get_event(False)
        self.assertTrue(isinstance(event, ChangeRestoredEvent))
        self.assertEquals(event.name, "change-restored")
        self.assertEquals(event.change.project, "project-name")
        self.assertEquals(event.change.branch, "branch-name")
        self.assertEquals(event.change.topic, "topic-name")
        self.assertEquals(event.change.change_id,
                          "Ideadbeefdeadbeefdeadbeefdeadbeefdeadbeef")
        self.assertEquals(event.change.number, "123456")
        self.assertEquals(event.change.subject, "Commit message subject")
        self.assertEquals(event.change.url, "http://review.example.com/123456")
        self.assertEquals(event.change.owner.name, "Owner Name")
        self.assertEquals(event.change.owner.email, "owner@example.com")
        self.assertEquals(event.restorer.name, "Restorer Name")
        self.assertEquals(event.restorer.email, "restorer@example.com")
        self.assertEquals(event.reason, "Restore reason")

    def test_topic_changed(self):
        _create_event("topic-changed-event", self.gerrit)
        event = self.gerrit.get_event(False)
        self.assertTrue(isinstance(event, TopicChangedEvent))
        self.assertEquals(event.name, "topic-changed")
        self.assertEquals(event.change.project, "project-name")
        self.assertEquals(event.change.branch, "branch-name")
        self.assertEquals(event.change.topic, "topic-name")
        self.assertEquals(event.change.change_id,
                          "Ideadbeefdeadbeefdeadbeefdeadbeefdeadbeef")
        self.assertEquals(event.change.number, "123456")
        self.assertEquals(event.change.subject, "Commit message subject")
        self.assertEquals(event.change.url, "http://review.example.com/123456")
        self.assertEquals(event.change.owner.name, "Owner Name")
        self.assertEquals(event.change.owner.email, "owner@example.com")
        self.assertEquals(event.changer.name, "Changer Name")
        self.assertEquals(event.changer.email, "changer@example.com")
        self.assertEquals(event.oldtopic, "old-topic")

    def test_user_defined_event(self):
        _create_event("user-defined-event", self.gerrit)
        event = self.gerrit.get_event(False)
        self.assertTrue(isinstance(event, UserDefinedEvent))
        self.assertEquals(event.title, "Event title")
        self.assertEquals(event.description, "Event description")

    def test_unhandled_event(self):
        data = _create_event("unhandled-event", self.gerrit)
        event = self.gerrit.get_event(False)
        self.assertTrue(isinstance(event, UnhandledEvent))
        self.assertEquals(event.json, json.loads(data))

    def test_invalid_json(self):
        _create_event("invalid-json", self.gerrit)
        event = self.gerrit.get_event(False)
        self.assertTrue(isinstance(event, ErrorEvent))

    def test_add_duplicate_event(self):
        try:
            @GerritEventFactory.register("user-defined-event")
            class AnotherUserDefinedEvent(GerritEvent):
                pass
        except:
            return
        self.fail("Did not raise exception when duplicate event registered")

if __name__ == '__main__':
    unittest.main()
