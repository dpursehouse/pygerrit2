.. :changelog:

History
-------

0.1.1 (2013-09-13)
++++++++++++++++++

- Support for Mac OSX
- Make the connection setup thread-safe
- Unknown event types are no longer treated as errors
- Clients can access event data that is not encapsulated by the event classes
- Better handling of errors when parsing json data in the event stream
- SSH username and port can be manually specified instead of relying on ``~/.ssh/config``
- Support for the ``merge-failed`` event
- Support for the ``reviewer-added`` event
- Support for the ``topic-changed`` event
- Add ``--verbose`` (debug logging) option in the example script
- Add ``--ignore-stream-errors`` option in the example script
- Improved documentation

0.1.0 (2013-08-02)
++++++++++++++++++

- First released version
