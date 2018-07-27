# Copyright (c) 2017 NTT Corp.
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

from blazarclient import exception
from blazarclient import shell
from blazarclient import tests
from blazarclient.v1.shell_commands import leases


class CreateLeaseTestCase(tests.TestCase):

    def setUp(self):
        super(CreateLeaseTestCase, self).setUp()
        self.cl = leases.CreateLease(shell.BlazarShell(), mock.Mock())

    def test_args2body_correct_phys_res_params(self):
        args = argparse.Namespace(
            start='2020-07-24 20:00',
            end='2020-08-09 22:30',
            before_end='2020-08-09 21:30',
            events=[],
            name='lease-test',
            reservations=[],
            physical_reservations=[
                'min=1,'
                'max=2,'
                'hypervisor_properties='
                '["and", [">=", "$vcpus", "2"], '
                '[">=", "$memory_mb", "2048"]],'
                'resource_properties='
                '["==", "$extra_key", "extra_value"],'
                'before_end=default'
            ]
        )
        expected = {
            'start': '2020-07-24 20:00',
            'end': '2020-08-09 22:30',
            'before_end': '2020-08-09 21:30',
            'events': [],
            'name': 'lease-test',
            'reservations': [
                {
                    'min': 1,
                    'max': 2,
                    'hypervisor_properties':
                        '["and", [">=", "$vcpus", "2"], '
                        '[">=", "$memory_mb", "2048"]]',
                    'resource_properties':
                        '["==", "$extra_key", "extra_value"]',
                    'resource_type': 'physical:host',
                    'before_end': 'default'
                }
            ]
        }
        self.assertDictEqual(self.cl.args2body(args), expected)

    def test_args2body_incorrect_phys_res_params(self):
        args = argparse.Namespace(
            start='2020-07-24 20:00',
            end='2020-08-09 22:30',
            before_end='2020-08-09 21:30',
            events=[],
            name='lease-test',
            reservations=[],
            physical_reservations=[
                'incorrect_param=1,'
                'min=1,'
                'max=2,'
                'hypervisor_properties='
                '["and", [">=", "$vcpus", "2"], '
                '[">=", "$memory_mb", "2048"]],'
                'resource_properties='
                '["==", "$extra_key", "extra_value"]'
            ]
        )
        self.assertRaises(exception.IncorrectLease,
                          self.cl.args2body,
                          args)

    def test_args2body_duplicated_phys_res_params(self):
        args = argparse.Namespace(
            start='2020-07-24 20:00',
            end='2020-08-09 22:30',
            before_end='2020-08-09 21:30',
            events=[],
            name='lease-test',
            reservations=[],
            physical_reservations=[
                'min=1,'
                'min=1,'
                'max=2,'
                'hypervisor_properties='
                '["and", [">=", "$vcpus", "2"], '
                '[">=", "$memory_mb", "2048"]],'
                'resource_properties='
                '["==", "$extra_key", "extra_value"]'
            ]
        )
        self.assertRaises(exception.DuplicatedLeaseParameters,
                          self.cl.args2body,
                          args)

    def test_args2body_correct_instance_res_params(self):
        args = argparse.Namespace(
            start='2020-07-24 20:00',
            end='2020-08-09 22:30',
            before_end='2020-08-09 21:30',
            events=[],
            name='lease-test',
            reservations=[
                'vcpus=4,'
                'memory_mb=1024,'
                'disk_gb=10,'
                'amount=2,'
                'affinity=True,'
                'resource_properties='
                '["==", "$extra_key", "extra_value"],'
                'resource_type=virtual:instance'
            ],
            physical_reservations=[
                'min=1,'
                'max=2,'
                'hypervisor_properties='
                '["and", [">=", "$vcpus", "2"], '
                '[">=", "$memory_mb", "2048"]],'
                'resource_properties='
                '["==", "$extra_key", "extra_value"],'
                'before_end=default'
            ]
        )
        expected = {
            'start': '2020-07-24 20:00',
            'end': '2020-08-09 22:30',
            'before_end': '2020-08-09 21:30',
            'events': [],
            'name': 'lease-test',
            'reservations': [
                {
                    'min': 1,
                    'max': 2,
                    'hypervisor_properties':
                        '["and", [">=", "$vcpus", "2"], '
                        '[">=", "$memory_mb", "2048"]]',
                    'resource_properties':
                        '["==", "$extra_key", "extra_value"]',
                    'resource_type': 'physical:host',
                    'before_end': 'default'
                },
                {
                    'vcpus': 4,
                    'memory_mb': 1024,
                    'disk_gb': 10,
                    'amount': 2,
                    'affinity': 'True',
                    'resource_properties':
                        '["==", "$extra_key", "extra_value"]',
                    'resource_type': 'virtual:instance'
                }
            ]
        }
        self.assertDictEqual(self.cl.args2body(args), expected)

    def test_args2body_start_now(self):
        args = argparse.Namespace(
            start='now',
            end='2020-08-09 22:30',
            before_end='2020-08-09 21:30',
            events=[],
            name='lease-test',
            reservations=[],
            physical_reservations=[
                'min=1,'
                'max=2,'
                'hypervisor_properties='
                '["and", [">=", "$vcpus", "2"], '
                '[">=", "$memory_mb", "2048"]],'
                'resource_properties='
                '["==", "$extra_key", "extra_value"],'
                'before_end=default'
            ]
        )
        expected = {
            'start': 'now',
            'end': '2020-08-09 22:30',
            'before_end': '2020-08-09 21:30',
            'events': [],
            'name': 'lease-test',
            'reservations': [
                {
                    'min': 1,
                    'max': 2,
                    'hypervisor_properties':
                        '["and", [">=", "$vcpus", "2"], '
                        '[">=", "$memory_mb", "2048"]]',
                    'resource_properties':
                        '["==", "$extra_key", "extra_value"]',
                    'resource_type': 'physical:host',
                    'before_end': 'default'
                }
            ]
        }
        self.assertDictEqual(self.cl.args2body(args), expected)


class UpdateLeaseTestCase(tests.TestCase):

    def setUp(self):
        super(UpdateLeaseTestCase, self).setUp()
        self.cl = leases.UpdateLease(shell.BlazarShell(), mock.Mock())

    def test_args2body_time_params(self):
        args = argparse.Namespace(
            name=None,
            prolong_for='1h',
            reduce_by=None,
            end_date=None,
            defer_by=None,
            advance_by=None,
            start_date=None,
            reservation=None
        )
        expected = {
            'prolong_for': '1h',
        }

        self.assertDictEqual(self.cl.args2body(args), expected)

    def test_args2body_host_reservation_params(self):
        args = argparse.Namespace(
            name=None,
            prolong_for=None,
            reduce_by=None,
            end_date=None,
            defer_by=None,
            advance_by=None,
            start_date=None,
            reservation=[
                'id=798379a6-194c-45dc-ba34-1b5171d5552f,'
                'max=3,'
                'hypervisor_properties='
                '["and", [">=", "$vcpus", "4"], '
                '[">=", "$memory_mb", "8192"]],'
                'resource_properties='
                '["==", "$extra_key", "extra_value"]'
            ]
        )
        expected = {
            'reservations': [
                {
                    'id': '798379a6-194c-45dc-ba34-1b5171d5552f',
                    'max': 3,
                    'hypervisor_properties':
                        '["and", [">=", "$vcpus", "4"], '
                        '[">=", "$memory_mb", "8192"]]',
                    'resource_properties':
                        '["==", "$extra_key", "extra_value"]'
                }
            ]
        }

        self.assertDictEqual(self.cl.args2body(args), expected)

    def test_args2body_instance_reservation_params(self):
        args = argparse.Namespace(
            name=None,
            prolong_for=None,
            reduce_by=None,
            end_date=None,
            defer_by=None,
            advance_by=None,
            start_date=None,
            reservation=[
                'id=798379a6-194c-45dc-ba34-1b5171d5552f,'
                'vcpus=3,memory_mb=1024,disk_gb=20,'
                'amount=4,affinity=False'
            ]
        )
        expected = {
            'reservations': [
                {
                    'id': '798379a6-194c-45dc-ba34-1b5171d5552f',
                    'vcpus': 3,
                    'memory_mb': 1024,
                    'disk_gb': 20,
                    'amount': 4,
                    'affinity': 'False'
                }
            ]
        }

        self.assertDictEqual(self.cl.args2body(args), expected)
