""" Models for Gerrit JSON data. """

from pygerrit import from_json


class Account(object):

    """ Gerrit user account (name and email address). """

    def __init__(self, json_data):
        self.name = from_json(json_data, "name")
        self.email = from_json(json_data, "email")

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
        self.change_id = from_json(json_data, "id")
        self.number = from_json(json_data, "number")
        self.subject = from_json(json_data, "subject")
        self.url = from_json(json_data, "url")
        self.owner = Account.from_json(json_data, "owner")


class Patchset(object):

    """ Gerrit patch set. """

    def __init__(self, json_data):
        self.number = from_json(json_data, "number")
        self.revision = from_json(json_data, "revision")
        self.ref = from_json(json_data, "ref")
        self.uploader = Account.from_json(json_data, "uploader")

    @staticmethod
    def from_json(json_data):
        r""" Create a Patchset instance.

        Return an instance of Patchset initialised with values from "patchSet"
        in `json_data`, or None if `json_data` does not contain "patchSet".

        """
        if "patchSet" in json_data:
            return Patchset(json_data["patchSet"])
        return None


class Approval(object):

    """ Gerrit approval (verified, code review, etc). """

    def __init__(self, json_data):
        self.category = from_json(json_data, "type")
        self.value = from_json(json_data, "value")
        self.description = from_json(json_data, "description")


class RefUpdate(object):

    """ Gerrit ref update. """

    def __init__(self, json_data):
        self.oldrev = from_json(json_data, "oldRev")
        self.newrev = from_json(json_data, "newRev")
        self.refname = from_json(json_data, "refName")
        self.project = from_json(json_data, "project")
