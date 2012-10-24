""" Gerrit SSH Client.

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

from os.path import abspath, expanduser, isfile
import re

from pygerrit.error import GerritError

from paramiko import SSHClient, SSHConfig
from paramiko.ssh_exception import SSHException


def _extract_version(version_string, pattern):
    """ Extract the version from `version_string` using `pattern`. """
    if version_string:
        match = pattern.match(version_string.strip())
        if match:
            return match.group(1)
    return ""


class GerritSSHCommandResult(object):

    """ Represents the results of a Gerrit command run over SSH. """

    def __init__(self, stdin, stdout, stderr):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr


class GerritSSHClient(SSHClient):

    """ Gerrit SSH Client, wrapping the paramiko SSH Client. """

    def __init__(self, hostname):
        """ Initialise and connect to SSH. """
        super(GerritSSHClient, self).__init__()
        self.load_system_host_keys()
        self.remote_version = None

        configfile = expanduser("~/.ssh/config")
        if not isfile(configfile):
            raise GerritError("ssh config file '%s' does not exist" %
                              configfile)

        config = SSHConfig()
        config.parse(open(configfile))
        data = config.lookup(hostname)
        if not data:
            raise GerritError("No ssh config for host %s" % hostname)
        if not 'hostname' in data or not 'port' in data or not 'user' in data:
            raise GerritError("Missing configuration data in %s" % configfile)
        key_filename = None
        if 'identityfile' in data:
            key_filename = abspath(expanduser(data['identityfile']))
            if not isfile(key_filename):
                raise GerritError("Identity file '%s' does not exist" %
                                  key_filename)
        try:
            port = int(data['port'])
        except ValueError:
            raise GerritError("Invalid port: %s" % data['port'])
        self.connect(hostname=data['hostname'],
                     port=port,
                     username=data['user'],
                     key_filename=key_filename)

    def get_remote_version(self):
        """ Return the version of the remote Gerrit server. """
        if self.remote_version is not None:
            return self.remote_version

        try:
            version_string = self._transport.remote_version
            pattern = re.compile(r'^.*GerritCodeReview_([a-z0-9-\.]*) .*$')
            self.remote_version = _extract_version(version_string, pattern)
        except AttributeError:
            try:
                result = self.run_gerrit_command("version")
            except GerritError:
                self.remote_version = ""
            else:
                version_string = result.stdout.read()
                pattern = re.compile(r'^gerrit version (.*)$')
                self.remote_version = _extract_version(version_string, pattern)
        return self.remote_version

    def run_gerrit_command(self, command):
        """ Run the given command.

        Run `command` and return a tuple of stdin, stdout, and stderr.

        """
        gerrit_command = ["gerrit"]
        if isinstance(command, list):
            gerrit_command += command
        else:
            gerrit_command.append(command)
        try:
            stdin, stdout, stderr = self.exec_command(" ".join(gerrit_command))
        except SSHException, err:
            raise GerritError("Command execution error: %s" % err)
        return GerritSSHCommandResult(stdin, stdout, stderr)
