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

from oslo_utils import timeutils

from blazarclient import base
from blazarclient.i18n import _
from blazarclient import utils


class LeaseClientManager(base.BaseClientManager):
    """Manager for the lease connected requests."""

    def create(self, name, start, end, reservations, events, before_end=None):
        """Creates lease from values passed."""
        values = {'name': name, 'start_date': start, 'end_date': end,
                  'reservations': reservations, 'events': events,
                  'before_end_date': before_end}

        resp, body = self.request_manager.post('/leases', body=values)
        return body['lease']

    def get(self, lease_id):
        """Describes lease specifications such as name, status and locked
        condition.
        """
        resp, body = self.request_manager.get('/leases/%s' % lease_id)
        return body['lease']

    def update(self, lease_id, name=None, prolong_for=None, reduce_by=None,
               end_date=None, advance_by=None, defer_by=None, start_date=None,
               reservations=None):
        """Update attributes of the lease."""
        values = {}
        if name:
            values['name'] = name

        lease_end_date_change = prolong_for or reduce_by or end_date
        lease_start_date_change = defer_by or advance_by or start_date
        lease = None

        if lease_end_date_change:
            lease = self.get(lease_id)
            if end_date:
                date = timeutils.parse_strtime(end_date, utils.API_DATE_FORMAT)
                values['end_date'] = date.strftime(utils.API_DATE_FORMAT)
            else:
                self._add_lease_date(values, lease, 'end_date',
                                     lease_end_date_change,
                                     prolong_for is not None)

        if lease_start_date_change:
            if lease is None:
                lease = self.get(lease_id)
            if start_date:
                date = timeutils.parse_strtime(start_date,
                                               utils.API_DATE_FORMAT)
                values['start_date'] = date.strftime(utils.API_DATE_FORMAT)
            else:
                self._add_lease_date(values, lease, 'start_date',
                                     lease_start_date_change,
                                     defer_by is not None)

        if reservations:
            values['reservations'] = reservations

        if not values:
            return _('No values to update passed.')
        resp, body = self.request_manager.put('/leases/%s' % lease_id,
                                              body=values)
        return body['lease']

    def delete(self, lease_id):
        """Deletes lease with specified ID."""
        resp, body = self.request_manager.delete('/leases/%s' % lease_id)

    def list(self, sort_by=None):
        """List all leases."""
        resp, body = self.request_manager.get('/leases')
        leases = body['leases']
        if sort_by:
            leases = sorted(leases, key=lambda lease: lease[sort_by])
        return leases

    def _add_lease_date(self, values, lease, key, delta_date, positive_delta):
        delta_sec = utils.from_elapsed_time_to_delta(
            delta_date,
            pos_sign=positive_delta)
        date = timeutils.parse_strtime(lease[key],
                                       utils.LEASE_DATE_FORMAT)
        values[key] = (date + delta_sec).strftime(utils.API_DATE_FORMAT)
