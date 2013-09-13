#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

""" Example of using the Gerrit client REST API. """

import logging
import optparse
import sys

from requests.auth import HTTPBasicAuth, HTTPDigestAuth

from pygerrit.rest import GerritRestAPI
from pygerrit.rest.auth import HTTPDigestAuthFromNetrc, HTTPBasicAuthFromNetrc


def _main():
    usage = "usage: %prog [options]"
    parser = optparse.OptionParser(usage=usage)

    parser.add_option('-g', '--gerrit-url', dest='gerrit_url',
                      help='gerrit server url')
    parser.add_option('-b', '--basic-auth', dest='basic_auth',
                      action='store_true',
                      help='use basic auth instead of digest')
    parser.add_option('-u', '--username', dest='username',
                      help='username')
    parser.add_option('-p', '--password', dest='password',
                      help='password')
    parser.add_option('-n', '--netrc', dest='netrc',
                      action='store_true',
                      help='Use credentials from netrc')
    parser.add_option('-v', '--verbose', dest='verbose',
                      action='store_true',
                      help='enable verbose (debug) logging')

    (options, _args) = parser.parse_args()

    level = logging.DEBUG if options.verbose else logging.INFO
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                        level=level)

    if not options.gerrit_url:
        parser.error("Must specify Gerrit URL with --gerrit-url")

    if options.username and options.password:
        if options.netrc:
            logging.warning("--netrc option ignored")
        if options.basic_auth:
            auth = HTTPBasicAuth(options.username, options.password)
        else:
            auth = HTTPDigestAuth(options.username, options.password)
    elif options.netrc:
        if options.basic_auth:
            auth = HTTPBasicAuthFromNetrc(url=options.gerrit_url)
        else:
            auth = HTTPDigestAuthFromNetrc(url=options.gerrit_url)
    else:
        auth = None

    rest = GerritRestAPI(url=options.gerrit_url, auth=auth)

    changes = rest.get("/changes/?q=owner:self%20status:open")
    logging.info("%d changes", len(changes))
    for change in changes:
        logging.info(change['change_id'])

if __name__ == "__main__":
    sys.exit(_main())
