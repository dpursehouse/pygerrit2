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

""" Models for Gerrit JSON data. """

from . import from_json


class Account(object):

    """ Gerrit user account (name and email address). """

    def __init__(self, json_data):
        self.name = from_json(json_data, "name")
        self.email = from_json(json_data, "email")
        self.username = from_json(json_data, "username")

    def __repr__(self):
        return u"<Account %s%s>" % (self.name,
                                    " (%s)" % self.email if self.email else "")

    @staticmethod
    def from_json(json_data, key):
        """ Create an Account instance.

        Return an instance of Account initialised with values from `key`
        in `json_data`, or None if `json_data` does not contain `key`.

        """
        if key in json_data:
            return Account(json_data[key])
        return None


class Change(object):

    """ Gerrit change. """

    def __init__(self, json_data):
        self.project = from_json(json_data, "project")
        self.branch = from_json(json_data, "branch")
        self.topic = from_json(json_data, "topic")
        self.change_id = from_json(json_data, "id")
        self.number = from_json(json_data, "number")
        self.subject = from_json(json_data, "subject")
        self.url = from_json(json_data, "url")
        self.owner = Account.from_json(json_data, "owner")
        self.sortkey = from_json(json_data, "sortKey")
        self.status = from_json(json_data, "status")
        self.current_patchset = CurrentPatchset.from_json(json_data)

    def __repr__(self):
        return u"<Change %s, %s, %s>" % (self.number, self.project, self.branch)


class Patchset(object):

    """ Gerrit patch set. """

    def __init__(self, json_data):
        self.number = from_json(json_data, "number")
        self.revision = from_json(json_data, "revision")
        self.ref = from_json(json_data, "ref")
        self.uploader = Account.from_json(json_data, "uploader")

    def __repr__(self):
        return u"<Patchset %s, %s>" % (self.number, self.revision)

    @staticmethod
    def from_json(json_data):
        r""" Create a Patchset instance.

        Return an instance of Patchset initialised with values from "patchSet"
        in `json_data`, or None if `json_data` does not contain "patchSet".

        """
        if "patchSet" in json_data:
            return Patchset(json_data["patchSet"])
        return None


class CurrentPatchset(Patchset):

    """ Gerrit current patch set. """

    def __init__(self, json_data):
        super(CurrentPatchset, self).__init__(json_data)
        self.author = Account.from_json(json_data, "author")
        self.approvals = []
        if "approvals" in json_data:
            for approval in json_data["approvals"]:
                self.approvals.append(Approval(approval))

    def __repr__(self):
        return u"<CurrentPatchset %s, %s>" % (self.number, self.revision)

    @staticmethod
    def from_json(json_data):
        r""" Create a CurrentPatchset instance.

        Return an instance of CurrentPatchset initialised with values from
        "currentPatchSet" in `json_data`, or None if `json_data` does not
        contain "currentPatchSet".

        """
        if "currentPatchSet" in json_data:
            return CurrentPatchset(json_data["currentPatchSet"])
        return None


class Approval(object):

    """ Gerrit approval (verified, code review, etc). """

    def __init__(self, json_data):
        self.category = from_json(json_data, "type")
        self.value = from_json(json_data, "value")
        self.description = from_json(json_data, "description")
        self.approver = Account.from_json(json_data, "by")

    def __repr__(self):
        return u"<Approval %s %s>" % (self.description, self.value)


class RefUpdate(object):

    """ Gerrit ref update. """

    def __init__(self, json_data):
        self.oldrev = from_json(json_data, "oldRev")
        self.newrev = from_json(json_data, "newRev")
        self.refname = from_json(json_data, "refName")
        self.project = from_json(json_data, "project")

    def __repr__(self):
        return "<RefUpdate %s %s %s %s>" % \
            (self.project, self.refname, self.oldrev, self.newrev)
