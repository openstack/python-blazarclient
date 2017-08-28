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


from blazarclient.v1 import hosts
from blazarclient.v1 import leases


class Client(object):
    """Top level object to communicate with Blazar.

    Contains managers to control requests that should be passed to each type of
    resources - leases, events, etc.

    **Examples**
        client = Client()
        client.lease.list()
        client.event.list(<lease_id>)
        ...
    """

    def __init__(self, session, *args, **kwargs):
        self.session = session
        self.version = '1'

        self.lease = leases.LeaseClientManager(session=self.session,
                                               version=self.version,
                                               *args,
                                               **kwargs)
        self.host = hosts.ComputeHostClientManager(session=self.session,
                                                   version=self.version,
                                                   *args,
                                                   **kwargs)
