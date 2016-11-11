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

from climateclient import base
from climateclient.i18n import _


class ComputeHostClientManager(base.BaseClientManager):
    """Manager for the ComputeHost connected requests."""

    def create(self, name, **kwargs):
        """Creates host from values passed."""
        values = {'name': name}
        values.update(**kwargs)

        return self._create('/os-hosts', values, response_key='host')

    def get(self, host_id):
        """Describes host specifications such as name and details."""
        return self._get('/os-hosts/%s' % host_id, 'host')

    def update(self, host_id, values):
        """Update attributes of the host."""
        if not values:
            return _('No values to update passed.')
        return self._update('/os-hosts/%s' % host_id, values,
                            response_key='host')

    def delete(self, host_id):
        """Deletes host with specified ID."""
        self._delete('/os-hosts/%s' % host_id)

    def list(self, sort_by=None):
        """List all hosts."""
        hosts = self._get('/os-hosts', 'hosts')
        if sort_by:
            hosts = sorted(hosts, key=lambda l: l[sort_by])
        return hosts
