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


from blazarclient.i18n import _


class BlazarClientException(Exception):
    """Base exception class."""
    message = _("An unknown exception occurred %s.")
    code = 500

    def __init__(self, message=None, **kwargs):
        self.kwargs = kwargs

        if 'code' not in self.kwargs:
            try:
                self.kwargs['code'] = self.code
            except AttributeError:
                pass

        if not message:
            message = self.message % kwargs

        super(BlazarClientException, self).__init__(message)


class CommandError(BlazarClientException):
    """Occurs if not all authentication vital options are set."""
    message = _("You have to provide all options like user name or tenant "
                "id to make authentication possible.")
    code = 401


class NotAuthorized(BlazarClientException):
    """HTTP 401 - Not authorized.

    User have no enough rights to perform action.
    """
    code = 401
    message = _("Not authorized request.")


class NoBlazarEndpoint(BlazarClientException):
    """Occurs if no endpoint for Blazar set in the Keystone."""
    message = _("No publicURL endpoint for Blazar found. Set endpoint "
                "for Blazar in the Keystone.")
    code = 404


class NoUniqueMatch(BlazarClientException):
    """Occurs if there are more than one appropriate resources."""
    message = _("There is no unique requested resource.")
    code = 409


class UnsupportedVersion(BlazarClientException):
    """Occurs if unsupported client version was requested."""
    message = _("Unsupported client version requested.")
    code = 406


class IncorrectLease(BlazarClientException):
    """Occurs if lease parameters are incorrect."""
    message = _("The lease parameters are incorrect.")
    code = 409


class DuplicatedLeaseParameters(BlazarClientException):
    """Occurs if lease parameters are duplicated."""
    message = _("The lease parameters are duplicated.")
    code = 400


class InsufficientAuthInformation(BlazarClientException):
    """Occurs if the auth info passed to blazar client is insufficient."""
    message = _("The passed arguments are insufficient "
                "for the authentication. The instance of "
                "keystoneauth1.session.Session class is required.")
    code = 400


class ResourcePropertyNotFound(BlazarClientException):
    """Occurs if the resource property specified does not exist"""
    message = _("The resource property does not exist.")
    code = 404
