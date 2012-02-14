""" Gerrit event stream interface.

Class to listen to the Gerrit event stream and dispatch events.

"""

import json


# Event types
CHANGE_MERGED = "change-merged"
PATCHSET_CREATED = "patchset-created"
COMMENT_ADDED = "comment-added"
CHANGE_ABANDONED = "change-abandoned"
CHANGE_RESTORED = "change-restored"
REF_UPDATED = "ref-updated"


class GerritStreamError(Exception):
    ''' GerritStreamError is raised when an error occurs while
    reading the Gerrit events stream.
    '''


class GerritAccount:
    ''' Representation of the Gerrit user account (name and email address)
    described in `json_data`.
    Raise GerritStreamError if name or email address field is missing.
    '''

    def __init__(self, json_data):
        try:
            self.name = json_data["name"]
            if "email" in json_data:
                self.email = json_data["email"]
            else:
                self.email = ""
        except KeyError, e:
            raise GerritStreamError("GerritAccount: %s" % e)


class GerritChange:
    ''' Representation of the Gerrit change described in `json_data`.
    Raise GerritStreamError if any of the required fields is missing.
    '''

    def __init__(self, json_data):
        try:
            self.project = json_data["project"]
            self.branch = json_data["branch"]
            self.id = json_data["id"]
            self.number = json_data["number"]
            self.subject = json_data["subject"]
            self.url = json_data["url"]
            self.owner = GerritAccount(json_data["owner"])
        except KeyError, e:
            raise GerritStreamError("GerritChange: %s" % e)


class GerritPatchset:
    ''' Representation of the Gerrit patch set described in `json_data`.
    Raise GerritStreamError if any of the required fields is missing.
    '''

    def __init__(self, json_data):
        try:
            self.number = json_data["number"]
            self.revision = json_data["revision"]
            self.ref = json_data["ref"]
            self.uploader = GerritAccount(json_data["uploader"])
        except KeyError, e:
            raise GerritStreamError("GerritPatchset: %s" % e)


class GerritApprovals:
    ''' Representation of the Gerrit approvals (verification and code review)
    described in `json_data`.
    Raise GerritStreamError if a required field is missing or has an
    unexpected value.
    '''

    def __init__(self, json_data):
        try:
            for approval in json_data:
                if approval["type"] == "VRIF":
                    self.verified = approval["value"]
                elif approval["type"] == "CRVW":
                    self.code_review = approval["value"]
                else:
                    raise GerritStreamError("GerritApprovals: Bad type %s"
                        % (approval["type"]))
        except KeyError, e:
            raise GerritStreamError("GerritApprovals: %s" % e)


class GerritRefUpdate:
    ''' Representation of the Gerrit "ref update" described in `json_data`.
    Raise GerritStreamError if any of the required fields is missing.
    '''

    def __init__(self, json_data):
        try:
            self.oldrev = json_data["oldRev"]
            self.newrev = json_data["newRev"]
            self.refname = json_data["refName"]
            self.project = json_data["project"]
        except KeyError, e:
            raise GerritStreamError("GerritRefUpdate: %s" % e)


class GerritEvent:
    ''' Gerrit event base class.
    '''

    def __init__(self):
        pass


class GerritPatchsetCreatedEvent(GerritEvent):
    ''' Representation of the Gerrit "patchset-created" event described in
    `json_data`.
    Raise GerritStreamError if any of the required fields is missing.
    '''

    def __init__(self, json_data):
        try:
            self.change = GerritChange(json_data["change"])
            self.patchset = GerritPatchset(json_data["patchSet"])
            self.uploader = GerritAccount(json_data["uploader"])
        except KeyError, e:
            raise GerritStreamError("GerritPatchsetCreatedEvent: %s" % e)


class GerritCommentAddedEvent(GerritEvent):
    ''' Representation of the Gerrit "comment-added" event described in
    `json_data`.
    Raise GerritStreamError if any of the required fields is missing.
    '''

    def __init__(self, json_data):
        try:
            self.change = GerritChange(json_data["change"])
            self.patchset = GerritPatchset(json_data["patchSet"])
            self.author = GerritAccount(json_data["author"])
            if "approvals" in json_data:
                self.approvals = GerritApprovals(json_data["approvals"])
            else:
                self.approvals = None
            self.comment = json_data["comment"]
        except ValueError, e:
            raise GerritStreamError("GerritCommentAddedEvent: %s" % e)


class GerritChangeMergedEvent(GerritEvent):
    ''' Representation of the Gerrit "change-merged" event described in
    `json_data`.
    Raise GerritStreamError if any of the required fields is missing.
    '''

    def __init__(self, json_data):
        try:
            self.change = GerritChange(json_data["change"])
            self.patchset = GerritPatchset(json_data["patchSet"])
            self.submitter = GerritAccount(json_data["submitter"])
        except KeyError, e:
            raise GerritStreamError("GerritChangeMergedEvent: %s" % e)


class GerritChangeAbandonedEvent(GerritEvent):
    ''' Representation of the Gerrit "change-abandoned" event described in
    `json_data`.
    Raise GerritStreamError if any of the required fields is missing.
    '''

    def __init__(self, json_data):
        try:
            self.change = GerritChange(json_data["change"])
            if "patchSet" in json_data:
                self.patchset = GerritPatchset(json_data["patchSet"])
            else:
                self.patchset = None
            self.abandoner = GerritAccount(json_data["abandoner"])
            self.reason = json_data["reason"]
        except KeyError, e:
            raise GerritStreamError("GerritChangeAbandonedEvent: %s"
                % (str(e)))


class GerritChangeRestoredEvent(GerritEvent):
    ''' Representation of the Gerrit "change-restored" event described in
    `json_data`.
    Raise GerritStreamError if any of the required fields is missing.
    '''

    def __init__(self, json_data):
        try:
            self.change = GerritChange(json_data["change"])
            if "patchSet" in json_data:
                self.patchset = GerritPatchset(json_data["patchSet"])
            else:
                self.patchset = None
            self.restorer = GerritAccount(json_data["restorer"])
        except KeyError, e:
            raise GerritStreamError("GerritChangeRestoredEvent: %s" % e)


class GerritRefUpdatedEvent(GerritEvent):
    ''' Representation of the Gerrit "ref-updated" event described in
    `json_data`.
    Raise GerritStreamError if any of the required fields is missing.
    '''

    def __init__(self, json_data):
        try:
            self.ref_update = GerritRefUpdate(json_data["refUpdate"])
            if "submitter" in json_data:
                self.submitter = GerritAccount(json_data["submitter"])
            else:
                self.submitter = None
        except KeyError, e:
            raise GerritStreamError("GerritRefUpdatedEvent: %s" % e)


class GerritStream:
    ''' Gerrit stream handler.
    '''

    # Map the event types to class names.
    _event_dict = {CHANGE_MERGED: "ChangeMerged",
                   PATCHSET_CREATED: "PatchsetCreated",
                   COMMENT_ADDED: "CommentAdded",
                   CHANGE_ABANDONED: "ChangeAbandoned",
                   CHANGE_RESTORED: "ChangeRestored",
                   REF_UPDATED: "RefUpdated"}

    def __init__(self):
        self.listeners = []

    def attach(self, listener):
        ''' Attach the `listener` to the list of listeners.
        Raise GerritStream error if the listener does not match the
        expected signature, or if its event handler is not callable.
        '''
        if not hasattr(listener, "on_gerrit_event"):
            raise GerritStreamError("Listener must have `on_gerrit_event` " \
                                    "event handler")
        if not callable(listener.on_gerrit_event):
            raise GerritStreamError("`on_gerrit_event` must be callable")
        if not listener.on_gerrit_event.func_code.co_argcount == 2:
            raise GerritStreamError("`on_gerrit_event` must take 1 arg")
        if not listener in self.listeners:
            self.listeners.append(listener)

    def detach(self, listener):
        ''' Remove the `listener` from the list of listeners.
        '''
        if listener in self.listeners:
            try:
                self.listeners.remove(listener)
            except ValueError:
                pass

    def _get_event(self, json_data):
        ''' Create a new 'GerritEvent' from the JSON object
        described in `json_data`.
        Return an instance of one of the GerritEvent subclasses.
        Raise GerritStreamError if any error occurs.
        '''
        event_type = json_data["type"]
        if event_type in self._event_dict:
            classname = "Gerrit" + self._event_dict[event_type] + "Event"
            try:
                return globals()[classname](json_data)
            except KeyError, e:
                raise GerritStreamError("Error creating event: %s" % e)

        raise GerritStreamError("Unexpected event type `%s`" % event_type)

    def _dispatch_event(self, event):
        ''' Dispatch the `event` to the listeners.
        '''
        for listener in self.listeners:
            listener.on_gerrit_event(event)

    def stream(self, inputstream):
        ''' Listen to the `inputstream` and handle JSON objects.
        '''
        try:
            done = 0
            while not done:
                line = inputstream.readline()
                if line:
                    data = json.loads(line)
                    self._dispatch_event(self._get_event(data))
                else:
                    break
        except IOError, e:
            raise GerritStreamError("Error reading event stream: %s" % e)
        except ValueError, e:
            raise GerritStreamError("Invalid JSON data in event stream: %s" % e)
