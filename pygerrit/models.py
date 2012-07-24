""" Models for Gerrit JSON data. """

from pygerrit.error import GerritError


class Account(object):
    ''' Representation of the Gerrit user account (name and email address)
    described in `json_data`.
    Raise GerritError if name or email address field is missing.
    '''

    def __init__(self, json_data):
        try:
            self.name = json_data["name"]
            if "email" in json_data:
                self.email = json_data["email"]
            else:
                self.email = ""
        except KeyError, e:
            raise GerritError("GerritAccount: %s" % e)


class Change(object):
    ''' Representation of the Gerrit change described in `json_data`.
    Raise GerritError if any of the required fields is missing.
    '''

    def __init__(self, json_data):
        try:
            self.project = json_data["project"]
            self.branch = json_data["branch"]
            self.change_id = json_data["id"]
            self.number = json_data["number"]
            self.subject = json_data["subject"]
            self.url = json_data["url"]
            self.owner = Account(json_data["owner"])
        except KeyError, e:
            raise GerritError("GerritChange: %s" % e)


class Patchset(object):
    ''' Representation of the Gerrit patch set described in `json_data`.
    Raise GerritError if any of the required fields is missing.
    '''

    def __init__(self, json_data):
        try:
            self.number = json_data["number"]
            self.revision = json_data["revision"]
            self.ref = json_data["ref"]
            self.uploader = Account(json_data["uploader"])
        except KeyError, e:
            raise GerritError("GerritPatchset: %s" % e)


class Approval(object):
    ''' Representation of a Gerrit approval (verification, code review, etc)
    described in `json_data`.
    Raise GerritError if a required field is missing or has an
    unexpected value.
    '''

    def __init__(self, json_data):
        if "type" not in json_data:
            raise GerritError("GerritApproval: Missing type")
        if "value" not in json_data:
            raise GerritError("GerritApproval: Missing value")
        self.category = json_data["type"]
        self.value = json_data["value"]
        if "description" in json_data:
            self.description = json_data["description"]
        else:
            self.description = None


class RefUpdate(object):
    ''' Representation of the Gerrit ref update described in `json_data`.
    Raise GerritError if any of the required fields is missing.
    '''

    def __init__(self, json_data):
        try:
            self.oldrev = json_data["oldRev"]
            self.newrev = json_data["newRev"]
            self.refname = json_data["refName"]
            self.project = json_data["project"]
        except KeyError, e:
            raise GerritError("GerritRefUpdate: %s" % e)
