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
Command-line interface to the Blazar APIs
"""
import argparse
import logging
import os
import sys

from cliff import app
from cliff import commandmanager
from keystoneauth1 import loading
from oslo_utils import encodeutils

from blazarclient import client as blazar_client
from blazarclient import exception
from blazarclient.v1.shell_commands import devices
from blazarclient.v1.shell_commands import floatingips
from blazarclient.v1.shell_commands import hosts
from blazarclient.v1.shell_commands import leases
from blazarclient.v1.shell_commands import networks
from blazarclient import version as base_version

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
    'host-unset': hosts.UnsetAttributeHost,
    'host-delete': hosts.DeleteHost,
    'host-allocation-show': hosts.ShowHostAllocation,
    'host-allocation-list': hosts.ListHostAllocations,
    'host-reallocate': hosts.ReallocateHost,
    'host-capability-list': hosts.ListHostCapabilities,
    'host-capability-show': hosts.ShowHostCapability,
    'host-capability-set': hosts.UpdateHostCapability,
    'network-list': networks.ListNetworks,
    'network-show': networks.ShowNetwork,
    'network-create': networks.CreateNetwork,
    'network-update': networks.UpdateNetwork,
    'network-unset': networks.UnsetAttributeNetwork,
    'network-delete': networks.DeleteNetwork,
    'network-allocation-show': networks.ShowNetworkAllocation,
    'network-allocation-list': networks.ListNetworkAllocations,
    'network-capability-list': networks.ListNetworkCapabilities,
    'network-capability-show': networks.ShowNetworkCapability,
    'network-capability-set': networks.UpdateNetworkCapability,
    'floatingip-list': floatingips.ListFloatingIPs,
    'floatingip-show': floatingips.ShowFloatingIP,
    'floatingip-create': floatingips.CreateFloatingIP,
    'floatingip-delete': floatingips.DeleteFloatingIP,
    'device-list': devices.ListDevices,
    'device-show': devices.ShowDevice,
    'device-create': devices.CreateDevice,
    'device-update': devices.UpdateDevice,
    'device-unset': devices.UnsetAttributeDevice,
    'device-delete': devices.DeleteDevice,
    'device-allocation-show': devices.ShowDeviceAllocation,
    'device-allocation-list': devices.ListDeviceAllocations,
    'device-reallocate': devices.ReallocateDevice,
    'device-capability-list': devices.ListDeviceCapabilities,
    'device-capability-show': devices.ShowDeviceCapability,
    'device-capability-set': devices.UpdateDeviceCapability,
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
        app.stdout.write('\nCommands for API %s:\n' % app.api_version)
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


class BlazarShell(app.App):
    """Manager class for the Blazar CLI."""
    CONSOLE_MESSAGE_FORMAT = '%(message)s'
    DEBUG_MESSAGE_FORMAT = '%(levelname)s: %(name)s %(message)s'
    log = logging.getLogger(__name__)

    def __init__(self):
        super(BlazarShell, self).__init__(
            description=__doc__.strip(),
            version=VERSION,
            command_manager=commandmanager.CommandManager('blazar.cli'), )
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
        help_action = parser.add_argument(
            '-h', '--help',
            action=HelpAction,
            nargs=0,
            default=self,
            help="show this help message and exit")
        parser.add_argument(
            '--debug',
            default=False,
            action='store_true',
            help='Print debugging output')

        # Removes help action to defer its execution
        self.deferred_help_action = help_action
        parser._actions.remove(help_action)
        del parser._option_string_actions['-h']
        del parser._option_string_actions['--help']
        parser.add_argument(
            '-h', '--help',
            action='store_true',
            dest='deferred_help',
            default=False,
            help="Show this help message and exit",
        )

        # Global arguments
        parser.add_argument(
            '--os-reservation-api-version',
            default=env('OS_RESERVATION_API_VERSION',
                        default=DEFAULT_API_VERSION),
            help='Accepts 1 now, defaults to 1.')
        parser.add_argument(
            '--os_reservation_api_version',
            help=argparse.SUPPRESS)

        # Deprecated arguments
        parser.add_argument(
            '--service-type', metavar='<service-type>',
            default=env('BLAZAR_SERVICE_TYPE'),
            help=('(deprecated) use --os-service-type instead. '
                  'Defaults to env[BLAZAR_SERVICE_TYPE].'))
        parser.add_argument(
            '--endpoint-type', metavar='<endpoint-type>',
            default=env('OS_ENDPOINT_TYPE'),
            help=('(deprecated) use --os-interface intstead. '
                  'Defaults to env[OS_ENDPOINT_TYPE].'))

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
        loading.register_auth_argparse_arguments(self.parser, argv)
        loading.session.register_argparse_arguments(self.parser)
        loading.adapter.register_argparse_arguments(
            self.parser, service_type='reservation')

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

            if self.options.deferred_help:
                self.deferred_help_action(self.parser, self.parser, None, None)

            self.configure_logging()
            self.interactive_mode = not remainder
            self.initialize_app(remainder)

        except Exception as err:
            if self.options.debug:
                self.log.exception(str(err))
                raise
            else:
                self.log.error(str(err))
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
                self.log.exception(str(err))
            else:
                self.log.error(str(err))
            try:
                self.clean_up(cmd, result, err)
            except Exception as err2:
                if self.options.debug:
                    self.log.exception(str(err2))
                else:
                    self.log.error('Could not clean up: %s',
                                   str(err2))
            if self.options.debug:
                raise
            else:
                try:
                    self.clean_up(cmd, result, None)
                except Exception as err3:
                    if self.options.debug:
                        self.log.exception(str(err3))
                    else:
                        self.log.error('Could not clean up: %s',
                                       str(err3))
        return result

    def authenticate_user(self):
        """Authenticate user and set client by using passed params."""
        auth = loading.load_auth_from_argparse_arguments(self.options)
        sess = loading.load_session_from_argparse_arguments(
            self.options, auth=auth)
        self.client = blazar_client.Client(
            self.options.os_reservation_api_version,
            session=sess,
            service_type=self.options.service_type or self.options.os_service_type,
            interface=self.options.endpoint_type or self.options.os_interface,
            region_name=self.options.os_region_name,
        )
        return

    def initialize_app(self, argv):
        """Global app init bits:

        * set up API versions
        * validate authentication info
        """

        super(BlazarShell, self).initialize_app(argv)

        cmd_name = None
        if argv:
            cmd_info = self.command_manager.find_command(argv)
            cmd_factory, cmd_name, sub_argv = cmd_info
        if self.interactive_mode or cmd_name != 'help':
            self.authenticate_user()

    def clean_up(self, cmd, result, err):
        self.log.debug('clean_up %s', cmd.__class__.__name__)
        if err:
            self.log.debug('got an error: %s', str(err))

    def configure_logging(self):
        """Create logging handlers for any log output."""
        root_logger = logging.getLogger('')

        # Set up logging to a file
        root_logger.setLevel(logging.DEBUG)

        # Send higher-level messages to the console via stderr
        console = logging.StreamHandler(self.stderr)
        if self.options.debug:
            console_level = logging.DEBUG
        else:
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
        return BlazarShell().run(list(map(encodeutils.safe_decode, argv)))
    except exception.BlazarClientException:
        return 1
    except Exception as e:
        print(str(e))
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
