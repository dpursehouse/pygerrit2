Pygerrit - Client library for interacting with Gerrit Code Review
=================================================================

Pygerrit is a Python library to interact with the
`Gerrit Code Review`_ system over ssh.

Installation
------------

To install pygerrit, simply:

.. code-block:: bash

    $ pip install pygerrit


Prerequisites
-------------

Pygerrit runs on Ubuntu 10.4 and Mac OSX 10.8.4 with Python 2.6.x and 2.7.x.
Support for other platforms and Python versions is not guaranteed.

To connect to the review server, pygerrit requires the ssh connection
parameters (hostname, port, username) to be present in the ``.ssh/config``
file for the current user:

.. code-block:: bash

    Host review
      HostName review.example.net
      Port 29418
      User username

Event Stream
------------

Gerrit offers a ``stream-events`` command that is run over ssh, and returns back
a stream of events (new change uploaded, change merged, comment added, etc) as
JSON text.

This library handles the parsing of the JSON text from the event stream,
encapsulating the data in event objects (Python classes), and allowing the
client to fetch them from a queue. It also allows users to easily add handling
of custom event types, for example if they are running a customised Gerrit
installation with non-standard events.

Refer to the `example`_ script for a brief example of how the interface
works.


Copyright and License
---------------------

Copyright 2011 Sony Ericsson Mobile Communications. All rights reserved.

Copyright 2012 Sony Mobile Communications. All rights reserved.

Licensed under The MIT License.  Please refer to the `LICENSE`_ file for full
license details.

.. _`Gerrit Code Review`: https://code.google.com/p/gerrit/
.. _example: https://github.com/sonyxperiadev/pygerrit/blob/master/example.py
.. _LICENSE: https://github.com/sonyxperiadev/pygerrit/blob/master/LICENSE
