#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Unit tests for the Gerrit event stream handler and event objects. """

import os
from StringIO import StringIO
import unittest

from pygerrit.events import PatchsetCreatedEvent, \
    RefUpdatedEvent, ChangeMergedEvent, CommentAddedEvent, \
    ChangeAbandonedEvent, ChangeRestoredEvent, \
    DraftPublishedEvent
from pygerrit.stream import GerritStream


def _get_stream(name):
    """ Get stream object containing JSON data.

    Return a `StringIO` instantiated with the contents of the file
    specified by `name`.  Newlines are removed.

    """
    data = open(os.path.join(os.environ["TESTDIR"], name))
    return StringIO(data.read().replace("\n", ""))


class TestPatchsetCreatedEvent(unittest.TestCase):

    """ Test that the `PatchsetCreatedEvent` event is dispatched properly. """

    def setUp(self):
        self.stream = GerritStream()
        self.stream.attach(self)
        self.event_received = False

    def on_gerrit_event(self, event):
        self.assertTrue(isinstance(event, PatchsetCreatedEvent))
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
        self.event_received = True

    def test_patchset_created_event(self):
        self.stream.stream(_get_stream("patchset-created-event.txt"))
        self.assertTrue(self.event_received)


class TestDraftPublishedEvent(unittest.TestCase):

    """ Test that the `DraftPublished` event is dispatched properly. """

    def setUp(self):
        self.stream = GerritStream()
        self.stream.attach(self)
        self.event_received = False

    def on_gerrit_event(self, event):
        self.assertTrue(isinstance(event, DraftPublishedEvent))
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
        self.event_received = True

    def test_draft_published_event(self):
        self.stream.stream(_get_stream("draft-published-event.txt"))
        self.assertTrue(self.event_received)


class TestRefUpdatedEvent(unittest.TestCase):

    """ Test that the `RefUpdated` event is dispatched properly. """

    def setUp(self):
        self.stream = GerritStream()
        self.stream.attach(self)
        self.event_received = False

    def on_gerrit_event(self, event):
        self.assertTrue(isinstance(event, RefUpdatedEvent))
        self.assertEquals(event.ref_update.project, "project-name")
        self.assertEquals(event.ref_update.oldrev,
                          "0000000000000000000000000000000000000000")
        self.assertEquals(event.ref_update.newrev,
                          "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef")
        self.assertEquals(event.ref_update.refname, "refs/tags/refname")
        self.assertEquals(event.submitter.name, "Submitter Name")
        self.assertEquals(event.submitter.email, "submitter@example.com")
        self.event_received = True

    def test_ref_updated_event(self):
        self.stream.stream(_get_stream("ref-updated-event.txt"))
        self.assertTrue(self.event_received)


class TestChangeMergedEvent(unittest.TestCase):

    """ Test that the `ChangeMerged` event is dispatched properly. """

    def setUp(self):
        self.stream = GerritStream()
        self.stream.attach(self)
        self.event_received = False

    def on_gerrit_event(self, event):
        self.assertTrue(isinstance(event, ChangeMergedEvent))
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
        self.event_received = True

    def test_change_merged_event(self):
        self.stream.stream(_get_stream("change-merged-event.txt"))
        self.assertTrue(self.event_received)


class TestCommentAddedEvent(unittest.TestCase):

    """ Test that the `CommentAdded` event is dispatched properly. """

    def setUp(self):
        self.stream = GerritStream()
        self.stream.attach(self)
        self.event_received = False

    def on_gerrit_event(self, event):
        self.assertTrue(isinstance(event, CommentAddedEvent))
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
        self.event_received = True

    def test_comment_added_event(self):
        self.stream.stream(_get_stream("comment-added-event.txt"))
        self.assertTrue(self.event_received)


class TestChangeAbandonedEvent(unittest.TestCase):

    """ Test that the `ChangeAbandoned` event is dispatched properly. """

    def setUp(self):
        self.stream = GerritStream()
        self.stream.attach(self)
        self.event_received = False

    def on_gerrit_event(self, event):
        self.assertTrue(isinstance(event, ChangeAbandonedEvent))
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
        self.event_received = True

    def test_change_abandoned_event(self):
        self.stream.stream(_get_stream("change-abandoned-event.txt"))
        self.assertTrue(self.event_received)


class TestChangeRestoredEvent(unittest.TestCase):

    """ Test that the `ChangeRestored` event is dispatched properly. """

    def setUp(self):
        self.stream = GerritStream()
        self.stream.attach(self)
        self.event_received = False

    def on_gerrit_event(self, event):
        self.assertTrue(isinstance(event, ChangeRestoredEvent))
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
        self.event_received = True

    def test_change_restored_event(self):
        self.stream.stream(_get_stream("change-restored-event.txt"))
        self.assertTrue(self.event_received)


if __name__ == '__main__':
    unittest.main()
