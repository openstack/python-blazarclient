# Copyright (c) 2019 StackHPC Ltd.
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


class FloatingIPClientManager(base.BaseClientManager):
    """Manager for floating IP requests."""

    def create(self, network_id, floating_ip_address, **kwargs):
        """Creates a floating IP from values passed."""
        values = {'floating_network_id': network_id,
                  'floating_ip_address': floating_ip_address}
        values.update(**kwargs)
        resp, body = self.request_manager.post('/floatingips', body=values)
        return body['floatingip']

    def get(self, floatingip_id):
        """Show floating IP details."""
        resp, body = self.request_manager.get(
            '/floatingips/%s' % floatingip_id)
        return body['floatingip']

    def delete(self, floatingip_id):
        """Deletes floating IP with specified ID."""
        resp, body = self.request_manager.delete(
            '/floatingips/%s' % floatingip_id)

    def list(self, sort_by=None):
        """List all floating IPs."""
        resp, body = self.request_manager.get('/floatingips')
        floatingips = body['floatingips']
        if sort_by:
            floatingips = sorted(floatingips, key=lambda fip: fip[sort_by])
        return floatingips
