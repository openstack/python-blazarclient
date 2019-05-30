# Copyright (c) 2019 StackHPC Ltd.
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
from blazarclient.v1.shell_commands import floatingips


class CreateFloatingIPTest(tests.TestCase):

    def setUp(self):
        super(CreateFloatingIPTest, self).setUp()
        self.create_floatingip = floatingips.CreateFloatingIP(
            shell.BlazarShell(), mock.Mock())

    def test_args2body(self):
        args = argparse.Namespace(
            network_id='1e17587e-a7ed-4b82-a17b-4beb32523e28',
            floating_ip_address='172.24.4.101',
        )

        expected = {
            'network_id': '1e17587e-a7ed-4b82-a17b-4beb32523e28',
            'floating_ip_address': '172.24.4.101',
        }

        ret = self.create_floatingip.args2body(args)
        self.assertDictEqual(ret, expected)


class ListFloatingIPsTest(tests.TestCase):

    def create_list_command(self, list_value):
        mock_floatingip_manager = mock.Mock()
        mock_floatingip_manager.list.return_value = list_value

        mock_client = mock.Mock()
        mock_client.floatingip = mock_floatingip_manager

        blazar_shell = shell.BlazarShell()
        blazar_shell.client = mock_client
        return (floatingips.ListFloatingIPs(blazar_shell, mock.Mock()),
                mock_floatingip_manager)

    def test_list_floatingips(self):
        list_value = [
            {'id': '84c4d37e-1f8b-45ce-897b-16ad7f49b0e9'},
            {'id': 'f180cf4c-f886-4dd1-8c36-854d17fbefb5'},
        ]

        list_floatingips, floatingip_manager = self.create_list_command(
            list_value)

        args = argparse.Namespace(sort_by='id', columns=['id'])
        expected = [['id'], [('84c4d37e-1f8b-45ce-897b-16ad7f49b0e9',),
                             ('f180cf4c-f886-4dd1-8c36-854d17fbefb5',)]]

        ret = list_floatingips.get_data(args)
        self.assertEqual(expected[0], ret[0])
        self.assertEqual(expected[1], [x for x in ret[1]])

        floatingip_manager.list.assert_called_once_with(sort_by='id')


class ShowFloatingIPTest(tests.TestCase):

    def create_show_command(self, list_value, get_value):
        mock_floatingip_manager = mock.Mock()
        mock_floatingip_manager.list.return_value = list_value
        mock_floatingip_manager.get.return_value = get_value

        mock_client = mock.Mock()
        mock_client.floatingip = mock_floatingip_manager

        blazar_shell = shell.BlazarShell()
        blazar_shell.client = mock_client
        return (floatingips.ShowFloatingIP(blazar_shell, mock.Mock()),
                mock_floatingip_manager)

    def test_show_floatingip(self):
        list_value = [
            {'id': '84c4d37e-1f8b-45ce-897b-16ad7f49b0e9'},
            {'id': 'f180cf4c-f886-4dd1-8c36-854d17fbefb5'},
        ]
        get_value = {
            'id': '84c4d37e-1f8b-45ce-897b-16ad7f49b0e9'}

        show_floatingip, floatingip_manager = self.create_show_command(
            list_value, get_value)

        args = argparse.Namespace(id='84c4d37e-1f8b-45ce-897b-16ad7f49b0e9')
        expected = [('id',), ('84c4d37e-1f8b-45ce-897b-16ad7f49b0e9',)]

        ret = show_floatingip.get_data(args)
        self.assertEqual(ret, expected)

        floatingip_manager.get.assert_called_once_with(
            '84c4d37e-1f8b-45ce-897b-16ad7f49b0e9')


class DeleteFloatingIPTest(tests.TestCase):

    def create_delete_command(self, list_value):
        mock_floatingip_manager = mock.Mock()
        mock_floatingip_manager.list.return_value = list_value

        mock_client = mock.Mock()
        mock_client.floatingip = mock_floatingip_manager

        blazar_shell = shell.BlazarShell()
        blazar_shell.client = mock_client
        return (floatingips.DeleteFloatingIP(blazar_shell, mock.Mock()),
                mock_floatingip_manager)

    def test_delete_floatingip(self):
        list_value = [
            {'id': '84c4d37e-1f8b-45ce-897b-16ad7f49b0e9'},
            {'id': 'f180cf4c-f886-4dd1-8c36-854d17fbefb5'},
        ]
        delete_floatingip, floatingip_manager = self.create_delete_command(
            list_value)

        args = argparse.Namespace(id='84c4d37e-1f8b-45ce-897b-16ad7f49b0e9')
        delete_floatingip.run(args)

        floatingip_manager.delete.assert_called_once_with(
            '84c4d37e-1f8b-45ce-897b-16ad7f49b0e9')
