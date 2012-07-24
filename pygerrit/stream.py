""" Gerrit event stream interface.

Class to listen to the Gerrit event stream and dispatch events.

"""

import json

from events import PatchsetCreatedEvent, \
    RefUpdatedEvent, ChangeMergedEvent, CommentAddedEvent, \
    ChangeAbandonedEvent, ChangeRestoredEvent, \
    DraftPublishedEvent


# Event types
CHANGE_MERGED = "change-merged"
PATCHSET_CREATED = "patchset-created"
DRAFT_PUBLISHED = "draft-published"
COMMENT_ADDED = "comment-added"
CHANGE_ABANDONED = "change-abandoned"
CHANGE_RESTORED = "change-restored"
REF_UPDATED = "ref-updated"


class GerritStreamError(Exception):
    ''' GerritStreamError is raised when an error occurs while
    reading the Gerrit events stream.
    '''


class GerritStream(object):
    ''' Gerrit stream handler.
    '''

    # Map the event types to class names.
    _event_dict = {CHANGE_MERGED: "ChangeMergedEvent",
                   PATCHSET_CREATED: "PatchsetCreatedEvent",
                   DRAFT_PUBLISHED: "DraftPublishedEvent",
                   COMMENT_ADDED: "CommentAddedEvent",
                   CHANGE_ABANDONED: "ChangeAbandonedEvent",
                   CHANGE_RESTORED: "ChangeRestoredEvent",
                   REF_UPDATED: "RefUpdatedEvent"}

    def __init__(self):
        self.listeners = []

    def attach(self, listener):
        ''' Attach the `listener` to the list of listeners.
        Raise GerritStreamError if the listener does not match the
        expected signature, or if its event handler is not callable.
        '''
        if not hasattr(listener, "on_gerrit_event"):
            raise GerritStreamError("Listener must have `on_gerrit_event` "
                                    "event handler method")
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
            classname = self._event_dict[event_type]
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
