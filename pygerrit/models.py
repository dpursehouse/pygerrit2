""" Models for Gerrit JSON data. """

from pygerrit.error import GerritError


class Account(object):

    """ Gerrit user account (name and email address). """

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

    """ Gerrit change. """

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

    """ Gerrit patch set. """

    def __init__(self, json_data):
        try:
            self.number = json_data["number"]
            self.revision = json_data["revision"]
            self.ref = json_data["ref"]
            self.uploader = Account(json_data["uploader"])
        except KeyError, e:
            raise GerritError("GerritPatchset: %s" % e)


class Approval(object):

    """ Gerrit approval (verified, code review, etc). """

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

    """ Gerrit ref update. """

    def __init__(self, json_data):
        try:
            self.oldrev = json_data["oldRev"]
            self.newrev = json_data["newRev"]
            self.refname = json_data["refName"]
            self.project = json_data["project"]
        except KeyError, e:
            raise GerritError("GerritRefUpdate: %s" % e)
