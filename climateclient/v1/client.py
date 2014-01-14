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


from climateclient.v1 import hosts
from climateclient.v1 import leases


class Client(object):
    """Top level object to communicate with Climate.

    Contains managers to control requests that should be passed to each type of
    resources - leases, events, etc.

    **Examples**
        client = Client()
        client.lease.list()
        client.event.list(<lease_id>)
        ...
    """

    def __init__(self, climate_url, auth_token):
        self.climate_url = climate_url
        self.auth_token = auth_token

        self.lease = leases.LeaseClientManager(self.climate_url,
                                               self.auth_token)
        self.host = hosts.ComputeHostClientManager(self.climate_url,
                                                   self.auth_token)
