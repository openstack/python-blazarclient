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

from unittest import mock

import testtools

from blazarclient import command
from blazarclient import tests


class OpenstackCommandTestCase(tests.TestCase):

    def setUp(self):
        super(OpenstackCommandTestCase, self).setUp()

    @testtools.skip("Have no idea how to test super")
    def test_run(self):
        pass

    @testtools.skip("Unskip it when get_data will do smthg")
    def test_get_data(self):
        pass

    @testtools.skip("Unskip it when get_data will do smthg")
    def test_take_action(self):
        pass


class TableFormatterTestCase(tests.TestCase):

    def setUp(self):
        super(TableFormatterTestCase, self).setUp()

    @testtools.skip("Have no idea how to test super")
    def test_emit_list(self):
        pass


class BlazarCommandTestCase(tests.TestCase):

    def setUp(self):
        super(BlazarCommandTestCase, self).setUp()

        self.app = mock.MagicMock()
        self.parser = self.patch(command.OpenStackCommand, 'get_parser')

        self.command = command.BlazarCommand(self.app, [])

    def test_get_client(self):
        # Test that either client_manager.reservation or client is used,
        # whichever exists

        client_manager = self.app.client_manager
        del self.app.client_manager
        client = self.command.get_client()
        self.assertEqual(self.app.client, client)

        self.app.client_manager = client_manager
        del self.app.client
        client = self.command.get_client()
        self.assertEqual(self.app.client_manager.reservation, client)

    def test_get_parser(self):
        self.command.get_parser('TestCase')
        self.parser.assert_called_once_with('TestCase')

    def test_format_output_data(self):
        data_before = {'key_string': 'string_value',
                       'key_dict': {'key': 'value'},
                       'key_list': ['1', '2', '3'],
                       'key_none': None}
        data_after = {'key_string': 'string_value',
                      'key_dict': '{"key": "value"}',
                      'key_list': '1\n2\n3',
                      'key_none': ''}

        self.command.format_output_data(data_before)

        self.assertEqual(data_after, data_before)


class CreateCommandTestCase(tests.TestCase):
    def setUp(self):
        super(CreateCommandTestCase, self).setUp()

        self.app = mock.MagicMock()
        self.create_command = command.CreateCommand(self.app, [])

        self.client = self.patch(self.create_command, 'get_client')

    @testtools.skip("Under construction")
    def test_get_data_data(self):
        data = {'key_string': 'string_value',
                'key_dict': "{'key0': 'value', 'key1': 'value'}",
                'key_list': "['1', '2', '3',]",
                'key_none': None}
        self.client.resource.return_value = mock.MagicMock(return_value=data)
        self.assertEqual(self.create_command.get_data({'a': 'b'}), None)


@testtools.skip("Under construction")
class UpdateCommandTestCase(tests.TestCase):
    def setUp(self):
        super(UpdateCommandTestCase, self).setUp()

        self.app = mock.MagicMock()
        self.update_command = command.UpdateCommand(self.app, [])


@testtools.skip("Under construction")
class DeleteCommandTestCase(tests.TestCase):
    def setUp(self):
        super(DeleteCommandTestCase, self).setUp()

        self.app = mock.MagicMock()
        self.delete_command = command.DeleteCommand(self.app, [])


@testtools.skip("Under construction")
class ListCommandTestCase(tests.TestCase):
    def setUp(self):
        super(ListCommandTestCase, self).setUp()

        self.app = mock.MagicMock()
        self.list_command = command.ListCommand(self.app, [])


@testtools.skip("Under construction")
class ShowCommandTestCase(tests.TestCase):
    def setUp(self):
        super(ShowCommandTestCase, self).setUp()

        self.app = mock.MagicMock()
        self.show_command = command.ShowCommand(self.app, [])
