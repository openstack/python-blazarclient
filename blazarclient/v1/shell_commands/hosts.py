# Copyright (c) 2014 Bull.
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

import logging

from blazarclient import command
from blazarclient import exception

HOST_ID_PATTERN = '^[0-9]+$'


class ListHosts(command.ListCommand):
    """Print a list of hosts."""
    resource = 'host'
    log = logging.getLogger(__name__ + '.ListHosts')
    list_columns = ['id', 'hypervisor_hostname', 'vcpus', 'memory_mb',
                    'local_gb']

    def get_parser(self, prog_name):
        parser = super(ListHosts, self).get_parser(prog_name)
        parser.add_argument(
            '--sort-by', metavar="<host_column>",
            help='column name used to sort result',
            default='hypervisor_hostname'
        )
        return parser


class ShowHost(command.ShowCommand):
    """Show host details."""
    resource = 'host'
    json_indent = 4
    name_key = 'hypervisor_hostname'
    id_pattern = HOST_ID_PATTERN
    log = logging.getLogger(__name__ + '.ShowHost')

    def get_parser(self, prog_name):
        parser = super(ShowHost, self).get_parser(prog_name)
        if self.allow_names:
            help_str = 'ID or name of %s to look up'
        else:
            help_str = 'ID of %s to look up'
        parser.add_argument('id', metavar=self.resource.upper(),
                            help=help_str % self.resource)
        return parser


class CreateHost(command.CreateCommand):
    """Create a host."""
    resource = 'host'
    json_indent = 4
    log = logging.getLogger(__name__ + '.CreateHost')

    def get_parser(self, prog_name):
        parser = super(CreateHost, self).get_parser(prog_name)
        parser.add_argument(
            'name', metavar=self.resource.upper(),
            help='Name of the host to add'
        )
        parser.add_argument(
            '--extra', metavar='<key>=<value>',
            action='append',
            dest='extra_capabilities',
            default=[],
            help='Extra capabilities key/value pairs to add for the host'
        )
        return parser

    def args2body(self, parsed_args):
        params = {}
        if parsed_args.name:
            params['name'] = parsed_args.name
        extras = {}
        if parsed_args.extra_capabilities:
            for capa in parsed_args.extra_capabilities:
                key, _sep, value = capa.partition('=')
                # NOTE(sbauza): multiple copies of the same capability will
                #               result in only the last value to be stored
                extras[key] = value
            params.update(extras)
        return params


class UpdateHost(command.UpdateCommand):
    """Update attributes of a host."""
    resource = 'host'
    json_indent = 4
    log = logging.getLogger(__name__ + '.UpdateHost')
    name_key = 'hypervisor_hostname'
    id_pattern = HOST_ID_PATTERN

    def get_parser(self, prog_name):
        parser = super(UpdateHost, self).get_parser(prog_name)
        parser.add_argument(
            '--extra', metavar='<key>=<value>',
            action='append',
            dest='extra_capabilities',
            default=[],
            help='Extra capabilities key/value pairs to update for the host'
        )
        return parser

    def args2body(self, parsed_args):
        params = {}
        extras = {}
        if parsed_args.extra_capabilities:
            for capa in parsed_args.extra_capabilities:
                key, _sep, value = capa.partition('=')
                # NOTE(sbauza): multiple copies of the same capability will
                #               result in only the last value to be stored
                extras[key] = value
            params['values'] = extras
        return params


class DeleteHost(command.DeleteCommand):
    """Delete a host."""
    resource = 'host'
    log = logging.getLogger(__name__ + '.DeleteHost')
    name_key = 'hypervisor_hostname'
    id_pattern = HOST_ID_PATTERN


class ShowHostProperty(command.ShowPropertyCommand):
    """Show host property."""
    resource = 'host'
    json_indent = 4
    log = logging.getLogger(__name__ + '.ShowHostProperty')


class ListHostProperties(command.ListCommand):
    """List host properties."""
    resource = 'host'
    log = logging.getLogger(__name__ + '.ListHostProperties')
    list_columns = ['property', 'private', 'property_values']

    def args2body(self, parsed_args):
        params = {
            'detail': parsed_args.detail,
            'all': parsed_args.all,
        }
        if parsed_args.sort_by:
            if parsed_args.sort_by in self.list_columns:
                params['sort_by'] = parsed_args.sort_by
            else:
                msg = 'Invalid sort option %s' % parsed_args.sort_by
                raise exception.BlazarClientException(msg)

        return params

    def retrieve_list(self, parsed_args):
        """Retrieve a list of resources from Blazar server."""
        blazar_client = self.get_client()
        body = self.args2body(parsed_args)
        resource_manager = getattr(blazar_client, self.resource)
        data = resource_manager.list_properties(**body)
        return data

    def get_parser(self, prog_name):
        parser = super(ListHostProperties, self).get_parser(prog_name)
        parser.add_argument(
            '--detail',
            action='store_true',
            help='Return properties with values and attributes.',
            default=False
        )
        parser.add_argument(
            '--sort-by', metavar="<property_column>",
            help='column name used to sort result',
            default='property'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Return all properties, public and private.',
            default=False
        )
        return parser


class UpdateHostProperty(command.UpdatePropertyCommand):
    """Update attributes of a host property."""
    resource = 'host'
    json_indent = 4
    log = logging.getLogger(__name__ + '.UpdateHostProperty')
    name_key = 'property_name'
