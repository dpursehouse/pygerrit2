""" Gerrit event classes. """

from pygerrit.error import GerritError
from pygerrit.models import Account, Approval, Change, Patchset, RefUpdate


class GerritEvent(object):

    """ Gerrit event base class. """

    def __init__(self):
        pass


class PatchsetCreatedEvent(GerritEvent):

    """ Gerrit "patchset-created" event. """

    def __init__(self, json_data):
        super(PatchsetCreatedEvent, self).__init__()
        try:
            self.change = Change(json_data["change"])
            self.patchset = Patchset(json_data["patchSet"])
            self.uploader = Account(json_data["uploader"])
        except KeyError, e:
            raise GerritError("PatchsetCreatedEvent: %s" % e)


class DraftPublishedEvent(GerritEvent):

    """ Gerrit "draft-published" event. """

    def __init__(self, json_data):
        super(DraftPublishedEvent, self).__init__()
        try:
            self.change = Change(json_data["change"])
            self.patchset = Patchset(json_data["patchSet"])
            self.uploader = Account(json_data["uploader"])
        except KeyError, e:
            raise GerritError("DraftPublishedEvent: %s" % e)


class CommentAddedEvent(GerritEvent):

    """ Gerrit "comment-added" event. """

    def __init__(self, json_data):
        super(CommentAddedEvent, self).__init__()
        try:
            self.change = Change(json_data["change"])
            self.patchset = Patchset(json_data["patchSet"])
            self.author = Account(json_data["author"])
            self.approvals = []
            if "approvals" in json_data:
                for approval in json_data["approvals"]:
                    self.approvals.append(Approval(approval))
            self.comment = json_data["comment"]
        except ValueError, e:
            raise GerritError("CommentAddedEvent: %s" % e)


class ChangeMergedEvent(GerritEvent):

    """ Gerrit "change-merged" event. """

    def __init__(self, json_data):
        super(ChangeMergedEvent, self).__init__()
        try:
            self.change = Change(json_data["change"])
            self.patchset = Patchset(json_data["patchSet"])
            self.submitter = Account(json_data["submitter"])
        except KeyError, e:
            raise GerritError("ChangeMergedEvent: %s" % e)


class ChangeAbandonedEvent(GerritEvent):

    """ Gerrit "change-abandoned" event. """

    def __init__(self, json_data):
        super(ChangeAbandonedEvent, self).__init__()
        try:
            self.change = Change(json_data["change"])
            self.patchset = Patchset.from_json(json_data)
            self.abandoner = Account(json_data["abandoner"])
            self.reason = json_data["reason"]
        except KeyError, e:
            raise GerritError("ChangeAbandonedEvent: %s" % e)


class ChangeRestoredEvent(GerritEvent):

    """ Gerrit "change-restored" event. """

    def __init__(self, json_data):
        super(ChangeRestoredEvent, self).__init__()
        try:
            self.change = Change(json_data["change"])
            self.patchset = Patchset.from_json(json_data)
            self.restorer = Account(json_data["restorer"])
            self.reason = json_data["reason"]
        except KeyError, e:
            raise GerritError("ChangeRestoredEvent: %s" % e)


class RefUpdatedEvent(GerritEvent):

    """ Gerrit "ref-updated" event. """

    def __init__(self, json_data):
        super(RefUpdatedEvent, self).__init__()
        try:
            self.ref_update = RefUpdate(json_data["refUpdate"])
            self.submitter = Account.from_json(json_data, "submitter")
        except KeyError, e:
            raise GerritError("RefUpdatedEvent: %s" % e)
