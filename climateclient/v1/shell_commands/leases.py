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

import argparse
import logging

from climateclient import command


class ListLeases(command.ListCommand):
    resource = 'lease'
    log = logging.getLogger(__name__ + '.ListLeases')
    list_columns = ['id', 'name', 'start_date', 'end_date']


class ShowLease(command.ShowCommand):
    resource = 'lease'
    json_indent = 4
    log = logging.getLogger(__name__ + '.ShowLease')


class CreateLease(command.CreateCommand):
    """Comprehended only for physical reservations.

    For physical reservations lease is created manually.

    For virtual reservations we need id of the reserved resource to create
    lease. When service creates reserved resource (Nova-VM, Cinder-volume,
    etc.) it comes to Climate and creates lease via Python client.

    """
    pass


class UpdateLease(command.UpdateCommand):
    resource = 'lease'
    log = logging.getLogger(__name__ + '.UpdateLease')

    def get_parser(self, prog_name):
        parser = super(UpdateLease, self).get_parser(prog_name)
        parser.add_argument(
            '--name',
            help='New name for the lease',
            default=None
        )
        parser.add_argument(
            '--prolong-for',
            help='Time to prolong lease for',
            default=None
        )
        parser.add_argument(
            '--prolong_for',
            help=argparse.SUPPRESS,
            default=None
        )
        return parser

    def args2body(self, parsed_args):
        params = {}
        if parsed_args.name:
            params['name'] = parsed_args.name
        if parsed_args.prolong_for:
            params['prolong_for'] = parsed_args.prolong_for
        return params


class DeleteLease(command.DeleteCommand):
    resource = 'lease'
    log = logging.getLogger(__name__ + '.DeleteLease')
