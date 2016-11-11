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

from climateclient import base
from climateclient.i18n import _
from climateclient import utils


class LeaseClientManager(base.BaseClientManager):
    """Manager for the lease connected requests."""

    def create(self, name, start, end, reservations, events):
        """Creates lease from values passed."""
        values = {'name': name, 'start_date': start, 'end_date': end,
                  'reservations': reservations, 'events': events}

        return self._create('/leases', values, 'lease')

    def get(self, lease_id):
        """Describes lease specifications such as name, status and locked
        condition.
        """
        return self._get('/leases/%s' % lease_id, 'lease')

    def update(self, lease_id, name=None, prolong_for=None, reduce_by=None,
               advance_by=None, defer_by=None):
        """Update attributes of the lease."""
        values = {}
        if name:
            values['name'] = name

        lease_end_date_change = prolong_for or reduce_by
        lease_start_date_change = defer_by or advance_by
        lease = None

        if lease_end_date_change:
            lease = self.get(lease_id)
            self._add_lease_date(values, lease, 'end_date',
                                 lease_end_date_change,
                                 prolong_for is not None)

        if lease_start_date_change:
            if lease is None:
                lease = self.get(lease_id)
            self._add_lease_date(values, lease, 'start_date',
                                 lease_start_date_change,
                                 defer_by is not None)

        if not values:
            return _('No values to update passed.')
        return self._update('/leases/%s' % lease_id, values,
                            response_key='lease')

    def delete(self, lease_id):
        """Deletes lease with specified ID."""
        self._delete('/leases/%s' % lease_id)

    def list(self, sort_by=None):
        """List all leases."""
        leases = self._get('/leases', 'leases')
        if sort_by:
            leases = sorted(leases, key=lambda l: l[sort_by])
        return leases

    def _add_lease_date(self, values, lease, key, delta_date, positive_delta):
        delta_sec = utils.from_elapsed_time_to_delta(
            delta_date,
            pos_sign=positive_delta)
        date = timeutils.parse_strtime(lease[key],
                                       utils.LEASE_DATE_FORMAT)
        values[key] = timeutils.strtime(date + delta_sec,
                                        utils.API_DATE_FORMAT)
