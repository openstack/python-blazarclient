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
import datetime
import logging
import re

from climateclient import command
from climateclient import exception


class ListLeases(command.ListCommand):
    resource = 'lease'
    log = logging.getLogger(__name__ + '.ListLeases')
    list_columns = ['id', 'name', 'start_date', 'end_date']


class ShowLease(command.ShowCommand):
    resource = 'lease'
    json_indent = 4
    log = logging.getLogger(__name__ + '.ShowLease')


class CreateLease(command.CreateCommand):
    resource = 'lease'
    log = logging.getLogger(__name__ + '.CreateLease')
    default_start = datetime.datetime.utcnow()
    default_end = default_start + datetime.timedelta(days=1)

    def get_parser(self, prog_name):
        parser = super(CreateLease, self).get_parser(prog_name)
        parser.add_argument(
            'name', metavar=self.resource.upper(),
            help='Name for the %s' % self.resource
        )
        parser.add_argument(
            '--start-date',
            dest='start',
            help='Time (YYYY-MM-DD HH:MM) UTC TZ for starting the lease '
                 '(default: now)',
            default=self.default_start
        )
        parser.add_argument(
            '--end-date',
            dest='end',
            help='Time (YYYY-MM-DD HH:MM) UTC TZ for ending the lease '
                 '(default: 24h later)',
            default=self.default_end
        )
        parser.add_argument(
            '--physical-reservation',
            metavar="<min=int,max=int,hypervisor_properties=str,"
                    "resource_properties=str>",
            action='append',
            dest='physical_reservations',
            help='Create a reservation for physical compute hosts. '
                 'Specify option multiple times to create multiple '
                 'reservations. '
                 'min: minimum number of hosts to reserve. '
                 'max: maximum number of hosts to reserve. '
                 'hypervisor_properties: JSON string, see doc. '
                 'resource_properties: JSON string, see doc. ',
            default=[]
        )
        parser.add_argument(
            '--reservation',
            metavar="<key=value>",
            action='append',
            dest='reservations',
            help='key/value pairs for creating a generic reservation. '
                 'Specify option multiple times to create multiple '
                 'reservations. ',
            default=[]
        )
        parser.add_argument(
            '--event', metavar='<event_type=str,event_date=time>',
            action='append',
            dest='events',
            help='Creates an event with key/value pairs for the lease. '
                 'Specify option multiple times to create multiple events. '
                 'event_type: type of event (e.g. notification). '
                 'event_date: Time for event (YYYY-MM-DD HH:MM) UTC TZ. ',
            default=[]
        )
        return parser

    def args2body(self, parsed_args):
        params = {}
        if parsed_args.name:
            params['name'] = parsed_args.name
        if not isinstance(parsed_args.start, datetime.datetime):
            try:
                parsed_args.start = datetime.datetime.strptime(
                    parsed_args.start, '%Y-%m-%d %H:%M')
            except ValueError:
                raise exception.IncorrectLease
        if not isinstance(parsed_args.end, datetime.datetime):
            try:
                parsed_args.end = datetime.datetime.strptime(
                    parsed_args.end, '%Y-%m-%d %H:%M')
            except ValueError:
                raise exception.IncorrectLease
        if parsed_args.start > parsed_args.end:
            raise exception.IncorrectLease
        params['start'] = datetime.datetime.strftime(parsed_args.start,
                                                     '%Y-%m-%d %H:%M')
        params['end'] = datetime.datetime.strftime(parsed_args.end,
                                                   '%Y-%m-%d %H:%M')

        params['reservations'] = []
        params['events'] = []

        physical_reservations = []
        for phys_res_str in parsed_args.physical_reservations:
            err_msg = ("Invalid physical-reservation argument '%s'. "
                       "Reservation arguments must be of the "
                       "form --physical-reservation <min=int,max=int,"
                       "hypervisor_properties=str,resource_properties=str>"
                       % phys_res_str)
            phys_res_info = {"min": "", "max": "", "hypervisor_properties": "",
                             "resource_properties": ""}
            prog = re.compile('^(\w+)=(\w+|\[[^]]+\])(?:,(.+))?$')

            def parse_params(params):
                match = prog.search(params)
                if match:
                    self.log.info("Matches: %s", match.groups())
                    k, v = match.group(1, 2)
                    if k in phys_res_info:
                        phys_res_info[k] = v
                    else:
                        raise exception.IncorrectLease(err_msg)
                    if len(match.groups()) == 3 and match.group(3) is not None:
                        parse_params(match.group(3))

            parse_params(phys_res_str)
            if not phys_res_info['min'] and not phys_res_info['max']:
                raise exception.IncorrectLease(err_msg)
            # NOTE(sbauza): The resource type should be conf-driven mapped with
            #               climate.conf file but that's potentially on another
            #               host
            phys_res_info['resource_type'] = 'physical:host'
            physical_reservations.append(phys_res_info)
        if physical_reservations:
            params['reservations'] += physical_reservations

        reservations = []
        for res_str in parsed_args.reservations:
            err_msg = ("Invalid reservation argument '%s'. "
                       "Reservation arguments must be of the "
                       "form --reservation <key=value>"
                       % res_str)
            res_info = {}
            for kv_str in res_str.split(","):
                try:
                    k, v = kv_str.split("=", 1)
                except ValueError:
                    raise exception.IncorrectLease(err_msg)
                res_info[k] = v
            reservations.append(res_info)
        if reservations:
            params['reservations'] += reservations

        if not params['reservations']:
            raise exception.IncorrectLease

        events = []
        for event_str in parsed_args.events:
            err_msg = ("Invalid event argument '%s'. "
                       "Event arguments must be of the "
                       "form --event <event_type=str,event_date=time>"
                       % event_str)
            event_info = {"event_type": "", "event_date": ""}
            for kv_str in event_str.split(","):
                try:
                    k, v = kv_str.split("=", 1)
                except ValueError:
                    raise exception.IncorrectLease(err_msg)
                if k in event_info:
                    event_info[k] = v
                else:
                    raise exception.IncorrectLease(err_msg)
            if not event_info['event_type'] and not event_info['event_date']:
                raise exception.IncorrectLease(err_msg)
            event_date = event_info['event_date']
            try:
                date = datetime.datetime.strptime(event_date, '%Y-%m-%d %H:%M')
                event_date = datetime.datetime.strftime(date, '%Y-%m-%d %H:%M')
                event_info['event_date'] = event_date
            except ValueError:
                raise exception.IncorrectLease
            events.append(event_info)
        if events:
            params['events'] = events

        return params


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
        #prolong-for and reduce_by are mutually exclusive
        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            '--prolong-for',
            help='Time to prolong lease for',
            default=None
        )
        group.add_argument(
            '--prolong_for',
            help=argparse.SUPPRESS,
            default=None
        )
        group.add_argument(
            '--reduce-by',
            help='Time to reduce lease by',
            default=None
        )
        return parser

    def args2body(self, parsed_args):
        params = {}
        if parsed_args.name:
            params['name'] = parsed_args.name
        if parsed_args.prolong_for:
            params['prolong_for'] = parsed_args.prolong_for
        if parsed_args.reduce_by:
            params['reduce_by'] = parsed_args.reduce_by
        return params


class DeleteLease(command.DeleteCommand):
    resource = 'lease'
    log = logging.getLogger(__name__ + '.DeleteLease')
