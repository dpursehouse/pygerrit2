#!/usr/bin/env python

""" Example of using the Gerrit client class. """

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
    gerrit.start_event_stream()
    try:
        while True:
            event = gerrit.get_event(block=options.blocking,
                                     timeout=options.timeout)
            if event:
                logging.info("Event: %s", event.name)
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
