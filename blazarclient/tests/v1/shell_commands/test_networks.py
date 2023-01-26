# Copyright (c) 2018 StackHPC
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

import argparse
import mock

from blazarclient import shell
from blazarclient import tests
from blazarclient.v1.shell_commands import networks


class CreateNetworkTest(tests.TestCase):

    def setUp(self):
        super(CreateNetworkTest, self).setUp()
        self.create_network = networks.CreateNetwork(shell.BlazarShell(), mock.Mock())

    def test_args2body(self):
        args = argparse.Namespace(
            network_type='vlan',
            physical_network='physnet1',
            segment_id='1234',
            extra_capabilities=[
                'extra_key1=extra_value1',
                'extra_key2=extra_value2',
            ]
        )

        expected = {
            'network_type': 'vlan',
            'physical_network': 'physnet1',
            'segment_id': '1234',
            'extra_key1': 'extra_value1',
            'extra_key2': 'extra_value2',
        }

        ret = self.create_network.args2body(args)
        self.assertDictEqual(ret, expected)


class UpdateNetworkTest(tests.TestCase):

    def create_update_command(self, list_value):
        mock_network_manager = mock.Mock()
        mock_network_manager.list.return_value = list_value

        mock_client = mock.Mock()
        mock_client.network = mock_network_manager

        blazar_shell = shell.BlazarShell()
        blazar_shell.client = mock_client
        return networks.UpdateNetwork(blazar_shell, mock.Mock()), mock_network_manager

    def test_update_network(self):
        list_value = [
            {'id': '101', 'networkname': 'network-1'},
            {'id': '201', 'networkname': 'network-2'},
        ]
        update_network, network_manager = self.create_update_command(list_value)
        args = argparse.Namespace(
            id='101',
            extra_capabilities=[
                'key1=value1',
                'key2=value2'
            ])
        expected = {
            'values': {
                'key1': 'value1',
                'key2': 'value2'
            }
        }
        update_network.run(args)
        network_manager.update.assert_called_once_with('101', **expected)


class ShowNetworkTest(tests.TestCase):

    def create_show_command(self, list_value, get_value):
        mock_network_manager = mock.Mock()
        mock_network_manager.list.return_value = list_value
        mock_network_manager.get.return_value = get_value

        mock_client = mock.Mock()
        mock_client.network = mock_network_manager

        blazar_shell = shell.BlazarShell()
        blazar_shell.client = mock_client
        return networks.ShowNetwork(blazar_shell, mock.Mock()), mock_network_manager

    def test_show_network(self):
        list_value = [
            {'id': '101'},
            {'id': '201'},
        ]
        get_value = {
            'id': '101'}

        show_network, network_manager = self.create_show_command(list_value,
                                                           get_value)

        args = argparse.Namespace(id='101')
        expected = [('id',), ('101',)]

        ret = show_network.get_data(args)
        self.assertEqual(ret, expected)

        network_manager.get.assert_called_once_with('101')


class DeleteNetworkTest(tests.TestCase):

    def create_delete_command(self, list_value):
        mock_network_manager = mock.Mock()
        mock_network_manager.list.return_value = list_value

        mock_client = mock.Mock()
        mock_client.network = mock_network_manager

        blazar_shell = shell.BlazarShell()
        blazar_shell.client = mock_client
        return networks.DeleteNetwork(blazar_shell, mock.Mock()), mock_network_manager

    def test_delete_network(self):
        list_value = [
            {'id': '101', 'networkname': 'network-1'},
            {'id': '201', 'networkname': 'network-2'},
        ]
        delete_network, network_manager = self.create_delete_command(list_value)

        args = argparse.Namespace(id='101')
        delete_network.run(args)

        network_manager.delete.assert_called_once_with('101')
