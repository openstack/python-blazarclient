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

from blazarclient import base
from blazarclient.i18n import _


class ComputeHostClientManager(base.BaseClientManager):
    """Manager for the ComputeHost connected requests."""

    def create(self, name, **kwargs):
        """Creates host from values passed."""
        values = {'name': name}
        values.update(**kwargs)
        resp, body = self.request_manager.post('/os-hosts', body=values)
        return body['host']

    def get(self, host_id):
        """Describe host specifications such as name and details."""
        resp, body = self.request_manager.get('/os-hosts/%s' % host_id)
        return body['host']

    def update(self, host_id, values):
        """Update attributes of the host."""
        if not values:
            return _('No values to update passed.')
        resp, body = self.request_manager.put(
            '/os-hosts/%s' % host_id, body=values
        )
        return body['host']

    def delete(self, host_id):
        """Delete host with specified ID."""
        resp, body = self.request_manager.delete('/os-hosts/%s' % host_id)

    def list(self, sort_by=None):
        """List all hosts."""
        resp, body = self.request_manager.get('/os-hosts')
        hosts = body['hosts']
        if sort_by:
            hosts = sorted(hosts, key=lambda l: l[sort_by])
        return hosts

    def get_allocation(self, host_id):
        """Get allocation for host."""
        resp, body = self.request_manager.get(
            '/os-hosts/%s/allocation' % host_id)
        return body['allocation']

    def list_allocations(self, sort_by=None):
        """List allocations for all hosts."""
        resp, body = self.request_manager.get('/os-hosts/allocations')
        allocations = body['allocations']
        if sort_by:
            allocations = sorted(allocations, key=lambda l: l[sort_by])
        return allocations
