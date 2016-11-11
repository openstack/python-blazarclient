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

import requests

from climateclient import exception
from climateclient.i18n import _


class BaseClientManager(object):
    """Base manager to  interact with a particular type of API.

    There are environments, nodes and jobs types of API requests.
    Manager provides CRUD operations for them.
    """
    def __init__(self, climate_url, auth_token):
        self.climate_url = climate_url
        self.auth_token = auth_token

    USER_AGENT = 'python-climateclient'

    def _get(self, url, response_key):
        """Sends get request to Climate.

        :param url: URL to the wanted Climate resource.
        :type url: str

        :param response_key: Type of resource (environment, node, job).
        :type response_key: str

        :returns: Resource entity (entities) that was (were) asked.
        :rtype: dict | list
        """
        resp, body = self.request(url, 'GET')
        return body[response_key]

    def _create(self, url, body, response_key):
        """Sends create request to Climate.

        :param url: URL to the wanted Climate resource.
        :type url: str

        :param body: Values resource to be created from.
        :type body: dict

        :param response_key: Type of resource (environment, node, job).
        :type response_key: str

        :returns: Resource entity that was created.
        :rtype: dict
        """
        resp, body = self.request(url, 'POST', body=body)
        return body[response_key]

    def _delete(self, url):
        """Sends delete request to Climate.

        :param url: URL to the wanted Climate resource.
        :type url: str
        """
        resp, body = self.request(url, 'DELETE')

    def _update(self, url, body, response_key=None):
        """Sends update request to Climate.

        :param url: URL to the wanted Climate resource.
        :type url: str

        :param body: Values resource to be updated from.
        :type body: dict

        :param response_key: Type of resource (environment, node, job).
        :type response_key: str

        :returns: Resource entity that was updated.
        :rtype: dict
        """
        resp, body = self.request(url, 'PUT', body=body)
        return body[response_key]

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
        kwargs['headers']['User-Agent'] = self.USER_AGENT
        kwargs['headers']['Accept'] = 'application/json'
        kwargs['headers']['x-auth-token'] = self.auth_token

        if 'body' in kwargs:
            kwargs['headers']['Content-Type'] = 'application/json'
            kwargs['data'] = json.dumps(kwargs['body'])
            del kwargs['body']

        resp = requests.request(method, self.climate_url + url, **kwargs)

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
            raise exception.ClimateClientException(body, code=resp.status_code)

        return resp, body
