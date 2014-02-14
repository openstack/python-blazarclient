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


import requests

from climateclient import base
from climateclient import exception
from climateclient import tests


class BaseClientManagerTestCase(tests.TestCase):

    def setUp(self):
        super(BaseClientManagerTestCase, self).setUp()

        self.url = "www.fake.com/reservation"
        self.token = "aaa-bbb-ccc"
        self.fake_key = "fake_key"
        self.response = "RESPONSE"
        self.exception = exception

        self.manager = base.BaseClientManager(self.url, self.token)
        self.request = self.patch(requests, "request")

    def test_get(self):
        self.patch(
            self.manager, "request").return_value = (
                self.response, {"fake_key": "FAKE"})
        self.assertEqual(self.manager._get(self.url, self.fake_key), "FAKE")

    def test_create(self):
        self.patch(
            self.manager, "request").return_value = (
                self.response, {"fake_key": "FAKE"})
        self.assertEqual(self.manager._create(self.url, {}, self.fake_key),
                         "FAKE")

    def test_delete(self):
        request = self.patch(self.manager, "request")
        request.return_value = (self.response, {"fake_key": "FAKE"})
        self.manager._delete(self.url)
        request.assert_called_once_with(self.url, "DELETE")

    def test_update(self):
        self.patch(
            self.manager, "request").return_value = (
                self.response, {"fake_key": "FAKE"})
        self.assertEqual(self.manager._update(self.url, {}, self.fake_key),
                         "FAKE")

    def test_request_ok_with_body(self):
        self.request.return_value.status_code = 200
        self.request.return_value.text = '{"key": "value"}'

        kwargs = {"body": {"key": "value"}}

        self.assertEqual((
            self.request(), {"key": "value"}),
            self.manager.request(self.url, "POST", **kwargs))

    def test_request_ok_without_body(self):
        self.request.return_value.status_code = 200
        self.request.return_value.text = "key"

        kwargs = {"body": "key"}

        self.assertEqual((
            self.request(), None),
            self.manager.request(self.url, "POST", **kwargs))

    def test_request_fail_with_body(self):
        self.request.return_value.status_code = 400
        self.request.return_value.text = '{"key": "value"}'

        kwargs = {"body": {"key": "value"}}

        self.assertRaises(exception.ClimateClientException,
                          self.manager.request,
                          self.url, "POST", **kwargs)

    def test_request_fail_without_body(self):
        self.request.return_value.status_code = 400
        self.request.return_value.text = "REAL_ERROR"

        kwargs = {"body": "key"}

        self.assertRaises(exception.ClimateClientException,
                          self.manager.request,
                          self.url, "POST", **kwargs)
