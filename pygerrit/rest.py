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
import logging
import requests

GERRIT_MAGIC_JSON_PREFIX = ")]}\'\n"
GERRIT_AUTH_SUFFIX = "/a"


def _decode_response(response):
    """ Decode the `response` received from a REST API call.

    Strip off Gerrit's magic prefix if it is there, and return decoded
    JSON content or raw text if it cannot be decoded as JSON.

    Raise requests.HTTPError if the response contains an HTTP error status
    code.

    """
    response.raise_for_status()
    content = response.content
    if content.startswith(GERRIT_MAGIC_JSON_PREFIX):
        content = content[len(GERRIT_MAGIC_JSON_PREFIX):]
    try:
        return json.loads(content)
    except ValueError:
        return content.strip()


class GerritRestAPI(object):

    """ Interface to the Gerrit REST API. """

    def __init__(self, url, auth=None, verify=True):
        """ Constructor.

        `url` is assumed to be the full URL to the server, including the
        'http(s)://' prefix.

        If `auth` is specified, it must be a derivation of the `AuthBase`
        class from the `requests` module.  The `url` will be adjusted if
        necessary to make sure it includes Gerrit's authentication suffix.

        If `verify` is False, the underlying requests library will be
        configured to not attempt to verify SSL certificates.

        """
        headers = {'Accept': 'application/json',
                   'Accept-Encoding': 'gzip'}
        self.kwargs = {'auth': auth,
                       'verify': verify,
                       'headers': headers}
        self.url = url.rstrip('/')
        self.session = requests.session()

        if auth:
            if not isinstance(auth, requests.auth.AuthBase):
                raise ValueError('Invalid auth type; must be derived '
                                 'from requests.auth.AuthBase')

            if not self.url.endswith(GERRIT_AUTH_SUFFIX):
                self.url += GERRIT_AUTH_SUFFIX
        else:
            if self.url.endswith(GERRIT_AUTH_SUFFIX):
                self.url = self.url[: - len(GERRIT_AUTH_SUFFIX)]

        if not self.url.endswith('/'):
            self.url += '/'
        logging.debug("url %s", self.url)

    def make_url(self, endpoint):
        """ Make the necessary url from `endpoint`.

        Strip leading slashes off the endpoint, and return the full
        url.

        Raise requests.RequestException on timeout or connection error.

        """
        endpoint = endpoint.lstrip('/')
        return self.url + endpoint

    def get(self, endpoint, **kwargs):
        """ Send HTTP GET to `endpoint`.

        Return JSON decoded result.

        Raise requests.RequestException on timeout or connection error.

        """
        kwargs.update(self.kwargs.copy())
        response = self.session.get(self.make_url(endpoint), **kwargs)
        return _decode_response(response)

    def put(self, endpoint, **kwargs):
        """ Send HTTP PUT to `endpoint`.

        Return JSON decoded result.

        Raise requests.RequestException on timeout or connection error.

        """
        kwargs.update(self.kwargs.copy())
        kwargs["headers"].update(
            {"Content-Type": "application/json;charset=UTF-8"})
        response = self.session.put(self.make_url(endpoint), **kwargs)
        return _decode_response(response)

    def post(self, endpoint, **kwargs):
        """ Send HTTP POST to `endpoint`.

        Return JSON decoded result.

        Raise requests.RequestException on timeout or connection error.

        """
        kwargs.update(self.kwargs.copy())
        kwargs["headers"].update(
            {"Content-Type": "application/json;charset=UTF-8"})
        response = self.session.post(self.make_url(endpoint), **kwargs)
        return _decode_response(response)

    def delete(self, endpoint, **kwargs):
        """ Send HTTP DELETE to `endpoint`.

        Return JSON decoded result.

        Raise requests.RequestException on timeout or connection error.

        """
        kwargs.update(self.kwargs.copy())
        response = self.session.delete(self.make_url(endpoint), **kwargs)
        return _decode_response(response)
