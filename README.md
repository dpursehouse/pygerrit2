# Pygerrit2 - Client library for interacting with Gerrit Code Review's REST API

![Version](https://img.shields.io/pypi/v/pygerrit2.svg)
![License](https://img.shields.io/pypi/l/pygerrit2.svg)
[![Build Status](https://travis-ci.org/dpursehouse/pygerrit2.svg?branch=master)](https://travis-ci.org/dpursehouse/pygerrit2)
[![Dependabot Status](https://api.dependabot.com/badges/status?host=github&repo=dpursehouse/pygerrit2)](https://dependabot.com)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

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
OSX | 3.8
Ubuntu (trusty) | 3.6
Ubuntu (xenial) | 3.7
Ubuntu (bionic) | 3.8

Support for Python 2.x is no longer guaranteed.

## Installation

To install pygerrit2, simply:

```bash
pip install pygerrit2
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

Note that it is not necessary to add the `/a/` prefix; it is automatically
added on all URLs when the API is instantiated with authentication.

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
credentials in the `.netrc` and use them with HTTP basic auth. If no
credentials are found, it will fall back to using no authentication.

To explicitly use anonymous access, i.e. no authentication, use the
`Anonymous` class:

```python
from pygerrit2 import GerritRestAPI, Anonymous

url = 'http://review.example.net'
auth = Anonymous()
rest = GerritRestAPI(url=url, auth=auth)
changes = rest.get("/changes/?q=status:open")
```

Note that the HTTP password is not the same as the SSH password. For
instructions on how to obtain the HTTP password, refer to Gerrit's
[HTTP upload settings documentation][settings].

Also note that in Gerrit version 2.14, support for HTTP Digest authentication
was removed and only HTTP Basic authentication is supported. When using
pygerrit2 against an earlier Gerrit version, it may be necessary to replace
the `HTTPBasic...` classes with the corresponding `HTTPDigest...` versions.

Refer to the [example script][example] for a full working example.

## Contributing

Contributions are welcome. Simply fork the repository, make your changes,
and submit a pull request.

### Tests

Run the tests with:

```bash
make test
```

The tests include unit tests and integration tests against various versions
of Gerrit running in Docker. Docker must be running on the development
environment.

### Code Formatting

Python code is formatted with [black][black]. To check the formatting, run:

```bash
make black-check
```

and to automatically apply formatting, run:

```bash
make black-format
```

Note that black requires minimum Python version 3.6.

### Making Releases

Done by the pygerrit2 maintainers whenever necessary or due.

Assumes a local [`~/.pypirc`][pypirc] file that looks something like this:

```bash
[distutils]
index-servers =
    pypi

[pypi]
username:<PyPI user>
password:<PyPI token>
```

Example steps used; assumes [twine][twine] installed locally:

```bash
git tag 2.0.15
make sdist
twine upload dist/pygerrit2-2.0.15.tar.gz
git push origin 2.0.15
```

Optional: announcing the new [release][release] highlights on Twitter; no known hashtag.

## Copyright and License

Copyright 2011 Sony Ericsson Mobile Communications. All rights reserved.

Copyright 2012 Sony Mobile Communications. All rights reserved.

Copyright 2016 David Pursehouse. All rights reserved.

Licensed under The MIT License.  Please refer to the [LICENSE file][license]
for full license details.

[black]: https://github.com/psf/black
[example]: https://github.com/dpursehouse/pygerrit2/blob/master/example.py
[gerrit]: https://gerritcodereview.com/
[license]: https://github.com/dpursehouse/pygerrit2/blob/master/LICENSE
[pygerrit]: https://github.com/sonyxperiadev/pygerrit
[pypirc]: https://packaging.python.org/specifications/pypirc/#common-configurations
[release]: https://pypi.org/project/pygerrit2/
[settings]: https://gerrit-documentation.storage.googleapis.com/Documentation/2.15.2/user-upload.html#http
[twine]: https://pypi.org/project/twine/
