""" Gerrit event classes. """

from pygerrit.error import GerritError
from pygerrit.models import Account, Approval, Change, Patchset, RefUpdate


class GerritEvent(object):
    ''' Gerrit event base class.
    '''

    def __init__(self):
        pass


class PatchsetCreatedEvent(GerritEvent):
    ''' Representation of the Gerrit "patchset-created" event described in
    `json_data`.
    Raise GerritError if any of the required fields is missing.
    '''

    def __init__(self, json_data):
        super(PatchsetCreatedEvent, self).__init__()
        try:
            self.change = Change(json_data["change"])
            self.patchset = Patchset(json_data["patchSet"])
            self.uploader = Account(json_data["uploader"])
        except KeyError, e:
            raise GerritError("PatchsetCreatedEvent: %s" % e)


class DraftPublishedEvent(GerritEvent):
    ''' Representation of the Gerrit "draft-published" event described in
    `json_data`.
    Raise GerritError if any of the required fields is missing.
    '''

    def __init__(self, json_data):
        super(DraftPublishedEvent, self).__init__()
        try:
            self.change = Change(json_data["change"])
            self.patchset = Patchset(json_data["patchSet"])
            self.uploader = Account(json_data["uploader"])
        except KeyError, e:
            raise GerritError("DraftPublishedEvent: %s" % e)


class CommentAddedEvent(GerritEvent):
    ''' Representation of the Gerrit "comment-added" event described in
    `json_data`.
    Raise GerritError if any of the required fields is missing.
    '''

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
    ''' Representation of the Gerrit "change-merged" event described in
    `json_data`.
    Raise GerritError if any of the required fields is missing.
    '''

    def __init__(self, json_data):
        super(ChangeMergedEvent, self).__init__()
        try:
            self.change = Change(json_data["change"])
            self.patchset = Patchset(json_data["patchSet"])
            self.submitter = Account(json_data["submitter"])
        except KeyError, e:
            raise GerritError("ChangeMergedEvent: %s" % e)


class ChangeAbandonedEvent(GerritEvent):
    ''' Representation of the Gerrit "change-abandoned" event described in
    `json_data`.
    Raise GerritError if any of the required fields is missing.
    '''

    def __init__(self, json_data):
        super(ChangeAbandonedEvent, self).__init__()
        try:
            self.change = Change(json_data["change"])
            if "patchSet" in json_data:
                self.patchset = Patchset(json_data["patchSet"])
            else:
                self.patchset = None
            self.abandoner = Account(json_data["abandoner"])
            self.reason = json_data["reason"]
        except KeyError, e:
            raise GerritError("ChangeAbandonedEvent: %s" % e)


class ChangeRestoredEvent(GerritEvent):
    ''' Representation of the Gerrit "change-restored" event described in
    `json_data`.
    Raise GerritError if any of the required fields is missing.
    '''

    def __init__(self, json_data):
        super(ChangeRestoredEvent, self).__init__()
        try:
            self.change = Change(json_data["change"])
            if "patchSet" in json_data:
                self.patchset = Patchset(json_data["patchSet"])
            else:
                self.patchset = None
            self.restorer = Account(json_data["restorer"])
            self.reason = json_data["reason"]
        except KeyError, e:
            raise GerritError("ChangeRestoredEvent: %s" % e)


class RefUpdatedEvent(GerritEvent):
    ''' Representation of the Gerrit "ref-updated" event described in
    `json_data`.
    Raise GerritError if any of the required fields is missing.
    '''

    def __init__(self, json_data):
        super(RefUpdatedEvent, self).__init__()
        try:
            self.ref_update = RefUpdate(json_data["refUpdate"])
            if "submitter" in json_data:
                self.submitter = Account(json_data["submitter"])
            else:
                self.submitter = None
        except KeyError, e:
            raise GerritError("RefUpdatedEvent: %s" % e)
