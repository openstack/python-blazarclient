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

import json

from keystoneauth1 import adapter
import requests

from blazarclient import exception
from blazarclient.i18n import _


class RequestManager(object):
    """Manager to create request from given Blazar URL and auth token."""

    def __init__(self, blazar_url, auth_token, user_agent):
        self.blazar_url = blazar_url
        self.auth_token = auth_token
        self.user_agent = user_agent

    def get(self, url):
        """Sends get request to Blazar.

        :param url: URL to the wanted Blazar resource.
        :type url: str
        """
        return self.request(url, 'GET')

    def post(self, url, body):
        """Sends post request to Blazar.

        :param url: URL to the wanted Blazar resource.
        :type url: str

        :param body: Values resource to be created from.
        :type body: dict
        """
        return self.request(url, 'POST', body=body)

    def delete(self, url):
        """Sends delete request to Blazar.

        :param url: URL to the wanted Blazar resource.
        :type url: str
        """
        return self.request(url, 'DELETE')

    def put(self, url, body):
        """Sends update request to Blazar.

        :param url: URL to the wanted Blazar resource.
        :type url: str

        :param body: Values resource to be updated from.
        :type body: dict
        """
        return self.request(url, 'PUT', body=body)

    def request(self, url, method, **kwargs):
        """Base request method.

        Adds specific headers and URL prefix to the request.

        :param url: Resource URL.
        :type url: str

        :param method: Method to be called (GET, POST, PUT, DELETE).
        :type method: str

        :returns: Response and body.
        :rtype: tuple
        """
        kwargs.setdefault('headers', kwargs.get('headers', {}))
        kwargs['headers']['User-Agent'] = self.user_agent
        kwargs['headers']['Accept'] = 'application/json'
        kwargs['headers']['x-auth-token'] = self.auth_token

        if 'body' in kwargs:
            kwargs['headers']['Content-Type'] = 'application/json'
            kwargs['data'] = json.dumps(kwargs['body'])
            del kwargs['body']

        resp = requests.request(method, self.blazar_url + url, **kwargs)

        try:
            body = json.loads(resp.text)
        except ValueError:
            body = None

        if resp.status_code >= 400:
            if body is not None:
                error_message = body.get('error_message', body)
            else:
                error_message = resp.text

            body = _("ERROR: {0}").format(error_message)
            raise exception.BlazarClientException(body, code=resp.status_code)

        return resp, body


class BaseClientManager(object):
    """Base class for managing resources of Blazar."""

    user_agent = 'python-blazarclient'

    def __init__(self, blazar_url, auth_token, session, **kwargs):
        self.blazar_url = blazar_url
        self.auth_token = auth_token
        self.session = session

        if self.session:
            self.request_manager = adapter.LegacyJsonAdapter(
                session=self.session,
                user_agent=self.user_agent,
                **kwargs
            )
        elif self.blazar_url and self.auth_token:
            self.request_manager = RequestManager(blazar_url=self.blazar_url,
                                                  auth_token=self.auth_token,
                                                  user_agent=self.user_agent)
        else:
            raise exception.InsufficientAuthInfomation
