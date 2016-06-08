Pygerrit2 - Client library for interacting with Gerrit Code Review's REST API
=============================================================================

.. image:: https://img.shields.io/pypi/v/pygerrit2.png

.. image:: https://img.shields.io/pypi/dm/pygerrit2.png

.. image:: https://img.shields.io/pypi/l/pygerrit2.png

Pygerrit2 provides a simple interface for clients to interact with
`Gerrit Code Review`_ via the REST API.

Prerequisites
-------------

Pygerrit2 is compatible with Python 2.6 and Python 2.7.  Support for Python 3
is experimental.

Pygerrit2 depends on the `requests`_ library.


Installation
------------

To install pygerrit2, simply::

    $ pip install pygerrit2


Usage
-----

This simple example shows how to get the user's open changes. Authentication
to Gerrit is done via HTTP Digest authentication, using an explicitly given
username and password::

    >>> from requests.auth import HTTPDigestAuth
    >>> from pygerrit2.rest import GerritRestAPI
    >>> auth = HTTPDigestAuth('username', 'password')
    >>> rest = GerritRestAPI(url='http://review.example.net', auth=auth)
    >>> changes = rest.get("/changes/?q=owner:self%20status:open")

Note that is is not necessary to add the ``/a/`` prefix on the endpoint
URLs. This is automatically added when the API is instantiated with an
authentication object.

If the user's HTTP username and password are defined in the ``.netrc``
file::

    machine review.example.net login MyUsername password MyPassword

then it is possible to authenticate with those credentials::

    >>> from pygerrit2.rest import GerritRestAPI
    >>> from pygerrit2.rest.auth import HTTPDigestAuthFromNetrc
    >>> url = 'http://review.example.net'
    >>> auth = HTTPDigestAuthFromNetrc(url=url)
    >>> rest = GerritRestAPI(url=url, auth=auth)
    >>> changes = rest.get("/changes/?q=owner:self%20status:open")

Note that the HTTP password is not the same as the SSH password. For
instructions on how to obtain the HTTP password, refer to Gerrit's
`HTTP upload settings`_ documentation.

Refer to the `example`_ script for a full working example.


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
