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

from climateclient import command


class ListHosts(command.ListCommand):
    resource = 'host'
    log = logging.getLogger(__name__ + '.ListHosts')
    list_columns = ['id', 'hypervisor_hostname', 'vcpus', 'memory_mb',
                    'local_gb']


class ShowHost(command.ShowCommand):
    resource = 'host'
    json_indent = 4
    # NOTE(sbauza): We can't find by name as there is currently no column
    #  called 'name' but rather 'hypervisor_hostname'
    allow_names = False
    log = logging.getLogger(__name__ + '.ShowHost')


class CreateHost(command.CreateCommand):
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
    resource = 'host'
    allow_names = False
    log = logging.getLogger(__name__ + '.UpdateHost')

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
    resource = 'host'
    # NOTE(sbauza): We can't find by name as there is currently no column
    #  called 'name' but rather 'hypervisor_hostname'
    allow_names = False
    log = logging.getLogger(__name__ + '.DeleteHost')
