#!/usr/bin/env python

""" Example of using the Gerrit client class.

The MIT License

Copyright 2012 Sony Mobile Communications. All rights reserved.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""

import logging
import optparse
import sys
import time

from pygerrit.client import GerritClient
from pygerrit.stream import GerritStreamErrorEvent


def _main():
    usage = "usage: %prog [options]"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('-g', '--gerrit-hostname', dest='hostname',
                      default='review',
                      help='gerrit server hostname (default: %default)')
    parser.add_option('-b', '--blocking', dest='blocking',
                      action='store_true',
                      help='block on event get (default: False)')
    parser.add_option('-t', '--timeout', dest='timeout',
                      default=None, type='int',
                      help='timeout (seconds) for blocking event get '
                           '(default: None)')

    (options, _args) = parser.parse_args()
    if options.timeout and not options.blocking:
        parser.error('Can only use -t with -b')

    logging.basicConfig(format='%(message)s', level=logging.INFO)

    gerrit = GerritClient(host=options.hostname)
    logging.info("Connected to Gerrit version [%s]", gerrit.gerrit_version())
    gerrit.start_event_stream()
    try:
        while True:
            event = gerrit.get_event(block=options.blocking,
                                     timeout=options.timeout)
            if event:
                logging.info("Event: %s", str(event))
                if isinstance(event, GerritStreamErrorEvent):
                    logging.error(event.error)
                    break
            else:
                logging.info("No event")
                if not options.blocking:
                    time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Terminated by user")
        gerrit.stop_event_stream()


if __name__ == "__main__":
    sys.exit(_main())
