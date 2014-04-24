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

from __future__ import print_function
import ast
import logging
import six

from cliff import command
from cliff.formatters import table
from cliff import lister
from cliff import show

from climateclient import exception
from climateclient import utils


class OpenStackCommand(command.Command):
    """Base class for OpenStack commands."""

    api = None

    def run(self, parsed_args):
        if not self.api:
            return
        else:
            return super(OpenStackCommand, self).run(parsed_args)

    def get_data(self, parsed_args):
        pass

    def take_action(self, parsed_args):
        return self.get_data(parsed_args)


class TableFormatter(table.TableFormatter):
    """This class is used to keep consistency with prettytable 0.6."""

    def emit_list(self, column_names, data, stdout, parsed_args):
        if column_names:
            super(TableFormatter, self).emit_list(column_names, data, stdout,
                                                  parsed_args)
        else:
            stdout.write('\n')


class ClimateCommand(OpenStackCommand):

    """Base Climate CLI command."""
    api = 'reservation'
    log = logging.getLogger(__name__ + '.ClimateCommand')
    values_specs = []
    json_indent = None
    resource = None
    allow_names = True

    def __init__(self, app, app_args):
        super(ClimateCommand, self).__init__(app, app_args)

        # NOTE(dbelova): This is no longer supported in cliff version 1.5.2
        # the same moment occurred in Neutron:
        # see https://bugs.launchpad.net/python-neutronclient/+bug/1265926

        # if hasattr(self, 'formatters'):
        #     self.formatters['table'] = TableFormatter()

    def get_client(self):
        return self.app.client

    def get_parser(self, prog_name):
        parser = super(ClimateCommand, self).get_parser(prog_name)
        return parser

    def format_output_data(self, data):
        for k, v in six.iteritems(data):
            if isinstance(v, six.text_type):
                try:
                    # Deserialize if possible into dict, lists, tuples...
                    v = ast.literal_eval(v)
                except SyntaxError:
                    # NOTE(sbauza): This is probably a datetime string, we need
                    #               to keep it unchanged.
                    pass
                except ValueError:
                    # NOTE(sbauza): This is not something AST can evaluate,
                    #               probably a string.
                    pass
            if isinstance(v, list):
                value = '\n'.join(utils.dumps(
                    i, indent=self.json_indent) if isinstance(i, dict)
                    else str(i) for i in v)
                data[k] = value
            elif isinstance(v, dict):
                value = utils.dumps(v, indent=self.json_indent)
                data[k] = value
            elif v is None:
                data[k] = ''

    def add_known_arguments(self, parser):
        pass

    def args2body(self, parsed_args):
        return {}


class CreateCommand(ClimateCommand, show.ShowOne):
    """Create resource with passed args."""

    api = 'reservation'
    resource = None
    log = None

    def get_data(self, parsed_args):
        self.log.debug('get_data(%s)' % parsed_args)
        climate_client = self.get_client()
        body = self.args2body(parsed_args)
        resource_manager = getattr(climate_client, self.resource)
        data = resource_manager.create(**body)
        self.format_output_data(data)

        if data:
            print(self.app.stdout, 'Created a new %s:' % self.resource)
        else:
            data = {'': ''}
        return zip(*sorted(six.iteritems(data)))


class UpdateCommand(ClimateCommand):
    """Update resource's information."""

    api = 'reservation'
    resource = None
    log = None

    def get_parser(self, prog_name):
        parser = super(UpdateCommand, self).get_parser(prog_name)
        if self.allow_names:
            help_str = 'ID or name of %s to delete'
        else:
            help_str = 'ID of %s to delete'
        parser.add_argument(
            'id', metavar=self.resource.upper(),
            help=help_str % self.resource
        )
        self.add_known_arguments(parser)
        return parser

    def run(self, parsed_args):
        self.log.debug('run(%s)' % parsed_args)
        climate_client = self.get_client()
        body = self.args2body(parsed_args)
        if self.allow_names:
            res_id = utils.find_resource_id_by_name_or_id(climate_client,
                                                          self.resource,
                                                          parsed_args.id)
        else:
            res_id = parsed_args.id
        resource_manager = getattr(climate_client, self.resource)
        resource_manager.update(res_id, **body)
        print(self.app.stdout, 'Updated %s: %s' % (self.resource,
                                                   parsed_args.id))
        return


class DeleteCommand(ClimateCommand):
    """Delete a given resource."""

    api = 'reservation'
    resource = None
    log = None

    def get_parser(self, prog_name):
        parser = super(DeleteCommand, self).get_parser(prog_name)
        if self.allow_names:
            help_str = 'ID or name of %s to delete'
        else:
            help_str = 'ID of %s to delete'
        parser.add_argument(
            'id', metavar=self.resource.upper(),
            help=help_str % self.resource)
        return parser

    def run(self, parsed_args):
        self.log.debug('run(%s)' % parsed_args)
        climate_client = self.get_client()
        resource_manager = getattr(climate_client, self.resource)
        if self.allow_names:
            res_id = utils.find_resource_id_by_name_or_id(climate_client,
                                                          self.resource,
                                                          parsed_args.id)
        else:
            res_id = parsed_args.id
        resource_manager.delete(res_id)
        print(self.app.stdout, 'Deleted %s: %s' % (self.resource,
                                                   parsed_args.id))
        return


class ListCommand(ClimateCommand, lister.Lister):
    """List resources that belong to a given tenant."""

    api = 'reservation'
    resource = None
    log = None
    _formatters = {}
    list_columns = []
    unknown_parts_flag = True

    def args2body(self, parsed_args):
        params = {}
        if parsed_args.sort_by:
            if parsed_args.sort_by in self.list_columns:
                params['sort_by'] = parsed_args.sort_by
            else:
                msg = 'Invalid sort option %s' % parsed_args.sort_by
                raise exception.ClimateClientException(msg)
        return params

    def get_parser(self, prog_name):
        parser = super(ListCommand, self).get_parser(prog_name)
        return parser

    def retrieve_list(self, parsed_args):
        """Retrieve a list of resources from Climate server"""
        climate_client = self.get_client()
        body = self.args2body(parsed_args)
        resource_manager = getattr(climate_client, self.resource)
        data = resource_manager.list(**body)
        return data

    def setup_columns(self, info, parsed_args):
        columns = len(info) > 0 and sorted(info[0].keys()) or []
        if not columns:
            parsed_args.columns = []
        elif parsed_args.columns:
            columns = [col for col in parsed_args.columns if col in columns]
        elif self.list_columns:
            columns = [col for col in self.list_columns if col in columns]
        return (
            columns,
            (utils.get_item_properties(s, columns, formatters=self._formatters)
             for s in info)
        )

    def get_data(self, parsed_args):
        self.log.debug('get_data(%s)' % parsed_args)
        data = self.retrieve_list(parsed_args)
        return self.setup_columns(data, parsed_args)


class ShowCommand(ClimateCommand, show.ShowOne):
    """Show information of a given resource."""

    api = 'reservation'
    resource = None
    log = None

    def get_parser(self, prog_name):
        parser = super(ShowCommand, self).get_parser(prog_name)
        if self.allow_names:
            help_str = 'ID or name of %s to look up'
        else:
            help_str = 'ID of %s to look up'
        parser.add_argument('id', metavar=self.resource.upper(),
                            help=help_str % self.resource)
        return parser

    def get_data(self, parsed_args):
        self.log.debug('get_data(%s)' % parsed_args)
        climate_client = self.get_client()

        if self.allow_names:
            res_id = utils.find_resource_id_by_name_or_id(climate_client,
                                                          self.resource,
                                                          parsed_args.id)
        else:
            res_id = parsed_args.id

        resource_manager = getattr(climate_client, self.resource)
        data = resource_manager.get(res_id)
        self.format_output_data(data)
        return zip(*sorted(six.iteritems(data)))
