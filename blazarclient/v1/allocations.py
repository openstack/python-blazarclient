# Copyright (c) 2019 University of Chicago.
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


class AllocationClientManager(base.BaseClientManager):
    """Manager for the ComputeHost connected requests."""

    def get(self, resource, resource_id):
        """Get allocation for resource identified by type and ID."""
        resp, body = self.request_manager.get(
            '/%s/%s/allocation' % (resource, resource_id))
        return body['allocation']

    def list(self, resource, sort_by=None):
        """List allocations for all resources of a type."""
        resp, body = self.request_manager.get('/%s/allocations' % resource)
        allocations = body['allocations']
        if sort_by:
            allocations = sorted(allocations, key=lambda alloc: alloc[sort_by])
        return allocations
