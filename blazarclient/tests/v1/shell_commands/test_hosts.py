# Copyright (c) 2018 NTT
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
from unittest import mock

from blazarclient import shell
from blazarclient import tests
from blazarclient.v1.shell_commands import hosts


class CreateHostTest(tests.TestCase):

    def setUp(self):
        super(CreateHostTest, self).setUp()
        self.create_host = hosts.CreateHost(shell.BlazarShell(), mock.Mock())

    def test_args2body(self):
        args = argparse.Namespace(
            name='test-host',
            extra_capabilities=[
                'extra_key1=extra_value1',
                'extra_key2=extra_value2',
            ]
        )

        expected = {
            'name': 'test-host',
            'extra_key1': 'extra_value1',
            'extra_key2': 'extra_value2',
        }

        ret = self.create_host.args2body(args)
        self.assertDictEqual(ret, expected)


class UpdateHostTest(tests.TestCase):

    def create_update_command(self, list_value):
        mock_host_manager = mock.Mock()
        mock_host_manager.list.return_value = list_value

        mock_client = mock.Mock()
        mock_client.host = mock_host_manager

        blazar_shell = shell.BlazarShell()
        blazar_shell.client = mock_client
        return hosts.UpdateHost(blazar_shell, mock.Mock()), mock_host_manager

    def test_update_host(self):
        list_value = [
            {'id': '101', 'hypervisor_hostname': 'host-1'},
            {'id': '201', 'hypervisor_hostname': 'host-2'},
        ]
        update_host, host_manager = self.create_update_command(list_value)
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
        update_host.run(args)
        host_manager.update.assert_called_once_with('101', **expected)

    def test_update_host_with_name(self):
        list_value = [
            {'id': '101', 'hypervisor_hostname': 'host-1'},
            {'id': '201', 'hypervisor_hostname': 'host-2'},
        ]
        update_host, host_manager = self.create_update_command(list_value)
        args = argparse.Namespace(
            id='host-1',
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
        update_host.run(args)
        host_manager.update.assert_called_once_with('101', **expected)

    def test_update_host_with_name_startwith_number(self):
        list_value = [
            {'id': '101', 'hypervisor_hostname': '1-host'},
            {'id': '201', 'hypervisor_hostname': '2-host'},
        ]
        update_host, host_manager = self.create_update_command(list_value)
        args = argparse.Namespace(
            id='1-host',
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
        update_host.run(args)
        host_manager.update.assert_called_once_with('101', **expected)


class UnsetAttributeHostTest(tests.TestCase):

    def create_unset_command(self, list_value):
        mock_host_manager = mock.Mock()
        mock_host_manager.list.return_value = list_value

        mock_client = mock.Mock()
        mock_client.host = mock_host_manager

        blazar_shell = shell.BlazarShell()
        blazar_shell.client = mock_client
        return hosts.UnsetAttributeHost(blazar_shell, mock.Mock()), mock_host_manager

    def test_unset_host(self):
        list_value = [
            {'id': '101', 'hypervisor_hostname': 'host-1'},
            {'id': '201', 'hypervisor_hostname': 'host-2'},
        ]
        unset_host, host_manager = self.create_unset_command(list_value)
        extra_caps = ['key1', 'key2']
        args = argparse.Namespace(
            id='101',
            extra_capabilities=extra_caps
        )
        expected = {
            'values': {key: None for key in extra_caps}
        }
        unset_host.run(args)
        host_manager.update.assert_called_once_with('101', **expected)

class ShowHostTest(tests.TestCase):

    def create_show_command(self, list_value, get_value):
        mock_host_manager = mock.Mock()
        mock_host_manager.list.return_value = list_value
        mock_host_manager.get.return_value = get_value

        mock_client = mock.Mock()
        mock_client.host = mock_host_manager

        blazar_shell = shell.BlazarShell()
        blazar_shell.client = mock_client
        return hosts.ShowHost(blazar_shell, mock.Mock()), mock_host_manager

    def test_show_host(self):
        list_value = [
            {'id': '101', 'hypervisor_hostname': 'host-1'},
            {'id': '201', 'hypervisor_hostname': 'host-2'},
        ]
        get_value = {
            'id': '101', 'hypervisor_hostname': 'host-1'}

        show_host, host_manager = self.create_show_command(list_value,
                                                           get_value)

        args = argparse.Namespace(id='101')
        expected = [('hypervisor_hostname', 'id'), ('host-1', '101')]

        ret = show_host.get_data(args)
        self.assertEqual(ret, expected)

        host_manager.get.assert_called_once_with('101')

    def test_show_host_with_name(self):
        list_value = [
            {'id': '101', 'hypervisor_hostname': 'host-1'},
            {'id': '201', 'hypervisor_hostname': 'host-2'},
        ]
        get_value = {
            'id': '101', 'hypervisor_hostname': 'host-1'}

        show_host, host_manager = self.create_show_command(list_value,
                                                           get_value)

        args = argparse.Namespace(id='host-1')
        expected = [('hypervisor_hostname', 'id'), ('host-1', '101')]

        ret = show_host.get_data(args)
        self.assertEqual(ret, expected)

        host_manager.get.assert_called_once_with('101')

    def test_show_host_with_name_startwith_number(self):
        list_value = [
            {'id': '101', 'hypervisor_hostname': '1-host'},
            {'id': '201', 'hypervisor_hostname': '2-host'},
        ]
        get_value = {
            'id': '101', 'hypervisor_hostname': '1-host'}

        show_host, host_manager = self.create_show_command(list_value,
                                                           get_value)
        args = argparse.Namespace(id='1-host')
        expected = [('hypervisor_hostname', 'id'), ('1-host', '101')]

        ret = show_host.get_data(args)
        self.assertEqual(ret, expected)

        host_manager.get.assert_called_once_with('101')


class DeleteHostTest(tests.TestCase):

    def create_delete_command(self, list_value):
        mock_host_manager = mock.Mock()
        mock_host_manager.list.return_value = list_value

        mock_client = mock.Mock()
        mock_client.host = mock_host_manager

        blazar_shell = shell.BlazarShell()
        blazar_shell.client = mock_client
        return hosts.DeleteHost(blazar_shell, mock.Mock()), mock_host_manager

    def test_delete_host(self):
        list_value = [
            {'id': '101', 'hypervisor_hostname': 'host-1'},
            {'id': '201', 'hypervisor_hostname': 'host-2'},
        ]
        delete_host, host_manager = self.create_delete_command(list_value)

        args = argparse.Namespace(id='101')
        delete_host.run(args)

        host_manager.delete.assert_called_once_with('101')

    def test_delete_host_with_name(self):
        list_value = [
            {'id': '101', 'hypervisor_hostname': 'host-1'},
            {'id': '201', 'hypervisor_hostname': 'host-2'},
        ]
        delete_host, host_manager = self.create_delete_command(list_value)

        args = argparse.Namespace(id='host-1')
        delete_host.run(args)

        host_manager.delete.assert_called_once_with('101')

    def test_delete_host_with_name_startwith_number(self):
        list_value = [
            {'id': '101', 'hypervisor_hostname': '1-host'},
            {'id': '201', 'hypervisor_hostname': '2-host'},
        ]
        delete_host, host_manager = self.create_delete_command(list_value)

        args = argparse.Namespace(id='1-host')
        delete_host.run(args)

        host_manager.delete.assert_called_once_with('101')
