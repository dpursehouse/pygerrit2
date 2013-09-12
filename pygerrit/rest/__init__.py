# The MIT License
#
# Copyright 2013 Sony Mobile Communications. All rights reserved.
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

""" Interface to the Gerrit REST API. """

import json
import requests

GERRIT_MAGIC_JSON_PREFIX = ")]}\'\n"
GERRIT_AUTH_SUFFIX = "/a"


class GerritRestAPIAuthentication(requests.auth.HTTPDigestAuth):

    """ HTTP Digest Auth with netrc credentials. """

    def __init__(self, url, username=None, password=None):
        self.username = username
        self.password = password
        if not self.has_credentials():
            (self.username, self.password) = \
                requests.utils.get_netrc_auth(url)
        if self.has_credentials():
            super(GerritRestAPIAuthentication, self).__init__(self.username,
                                                              self.password)

    def __call__(self, req):
        if (self.username and self.password):
            req = super(GerritRestAPIAuthentication, self).__call__(req)
        return req

    def has_credentials(self):
        """ Return True if authentication credentials are present. """
        return (self.username is not None and self.password is not None)


class GerritRestAPIError(Exception):

    """ Raised when an error occurs during Gerrit REST API access. """

    def __init__(self, code, message=None):
        super(GerritRestAPIError, self).__init__()
        self.code = code
        self.message = message

    def __str__(self):
        if self.message:
            return "%d: %s" % (self.code, self.message)
        else:
            return "%d" % self.code


def _decode_response(response):
    """ Decode the `response` received from a REST API call.

    Strip off Gerrit's magic prefix if it is there, and return decoded
    JSON content or raw text if it cannot be decoded as JSON.

    Raise GerritRestAPIError if the response contains an HTTP error status
    code.

    """
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise GerritRestAPIError(response.status_code, str(e))

    content = response.content
    if content.startswith(GERRIT_MAGIC_JSON_PREFIX):
        content = content[len(GERRIT_MAGIC_JSON_PREFIX):]
    try:
        return json.loads(content)
    except ValueError:
        return content.strip()


class GerritRestAPI(object):

    """ Interface to the Gerrit REST API. """

    def __init__(self, url, username=None, password=None):
        """ Constructor.

        `url` is assumed to be the full URL to the server, including the
        'http(s)://' prefix.

        HTTP digest authentication is used with the given `username` and
        `password`.  If both are not given, an attempt is made to get them
        from the netrc file.  If that fails, anonymous access is used and
        functionality is limited.

        """
        self.kwargs = {}
        self.url = url
        self.session = requests.session()

        self.url = url.rstrip('/')
        auth = GerritRestAPIAuthentication(url, username, password)
        if auth.has_credentials():
            self.kwargs['auth'] = auth
            if not self.url.endswith(GERRIT_AUTH_SUFFIX):
                self.url += GERRIT_AUTH_SUFFIX
        else:
            if self.url.endswith(GERRIT_AUTH_SUFFIX):
                self.url = self.url[: - len(GERRIT_AUTH_SUFFIX)]
        if not self.url.endswith('/'):
            self.url += '/'

    def make_url(self, endpoint):
        """ Make the necessary url from `endpoint`.

        Strip leading slashes off the endpoint, and return the full
        url.

        """
        endpoint = endpoint.lstrip('/')
        return self.url + endpoint

    def get(self, endpoint, params=None):
        """ Send HTTP GET to `endpoint`.

        Return JSON decoded result.

        """
        kwargs = self.kwargs.copy()
        if params:
            kwargs['params'] = params
        response = self.session.get(self.make_url(endpoint), **kwargs)
        return _decode_response(response)

    def put(self, endpoint, params=None, data=None):
        """ Send HTTP PUT to `endpoint`.

        Return JSON decoded result.

        """
        kwargs = self.kwargs.copy()
        if params:
            kwargs['params'] = params
        if data:
            kwargs['data'] = data
        response = self.session.put(self.make_url(endpoint), **kwargs)
        return _decode_response(response)

    def post(self, endpoint, params=None, data=None):
        """ Send HTTP POST to `endpoint`.

        Return JSON decoded result.

        """
        kwargs = self.kwargs.copy()
        if params:
            kwargs['params'] = params
        if data:
            kwargs['data'] = data
        response = self.session.post(self.make_url(endpoint), **kwargs)
        return _decode_response(response)

    def delete(self, endpoint):
        """ Send HTTP DELETE to `endpoint`.

        Return JSON decoded result.

        """
        kwargs = self.kwargs.copy()
        response = self.session.delete(self.make_url(endpoint), **kwargs)
        return _decode_response(response)
