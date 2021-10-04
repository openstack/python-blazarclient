#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from unittest import mock

from blazarclient.osc import plugin
from blazarclient import tests


class ReservationPluginTests(tests.TestCase):

    @mock.patch("blazarclient.v1.client.Client")
    def test_make_client(self, mock_client):
        instance = mock.Mock()
        instance._api_version = {"reservation": "1"}
        endpoint = "blazar_endpoint"
        instance.get_endpoint_for_service_type = mock.Mock(
            return_value=endpoint
        )

        plugin.make_client(instance)

        mock_client.assert_called_with(
            "1",
            session=instance.session,
            endpoint_override=endpoint
        )
