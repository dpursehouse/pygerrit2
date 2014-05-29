# The MIT License
#
# Copyright 2011 Sony Ericsson Mobile Communications. All rights reserved.
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

""" Gerrit event classes. """

import json
import logging

from .error import GerritError
from .models import Account, Approval, Change, Patchset, RefUpdate


class GerritEventFactory(object):

    """ Gerrit event factory. """

    _events = {}

    @classmethod
    def register(cls, name):
        """ Decorator to register the event identified by `name`.

        Return the decorated class.

        Raise GerritError if the event is already registered.

        """

        def decorate(klazz):
            """ Decorator. """
            if name in cls._events:
                raise GerritError("Duplicate event: %s" % name)
            cls._events[name] = [klazz.__module__, klazz.__name__]
            klazz.name = name
            return klazz
        return decorate

    @classmethod
    def create(cls, data):
        """ Create a new event instance.

        Return an instance of the `GerritEvent` subclass after converting
        `data` to json.

        Raise GerritError if json parsed from `data` does not contain a `type`
        key.

        """
        try:
            json_data = json.loads(data)
        except ValueError as err:
            logging.debug("Failed to load json data: %s: [%s]", str(err), data)
            json_data = json.loads(ErrorEvent.error_json(err))

        if not "type" in json_data:
            raise GerritError("`type` not in json_data")
        name = json_data["type"]
        if not name in cls._events:
            name = 'unhandled-event'
        event = cls._events[name]
        module_name = event[0]
        class_name = event[1]
        module = __import__(module_name, fromlist=[module_name])
        klazz = getattr(module, class_name)
        return klazz(json_data)


class GerritEvent(object):

    """ Gerrit event base class. """

    def __init__(self, json_data):
        self.json = json_data


@GerritEventFactory.register("unhandled-event")
class UnhandledEvent(GerritEvent):

    """ Unknown event type received in json data from Gerrit's event stream. """

    def __init__(self, json_data):
        super(UnhandledEvent, self).__init__(json_data)

    def __repr__(self):
        return u"<UnhandledEvent>"


@GerritEventFactory.register("error-event")
class ErrorEvent(GerritEvent):

    """ Error occurred when processing json data from Gerrit's event stream. """

    def __init__(self, json_data):
        super(ErrorEvent, self).__init__(json_data)
        self.error = json_data["error"]

    @classmethod
    def error_json(cls, error):
        """ Return a json string for the `error`. """
        return '{"type":"error-event",' \
               '"error":"%s"}' % str(error)

    def __repr__(self):
        return u"<ErrorEvent: %s>" % self.error


@GerritEventFactory.register("patchset-created")
class PatchsetCreatedEvent(GerritEvent):

    """ Gerrit "patchset-created" event. """

    def __init__(self, json_data):
        super(PatchsetCreatedEvent, self).__init__(json_data)
        try:
            self.change = Change(json_data["change"])
            self.patchset = Patchset(json_data["patchSet"])
            self.uploader = Account(json_data["uploader"])
        except KeyError as e:
            raise GerritError("PatchsetCreatedEvent: %s" % e)

    def __repr__(self):
        return u"<PatchsetCreatedEvent>: %s %s %s" % (self.change,
                                                      self.patchset,
                                                      self.uploader)


@GerritEventFactory.register("draft-published")
class DraftPublishedEvent(GerritEvent):

    """ Gerrit "draft-published" event. """

    def __init__(self, json_data):
        super(DraftPublishedEvent, self).__init__(json_data)
        try:
            self.change = Change(json_data["change"])
            self.patchset = Patchset(json_data["patchSet"])
            self.uploader = Account(json_data["uploader"])
        except KeyError as e:
            raise GerritError("DraftPublishedEvent: %s" % e)

    def __repr__(self):
        return u"<DraftPublishedEvent>: %s %s %s" % (self.change,
                                                     self.patchset,
                                                     self.uploader)


@GerritEventFactory.register("comment-added")
class CommentAddedEvent(GerritEvent):

    """ Gerrit "comment-added" event. """

    def __init__(self, json_data):
        super(CommentAddedEvent, self).__init__(json_data)
        try:
            self.change = Change(json_data["change"])
            self.patchset = Patchset(json_data["patchSet"])
            self.author = Account(json_data["author"])
            self.approvals = []
            if "approvals" in json_data:
                for approval in json_data["approvals"]:
                    self.approvals.append(Approval(approval))
            self.comment = json_data["comment"]
        except (KeyError, ValueError) as e:
            raise GerritError("CommentAddedEvent: %s" % e)

    def __repr__(self):
        return u"<CommentAddedEvent>: %s %s %s" % (self.change,
                                                   self.patchset,
                                                   self.author)


@GerritEventFactory.register("change-merged")
class ChangeMergedEvent(GerritEvent):

    """ Gerrit "change-merged" event. """

    def __init__(self, json_data):
        super(ChangeMergedEvent, self).__init__(json_data)
        try:
            self.change = Change(json_data["change"])
            self.patchset = Patchset(json_data["patchSet"])
            self.submitter = Account(json_data["submitter"])
        except KeyError as e:
            raise GerritError("ChangeMergedEvent: %s" % e)

    def __repr__(self):
        return u"<ChangeMergedEvent>: %s %s %s" % (self.change,
                                                   self.patchset,
                                                   self.submitter)


@GerritEventFactory.register("merge-failed")
class MergeFailedEvent(GerritEvent):

    """ Gerrit "merge-failed" event. """

    def __init__(self, json_data):
        super(MergeFailedEvent, self).__init__(json_data)
        try:
            self.change = Change(json_data["change"])
            self.patchset = Patchset(json_data["patchSet"])
            self.submitter = Account(json_data["submitter"])
            if 'reason' in json_data:
                self.reason = json_data["reason"]
        except KeyError as e:
            raise GerritError("MergeFailedEvent: %s" % e)

    def __repr__(self):
        return u"<MergeFailedEvent>: %s %s %s" % (self.change,
                                                  self.patchset,
                                                  self.submitter)


@GerritEventFactory.register("change-abandoned")
class ChangeAbandonedEvent(GerritEvent):

    """ Gerrit "change-abandoned" event. """

    def __init__(self, json_data):
        super(ChangeAbandonedEvent, self).__init__(json_data)
        try:
            self.change = Change(json_data["change"])
            self.abandoner = Account(json_data["abandoner"])
            if 'reason' in json_data:
                self.reason = json_data["reason"]
        except KeyError as e:
            raise GerritError("ChangeAbandonedEvent: %s" % e)

    def __repr__(self):
        return u"<ChangeAbandonedEvent>: %s %s" % (self.change,
                                                   self.abandoner)


@GerritEventFactory.register("change-restored")
class ChangeRestoredEvent(GerritEvent):

    """ Gerrit "change-restored" event. """

    def __init__(self, json_data):
        super(ChangeRestoredEvent, self).__init__(json_data)
        try:
            self.change = Change(json_data["change"])
            self.restorer = Account(json_data["restorer"])
            if 'reason' in json_data:
                self.reason = json_data["reason"]
        except KeyError as e:
            raise GerritError("ChangeRestoredEvent: %s" % e)

    def __repr__(self):
        return u"<ChangeRestoredEvent>: %s %s" % (self.change,
                                                  self.restorer)


@GerritEventFactory.register("ref-updated")
class RefUpdatedEvent(GerritEvent):

    """ Gerrit "ref-updated" event. """

    def __init__(self, json_data):
        super(RefUpdatedEvent, self).__init__(json_data)
        try:
            self.ref_update = RefUpdate(json_data["refUpdate"])
            self.submitter = Account.from_json(json_data, "submitter")
        except KeyError as e:
            raise GerritError("RefUpdatedEvent: %s" % e)

    def __repr__(self):
        return u"<RefUpdatedEvent>: %s %s" % (self.ref_update, self.submitter)


@GerritEventFactory.register("reviewer-added")
class ReviewerAddedEvent(GerritEvent):

    """ Gerrit "reviewer-added" event. """

    def __init__(self, json_data):
        super(ReviewerAddedEvent, self).__init__(json_data)
        try:
            self.change = Change(json_data["change"])
            self.patchset = Patchset.from_json(json_data)
            self.reviewer = Account(json_data["reviewer"])
        except KeyError as e:
            raise GerritError("ReviewerAddedEvent: %s" % e)

    def __repr__(self):
        return u"<ReviewerAddedEvent>: %s %s %s" % (self.change,
                                                    self.patchset,
                                                    self.reviewer)


@GerritEventFactory.register("topic-changed")
class TopicChangedEvent(GerritEvent):

    """ Gerrit "topic-changed" event. """

    def __init__(self, json_data):
        super(TopicChangedEvent, self).__init__(json_data)
        try:
            self.change = Change(json_data["change"])
            self.changer = Account(json_data["changer"])
            if "oldTopic" in json_data:
                self.oldtopic = json_data["oldTopic"]
            else:
                self.oldtopic = ""
        except KeyError as e:
            raise GerritError("TopicChangedEvent: %s" % e)

    def __repr__(self):
        return u"<TopicChangedEvent>: %s %s [%s]" % (self.change,
                                                     self.changer,
                                                     self.oldtopic)
