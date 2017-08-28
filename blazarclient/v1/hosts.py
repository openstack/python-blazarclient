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

from keystoneauth1 import adapter

from blazarclient.i18n import _


class ComputeHostClientManager(adapter.LegacyJsonAdapter):
    """Manager for the ComputeHost connected requests."""

    client_name = 'python-blazarclient'

    def create(self, name, **kwargs):
        """Creates host from values passed."""
        values = {'name': name}
        values.update(**kwargs)
        resp, body = self.post('/os-hosts', body=values)
        return body['host']

    def get(self, host_id):
        """Describes host specifications such as name and details."""
        resp, body = super(ComputeHostClientManager,
                           self).get('/os-hosts/%s' % host_id)
        return body['host']

    def update(self, host_id, values):
        """Update attributes of the host."""
        if not values:
            return _('No values to update passed.')
        resp, body = self.put('/os-hosts/%s' % host_id, body=values)
        return body['host']

    def delete(self, host_id):
        """Deletes host with specified ID."""
        resp, body = super(ComputeHostClientManager,
                           self).delete('/os-hosts/%s' % host_id)

    def list(self, sort_by=None):
        """List all hosts."""
        resp, body = super(ComputeHostClientManager,
                           self).get('/os-hosts')
        hosts = body['hosts']
        if sort_by:
            hosts = sorted(hosts, key=lambda l: l[sort_by])
        return hosts
