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

import re
import six
import sys

import fixtures
#note(n.s.): you may need it later
#import mock
import testtools

#note(n.s.): you may need it later
#from blazarclient import client as blazar_client
#from blazarclient import exception
from blazarclient import shell
from blazarclient import tests

FAKE_ENV = {'OS_USERNAME': 'username',
            'OS_USER_DOMAIN_ID': 'user_domain_id',
            'OS_PASSWORD': 'password',
            'OS_TENANT_NAME': 'tenant_name',
            'OS_PROJECT_NAME': 'project_name',
            'OS_PROJECT_DOMAIN_ID': 'project_domain_id',
            'OS_AUTH_URL': 'http://no.where'}


class BlazarShellTestCase(tests.TestCase):

    def make_env(self, exclude=None, fake_env=FAKE_ENV):
        env = dict((k, v) for k, v in fake_env.items() if k != exclude)
        self.useFixture(fixtures.MonkeyPatch('os.environ', env))

    def setUp(self):
        super(BlazarShellTestCase, self).setUp()

        #Create shell for non-specific tests
        self.blazar_shell = shell.BlazarShell()

    def shell(self, argstr, exitcodes=(0,)):
        orig = sys.stdout
        orig_stderr = sys.stderr
        try:
            sys.stdout = six.StringIO()
            sys.stderr = six.StringIO()
            _shell = shell.BlazarShell()
            _shell.initialize_app(argstr.split())
        except SystemExit:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            self.assertIn(exc_value.code, exitcodes)
        finally:
            stdout = sys.stdout.getvalue()
            sys.stdout.close()
            sys.stdout = orig
            stderr = sys.stderr.getvalue()
            sys.stderr.close()
            sys.stderr = orig_stderr
        return (stdout, stderr)

    def test_help_unknown_command(self):
        self.assertRaises(ValueError, self.shell, 'bash-completion')

    @testtools.skip('lol')
    def test_bash_completion(self):
        stdout, stderr = self.shell('bash-completion')
        # just check we have some output
        required = [
            '.*--matching',
            '.*--wrap',
            '.*help',
            '.*secgroup-delete-rule',
            '.*--priority']
        for r in required:
            self.assertThat((stdout + stderr),
                            testtools.matchers.MatchesRegex(
                                r, re.DOTALL | re.MULTILINE))

    @testtools.skip('lol')
    def test_authenticate_user(self):
        obj = shell.BlazarShell()
        obj.initialize_app('list-leases')
        obj.options.os_token = 'aaaa-bbbb-cccc'
        obj.options.os_cacert = 'cert'

        obj.authenticate_user()
