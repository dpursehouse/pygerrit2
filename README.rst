Pygerrit - Client library for interacting with Gerrit Code Review
=================================================================

Pygerrit is a Python library to interact with the
`Gerrit Code Review`_ system over ssh or via the REST API.

Installation
------------

To install pygerrit, simply::

    $ pip install pygerrit


Prerequisites
-------------

Pygerrit has been tested on Ubuntu 10.4 and Mac OSX 10.8.4, with Python 2.6.x
and 2.7.x.  Support for other platforms and Python versions is not guaranteed.


Configuration
-------------

For easier connection to the review server over ssh, the ssh connection
parameters (hostname, port, username) can be given in the user's ``.ssh/config``
file::

    Host review
      HostName review.example.net
      Port 29418
      User username


For easier connection to the review server over the REST API, the user's
HTTP username and password can be given in the user's ``.netrc`` file::

    machine review login MyUsername password MyPassword


For instructions on how to obtain the HTTP password, refer to Gerrit's
`HTTP upload settings`_ documentation.


SSH Interface
-------------

The SSH interface can be used to run commands on the Gerrit server::

    >>> from pygerrit.ssh import GerritSSHClient
    >>> client = GerritSSHClient("review")
    >>> result = client.run_gerrit_command("version")
    >>> result
    <GerritSSHCommandResult [version]>
    >>> result.stdout
    <paramiko.ChannelFile from <paramiko.Channel 2 (closed) -> <paramiko.Transport at 0xd2387d90L (cipher aes128-cbc, 128 bits) (active; 0 open channel(s))>>>
    >>> result.stdout.read()
    'gerrit version 2.6.1\n'
    >>>

Event Stream
------------

Gerrit offers a ``stream-events`` command that is run over ssh, and returns back
a stream of events (new change uploaded, change merged, comment added, etc) as
JSON text.

This library handles the parsing of the JSON text from the event stream,
encapsulating the data in event objects (Python classes), and allowing the
client to fetch them from a queue. It also allows users to easily add handling
of custom event types, for example if they are running a customised Gerrit
installation with non-standard events::

    >>> from pygerrit.client import GerritClient
    >>> client = GerritClient("review")
    >>> client.gerrit_version()
    '2.6.1'
    >>> client.start_event_stream()
    >>> client.get_event()
    <CommentAddedEvent>: <Change 12345, platform/packages/apps/Example, master> <Patchset 1, 5c4b2f76297f04fbab77eb8c3462e087bc4b6f90> <Account Bob Example (bob.example@example.com)>
    >>> client.get_event()
    <CommentAddedEvent>: <Change 67890, platform/frameworks/example, master> <Patchset 2, c7d4f9956c80b1df66a66d66dea3960e71de4910> <Account John Example (john.example@example.com)>
    >>> client.stop_event_stream()
    >>>


Refer to the `example`_ script for a more detailed example of how the SSH
event stream interface works.

REST API
--------

Gerrit offers a feature-rich REST API.  This library provides a simple
interface for clients to interact with Gerrit via the REST API::

    >>> from requests.auth import HTTPDigestAuth
    >>> from pygerrit.rest import GerritRestAPI
    >>> auth = HTTPDigestAuth('username', 'password')
    >>> rest = GerritRestAPI(url='http://review.example.net', auth=auth)
    >>> changes = rest.get("/changes/?q=owner:self%20status:open")


Refer to the `rest_example`_ script for a more detailed example of how the
REST API interface works.

Copyright and License
---------------------

Copyright 2011 Sony Ericsson Mobile Communications. All rights reserved.

Copyright 2012 Sony Mobile Communications. All rights reserved.

Licensed under The MIT License.  Please refer to the `LICENSE`_ file for full
license details.

.. _`Gerrit Code Review`: https://code.google.com/p/gerrit/
.. _example: https://github.com/sonyxperiadev/pygerrit/blob/master/example.py
.. _rest_example: https://github.com/sonyxperiadev/pygerrit/blob/master/rest_example.py
.. _`HTTP upload settings`: http://gerrit-documentation.googlecode.com/svn/Documentation/2.7/user-upload.html#http
.. _LICENSE: https://github.com/sonyxperiadev/pygerrit/blob/master/LICENSE
