""" Gerrit event classes. """

from pygerrit.error import GerritError
from pygerrit.models import Account, Approval, Change, Patchset, RefUpdate


class GerritEventFactory(object):

    """ Gerrit event factory. """

    _events = {}

    @classmethod
    def register(cls, name):
        """ Decorator to register the event identified by `name`.

        Raise GerritError if the event is already registered.

        """

        def decorate(klazz):
            if name in cls._events:
                raise GerritError("Duplicate event: %s" % name)
            cls._events[name] = klazz.__name__
            klazz.name = name
            return klazz
        return decorate

    @classmethod
    def create(cls, json_data):
        """ Create a new event instance.

        Return an instance of the `GerritEvent` subclass from `json_data`
        Raise GerritError if `json_data` does not contain a `type` key, or
        no corresponding event is registered.

        """
        if not "type" in json_data:
            raise GerritError("`type` not in json_data")
        name = json_data["type"]
        if not name in cls._events:
            raise GerritError("Unknown event: %s" % name)
        classname = cls._events[name]
        return globals()[classname](json_data)


class GerritEvent(object):

    """ Gerrit event base class. """

    def __init__(self):
        pass


@GerritEventFactory.register("patchset-created")
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


@GerritEventFactory.register("draft-published")
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


@GerritEventFactory.register("comment-added")
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


@GerritEventFactory.register("change-merged")
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


@GerritEventFactory.register("change-abandoned")
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


@GerritEventFactory.register("change-restored")
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


@GerritEventFactory.register("ref-updated")
class RefUpdatedEvent(GerritEvent):

    """ Gerrit "ref-updated" event. """

    def __init__(self, json_data):
        super(RefUpdatedEvent, self).__init__()
        try:
            self.ref_update = RefUpdate(json_data["refUpdate"])
            self.submitter = Account.from_json(json_data, "submitter")
        except KeyError, e:
            raise GerritError("RefUpdatedEvent: %s" % e)
