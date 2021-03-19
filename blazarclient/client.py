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

from oslo_utils import importutils

from blazarclient import exception
from blazarclient.i18n import _


def Client(version=1, service_type='reservation', *args, **kwargs):
    version_map = {
        '1': 'blazarclient.v1.client.Client',
        '1a0': 'blazarclient.v1.client.Client',
    }
    try:
        client_path = version_map[str(version)]
    except (KeyError, ValueError):
        msg = _("Invalid client version '%(version)s'. "
                "Must be one of: %(available_version)s") % ({
                    'version': version,
                    'available_version': ', '.join(version_map.keys())
                })
        raise exception.UnsupportedVersion(msg)

    return importutils.import_object(client_path, *args, **kwargs)
