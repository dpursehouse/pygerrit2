Pygerrit - Client library for interacting with Gerrit Code Review
=================================================================

.. image:: https://badge.fury.io/py/pygerrit.png
    :target: http://badge.fury.io/py/pygerrit

.. image:: https://pypip.in/d/pygerrit/badge.png
        :target: https://crate.io/packages/pygerrit/

Pygerrit is a Python library to interact with the
`Gerrit Code Review`_ system's REST API.

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

For easier connection to the review server over the REST API, the user's
HTTP username and password can be given in the user's ``.netrc`` file::

    machine review login MyUsername password MyPassword


For instructions on how to obtain the HTTP password, refer to Gerrit's
`HTTP upload settings`_ documentation.


REST API
--------

Gerrit offers a feature-rich REST API.  This library provides a simple
interface for clients to interact with Gerrit via the REST API::

    >>> from requests.auth import HTTPDigestAuth
    >>> from pygerrit.rest import GerritRestAPI
    >>> auth = HTTPDigestAuth('username', 'password')
    >>> rest = GerritRestAPI(url='http://review.example.net', auth=auth)
    >>> changes = rest.get("/changes/?q=owner:self%20status:open")


Refer to the `example`_ script for a more detailed example of how the
REST API interface works.

Copyright and License
---------------------

Copyright 2011 Sony Ericsson Mobile Communications. All rights reserved.

Copyright 2012 Sony Mobile Communications. All rights reserved.

Licensed under The MIT License.  Please refer to the `LICENSE`_ file for full
license details.

.. _`Gerrit Code Review`: https://code.google.com/p/gerrit/
.. _example: https://github.com/sonyxperiadev/pygerrit/blob/master/example.py
.. _`HTTP upload settings`: https://gerrit-documentation.storage.googleapis.com/Documentation/2.8/user-upload.html#http
.. _LICENSE: https://github.com/sonyxperiadev/pygerrit/blob/master/LICENSE
