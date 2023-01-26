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

# Matches integers or UUIDs
HOST_ID_PATTERN = r'^([0-9]+|([0-9a-fA-F]{8}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{12}))$'


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

class UnsetAttributeHost(UpdateHost):
    """Unset attributes of a host."""
    log = logging.getLogger(__name__ + '.UnsetAttributeHost')

    def get_parser(self, prog_name):
        parser = super(UpdateHost, self).get_parser(prog_name)
        parser.add_argument(
            '--extra', metavar='<key>',
            action='append',
            dest='extra_capabilities',
            default=[],
            help='Extra capability keys which should be unset from the host.',
        )
        return parser

    def args2body(self, parsed_args):
        if parsed_args.extra_capabilities:
            return {
                'values': {
                    cap: None for cap in parsed_args.extra_capabilities
                }
            }
        else:
            return {}

class DeleteHost(command.DeleteCommand):
    """Delete a host."""
    resource = 'host'
    log = logging.getLogger(__name__ + '.DeleteHost')
    name_key = 'hypervisor_hostname'
    id_pattern = HOST_ID_PATTERN


class ShowHostAllocation(command.ShowAllocationCommand):
    """Show host allocation details."""
    resource = 'host'
    json_indent = 4
    id_pattern = HOST_ID_PATTERN
    log = logging.getLogger(__name__ + '.ShowHostAllocation')


class ListHostAllocations(command.ListAllocationCommand):
    """List host allocations."""
    resource = 'host'
    log = logging.getLogger(__name__ + '.ListHostAllocations')
    list_columns = ['resource_id', 'reservations']

    def get_parser(self, prog_name):
        parser = super(ListHostAllocations, self).get_parser(prog_name)
        parser.add_argument(
            '--sort-by', metavar="<host_column>",
            help='column name used to sort result',
            default='resource_id'
        )
        return parser


class ReallocateHost(command.ReallocateCommand):
    """Reallocate host from current allocations."""
    resource = 'host'
    json_indent = 4
    log = logging.getLogger(__name__ + '.ReallocateHost')
    name_key = 'hypervisor_hostname'
    id_pattern = HOST_ID_PATTERN

    def get_parser(self, prog_name):
        parser = super(ReallocateHost, self).get_parser(prog_name)
        parser.add_argument(
            '--lease-id',
            help='Lease ID to reallocate host from.')
        parser.add_argument(
            '--reservation-id',
            help='Reservation ID to reallocate host from')
        return parser

    def args2body(self, parsed_args):
        params = {}

        if parsed_args.reservation_id:
            params['reservation_id'] = parsed_args.reservation_id
        elif parsed_args.lease_id:
            params['lease_id'] = parsed_args.lease_id

        return params


class ShowHostCapability(command.ShowCapabilityCommand):
    """Show host capability."""
    resource = 'host'
    json_indent = 4
    log = logging.getLogger(__name__ + '.ShowHostCapability')


class ListHostCapabilities(command.ListCommand):
    """List host capabilities."""
    resource = 'host'
    log = logging.getLogger(__name__ + '.ListHostCapabilities')
    list_columns = ['property', 'private', 'capability_values']

    def args2body(self, parsed_args):
        params = {'detail': parsed_args.detail}
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
        data = resource_manager.list_capabilities(**body)
        return data

    def get_parser(self, prog_name):
        parser = super(ListHostCapabilities, self).get_parser(prog_name)
        parser.add_argument(
            '--detail',
            action='store_true',
            help='Return capabilities with values and attributes.',
            default=False
        )
        parser.add_argument(
            '--sort-by', metavar="<extra_capability_column>",
            help='column name used to sort result',
            default='property'
        )
        return parser


class UpdateHostCapability(command.UpdateCapabilityCommand):
    """Update attributes of a host capability."""
    resource = 'host'
    json_indent = 4
    log = logging.getLogger(__name__ + '.UpdateHostCapability')
    name_key = 'capability_name'
