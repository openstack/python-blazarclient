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

from oslo_serialization import jsonutils
from oslo_utils import strutils

from blazarclient import command
from blazarclient import exception


# All valid reservation parameters must be added to CREATE_RESERVATION_KEYS to
# make them parsable. Note that setting the default value to None ensures that
# the parameter is not included in the POST request if absent.
CREATE_RESERVATION_KEYS = {
    "physical:host": {
        "min": "",
        "max": "",
        "hypervisor_properties": "",
        "resource_properties": "",
        "before_end": None,
        "resource_type": 'physical:host'
    },
    "virtual:floatingip": {
        "amount": 1,
        "network_id": None,
        "required_floatingips": [],
        "resource_type": 'virtual:floatingip'
    },
    "virtual:instance": {
        "vcpus": "",
        "memory_mb": "",
        "disk_gb": "",
        "amount": "",
        "affinity": "None",
        "resource_properties": "",
        "resource_type": 'virtual:instance'
    },
    "others": {
        ".*": None
    }
}


def _utc_now():
    """Wrap datetime.datetime.utcnow so it can be mocked in unit tests.

    This is required because some of the tests require understanding the
    'current time'; simply mocking utcnow() is made very difficult by
    the many different ways the datetime package is used in this module.
    """
    return datetime.datetime.utcnow()


class ListLeases(command.ListCommand):
    """Print a list of leases."""
    resource = 'lease'
    log = logging.getLogger(__name__ + '.ListLeases')
    list_columns = ['id', 'name', 'start_date', 'end_date']

    def get_parser(self, prog_name):
        parser = super(ListLeases, self).get_parser(prog_name)
        parser.add_argument(
            '--sort-by', metavar="<lease_column>",
            help='column name used to sort result',
            default='name'
        )
        return parser


class ShowLease(command.ShowCommand):
    """Show details about the given lease."""
    resource = 'lease'
    json_indent = 4
    log = logging.getLogger(__name__ + '.ShowLease')


class CreateLeaseBase(command.CreateCommand):
    """Create a lease."""
    resource = 'lease'
    json_indent = 4
    log = logging.getLogger(__name__ + '.CreateLease')
    default_start = 'now'
    default_end = _utc_now() + datetime.timedelta(days=1)

    def get_parser(self, prog_name):
        parser = super(CreateLeaseBase, self).get_parser(prog_name)
        parser.add_argument(
            'name', metavar=self.resource.upper(),
            help='Name for the %s' % self.resource
        )
        parser.add_argument(
            '--start-date',
            dest='start',
            help='Time (YYYY-MM-DD HH:MM) UTC TZ for starting the lease '
                 '(default: current time on the server)',
            default=self.default_start
        )
        parser.add_argument(
            '--end-date',
            dest='end',
            help='Time (YYYY-MM-DD HH:MM) UTC TZ for ending the lease '
                 '(default: 24h from now)',
            default=self.default_end
        )
        parser.add_argument(
            '--before-end-date',
            dest='before_end',
            help='Time (YYYY-MM-DD HH:MM) UTC TZ for taking an action before '
                 'the end of the lease (default: depends on system default)',
            default=None
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
        params = self._generate_params(parsed_args)
        if not params['reservations']:
            raise exception.IncorrectLease
        return params

    def _generate_params(self, parsed_args):
        params = {}
        if parsed_args.name:
            params['name'] = parsed_args.name
        if not isinstance(parsed_args.start, datetime.datetime):
            if parsed_args.start != 'now':
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

        if parsed_args.start == 'now':
            start = _utc_now()
        else:
            start = parsed_args.start

        if start > parsed_args.end:
            raise exception.IncorrectLease

        if parsed_args.before_end:
            try:
                parsed_args.before_end = datetime.datetime.strptime(
                    parsed_args.before_end, '%Y-%m-%d %H:%M')
            except ValueError:
                raise exception.IncorrectLease
            if (parsed_args.before_end < start or
                    parsed_args.end < parsed_args.before_end):
                raise exception.IncorrectLease
            params['before_end'] = datetime.datetime.strftime(
                parsed_args.before_end, '%Y-%m-%d %H:%M')

        if parsed_args.start == 'now':
            params['start'] = parsed_args.start
        else:
            params['start'] = datetime.datetime.strftime(parsed_args.start,
                                                         '%Y-%m-%d %H:%M')
        params['end'] = datetime.datetime.strftime(parsed_args.end,
                                                   '%Y-%m-%d %H:%M')

        params['reservations'] = []
        params['events'] = []

        reservations = []
        for res_str in parsed_args.reservations:
            err_msg = ("Invalid reservation argument '%s'. "
                       "Reservation arguments must be of the "
                       "form --reservation <key=value>"
                       % res_str)

            if "physical:host" in res_str:
                defaults = CREATE_RESERVATION_KEYS['physical:host']
            elif "virtual:instance" in res_str:
                defaults = CREATE_RESERVATION_KEYS['virtual:instance']
            elif "virtual:floatingip" in res_str:
                defaults = CREATE_RESERVATION_KEYS['virtual:floatingip']
            else:
                defaults = CREATE_RESERVATION_KEYS['others']

            res_info = self._parse_params(res_str, defaults, err_msg)
            reservations.append(res_info)

        if reservations:
            params['reservations'] += reservations

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

    def _parse_params(self, str_params, default, err_msg):
        request_params = {}
        prog = re.compile('^(?:(.*),)?(%s)=(.*)$'
                          % "|".join(default.keys()))

        while str_params != "":
            match = prog.search(str_params)

            if match is None:
                raise exception.IncorrectLease(err_msg)

            self.log.info("Matches: %s", match.groups())
            k, v = match.group(2, 3)
            if k in request_params.keys():
                raise exception.DuplicatedLeaseParameters(err_msg)
            else:
                if strutils.is_int_like(v):
                    request_params[k] = int(v)
                elif isinstance(default[k], list):
                    request_params[k] = jsonutils.loads(v)
                else:
                    request_params[k] = v

            str_params = match.group(1) if match.group(1) else ""

        request_params.update({k: v for k, v in default.items()
                               if k not in request_params.keys() and
                               v is not None})
        return request_params


class CreateLease(CreateLeaseBase):

    def get_parser(self, prog_name):
        parser = super(CreateLease, self).get_parser(prog_name)
        parser.add_argument(
            '--physical-reservation',
            metavar="<min=int,max=int,hypervisor_properties=str,"
                    "resource_properties=str,before_end=str>",
            action='append',
            dest='physical_reservations',
            help='Create a reservation for physical compute hosts. '
                 'Specify option multiple times to create multiple '
                 'reservations. '
                 'min: minimum number of hosts to reserve. '
                 'max: maximum number of hosts to reserve. '
                 'hypervisor_properties: JSON string, see doc. '
                 'resource_properties: JSON string, see doc. '
                 'before_end: JSON string, see doc. ',
            default=[]
        )
        return parser

    def args2body(self, parsed_args):
        params = self._generate_params(parsed_args)

        physical_reservations = []
        for phys_res_str in parsed_args.physical_reservations:
            err_msg = ("Invalid physical-reservation argument '%s'. "
                       "Reservation arguments must be of the "
                       "form --physical-reservation <min=int,max=int,"
                       "hypervisor_properties=str,resource_properties=str,"
                       "before_end=str>"
                       % phys_res_str)
            defaults = CREATE_RESERVATION_KEYS["physical:host"]
            phys_res_info = self._parse_params(phys_res_str, defaults, err_msg)

            if not (phys_res_info['min'] and phys_res_info['max']):
                raise exception.IncorrectLease(err_msg)

            if not (strutils.is_int_like(phys_res_info['min']) and
                    strutils.is_int_like(phys_res_info['max'])):
                raise exception.IncorrectLease(err_msg)

            min_host = int(phys_res_info['min'])
            max_host = int(phys_res_info['max'])

            if min_host > max_host:
                err_msg = ("Invalid physical-reservation argument '%s'. "
                           "Reservation argument min value must be "
                           "less than max value"
                           % phys_res_str)
                raise exception.IncorrectLease(err_msg)

            if min_host == 0 or max_host == 0:
                err_msg = ("Invalid physical-reservation argument '%s'. "
                           "Reservation arguments min and max values "
                           "must be greater than or equal to 1"
                           % phys_res_str)
                raise exception.IncorrectLease(err_msg)

            # NOTE(sbauza): The resource type should be conf-driven mapped with
            #               blazar.conf file but that's potentially on another
            #               host
            phys_res_info['resource_type'] = 'physical:host'
            physical_reservations.append(phys_res_info)
        if physical_reservations:
            # We prepend the physical_reservations to preserve legacy order
            # of reservations
            params['reservations'] = physical_reservations \
                + params['reservations']

        return params


class UpdateLease(command.UpdateCommand):
    """Update a lease."""
    resource = 'lease'
    json_indent = 4
    log = logging.getLogger(__name__ + '.UpdateLease')

    def get_parser(self, prog_name):
        parser = super(UpdateLease, self).get_parser(prog_name)
        parser.add_argument(
            '--name',
            help='New name for the lease',
            default=None
        )
        parser.add_argument(
            '--reservation',
            metavar="<key=value>",
            action='append',
            help='Reservation values to update. The reservation must be '
                 'selected with the id=<reservation-id> key-value pair.',
            default=None)

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
        group.add_argument(
            '--end-date',
            help='end date of the lease',
            default=None)

        #defer-by and a 'future' advance-by are mutually exclusive
        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            '--defer-by',
            help='Time to defer the lease start',
            default=None
        )
        group.add_argument(
            '--advance-by',
            help='Time to advance the lease start',
            default=None
        )
        group.add_argument(
            '--start-date',
            help='start date of the lease',
            default=None)

        return parser

    def args2body(self, parsed_args):
        params = {}
        if parsed_args.name:
            params['name'] = parsed_args.name
        if parsed_args.prolong_for:
            params['prolong_for'] = parsed_args.prolong_for
        if parsed_args.reduce_by:
            params['reduce_by'] = parsed_args.reduce_by
        if parsed_args.end_date:
            params['end_date'] = parsed_args.end_date
        if parsed_args.defer_by:
            params['defer_by'] = parsed_args.defer_by
        if parsed_args.advance_by:
            params['advance_by'] = parsed_args.advance_by
        if parsed_args.start_date:
            params['start_date'] = parsed_args.start_date
        if parsed_args.reservation:
            keys = set([
                # General keys
                'id',
                # Keys for host reservation
                'min', 'max', 'hypervisor_properties', 'resource_properties',
                # Keys for instance reservation
                'vcpus', 'memory_mb', 'disk_gb', 'amount', 'affinity',
                # Keys for floating IP reservation
                'amount', 'network_id', 'required_floatingips',
            ])
            list_keys = ['required_floatingips']
            params['reservations'] = []
            reservations = []
            for res_str in parsed_args.reservation:
                err_msg = ("Invalid reservation argument '%s'. "
                           "Reservation arguments must be of the form "
                           "--reservation <key=value>" % res_str)
                res_info = {}
                prog = re.compile('^(?:(.*),)?(%s)=(.*)$' % '|'.join(keys))

                def parse_params(params):
                    match = prog.search(params)
                    if match:
                        k, v = match.group(2, 3)
                        if k in list_keys:
                            v = jsonutils.loads(v)
                        elif strutils.is_int_like(v):
                            v = int(v)
                        res_info[k] = v
                        if match.group(1) is not None:
                            parse_params(match.group(1))

                parse_params(res_str)
                if res_info:
                    if 'id' not in res_info:
                        raise exception.IncorrectLease(
                            'The key-value pair id=<reservation_id> is '
                            'required for the --reservation argument')
                    reservations.append(res_info)
            if not reservations:
                raise exception.IncorrectLease(err_msg)
            params['reservations'] = reservations
        return params


class DeleteLease(command.DeleteCommand):
    """Delete a lease."""
    resource = 'lease'
    log = logging.getLogger(__name__ + '.DeleteLease')
