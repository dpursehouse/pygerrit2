#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Unit tests for the Gerrit event stream events objects."""

import json
import os
import unittest

from pygerrit.events import PatchsetCreatedEvent, \
    RefUpdatedEvent, ChangeMergedEvent, CommentAddedEvent, \
    ChangeAbandonedEvent, ChangeRestoredEvent, \
    DraftPublishedEvent
from pygerrit.stream import GerritStream


class TestGerritStreamEvents(unittest.TestCase):
    """ Test that the event handling works properly in the GerritStream
    class.
    """

    def setUp(self):
        """Set up the gerrit stream object."""
        self.stream = GerritStream()

    def _get_event(self, name):
        """Instantiate an event from data in the file specified by `name`.
        Return some form of `GerritEvent`."""
        data = open(os.path.join(os.environ["TESTDIR"], name))
        return self.stream._get_event(json.loads(data.read()))

    def test_patchset_created_event(self):
        """Tests that the `PatchsetCreatedEvent` event is properly
        generated.  Also implicitly tests that the `Change`,
        `Account`, and `Patchset` classes behave properly.

        """
        event = self._get_event("patchset-created-event.txt")
        self.assertTrue(isinstance(event, PatchsetCreatedEvent))
        self.assertEquals(event.change.project, "project-name")
        self.assertEquals(event.change.branch, "branch-name")
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

    def test_draft_published_event(self):
        """Tests that the `DraftPublishedEvent` event is properly
        generated.

        """
        event = self._get_event("draft-published-event.txt")
        self.assertTrue(isinstance(event, DraftPublishedEvent))
        self.assertEquals(event.change.project, "project-name")
        self.assertEquals(event.change.branch, "branch-name")
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

    def test_ref_updated_event(self):
        """Tests that the `RefUpdatedEvent` event is properly
        generated.  Also implicitly tests that the `RefUpdate`,
        class behaves properly.

        """
        event = self._get_event("ref-updated-event.txt")
        self.assertTrue(isinstance(event, RefUpdatedEvent))
        self.assertEquals(event.ref_update.project, "project-name")
        self.assertEquals(event.ref_update.oldrev,
                          "0000000000000000000000000000000000000000")
        self.assertEquals(event.ref_update.newrev,
                          "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef")
        self.assertEquals(event.ref_update.refname, "refs/tags/refname")
        self.assertEquals(event.submitter.name, "Submitter Name")
        self.assertEquals(event.submitter.email, "submitter@example.com")

    def test_change_merged_event(self):
        """Tests that the `ChangeMergedEvent` event is properly
        generated.

        """
        event = self._get_event("change-merged-event.txt")
        self.assertTrue(isinstance(event, ChangeMergedEvent))
        self.assertEquals(event.change.project, "project-name")
        self.assertEquals(event.change.branch, "branch-name")
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

    def test_comment_added_event(self):
        """Tests that the `CommentAddedEvent` event is properly
        generated.  Also implicitly tests that the `Approval` class
        behaves properly.

        """
        event = self._get_event("comment-added-event.txt")
        self.assertTrue(isinstance(event, CommentAddedEvent))
        self.assertEquals(event.change.project, "project-name")
        self.assertEquals(event.change.branch, "branch-name")
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

    def test_change_abandoned_event(self):
        """Tests that the `ChangeAbandonedEvent` event is properly
        generated.

        """
        event = self._get_event("change-abandoned-event.txt")
        self.assertTrue(isinstance(event, ChangeAbandonedEvent))
        self.assertEquals(event.change.project, "project-name")
        self.assertEquals(event.change.branch, "branch-name")
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

    def test_change_restored_event(self):
        """Tests that the `ChangeRestoredEvent` event is properly
        generated.

        """
        event = self._get_event("change-restored-event.txt")
        self.assertTrue(isinstance(event, ChangeRestoredEvent))
        self.assertEquals(event.change.project, "project-name")
        self.assertEquals(event.change.branch, "branch-name")
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


if __name__ == '__main__':
    unittest.main()
