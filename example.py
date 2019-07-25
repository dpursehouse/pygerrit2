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

"""Example of using the Gerrit client REST API."""

import argparse
import logging
import sys

from requests.exceptions import RequestException

try:
    from requests_kerberos import HTTPKerberosAuth, OPTIONAL

    _KERBEROS_SUPPORT = True
except ImportError:
    _KERBEROS_SUPPORT = False

from pygerrit2 import GerritRestAPI
from pygerrit2 import HTTPDigestAuthFromNetrc, HTTPBasicAuthFromNetrc
from pygerrit2 import HTTPBasicAuth, HTTPDigestAuth


def _main():
    descr = "Send request using Gerrit HTTP API"
    parser = argparse.ArgumentParser(
        description=descr, formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "-g", "--gerrit-url", dest="gerrit_url", required=True, help="gerrit server url"
    )
    parser.add_argument(
        "-b",
        "--basic-auth",
        dest="basic_auth",
        action="store_true",
        help="(deprecated) use basic auth instead of digest",
    )
    parser.add_argument(
        "-d",
        "--digest-auth",
        dest="digest_auth",
        action="store_true",
        help="use digest auth instead of basic",
    )
    if _KERBEROS_SUPPORT:
        parser.add_argument(
            "-k",
            "--kerberos-auth",
            dest="kerberos_auth",
            action="store_true",
            help="use kerberos auth",
        )
    parser.add_argument("-u", "--username", dest="username", help="username")
    parser.add_argument("-p", "--password", dest="password", help="password")
    parser.add_argument(
        "-n",
        "--netrc",
        dest="netrc",
        action="store_true",
        help="Use credentials from netrc",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        dest="verbose",
        action="store_true",
        help="enable verbose (debug) logging",
    )

    options = parser.parse_args()

    level = logging.DEBUG if options.verbose else logging.INFO
    logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=level)

    if _KERBEROS_SUPPORT and options.kerberos_auth:
        if options.username or options.password or options.basic_auth or options.netrc:
            parser.error(
                "--kerberos-auth may not be used together with "
                "--username, --password, --basic-auth or --netrc"
            )
        auth = HTTPKerberosAuth(mutual_authentication=OPTIONAL)
    elif options.username and options.password:
        if options.netrc:
            logging.warning("--netrc option ignored")
        if options.digest_auth:
            auth = HTTPDigestAuth(options.username, options.password)
        else:
            auth = HTTPBasicAuth(options.username, options.password)
    elif options.netrc:
        if options.digest_auth:
            auth = HTTPDigestAuthFromNetrc(url=options.gerrit_url)
        else:
            auth = HTTPBasicAuthFromNetrc(url=options.gerrit_url)
    else:
        auth = None

    rest = GerritRestAPI(url=options.gerrit_url, auth=auth)

    try:
        query = ["status:open"]
        if auth:
            query += ["owner:self"]
        else:
            query += ["limit:10"]
        changes = rest.get("/changes/?q=%s" % "%20".join(query))
        logging.info("%d changes", len(changes))
        for change in changes:
            logging.info(change["change_id"])
    except RequestException as err:
        logging.error("Error: %s", str(err))


if __name__ == "__main__":
    sys.exit(_main())
