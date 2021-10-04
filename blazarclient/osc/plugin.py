# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

from osc_lib import utils


LOG = logging.getLogger(__name__)

DEFAULT_API_VERSION = '1'

# Required by the OSC plugin interface
API_NAME = 'reservation'
API_VERSION_OPTION = 'os_reservations_api_version'
API_VERSIONS = {
    '1': 'blazarclient.v1.client.Client',
}


# Required by the OSC plugin interface
def make_client(instance):
    reservation_client = utils.get_client_class(
        API_NAME,
        instance._api_version[API_NAME],
        API_VERSIONS)

    LOG.debug("Instantiating reservation client: %s", reservation_client)

    client = reservation_client(
        instance._api_version[API_NAME],
        session=instance.session,
        endpoint_override=instance.get_endpoint_for_service_type(
            API_NAME,
            interface=instance.interface,
            region_name=instance._region_name)
    )
    return client


# Required by the OSC plugin interface
def build_option_parser(parser):
    """Hook to add global options.
    Called from openstackclient.shell.OpenStackShell.__init__()
    after the builtin parser has been initialized.  This is
    where a plugin can add global options such as an API version setting.
    :param argparse.ArgumentParser parser: The parser object that has been
        initialized by OpenStackShell.
    """
    parser.add_argument(
        "--os-reservation-api-version",
        metavar="<reservation-api-version>",
        help="Reservation API version, default="
             "{} (Env: OS_RESERVATION_API_VERSION)".format(
                 DEFAULT_API_VERSION)
    )
    return parser
