Pygerrit2 - Client library for interacting with Gerrit Code Review's REST API
=============================================================================

.. image:: https://img.shields.io/pypi/v/pygerrit2.png

.. image:: https://img.shields.io/pypi/dm/pygerrit2.png

.. image:: https://img.shields.io/pypi/l/pygerrit2.png

Pygerrit2 provides a simple interface for clients to interact with
`Gerrit Code Review`_ via the REST API.

Prerequisites
-------------

Pygerrit2 has been tested on Ubuntu 10.4 and Mac OSX 10.8.4, with Python 2.6.x
and 2.7.x.  Support for other platforms and Python versions is not guaranteed.

Pygerrit2 depends on the `requests`_ library.


Installation
------------

To install pygerrit2, simply::

    $ pip install pygerrit2


Configuration
-------------

For easier connection to the review server over the REST API, the user's
HTTP username and password can be given in the user's ``.netrc`` file::

    machine review login MyUsername password MyPassword


For instructions on how to obtain the HTTP password, refer to Gerrit's
`HTTP upload settings`_ documentation.


REST API
--------

This simple example shows how to get the user's open changes, authenticating
to Gerrit via HTTP Digest authentication using an explicitly given username and
password::

    >>> from requests.auth import HTTPDigestAuth
    >>> from pygerrit2.rest import GerritRestAPI
    >>> auth = HTTPDigestAuth('username', 'password')
    >>> rest = GerritRestAPI(url='http://review.example.net', auth=auth)
    >>> changes = rest.get("/changes/?q=owner:self%20status:open")


Refer to the `example`_ script for a more detailed example of how the
REST API interface works.


Copyright and License
---------------------

Copyright 2011 Sony Ericsson Mobile Communications. All rights reserved.

Copyright 2012 Sony Mobile Communications. All rights reserved.

Copyright 2016 David Pursehouse. All rights reserved.

Licensed under The MIT License.  Please refer to the `LICENSE`_ file for full
license details.

.. _`Gerrit Code Review`: https://gerritcodereview.com/
.. _`requests`: https://github.com/kennethreitz/requests
.. _example: https://github.com/dpursehouse/pygerrit2/blob/master/example.py
.. _`HTTP upload settings`: https://gerrit-documentation.storage.googleapis.com/Documentation/2.12/user-upload.html#http
.. _LICENSE: https://github.com/dpursehouse/pygerrit2/blob/master/LICENSE
