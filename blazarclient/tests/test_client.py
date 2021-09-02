# Copyright (c) 2014 Mirantis Inc.
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

from oslo_utils import importutils

from blazarclient import client
from blazarclient import exception
from blazarclient import tests


class BaseClientTestCase(tests.TestCase):

    def setUp(self):
        super(BaseClientTestCase, self).setUp()

        self.client = client

        self.import_obj = self.patch(importutils, "import_object")

    def test_with_v1(self):
        self.client.Client()
        self.import_obj.assert_called_once_with(
            'blazarclient.v1.client.Client',
            service_type='reservation')

    def test_with_v1a0(self):
        self.client.Client(version='1a0')
        self.import_obj.assert_called_once_with(
            'blazarclient.v1.client.Client',
            service_type='reservation')

    def test_with_wrong_vers(self):
        self.assertRaises(exception.UnsupportedVersion,
                          self.client.Client,
                          version='0.0')
