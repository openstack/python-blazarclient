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


import mock

from blazarclient import base
from blazarclient import exception
from blazarclient import tests


class RequestManagerTestCase(tests.TestCase):

    def setUp(self):
        super(RequestManagerTestCase, self).setUp()

        self.blazar_url = "www.fake.com/reservation"
        self.auth_token = "aaa-bbb-ccc"
        self.user_agent = "python-blazarclient"
        self.manager = base.RequestManager(blazar_url=self.blazar_url,
                                           auth_token=self.auth_token,
                                           user_agent=self.user_agent)

    @mock.patch('blazarclient.base.RequestManager.request',
                return_value=(200, {"fake": "FAKE"}))
    def test_get(self, m):
        url = '/leases'
        resp, body = self.manager.get(url)
        self.assertEqual(resp, 200)
        self.assertDictEqual(body, {"fake": "FAKE"})
        m.assert_called_once_with(url, "GET")

    @mock.patch('blazarclient.base.RequestManager.request',
                return_value=(200, {"fake": "FAKE"}))
    def test_post(self, m):
        url = '/leases'
        req_body = {
            'start': '2020-07-24 20:00',
            'end': '2020-08-09 22:30',
            'before_end': '2020-08-09 21:30',
            'events': [],
            'name': 'lease-test',
            'reservations': [
                {
                    'min': '1',
                    'max': '2',
                    'hypervisor_properties':
                        '[">=", "$vcpus", "2"]',
                    'resource_properties':
                        '["==", "$extra_key", "extra_value"]',
                    'resource_type': 'physical:host',
                    'before_end': 'default'
                }
            ]
        }
        resp, body = self.manager.post(url, req_body)
        self.assertEqual(resp, 200)
        self.assertDictEqual(body, {"fake": "FAKE"})
        m.assert_called_once_with(url, "POST", body=req_body)

    @mock.patch('blazarclient.base.RequestManager.request',
                return_value=(200, {"fake": "FAKE"}))
    def test_delete(self, m):
        url = '/leases/aaa-bbb-ccc'
        resp, body = self.manager.delete(url)
        self.assertEqual(resp, 200)
        self.assertDictEqual(body, {"fake": "FAKE"})
        m.assert_called_once_with(url, "DELETE")

    @mock.patch('blazarclient.base.RequestManager.request',
                return_value=(200, {"fake": "FAKE"}))
    def test_put(self, m):
        url = '/leases/aaa-bbb-ccc'
        req_body = {
            'name': 'lease-test',
        }
        resp, body = self.manager.put(url, req_body)
        self.assertEqual(resp, 200)
        self.assertDictEqual(body, {"fake": "FAKE"})
        m.assert_called_once_with(url, "PUT", body=req_body)

    @mock.patch('requests.request')
    def test_request_ok_with_body(self, m):
        m.return_value.status_code = 200
        m.return_value.text = '{"resp_key": "resp_value"}'
        url = '/leases'
        kwargs = {"body": {"req_key": "req_value"}}
        self.assertEqual(self.manager.request(url, "POST", **kwargs),
                         (m(), {"resp_key": "resp_value"}))

    @mock.patch('requests.request')
    def test_request_ok_without_body(self, m):
        m.return_value.status_code = 200
        m.return_value.text = "resp"
        url = '/leases'
        kwargs = {"body": {"req_key": "req_value"}}
        self.assertEqual(self.manager.request(url, "POST", **kwargs),
                         (m(), None))

    @mock.patch('requests.request')
    def test_request_fail_with_body(self, m):
        m.return_value.status_code = 400
        m.return_value.text = '{"resp_key": "resp_value"}'
        url = '/leases'
        kwargs = {"body": {"req_key": "req_value"}}
        self.assertRaises(exception.BlazarClientException,
                          self.manager.request, url, "POST", **kwargs)

    @mock.patch('requests.request')
    def test_request_fail_without_body(self, m):
        m.return_value.status_code = 400
        m.return_value.text = "resp"
        url = '/leases'
        kwargs = {"body": {"req_key": "req_value"}}
        self.assertRaises(exception.BlazarClientException,
                          self.manager.request, url, "POST", **kwargs)


class SessionClientTestCase(tests.TestCase):

    def setUp(self):
        super(SessionClientTestCase, self).setUp()
        self.manager = base.SessionClient(user_agent="python-blazarclient",
                                          session=mock.MagicMock())

    @mock.patch('blazarclient.base.adapter.LegacyJsonAdapter.request')
    def test_request_ok(self, m):
        mock_resp = mock.Mock()
        mock_resp.status_code = 200
        mock_body = {"resp_key": "resp_value"}
        m.return_value = (mock_resp, mock_body)
        url = '/leases'
        kwargs = {"body": {"req_key": "req_value"}}
        resp, body = self.manager.request(url, "POST", **kwargs)
        self.assertEqual((resp, body), (mock_resp, mock_body))

    @mock.patch('blazarclient.base.adapter.LegacyJsonAdapter.request')
    def test_request_fail(self, m):
        resp = mock.Mock()
        resp.status_code = 400
        body = {"error message": "error"}
        m.return_value = (resp, body)
        url = '/leases'
        kwargs = {"body": {"req_key": "req_value"}}
        self.assertRaises(exception.BlazarClientException,
                          self.manager.request, url, "POST", **kwargs)


class BaseClientManagerTestCase(tests.TestCase):

    def setUp(self):
        super(BaseClientManagerTestCase, self).setUp()

        self.blazar_url = "www.fake.com/reservation"
        self.auth_token = "aaa-bbb-ccc"
        self.session = mock.MagicMock()
        self.user_agent = "python-blazarclient"

    def test_init_with_session(self):
        manager = base.BaseClientManager(blazar_url=None,
                                         auth_token=None,
                                         session=self.session)
        self.assertIsInstance(manager.request_manager,
                              base.SessionClient)

    def test_init_with_url_and_token(self):
        manager = base.BaseClientManager(blazar_url=self.blazar_url,
                                         auth_token=self.auth_token,
                                         session=None)
        self.assertIsInstance(manager.request_manager,
                              base.RequestManager)

    def test_init_with_insufficient_info(self):
        self.assertRaises(exception.InsufficientAuthInformation,
                          base.BaseClientManager,
                          blazar_url=None,
                          auth_token=self.auth_token,
                          session=None)
