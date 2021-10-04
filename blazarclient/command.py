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
import ast
import logging

from cliff import command
from cliff.formatters import table
from cliff import lister
from cliff import show

from blazarclient import exception
from blazarclient import utils

HEX_ELEM = '[0-9A-Fa-f]'
UUID_PATTERN = '-'.join([HEX_ELEM + '{8}', HEX_ELEM + '{4}',
                         HEX_ELEM + '{4}', HEX_ELEM + '{4}',
                         HEX_ELEM + '{12}'])


class OpenStackCommand(command.Command):
    """Base class for OpenStack commands."""

    api = None

    def run(self, parsed_args):
        if not self.api:
            return
        else:
            return super(OpenStackCommand, self).run(parsed_args)

    def get_data(self, parsed_args):
        pass

    def take_action(self, parsed_args):
        return self.get_data(parsed_args)


class TableFormatter(table.TableFormatter):
    """This class is used to keep consistency with prettytable 0.6."""

    def emit_list(self, column_names, data, stdout, parsed_args):
        if column_names:
            super(TableFormatter, self).emit_list(column_names, data, stdout,
                                                  parsed_args)
        else:
            stdout.write('\n')


class BlazarCommand(OpenStackCommand):

    """Base Blazar CLI command."""
    api = 'reservation'
    log = logging.getLogger(__name__ + '.BlazarCommand')
    values_specs = []
    json_indent = None
    resource = None
    allow_names = True
    name_key = None
    id_pattern = UUID_PATTERN

    def __init__(self, app, app_args):
        super(BlazarCommand, self).__init__(app, app_args)

        # NOTE(dbelova): This is no longer supported in cliff version 1.5.2
        # the same moment occurred in Neutron:
        # see https://bugs.launchpad.net/python-neutronclient/+bug/1265926

        # if hasattr(self, 'formatters'):
        #     self.formatters['table'] = TableFormatter()

    def get_client(self):
        # client_manager.reservation is used for osc_lib, and should be used
        # if it exists
        if hasattr(self.app, 'client_manager'):
            return self.app.client_manager.reservation
        else:
            return self.app.client

    def get_parser(self, prog_name):
        parser = super(BlazarCommand, self).get_parser(prog_name)
        return parser

    def format_output_data(self, data):
        for k, v in data.items():
            if isinstance(v, str):
                try:
                    # Deserialize if possible into dict, lists, tuples...
                    v = ast.literal_eval(v)
                except SyntaxError:
                    # NOTE(sbauza): This is probably a datetime string, we need
                    #               to keep it unchanged.
                    pass
                except ValueError:
                    # NOTE(sbauza): This is not something AST can evaluate,
                    #               probably a string.
                    pass
            if isinstance(v, list):
                value = '\n'.join(utils.dumps(
                    i, indent=self.json_indent) if isinstance(i, dict)
                    else str(i) for i in v)
                data[k] = value
            elif isinstance(v, dict):
                value = utils.dumps(v, indent=self.json_indent)
                data[k] = value
            elif v is None:
                data[k] = ''

    def add_known_arguments(self, parser):
        pass

    def args2body(self, parsed_args):
        return {}


class CreateCommand(BlazarCommand, show.ShowOne):
    """Create resource with passed args."""

    api = 'reservation'
    resource = None
    log = None

    def get_data(self, parsed_args):
        self.log.debug('get_data(%s)' % parsed_args)
        blazar_client = self.get_client()
        body = self.args2body(parsed_args)
        resource_manager = getattr(blazar_client, self.resource)
        data = resource_manager.create(**body)
        self.format_output_data(data)

        if data:
            print('Created a new %s:' % self.resource, file=self.app.stdout)
        else:
            data = {'': ''}
        return list(zip(*sorted(data.items())))


class UpdateCommand(BlazarCommand):
    """Update resource's information."""

    api = 'reservation'
    resource = None
    log = None

    def get_parser(self, prog_name):
        parser = super(UpdateCommand, self).get_parser(prog_name)
        if self.allow_names:
            help_str = 'ID or name of %s to update'
        else:
            help_str = 'ID of %s to update'
        parser.add_argument(
            'id', metavar=self.resource.upper(),
            help=help_str % self.resource
        )
        self.add_known_arguments(parser)
        return parser

    def run(self, parsed_args):
        self.log.debug('run(%s)' % parsed_args)
        blazar_client = self.get_client()
        body = self.args2body(parsed_args)
        if self.allow_names:
            res_id = utils.find_resource_id_by_name_or_id(blazar_client,
                                                          self.resource,
                                                          parsed_args.id,
                                                          self.name_key,
                                                          self.id_pattern)
        else:
            res_id = parsed_args.id
        resource_manager = getattr(blazar_client, self.resource)
        resource_manager.update(res_id, **body)
        print('Updated %s: %s' % (self.resource, parsed_args.id),
              file=self.app.stdout)
        return


class DeleteCommand(BlazarCommand):
    """Delete a given resource."""

    api = 'reservation'
    resource = None
    log = None

    def get_parser(self, prog_name):
        parser = super(DeleteCommand, self).get_parser(prog_name)
        if self.allow_names:
            help_str = 'ID or name of %s to delete'
        else:
            help_str = 'ID of %s to delete'
        parser.add_argument(
            'id', metavar=self.resource.upper(),
            help=help_str % self.resource)
        return parser

    def run(self, parsed_args):
        self.log.debug('run(%s)' % parsed_args)
        blazar_client = self.get_client()
        resource_manager = getattr(blazar_client, self.resource)
        if self.allow_names:
            res_id = utils.find_resource_id_by_name_or_id(blazar_client,
                                                          self.resource,
                                                          parsed_args.id,
                                                          self.name_key,
                                                          self.id_pattern)
        else:
            res_id = parsed_args.id
        resource_manager.delete(res_id)
        print('Deleted %s: %s' % (self.resource, parsed_args.id),
              file=self.app.stdout)
        return


class ListCommand(BlazarCommand, lister.Lister):
    """List resources that belong to a given tenant."""

    api = 'reservation'
    resource = None
    log = None
    _formatters = {}
    list_columns = []
    unknown_parts_flag = True

    def args2body(self, parsed_args):
        params = {}
        if parsed_args.sort_by:
            if parsed_args.sort_by in self.list_columns:
                params['sort_by'] = parsed_args.sort_by
            else:
                msg = 'Invalid sort option %s' % parsed_args.sort_by
                raise exception.BlazarClientException(msg)
        return params

    def get_parser(self, prog_name):
        parser = super(ListCommand, self).get_parser(prog_name)
        return parser

    def retrieve_list(self, parsed_args):
        """Retrieve a list of resources from Blazar server."""
        blazar_client = self.get_client()
        body = self.args2body(parsed_args)
        resource_manager = getattr(blazar_client, self.resource)
        data = resource_manager.list(**body)
        return data

    def setup_columns(self, info, parsed_args):
        columns = len(info) > 0 and sorted(info[0].keys()) or []
        if not columns:
            parsed_args.columns = []
        elif parsed_args.columns:
            columns = [col for col in parsed_args.columns if col in columns]
        elif self.list_columns:
            columns = [col for col in self.list_columns if col in columns]
        return (
            columns,
            (utils.get_item_properties(s, columns, formatters=self._formatters)
             for s in info)
        )

    def get_data(self, parsed_args):
        self.log.debug('get_data(%s)' % parsed_args)
        data = self.retrieve_list(parsed_args)
        return self.setup_columns(data, parsed_args)


class ListAllocationCommand(ListCommand, lister.Lister):
    """List allocations that belong to a given tenant."""

    def retrieve_list(self, parsed_args):
        """Retrieve a list of resources from Blazar server."""
        blazar_client = self.get_client()
        body = self.args2body(parsed_args)
        resource_manager = getattr(blazar_client, self.resource)
        data = resource_manager.list_allocations(**body)
        return data


class ShowCommand(BlazarCommand, show.ShowOne):
    """Show information of a given resource."""

    api = 'reservation'
    resource = None
    log = None

    def get_parser(self, prog_name):
        parser = super(ShowCommand, self).get_parser(prog_name)
        if self.allow_names:
            help_str = 'ID or name of %s to look up'
        else:
            help_str = 'ID of %s to look up'
        parser.add_argument('id', metavar=self.resource.upper(),
                            help=help_str % self.resource)
        return parser

    def get_data(self, parsed_args):
        self.log.debug('get_data(%s)' % parsed_args)
        blazar_client = self.get_client()

        if self.allow_names:
            res_id = utils.find_resource_id_by_name_or_id(blazar_client,
                                                          self.resource,
                                                          parsed_args.id,
                                                          self.name_key,
                                                          self.id_pattern)
        else:
            res_id = parsed_args.id

        resource_manager = getattr(blazar_client, self.resource)
        data = resource_manager.get(res_id)
        self.format_output_data(data)
        return list(zip(*sorted(data.items())))


class ShowAllocationCommand(ShowCommand, show.ShowOne):
    """Show allocations for a given resource."""

    def get_data(self, parsed_args):
        self.log.debug('get_data(%s)' % parsed_args)
        blazar_client = self.get_client()
        resource_manager = getattr(blazar_client, self.resource)
        data = resource_manager.get_allocation(parsed_args.id)
        self.format_output_data(data)
        return list(zip(*sorted(data.items())))


class ReallocateCommand(BlazarCommand):
    """Reallocate host from current leases."""

    api = 'reservation'
    resource = None
    log = None

    def get_parser(self, prog_name):
        parser = super(ReallocateCommand, self).get_parser(prog_name)
        if self.allow_names:
            help_str = 'ID or name of %s to update'
        else:
            help_str = 'ID of %s to update'
        parser.add_argument(
            'id', metavar=self.resource.upper(),
            help=help_str % self.resource
        )
        self.add_known_arguments(parser)
        return parser

    def run(self, parsed_args):
        self.log.debug('run(%s)' % parsed_args)
        blazar_client = self.get_client()
        body = self.args2body(parsed_args)
        if self.allow_names:
            res_id = utils.find_resource_id_by_name_or_id(blazar_client,
                                                          self.resource,
                                                          parsed_args.id,
                                                          self.name_key,
                                                          self.id_pattern)
        else:
            res_id = parsed_args.id
        resource_manager = getattr(blazar_client, self.resource)
        resource_manager.reallocate(res_id, body)
        print('Reallocated %s: %s' % (self.resource, parsed_args.id),
              file=self.app.stdout)
        return


class ShowCapabilityCommand(BlazarCommand, show.ShowOne):
    """Show information of a given resource."""

    api = 'reservation'
    resource = None
    log = None

    def get_parser(self, prog_name):
        parser = super(ShowCapabilityCommand, self).get_parser(prog_name)
        parser.add_argument('capability_name', metavar='CAPABILITY_NAME',
                            help='Name of extra capablity.')
        return parser

    def get_data(self, parsed_args):
        self.log.debug('get_data(%s)' % parsed_args)
        blazar_client = self.get_client()
        resource_manager = getattr(blazar_client, self.resource)
        data = resource_manager.get_capability(parsed_args.capability_name)
        self.format_output_data(data)
        return list(zip(*sorted(data.items())))


class UpdateCapabilityCommand(BlazarCommand):
    api = 'reservation'
    resource = None
    log = None

    def run(self, parsed_args):
        self.log.debug('run(%s)' % parsed_args)
        blazar_client = self.get_client()
        body = self.args2body(parsed_args)
        resource_manager = getattr(blazar_client, self.resource)
        resource_manager.set_capability(**body)
        print(
            'Updated %s extra capability: %s' % (
                self.resource, parsed_args.capability_name),
            file=self.app.stdout)
        return

    def get_parser(self, prog_name):
        parser = super(UpdateCapabilityCommand, self).get_parser(prog_name)
        parser.add_argument(
            'capability_name', metavar='CAPABILITY_NAME',
            help='Name of extra capability to patch.'
        )
        parser.add_argument(
            '--private',
            action='store_true',
            default=False,
            help='Set capability to private.'
        )
        parser.add_argument(
            '--public',
            action='store_true',
            default=False,
            help='Set capability to public.'
        )
        return parser

    def args2body(self, parsed_args):
        return dict(
            capability_name=parsed_args.capability_name,
            private=(parsed_args.private is True))
