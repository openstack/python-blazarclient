# Copyright (c) 2013 Mirantis Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Command-line interface to the Climate APIs
"""

from __future__ import print_function
import argparse
import logging
import os
import sys

from cliff import app
from cliff import commandmanager
from keystoneclient import exceptions as keystone_exceptions
import keystoneclient.v2_0 as keystone_client

from climateclient import client as climate_client
from climateclient import exception
from climateclient.openstack.common import strutils
from climateclient import utils
from climateclient.v1.shell_commands import hosts
from climateclient.v1.shell_commands import leases
from climateclient import version as base_version

COMMANDS_V1 = {
    'lease-list': leases.ListLeases,
    'lease-show': leases.ShowLease,
    'lease-create': leases.CreateLease,
    'lease-update': leases.UpdateLease,
    'lease-delete': leases.DeleteLease,
    'host-list': hosts.ListHosts,
    'host-show': hosts.ShowHost,
    'host-create': hosts.CreateHost,
    'host-update': hosts.UpdateHost,
    'host-delete': hosts.DeleteHost
}

VERSION = 1
DEFAULT_API_VERSION = 1
COMMANDS = {'v1': COMMANDS_V1}


def run_command(cmd, cmd_parser, sub_argv):
    _argv = sub_argv
    index = -1
    values_specs = []
    if '--' in sub_argv:
        index = sub_argv.index('--')
        _argv = sub_argv[:index]
        values_specs = sub_argv[index:]
    known_args, _values_specs = cmd_parser.parse_known_args(_argv)
    cmd.values_specs = (index == -1 and _values_specs or values_specs)
    return cmd.run(known_args)


def env(*_vars, **kwargs):
    """Search for the first defined of possibly many env vars.

    Returns the first environment variable defined in vars, or
    returns the default defined in kwargs.

    """
    for v in _vars:
        value = os.environ.get(v, None)
        if value:
            return value
    return kwargs.get('default', '')


class HelpAction(argparse.Action):
    """Provide a custom action so the -h and --help options
    to the main app will print a list of the commands.

    The commands are determined by checking the CommandManager
    instance, passed in as the "default" value for the action.
    """
    def __call__(self, parser, namespace, values, option_string=None):
        outputs = []
        max_len = 0
        app = self.default
        parser.print_help(app.stdout)
        app.stdout.write('\nCommands for API v%s:\n' % app.api_version)
        command_manager = app.command_manager
        for name, ep in sorted(command_manager):
            factory = ep.load()
            cmd = factory(self, None)
            one_liner = cmd.get_description().split('\n')[0]
            outputs.append((name, one_liner))
            max_len = max(len(name), max_len)
        for (name, one_liner) in outputs:
            app.stdout.write('  %s  %s\n' % (name.ljust(max_len), one_liner))
        sys.exit(0)


class ClimateShell(app.App):
    """Manager class for the Climate CLI."""
    CONSOLE_MESSAGE_FORMAT = '%(message)s'
    DEBUG_MESSAGE_FORMAT = '%(levelname)s: %(name)s %(message)s'
    log = logging.getLogger(__name__)

    def __init__(self):
        super(ClimateShell, self).__init__(
            description=__doc__.strip(),
            version=VERSION,
            command_manager=commandmanager.CommandManager('climate.cli'), )
        self.commands = COMMANDS

    def build_option_parser(self, description, version, argparse_kwargs=None):
        """Return an argparse option parser for this application.

        Subclasses may override this method to extend
        the parser with more global options.
        """
        parser = argparse.ArgumentParser(
            description=description,
            add_help=False)
        parser.add_argument(
            '--version',
            action='version',
            version=base_version.__version__)
        parser.add_argument(
            '-v', '--verbose',
            action='count',
            dest='verbose_level',
            default=self.DEFAULT_VERBOSE_LEVEL,
            help='Increase verbosity of output. Can be repeated.')
        parser.add_argument(
            '-q', '--quiet',
            action='store_const',
            dest='verbose_level',
            const=0,
            help='suppress output except warnings and errors')
        parser.add_argument(
            '-h', '--help',
            action=HelpAction,
            nargs=0,
            default=self,
            help="show this help message and exit")
        parser.add_argument(
            '--debug',
            default=False,
            action='store_true',
            help='show tracebacks on errors')

        # Global arguments
        parser.add_argument(
            '--os-reservation-api-version',
            default=env('OS_RESERVATION_API_VERSION',
                        default=DEFAULT_API_VERSION),
            help='Accepts 1 now, defaults to 1.')
        parser.add_argument(
            '--os_reservation_api_version',
            help=argparse.SUPPRESS)
        parser.add_argument(
            '--os-auth-strategy', metavar='<auth-strategy>',
            default=env('OS_AUTH_STRATEGY', default='keystone'),
            help='Authentication strategy (Env: OS_AUTH_STRATEGY'
            ', default keystone). For now, any other value will'
            ' disable the authentication')
        parser.add_argument(
            '--os_auth_strategy',
            help=argparse.SUPPRESS)
        parser.add_argument(
            '--os-auth-url', metavar='<auth-url>',
            default=env('OS_AUTH_URL'),
            help='Authentication URL (Env: OS_AUTH_URL)')
        parser.add_argument(
            '--os_auth_url',
            help=argparse.SUPPRESS)
        parser.add_argument(
            '--os-tenant-name', metavar='<auth-tenant-name>',
            default=env('OS_TENANT_NAME'),
            help='Authentication tenant name (Env: OS_TENANT_NAME)')
        parser.add_argument(
            '--os_tenant_name',
            help=argparse.SUPPRESS)
        parser.add_argument(
            '--os-tenant-id', metavar='<auth-tenant-id>',
            default=env('OS_TENANT_ID'),
            help='Authentication tenant name (Env: OS_TENANT_ID)')
        parser.add_argument(
            '--os-username', metavar='<auth-username>',
            default=utils.env('OS_USERNAME'),
            help='Authentication username (Env: OS_USERNAME)')
        parser.add_argument(
            '--os_username',
            help=argparse.SUPPRESS)
        parser.add_argument(
            '--os-password', metavar='<auth-password>',
            default=utils.env('OS_PASSWORD'),
            help='Authentication password (Env: OS_PASSWORD)')
        parser.add_argument(
            '--os_password',
            help=argparse.SUPPRESS)
        parser.add_argument(
            '--os-region-name', metavar='<auth-region-name>',
            default=env('OS_REGION_NAME'),
            help='Authentication region name (Env: OS_REGION_NAME)')
        parser.add_argument(
            '--os_region_name',
            help=argparse.SUPPRESS)
        parser.add_argument(
            '--os-token', metavar='<token>',
            default=env('OS_TOKEN'),
            help='Defaults to env[OS_TOKEN]')
        parser.add_argument(
            '--os_token',
            help=argparse.SUPPRESS)
        parser.add_argument(
            '--endpoint-type', metavar='<endpoint-type>',
            default=env('OS_ENDPOINT_TYPE', default='publicURL'),
            help='Defaults to env[OS_ENDPOINT_TYPE] or publicURL.')
        parser.add_argument(
            '--os-cacert',
            metavar='<ca-certificate>',
            default=env('OS_CACERT', default=None),
            help="Specify a CA bundle file to use in "
                 "verifying a TLS (https) server certificate. "
                 "Defaults to env[OS_CACERT]")
        parser.add_argument(
            '--insecure',
            action='store_true',
            default=env('CLIMATECLIENT_INSECURE', default=False),
            help="Explicitly allow climateclient to perform \"insecure\" "
                 "SSL (https) requests. The server's certificate will "
                 "not be verified against any certificate authorities. "
                 "This option should be used with caution.")

        return parser

    def _bash_completion(self):
        """Prints all of the commands and options for bash-completion."""
        commands = set()
        options = set()

        for option, _action in self.parser._option_string_actions.items():
            options.add(option)

        for command_name, command in self.command_manager:
            commands.add(command_name)
            cmd_factory = command.load()
            cmd = cmd_factory(self, None)
            cmd_parser = cmd.get_parser('')
            for option, _action in cmd_parser._option_string_actions.items():
                options.add(option)

        print(' '.join(commands | options))

    def run(self, argv):
        """Equivalent to the main program for the application.

        :param argv: input arguments and options
        :paramtype argv: list of str
        """

        try:
            self.options, remainder = self.parser.parse_known_args(argv)

            self.api_version = 'v%s' % self.options.os_reservation_api_version
            for k, v in self.commands[self.api_version].items():
                self.command_manager.add_command(k, v)

            index = 0
            command_pos = -1
            help_pos = -1
            help_command_pos = -1

            for arg in argv:
                if arg == 'bash-completion':
                    self._bash_completion()
                    return 0
                if arg in self.commands[self.api_version]:
                    if command_pos == -1:
                        command_pos = index
                elif arg in ('-h', '--help'):
                    if help_pos == -1:
                        help_pos = index
                elif arg == 'help':
                    if help_command_pos == -1:
                        help_command_pos = index
                index += 1

            if -1 < command_pos < help_pos:
                argv = ['help', argv[command_pos]]
            if help_command_pos > -1 and command_pos == -1:
                argv[help_command_pos] = '--help'

            self.configure_logging()
            self.interactive_mode = not remainder
            self.initialize_app(remainder)

        except Exception as err:
            if self.options.debug:
                self.log.exception(unicode(err))
                raise
            else:
                self.log.error(unicode(err))
            return 1
        if self.interactive_mode:
            _argv = [sys.argv[0]]
            sys.argv = _argv
            result = self.interact()
        else:
            result = self.run_subcommand(remainder)
        return result

    def run_subcommand(self, argv):
        subcommand = self.command_manager.find_command(argv)
        cmd_factory, cmd_name, sub_argv = subcommand
        cmd = cmd_factory(self, self.options)
        result = 1
        try:
            self.prepare_to_run_command(cmd)
            full_name = (cmd_name if self.interactive_mode else
                         ' '.join([self.NAME, cmd_name]))
            cmd_parser = cmd.get_parser(full_name)
            return run_command(cmd, cmd_parser, sub_argv)
        except Exception as err:
            if self.options.debug:
                self.log.exception(unicode(err))
            else:
                self.log.error(unicode(err))
            try:
                self.clean_up(cmd, result, err)
            except Exception as err2:
                if self.options.debug:
                    self.log.exception(unicode(err2))
                else:
                    self.log.error('Could not clean up: %s', unicode(err2))
            if self.options.debug:
                raise
            else:
                try:
                    self.clean_up(cmd, result, None)
                except Exception as err3:
                    if self.options.debug:
                        self.log.exception(unicode(err3))
                    else:
                        self.log.error('Could not clean up: %s', unicode(err3))
        return result

    def authenticate_user(self):
        """Make sure the user has provided all of the authentication
        info we need.
        """
        if not self.options.os_token:
            if not self.options.os_username:
                raise exception.CommandError(
                    "You must provide a username via"
                    " either --os-username or env[OS_USERNAME]")

            if not self.options.os_password:
                raise exception.CommandError(
                    "You must provide a password via"
                    " either --os-password or env[OS_PASSWORD]")

            if (not self.options.os_tenant_name and
                    not self.options.os_tenant_id):
                raise exception.CommandError(
                    "You must provide a tenant_name or tenant_id via"
                    "  --os-tenant-name, env[OS_TENANT_NAME]"
                    "  --os-tenant-id, or via env[OS_TENANT_ID]")

            if not self.options.os_auth_url:
                raise exception.CommandError(
                    "You must provide an auth url via"
                    " either --os-auth-url or via env[OS_AUTH_URL]")

        keystone = keystone_client.Client(
            token=self.options.os_token,
            auth_url=self.options.os_auth_url,
            tenant_id=self.options.os_tenant_id,
            tenant_name=self.options.os_tenant_name,
            password=self.options.os_password,
            region_name=self.options.os_region_name,
            username=self.options.os_username,
            insecure=self.options.insecure,
            cert=self.options.os_cacert
        )

        auth = keystone.authenticate()

        if auth:
            try:
                climate_url = keystone.service_catalog.url_for(
                    service_type='reservation'
                )
            except keystone_exceptions.EndpointNotFound:
                raise exception.NoClimateEndpoint()
        else:
            raise exception.NotAuthorized("User %s is not authorized." %
                                          self.options.os_username)

        client = climate_client.Client(self.options.os_reservation_api_version,
                                       climate_url=climate_url,
                                       auth_token=keystone.auth_token)
        self.client = client
        return

    def initialize_app(self, argv):
        """Global app init bits:

        * set up API versions
        * validate authentication info
        """

        super(ClimateShell, self).initialize_app(argv)

        cmd_name = None
        if argv:
            cmd_info = self.command_manager.find_command(argv)
            cmd_factory, cmd_name, sub_argv = cmd_info
        if self.interactive_mode or cmd_name != 'help':
            self.authenticate_user()

    def clean_up(self, cmd, result, err):
        self.log.debug('clean_up %s', cmd.__class__.__name__)
        if err:
            self.log.debug('got an error: %s', unicode(err))

    def configure_logging(self):
        """Create logging handlers for any log output."""
        root_logger = logging.getLogger('')

        # Set up logging to a file
        root_logger.setLevel(logging.DEBUG)

        # Send higher-level messages to the console via stderr
        console = logging.StreamHandler(self.stderr)
        console_level = {0: logging.WARNING,
                         1: logging.INFO,
                         2: logging.DEBUG}.get(self.options.verbose_level,
                                               logging.DEBUG)
        console.setLevel(console_level)
        if logging.DEBUG == console_level:
            formatter = logging.Formatter(self.DEBUG_MESSAGE_FORMAT)
        else:
            formatter = logging.Formatter(self.CONSOLE_MESSAGE_FORMAT)
        console.setFormatter(formatter)
        root_logger.addHandler(console)
        return


def main(argv=sys.argv[1:]):
    try:
        return ClimateShell().run(map(strutils.safe_decode, argv))
    except exception.ClimateClientException:
        return 1
    except Exception as e:
        print(unicode(e))
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
