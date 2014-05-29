# The MIT License
#
# Copyright 2012 Sony Mobile Communications. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

""" Gerrit SSH Client. """

from os.path import abspath, expanduser, isfile
import re
import socket
from threading import Event, Lock

from .error import GerritError

from paramiko import SSHClient, SSHConfig
from paramiko.ssh_exception import SSHException


def _extract_version(version_string, pattern):
    """ Extract the version from `version_string` using `pattern`.

    Return the version as a string, with leading/trailing whitespace
    stripped.

    """
    if version_string:
        match = pattern.match(version_string.strip())
        if match:
            return match.group(1)
    return ""


class GerritSSHCommandResult(object):

    """ Represents the results of a Gerrit command run over SSH. """

    def __init__(self, command, stdin, stdout, stderr):
        self.command = command
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr

    def __repr__(self):
        return "<GerritSSHCommandResult [%s]>" % self.command


class GerritSSHClient(SSHClient):

    """ Gerrit SSH Client, wrapping the paramiko SSH Client. """

    def __init__(self, hostname, username=None, port=None):
        """ Initialise and connect to SSH. """
        super(GerritSSHClient, self).__init__()
        self.remote_version = None
        self.hostname = hostname
        self.username = username
        self.key_filename = None
        self.port = port
        self.connected = Event()
        self.lock = Lock()

    def _configure(self):
        """ Configure the ssh parameters from the config file. """
        configfile = expanduser("~/.ssh/config")
        if not isfile(configfile):
            raise GerritError("ssh config file '%s' does not exist" %
                              configfile)

        config = SSHConfig()
        config.parse(open(configfile))
        data = config.lookup(self.hostname)
        if not data:
            raise GerritError("No ssh config for host %s" % self.hostname)
        if not 'hostname' in data or not 'port' in data or not 'user' in data:
            raise GerritError("Missing configuration data in %s" % configfile)
        self.hostname = data['hostname']
        self.username = data['user']
        if 'identityfile' in data:
            key_filename = abspath(expanduser(data['identityfile'][0]))
            if not isfile(key_filename):
                raise GerritError("Identity file '%s' does not exist" %
                                  key_filename)
            self.key_filename = key_filename
        try:
            self.port = int(data['port'])
        except ValueError:
            raise GerritError("Invalid port: %s" % data['port'])

    def _do_connect(self):
        """ Connect to the remote. """
        self.load_system_host_keys()
        if self.username is None or self.port is None:
            self._configure()
        try:
            self.connect(hostname=self.hostname,
                         port=self.port,
                         username=self.username,
                         key_filename=self.key_filename)
        except socket.error as e:
            raise GerritError("Failed to connect to server: %s" % e)

        try:
            version_string = self._transport.remote_version
            pattern = re.compile(r'^.*GerritCodeReview_([a-z0-9-\.]*) .*$')
            self.remote_version = _extract_version(version_string, pattern)
        except AttributeError:
            self.remote_version = None

    def _connect(self):
        """ Connect to the remote if not already connected. """
        if not self.connected.is_set():
            try:
                self.lock.acquire()
                # Another thread may have connected while we were
                # waiting to acquire the lock
                if not self.connected.is_set():
                    self._do_connect()
                    self.connected.set()
            except GerritError:
                raise
            finally:
                self.lock.release()

    def get_remote_version(self):
        """ Return the version of the remote Gerrit server. """
        if self.remote_version is None:
            result = self.run_gerrit_command("version")
            version_string = result.stdout.read()
            pattern = re.compile(r'^gerrit version (.*)$')
            self.remote_version = _extract_version(version_string, pattern)
        return self.remote_version

    def get_remote_info(self):
        """ Return the username, and version of the remote Gerrit server. """
        version = self.get_remote_version()
        return (self.username, version)

    def run_gerrit_command(self, command):
        """ Run the given command.

        Make sure we're connected to the remote server, and run `command`.

        Return the results as a `GerritSSHCommandResult`.

        Raise `ValueError` if `command` is not a string, or `GerritError` if
        command execution fails.

        """
        if not isinstance(command, basestring):
            raise ValueError("command must be a string")
        gerrit_command = "gerrit " + command

        self._connect()
        try:
            stdin, stdout, stderr = self.exec_command(gerrit_command,
                                                      bufsize=1,
                                                      timeout=None,
                                                      get_pty=False)
        except SSHException as err:
            raise GerritError("Command execution error: %s" % err)
        return GerritSSHCommandResult(command, stdin, stdout, stderr)
