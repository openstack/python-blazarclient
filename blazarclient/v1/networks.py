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


class NetworkClientManager(base.BaseClientManager):
    """Manager for network segment requests."""

    def create(self, network_type, physical_network, segment_id, **kwargs):
        """Creates a network segment from values passed."""
        values = {'network_type': network_type,
                  'physical_network': physical_network,
                  'segment_id': segment_id}
        values.update(**kwargs)
        resp, body = self.request_manager.post('/networks', body=values)
        return body['network']

    def get(self, network_id):
        """Show network segment details."""
        resp, body = self.request_manager.get('/networks/%s' % network_id)
        return body['network']

    def update(self, network_id, values):
        """Update attributes of the network segment."""
        if not values:
            return _('No values to update passed.')
        resp, body = self.request_manager.put(
            '/networks/%s' % network_id, body=values
        )
        return body['network']

    def delete(self, network_id):
        """Delete network segment with specified ID."""
        resp, body = self.request_manager.delete('/networks/%s' % network_id)

    def list(self, sort_by=None):
        """List all network segments."""
        resp, body = self.request_manager.get('/networks')
        networks = body['networks']
        if sort_by:
            networks = sorted(networks, key=lambda l: l[sort_by])
        return networks

    def get_allocation(self, network_id):
        """Get allocation for network."""
        resp, body = self.request_manager.get(
            '/networks/%s/allocation' % network_id)
        return body['allocation']

    def list_allocations(self, sort_by=None):
        """List allocations for all networks."""
        resp, body = self.request_manager.get('/networks/allocations')
        allocations = body['allocations']
        if sort_by:
            allocations = sorted(allocations, key=lambda l: l[sort_by])
        return allocations
