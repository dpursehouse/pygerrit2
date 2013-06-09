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


def _decode_response(response):
    """ Decode the `response` received from a REST API call.

    Strip off Gerrit's magic prefix if it is there, and return decoded
    JSON content or raw text if it cannot be decoded as JSON.

    """
    content = response.content
    if content.startswith(GERRIT_MAGIC_JSON_PREFIX):
        content = content[len(GERRIT_MAGIC_JSON_PREFIX):]
    try:
        return json.loads(content)
    except ValueError:
        return content.strip()


class GerritRestAPI(object):

    """ Interface to the Gerrit REST API. """

    def __init__(self, url):
        """ Constructor.

        `url` is assumed to be the full URL to the server, including the
        'http(s)://' prefix.

        """
        self.kwargs = {}
        self.url = url
        self.session = requests.session()

    def _get(self, endpoint, params=None):
        """ Send HTTP GET to `endpoint`.

        Return JSON decoded result.

        """
        kwargs = self.kwargs.copy()
        if params:
            kwargs['params'] = params
        response = self.session.get(self.url + endpoint, **kwargs)
        return _decode_response(response)

    def _put(self, endpoint, params=None, data=None):
        """ Send HTTP PUT to `endpoint`.

        Return JSON decoded result.

        """
        kwargs = self.kwargs.copy()
        if params:
            kwargs['params'] = params
        if data:
            kwargs['data'] = data
        response = self.session.put(self.url + endpoint, **kwargs)
        return _decode_response(response)

    def _post(self, endpoint, params=None, data=None):
        """ Send HTTP POST to `endpoint`.

        Return JSON decoded result.

        """
        kwargs = self.kwargs.copy()
        if params:
            kwargs['params'] = params
        if data:
            kwargs['data'] = data
        response = self.session.post(self.url + endpoint, **kwargs)
        return _decode_response(response)

    def _delete(self, endpoint):
        """ Send HTTP DELETE to `endpoint`.

        Return JSON decoded result.

        """
        kwargs = self.kwargs.copy()
        response = self.session.delete(self.url + endpoint, **kwargs)
        return _decode_response(response)
