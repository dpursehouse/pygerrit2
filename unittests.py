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
from pygerrit import GerritReviewMessageFormatter
from pygerrit.rest import GerritReview

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
        self.assertEqual(event.name, "patchset-created")
        self.assertEqual(event.change.project, "project-name")
        self.assertEqual(event.change.branch, "branch-name")
        self.assertEqual(event.change.topic, "topic-name")
        self.assertEqual(event.change.change_id,
                         "Ideadbeefdeadbeefdeadbeefdeadbeefdeadbeef")
        self.assertEqual(event.change.number, "123456")
        self.assertEqual(event.change.subject, "Commit message subject")
        self.assertEqual(event.change.url, "http://review.example.com/123456")
        self.assertEqual(event.change.owner.name, "Owner Name")
        self.assertEqual(event.change.owner.email, "owner@example.com")
        self.assertEqual(event.patchset.number, "4")
        self.assertEqual(event.patchset.revision,
                         "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef")
        self.assertEqual(event.patchset.ref, "refs/changes/56/123456/4")
        self.assertEqual(event.patchset.uploader.name, "Uploader Name")
        self.assertEqual(event.patchset.uploader.email, "uploader@example.com")
        self.assertEqual(event.uploader.name, "Uploader Name")
        self.assertEqual(event.uploader.email, "uploader@example.com")

    def test_draft_published(self):
        _create_event("draft-published-event", self.gerrit)
        event = self.gerrit.get_event(False)
        self.assertTrue(isinstance(event, DraftPublishedEvent))
        self.assertEqual(event.name, "draft-published")
        self.assertEqual(event.change.project, "project-name")
        self.assertEqual(event.change.branch, "branch-name")
        self.assertEqual(event.change.topic, "topic-name")
        self.assertEqual(event.change.change_id,
                         "Ideadbeefdeadbeefdeadbeefdeadbeefdeadbeef")
        self.assertEqual(event.change.number, "123456")
        self.assertEqual(event.change.subject, "Commit message subject")
        self.assertEqual(event.change.url, "http://review.example.com/123456")
        self.assertEqual(event.change.owner.name, "Owner Name")
        self.assertEqual(event.change.owner.email, "owner@example.com")
        self.assertEqual(event.patchset.number, "4")
        self.assertEqual(event.patchset.revision,
                         "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef")
        self.assertEqual(event.patchset.ref, "refs/changes/56/123456/4")
        self.assertEqual(event.patchset.uploader.name, "Uploader Name")
        self.assertEqual(event.patchset.uploader.email, "uploader@example.com")
        self.assertEqual(event.uploader.name, "Uploader Name")
        self.assertEqual(event.uploader.email, "uploader@example.com")

    def test_ref_updated(self):
        _create_event("ref-updated-event", self.gerrit)
        event = self.gerrit.get_event(False)
        self.assertTrue(isinstance(event, RefUpdatedEvent))
        self.assertEqual(event.name, "ref-updated")
        self.assertEqual(event.ref_update.project, "project-name")
        self.assertEqual(event.ref_update.oldrev,
                         "0000000000000000000000000000000000000000")
        self.assertEqual(event.ref_update.newrev,
                         "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef")
        self.assertEqual(event.ref_update.refname, "refs/tags/refname")
        self.assertEqual(event.submitter.name, "Submitter Name")
        self.assertEqual(event.submitter.email, "submitter@example.com")

    def test_change_merged(self):
        _create_event("change-merged-event", self.gerrit)
        event = self.gerrit.get_event(False)
        self.assertTrue(isinstance(event, ChangeMergedEvent))
        self.assertEqual(event.name, "change-merged")
        self.assertEqual(event.change.project, "project-name")
        self.assertEqual(event.change.branch, "branch-name")
        self.assertEqual(event.change.topic, "topic-name")
        self.assertEqual(event.change.change_id,
                         "Ideadbeefdeadbeefdeadbeefdeadbeefdeadbeef")
        self.assertEqual(event.change.number, "123456")
        self.assertEqual(event.change.subject, "Commit message subject")
        self.assertEqual(event.change.url, "http://review.example.com/123456")
        self.assertEqual(event.change.owner.name, "Owner Name")
        self.assertEqual(event.change.owner.email, "owner@example.com")
        self.assertEqual(event.patchset.number, "4")
        self.assertEqual(event.patchset.revision,
                         "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef")
        self.assertEqual(event.patchset.ref, "refs/changes/56/123456/4")
        self.assertEqual(event.patchset.uploader.name, "Uploader Name")
        self.assertEqual(event.patchset.uploader.email, "uploader@example.com")
        self.assertEqual(event.submitter.name, "Submitter Name")
        self.assertEqual(event.submitter.email, "submitter@example.com")

    def test_merge_failed(self):
        _create_event("merge-failed-event", self.gerrit)
        event = self.gerrit.get_event(False)
        self.assertTrue(isinstance(event, MergeFailedEvent))
        self.assertEqual(event.name, "merge-failed")
        self.assertEqual(event.change.project, "project-name")
        self.assertEqual(event.change.branch, "branch-name")
        self.assertEqual(event.change.topic, "topic-name")
        self.assertEqual(event.change.change_id,
                         "Ideadbeefdeadbeefdeadbeefdeadbeefdeadbeef")
        self.assertEqual(event.change.number, "123456")
        self.assertEqual(event.change.subject, "Commit message subject")
        self.assertEqual(event.change.url, "http://review.example.com/123456")
        self.assertEqual(event.change.owner.name, "Owner Name")
        self.assertEqual(event.change.owner.email, "owner@example.com")
        self.assertEqual(event.patchset.number, "4")
        self.assertEqual(event.patchset.revision,
                         "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef")
        self.assertEqual(event.patchset.ref, "refs/changes/56/123456/4")
        self.assertEqual(event.patchset.uploader.name, "Uploader Name")
        self.assertEqual(event.patchset.uploader.email, "uploader@example.com")
        self.assertEqual(event.submitter.name, "Submitter Name")
        self.assertEqual(event.submitter.email, "submitter@example.com")
        self.assertEqual(event.reason, "Merge failed reason")

    def test_comment_added(self):
        _create_event("comment-added-event", self.gerrit)
        event = self.gerrit.get_event(False)
        self.assertTrue(isinstance(event, CommentAddedEvent))
        self.assertEqual(event.name, "comment-added")
        self.assertEqual(event.change.project, "project-name")
        self.assertEqual(event.change.branch, "branch-name")
        self.assertEqual(event.change.topic, "topic-name")
        self.assertEqual(event.change.change_id,
                         "Ideadbeefdeadbeefdeadbeefdeadbeefdeadbeef")
        self.assertEqual(event.change.number, "123456")
        self.assertEqual(event.change.subject, "Commit message subject")
        self.assertEqual(event.change.url, "http://review.example.com/123456")
        self.assertEqual(event.change.owner.name, "Owner Name")
        self.assertEqual(event.change.owner.email, "owner@example.com")
        self.assertEqual(event.patchset.number, "4")
        self.assertEqual(event.patchset.revision,
                         "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef")
        self.assertEqual(event.patchset.ref, "refs/changes/56/123456/4")
        self.assertEqual(event.patchset.uploader.name, "Uploader Name")
        self.assertEqual(event.patchset.uploader.email, "uploader@example.com")
        self.assertEqual(len(event.approvals), 2)
        self.assertEqual(event.approvals[0].category, "CRVW")
        self.assertEqual(event.approvals[0].description, "Code Review")
        self.assertEqual(event.approvals[0].value, "1")
        self.assertEqual(event.approvals[1].category, "VRIF")
        self.assertEqual(event.approvals[1].description, "Verified")
        self.assertEqual(event.approvals[1].value, "1")
        self.assertEqual(event.author.name, "Author Name")
        self.assertEqual(event.author.email, "author@example.com")

    def test_reviewer_added(self):
        _create_event("reviewer-added-event", self.gerrit)
        event = self.gerrit.get_event(False)
        self.assertTrue(isinstance(event, ReviewerAddedEvent))
        self.assertEqual(event.name, "reviewer-added")
        self.assertEqual(event.change.project, "project-name")
        self.assertEqual(event.change.branch, "branch-name")
        self.assertEqual(event.change.topic, "topic-name")
        self.assertEqual(event.change.change_id,
                         "Ideadbeefdeadbeefdeadbeefdeadbeefdeadbeef")
        self.assertEqual(event.change.number, "123456")
        self.assertEqual(event.change.subject, "Commit message subject")
        self.assertEqual(event.change.url, "http://review.example.com/123456")
        self.assertEqual(event.change.owner.name, "Owner Name")
        self.assertEqual(event.change.owner.email, "owner@example.com")
        self.assertEqual(event.patchset.number, "4")
        self.assertEqual(event.patchset.revision,
                         "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef")
        self.assertEqual(event.patchset.ref, "refs/changes/56/123456/4")
        self.assertEqual(event.patchset.uploader.name, "Uploader Name")
        self.assertEqual(event.patchset.uploader.email, "uploader@example.com")
        self.assertEqual(event.reviewer.name, "Reviewer Name")
        self.assertEqual(event.reviewer.email, "reviewer@example.com")

    def test_change_abandoned(self):
        _create_event("change-abandoned-event", self.gerrit)
        event = self.gerrit.get_event(False)
        self.assertTrue(isinstance(event, ChangeAbandonedEvent))
        self.assertEqual(event.name, "change-abandoned")
        self.assertEqual(event.change.project, "project-name")
        self.assertEqual(event.change.branch, "branch-name")
        self.assertEqual(event.change.topic, "topic-name")
        self.assertEqual(event.change.change_id,
                         "Ideadbeefdeadbeefdeadbeefdeadbeefdeadbeef")
        self.assertEqual(event.change.number, "123456")
        self.assertEqual(event.change.subject, "Commit message subject")
        self.assertEqual(event.change.url, "http://review.example.com/123456")
        self.assertEqual(event.change.owner.name, "Owner Name")
        self.assertEqual(event.change.owner.email, "owner@example.com")
        self.assertEqual(event.abandoner.name, "Abandoner Name")
        self.assertEqual(event.abandoner.email, "abandoner@example.com")
        self.assertEqual(event.reason, "Abandon reason")

    def test_change_restored(self):
        _create_event("change-restored-event", self.gerrit)
        event = self.gerrit.get_event(False)
        self.assertTrue(isinstance(event, ChangeRestoredEvent))
        self.assertEqual(event.name, "change-restored")
        self.assertEqual(event.change.project, "project-name")
        self.assertEqual(event.change.branch, "branch-name")
        self.assertEqual(event.change.topic, "topic-name")
        self.assertEqual(event.change.change_id,
                         "Ideadbeefdeadbeefdeadbeefdeadbeefdeadbeef")
        self.assertEqual(event.change.number, "123456")
        self.assertEqual(event.change.subject, "Commit message subject")
        self.assertEqual(event.change.url, "http://review.example.com/123456")
        self.assertEqual(event.change.owner.name, "Owner Name")
        self.assertEqual(event.change.owner.email, "owner@example.com")
        self.assertEqual(event.restorer.name, "Restorer Name")
        self.assertEqual(event.restorer.email, "restorer@example.com")
        self.assertEqual(event.reason, "Restore reason")

    def test_topic_changed(self):
        _create_event("topic-changed-event", self.gerrit)
        event = self.gerrit.get_event(False)
        self.assertTrue(isinstance(event, TopicChangedEvent))
        self.assertEqual(event.name, "topic-changed")
        self.assertEqual(event.change.project, "project-name")
        self.assertEqual(event.change.branch, "branch-name")
        self.assertEqual(event.change.topic, "topic-name")
        self.assertEqual(event.change.change_id,
                         "Ideadbeefdeadbeefdeadbeefdeadbeefdeadbeef")
        self.assertEqual(event.change.number, "123456")
        self.assertEqual(event.change.subject, "Commit message subject")
        self.assertEqual(event.change.url, "http://review.example.com/123456")
        self.assertEqual(event.change.owner.name, "Owner Name")
        self.assertEqual(event.change.owner.email, "owner@example.com")
        self.assertEqual(event.changer.name, "Changer Name")
        self.assertEqual(event.changer.email, "changer@example.com")
        self.assertEqual(event.oldtopic, "old-topic")

    def test_user_defined_event(self):
        _create_event("user-defined-event", self.gerrit)
        event = self.gerrit.get_event(False)
        self.assertTrue(isinstance(event, UserDefinedEvent))
        self.assertEqual(event.title, "Event title")
        self.assertEqual(event.description, "Event description")

    def test_unhandled_event(self):
        data = _create_event("unhandled-event", self.gerrit)
        event = self.gerrit.get_event(False)
        self.assertTrue(isinstance(event, UnhandledEvent))
        self.assertEqual(event.json, json.loads(data))

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


class TestGerritReviewMessageFormatter(unittest.TestCase):

    """ Test that the GerritReviewMessageFormatter class behaves properly. """

    def _check_test_case_fields(self, test_case, i):
        for field in EXPECTED_TEST_CASE_FIELDS:
            self.assertTrue(field in test_case,
                            "field '%s' not present in test case #%d" %
                            (field, i))
        self.assertTrue(isinstance(test_case['paragraphs'], list),
                        "'paragraphs' field is not a list in test case #%d" % i)

    def test_is_empty(self):
        """ Test if message is empty for missing header and footer. """
        f = GerritReviewMessageFormatter(header=None, footer=None)
        self.assertTrue(f.is_empty())
        f.append(['test'])
        self.assertFalse(f.is_empty())

    def test_message_formatting(self):
        """ Test message formatter for different test cases. """
        for i in range(len(TEST_CASES)):
            test_case = TEST_CASES[i]
            self._check_test_case_fields(test_case, i)
            f = GerritReviewMessageFormatter(header=test_case['header'],
                                             footer=test_case['footer'])
            for paragraph in test_case['paragraphs']:
                f.append(paragraph)
            m = f.format()
            self.assertEqual(m, test_case['result'],
                             "Formatted message does not match expected "
                             "result in test case #%d:\n[%s]" % (i, m))


class TestGerritReview(unittest.TestCase):

    """ Test that the GerritReview class behaves properly. """

    def test_str(self):
        """ Test for str function. """
        obj = GerritReview()
        self.assertEqual(str(obj), '{}')

        obj2 = GerritReview(labels={'Verified': 1, 'Code-Review': -1})
        self.assertEqual(
            str(obj2),
            '{"labels": {"Verified": 1, "Code-Review": -1}}')

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
            '{"labels": {"Verified": 1, "Code-Review": -1},'
            ' "comments": {"Makefile": [{"line": 10, "message": "test"}]}}')

        obj5 = GerritReview(comments=[{'filename': 'Makefile', 'line': 15,
                            'message': 'test'}, {'filename': 'Make',
                            'line': 10, 'message': 'test1'}])
        self.assertEqual(
            str(obj5),
            '{"comments": {"Make": [{"line": 10, "message": "test1"}],'
            ' "Makefile": [{"line": 15, "message": "test"}]}}')


if __name__ == '__main__':
    unittest.main()
