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

"""Interface to the Gerrit REST API."""

import json
import logging
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from .auth import HTTPBasicAuthFromNetrc, Anonymous

logger = logging.getLogger("pygerrit2")
fmt = "%(asctime)s-[%(name)s-%(levelname)s] %(message)s"
datefmt = "[%y-%m-%d %H:%M:%S]"
sh = logging.StreamHandler()
sh.setLevel(logging.WARNING)
sh.setFormatter(logging.Formatter(fmt, datefmt))
if not logger.handlers:
    logger.addHandler(sh)

GERRIT_MAGIC_JSON_PREFIX = ")]}'\n"
GERRIT_AUTH_SUFFIX = "/a"
DEFAULT_HEADERS = {"Accept": "application/json", "Accept-Encoding": "gzip"}


def _decode_response(response):
    """Strip off Gerrit's magic prefix and decode a response.

    :returns:
        Decoded JSON content as a dict, or raw text if content could not be
        decoded as JSON.

    :raises:
        requests.HTTPError if the response contains an HTTP error status code.

    """
    content_type = response.headers.get("content-type", "")
    logger.debug(
        "status[%s] content_type[%s] encoding[%s]"
        % (response.status_code, content_type, response.encoding)
    )
    response.raise_for_status()
    content = response.content.strip()
    if response.encoding:
        content = content.decode(response.encoding)
    if not content:
        logger.debug("no content in response")
        return content
    if content_type.split(";")[0] != "application/json":
        return content
    if content.startswith(GERRIT_MAGIC_JSON_PREFIX):
        index = len(GERRIT_MAGIC_JSON_PREFIX)
        content = content[index:]
    try:
        return json.loads(content)
    except ValueError:
        logger.error("Invalid json content: %s", content)
        raise


class GerritRestAPI(object):
    """Interface to the Gerrit REST API.

    :arg str url: The full URL to the server, including the `http(s)://`
        prefix. If `auth` is given, `url` will be automatically adjusted to
        include Gerrit's authentication suffix.
    :arg auth: (optional) Authentication handler.  Must be derived from
        `requests.auth.AuthBase`.
    :arg boolean verify: (optional) Set to False to disable verification of
        SSL certificates.

    """

    def __init__(self, url, auth=None, verify=True):
        """See class docstring."""
        self.kwargs = {"auth": auth, "verify": verify}
        self.url = url.rstrip("/")
        self.session = requests.session()
        retry = Retry(
            total=5,
            read=5,
            connect=5,
            backoff_factor=0.3,
            status_forcelist=(500, 502, 504),
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        if not auth:
            try:
                auth = HTTPBasicAuthFromNetrc(url)
            except ValueError as e:
                logger.debug("Error parsing netrc: %s", str(e))
                pass
        elif isinstance(auth, Anonymous):
            logger.debug("Anonymous")
            auth = None

        if auth:
            if not isinstance(auth, requests.auth.AuthBase):
                raise ValueError(
                    "Invalid auth type; must be derived from requests.auth.AuthBase"
                )

            if not self.url.endswith(GERRIT_AUTH_SUFFIX):
                self.url += GERRIT_AUTH_SUFFIX
        else:
            if self.url.endswith(GERRIT_AUTH_SUFFIX):
                self.url = self.url[: -len(GERRIT_AUTH_SUFFIX)]

        # Keep a copy of the auth, only needed for tests
        self.auth = auth

        if not self.url.endswith("/"):
            self.url += "/"

    def make_url(self, endpoint):
        """Make the full url for the endpoint.

        :arg str endpoint: The endpoint.

        :returns:
            The full url.

        """
        endpoint = endpoint.lstrip("/")
        return self.url + endpoint

    def translate_kwargs(self, **kwargs):
        """Translate kwargs replacing `data` with `json` if necessary."""
        local_kwargs = self.kwargs.copy()
        local_kwargs.update(kwargs)

        if "data" in local_kwargs and "json" in local_kwargs:
            raise ValueError("Cannot use data and json together")

        if "data" in local_kwargs and isinstance(local_kwargs["data"], dict):
            local_kwargs.update({"json": local_kwargs["data"]})
            del local_kwargs["data"]

        if "timeout" not in local_kwargs:
            local_kwargs.update({"timeout": 10})

        headers = DEFAULT_HEADERS.copy()
        if "headers" in kwargs:
            headers.update(kwargs["headers"])
        if "json" in local_kwargs:
            headers.update({"Content-Type": "application/json;charset=UTF-8"})
        local_kwargs.update({"headers": headers})

        return local_kwargs

    def get(self, endpoint, return_response=False, **kwargs):
        """Send HTTP GET to the endpoint.

        :arg str endpoint: The endpoint to send to.
        :arg bool return_response: If true will also return the response

        :returns:
            JSON decoded result.

        :raises:
            requests.RequestException on timeout or connection error.

        """
        args = self.translate_kwargs(**kwargs)
        response = self.session.get(self.make_url(endpoint), **args)

        decoded_response = _decode_response(response)

        if return_response:
            return decoded_response, response
        return decoded_response

    def put(self, endpoint, return_response=False, **kwargs):
        """Send HTTP PUT to the endpoint.

        :arg str endpoint: The endpoint to send to.

        :returns:
            JSON decoded result.

        :raises:
            requests.RequestException on timeout or connection error.

        """
        args = self.translate_kwargs(**kwargs)
        response = self.session.put(self.make_url(endpoint), **args)

        decoded_response = _decode_response(response)

        if return_response:
            return decoded_response, response
        return decoded_response

    def post(self, endpoint, return_response=False, **kwargs):
        """Send HTTP POST to the endpoint.

        :arg str endpoint: The endpoint to send to.

        :returns:
            JSON decoded result.

        :raises:
            requests.RequestException on timeout or connection error.

        """
        args = self.translate_kwargs(**kwargs)
        response = self.session.post(self.make_url(endpoint), **args)

        decoded_response = _decode_response(response)

        if return_response:
            return decoded_response, response
        return decoded_response

    def delete(self, endpoint, return_response=False, **kwargs):
        """Send HTTP DELETE to the endpoint.

        :arg str endpoint: The endpoint to send to.

        :returns:
            JSON decoded result.

        :raises:
            requests.RequestException on timeout or connection error.

        """
        args = self.translate_kwargs(**kwargs)
        response = self.session.delete(self.make_url(endpoint), **args)

        decoded_response = _decode_response(response)

        if return_response:
            return decoded_response, response
        return decoded_response

    def review(self, change_id, revision, review):
        """Submit a review.

        :arg str change_id: The change ID.
        :arg str revision: The revision.
        :arg str review: The review details as a :class:`GerritReview`.

        :returns:
            JSON decoded result.

        :raises:
            requests.RequestException on timeout or connection error.

        """
        endpoint = "changes/%s/revisions/%s/review" % (change_id, revision)
        self.post(
            endpoint, data=str(review), headers={"Content-Type": "application/json"}
        )


class GerritReview(object):
    """Encapsulation of a Gerrit review.

    :arg str message: (optional) Cover message.
    :arg dict labels: (optional) Review labels.
    :arg dict comments: (optional) Inline comments.
    :arg str tag: (optional) Review tag.

    """

    def __init__(self, message=None, labels=None, comments=None, tag=None):
        """See class docstring."""
        self.message = message if message else ""
        self.tag = tag if tag else ""
        if labels:
            if not isinstance(labels, dict):
                raise ValueError("labels must be a dict.")
            self.labels = labels
        else:
            self.labels = {}
        if comments:
            if not isinstance(comments, list):
                raise ValueError("comments must be a list.")
            self.comments = {}
            self.add_comments(comments)
        else:
            self.comments = {}

    def set_message(self, message):
        """Set review cover message.

        :arg str message: Cover message.

        """
        self.message = message

    def set_tag(self, tag):
        """Set review tag.

        :arg str tag: Review tag.

        """
        self.tag = tag

    def add_labels(self, labels):
        """Add labels.

        :arg dict labels: Labels to add, for example

        Usage::

            add_labels({'Verified': 1,
                        'Code-Review': -1})

        """
        self.labels.update(labels)

    def add_comments(self, comments):
        """Add inline comments.

        :arg dict comments: Comments to add.

        Usage::

            add_comments([{'filename': 'Makefile',
                           'line': 10,
                           'message': 'inline message'}])

            add_comments([{'filename': 'Makefile',
                           'range': {'start_line': 0,
                                     'start_character': 1,
                                     'end_line': 0,
                                     'end_character': 5},
                           'message': 'inline message'}])

        """
        for comment in comments:
            if "filename" and "message" in list(comment.keys()):
                msg = {}
                if "range" in list(comment.keys()):
                    msg = {"range": comment["range"], "message": comment["message"]}
                elif "line" in list(comment.keys()):
                    msg = {"line": comment["line"], "message": comment["message"]}
                else:
                    continue
                file_comment = {comment["filename"]: [msg]}
                if self.comments:
                    if comment["filename"] in list(self.comments.keys()):
                        self.comments[comment["filename"]].append(msg)
                    else:
                        self.comments.update(file_comment)
                else:
                    self.comments.update(file_comment)

    def __str__(self):
        """Return a string representation."""
        review_input = {}
        if self.message:
            review_input.update({"message": self.message})
        if self.tag:
            review_input.update({"tag": self.tag})
        if self.labels:
            review_input.update({"labels": self.labels})
        if self.comments:
            review_input.update({"comments": self.comments})
        return json.dumps(review_input, sort_keys=True)
