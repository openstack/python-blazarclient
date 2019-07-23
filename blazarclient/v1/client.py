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

import logging

from blazarclient.v1 import floatingips
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

    version = '1'

    def __init__(self, blazar_url=None, auth_token=None, session=None,
                 **kwargs):
        self.blazar_url = blazar_url
        self.auth_token = auth_token
        self.session = session

        if not self.session:
            logging.warning('Use a keystoneauth session object for the '
                            'authentication. The authentication with '
                            'blazar_url and auth_token is deprecated.')

        self.lease = leases.LeaseClientManager(blazar_url=self.blazar_url,
                                               auth_token=self.auth_token,
                                               session=self.session,
                                               version=self.version,
                                               **kwargs)
        self.host = hosts.ComputeHostClientManager(blazar_url=self.blazar_url,
                                                   auth_token=self.auth_token,
                                                   session=self.session,
                                                   version=self.version,
                                                   **kwargs)
        self.floatingip = floatingips.FloatingIPClientManager(
            blazar_url=self.blazar_url,
            auth_token=self.auth_token,
            session=self.session,
            version=self.version,
            **kwargs)
