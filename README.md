# Pygerrit2 - Client library for interacting with Gerrit Code Review's REST API

![Version](https://img.shields.io/pypi/v/pygerrit2.svg)
![License](https://img.shields.io/pypi/l/pygerrit2.svg)
[![Build Status](https://travis-ci.org/dpursehouse/pygerrit2.svg?branch=master)](https://travis-ci.org/dpursehouse/pygerrit2)

Pygerrit2 provides a simple interface for clients to interact with
[Gerrit Code Review][gerrit] via the REST API. It is based on [pygerrit][pygerrit]
which was originally developed at Sony Mobile, but is no longer
actively maintained.

Unlike the original pygerrit, pygerrit2 does not provide any SSH
interface. Users who require an SSH interface should continue to use
[pygerrit][pygerrit].

## Prerequisites

Pygerrit2 is tested on the following platforms and Python versions:

Platform | Python version(s)
-------- | -----------------
OSX | 3.7
Ubuntu (trusty) | 3.5, 3.6
Ubuntu (xenial) | 3.7

Support for Python 2.x is no longer guaranteed.

## Installation

To install pygerrit2, simply:

```bash
$ pip install pygerrit2
```

## Usage

This simple example shows how to get the user's open changes. Authentication
to Gerrit is done via HTTP Basic authentication, using an explicitly given
username and password:

```python
from pygerrit2 import GerritRestAPI, HTTPBasicAuth

auth = HTTPBasicAuth('username', 'password')
rest = GerritRestAPI(url='http://review.example.net', auth=auth)
changes = rest.get("/changes/?q=owner:self%20status:open")
```

Note that is is not necessary to add the `/a/` prefix on the endpoint
URLs. This is automatically added when the API is instantiated with an
authentication object.

If the user's HTTP username and password are defined in the `.netrc`
file:

```bash
machine review.example.net login MyUsername password MyPassword
```

then it is possible to authenticate with those credentials:

```python
from pygerrit2 import GerritRestAPI, HTTPBasicAuthFromNetrc

url = 'http://review.example.net'
auth = HTTPBasicAuthFromNetrc(url=url)
rest = GerritRestAPI(url=url, auth=auth)
changes = rest.get("/changes/?q=owner:self%20status:open")
```

If no `auth` parameter is specified, pygerrit2 will attempt to find
credentials in the `netrc` and use them with HTTP basic auth. If no
credentials are found, it will fall back to using no authentication.

Note that the HTTP password is not the same as the SSH password. For
instructions on how to obtain the HTTP password, refer to Gerrit's
[HTTP upload settings documentation][settings].

Also note that in Gerrit version 2.14, support for HTTP Digest authentication
was removed and only HTTP Basic authentication is supported. When using
pygerrit2 against an earlier Gerrit version, it may be necessary to replace
the `HTTPBasic...` classes with the corresponding `HTTPDigest...` versions.

Refer to the [example script][example] for a full working example.


# Copyright and License

Copyright 2011 Sony Ericsson Mobile Communications. All rights reserved.

Copyright 2012 Sony Mobile Communications. All rights reserved.

Copyright 2016 David Pursehouse. All rights reserved.

Licensed under The MIT License.  Please refer to the [LICENSE file][license]
for full license details.

[gerrit]: https://gerritcodereview.com/
[example]: https://github.com/dpursehouse/pygerrit2/blob/master/example.py
[settings]: https://gerrit-documentation.storage.googleapis.com/Documentation/2.15.2/user-upload.html#http
[license]: https://github.com/dpursehouse/pygerrit2/blob/master/LICENSE
[pygerrit]: https://github.com/sonyxperiadev/pygerrit
