# Copyright (c) 2019 StackHPC Ltd.
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


class ListFloatingIPs(command.ListCommand):
    """Print a list of floating IPs."""
    resource = 'floatingip'
    log = logging.getLogger(__name__ + '.ListFloatingIPs')
    list_columns = ['id', 'floating_ip_address', 'floating_network_id']

    def get_parser(self, prog_name):
        parser = super(ListFloatingIPs, self).get_parser(prog_name)
        parser.add_argument(
            '--sort-by', metavar="<floatingip_column>",
            help='column name used to sort result',
            default='id'
        )
        return parser


class ShowFloatingIP(command.ShowCommand):
    """Show floating IP details."""
    resource = 'floatingip'
    allow_names = False
    json_indent = 4
    log = logging.getLogger(__name__ + '.ShowFloatingIP')


class CreateFloatingIP(command.CreateCommand):
    """Create a floating IP."""
    resource = 'floatingip'
    json_indent = 4
    log = logging.getLogger(__name__ + '.CreateFloatingIP')

    def get_parser(self, prog_name):
        parser = super(CreateFloatingIP, self).get_parser(prog_name)
        parser.add_argument(
            'network_id', metavar='NETWORK_ID',
            help='External network ID to which the floating IP belongs'
        )
        parser.add_argument(
            'floating_ip_address', metavar='FLOATING_IP_ADDRESS',
            help='Floating IP address to add to Blazar'
        )
        return parser

    def args2body(self, parsed_args):
        params = {}
        if parsed_args.network_id:
            params['network_id'] = parsed_args.network_id
        if parsed_args.floating_ip_address:
            params['floating_ip_address'] = parsed_args.floating_ip_address
        return params


class DeleteFloatingIP(command.DeleteCommand):
    """Delete a floating IP."""
    resource = 'floatingip'
    allow_names = False
    log = logging.getLogger(__name__ + '.DeleteFloatingIP')
