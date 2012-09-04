""" Gerrit SSH Client. """

from os.path import abspath, expanduser, isfile

from pygerrit.error import GerritError

from paramiko import SSHClient, SSHConfig


class GerritSSHClient(SSHClient):

    """ Gerrit SSH Client, wrapping the paramiko SSH Client. """

    def __init__(self, hostname):
        """ Initialise and connect to SSH. """
        super(GerritSSHClient, self).__init__()
        self.load_system_host_keys()

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

    def run_gerrit_command(self, command):
        """ Run the given command.

        Run `command` and return a tuple of stdin, stdout, and stderr.

        """
        gerrit_command = ["gerrit"]
        if isinstance(command, list):
            gerrit_command += command
        else:
            gerrit_command.append(command)
        return self.exec_command(" ".join(gerrit_command))
