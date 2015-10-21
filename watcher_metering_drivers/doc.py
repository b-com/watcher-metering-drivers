# -*- encoding: utf-8 -*-
# Copyright 2014
# The Cloudscaling Group, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import unicode_literals
from docutils import nodes
from docutils.parsers.rst import Directive
from docutils.parsers.rst import directives
from docutils.statemachine import ViewList
from stevedore.extension import ExtensionManager
from watcher_metering_drivers.version import version_info


class DriversDoc(Directive):

    def add_line(self, line, *lineno):
        """Append one line of generated reST to the output."""
        self.result.append(line, directives.unchanged, *lineno)

    def run(self):
        self.result = ViewList()

        ext_manager = ExtensionManager(namespace='watcher_metering.drivers')
        extensions = ext_manager.extensions

        get_mod_label = lambda mod: mod.rpartition(".")[-1].upper()

        # Aggregates drivers based on their module name (i.e import path)
        modules = set(map(lambda ext: ext.plugin.__module__, extensions))

        grouped_drivers = {
            get_mod_label(mod): (mod, [
                ext.plugin for ext in extensions
                if ext.plugin.__module__ == mod
            ])
            for mod in modules
        }

        for group_name, (mod, drivers) in grouped_drivers.items():
            self.add_driver_group(group_name, mod, drivers)

        node = nodes.paragraph()
        node.document = self.state.document
        self.state.nested_parse(self.result, 0, node)
        return node.children

    def add_driver_group(self, group_name, module, drivers):
        self.add_line("**%s**" % group_name)
        self.add_line('\n')

        # For indexation
        self.add_line('.. automodule:: %s' % module)
        self.add_line('\n')

        for driver_cls in drivers:
            self.add_driver(driver_cls, module)

    def add_driver(self, driver_cls, module):
        self.add_line('.. automodule:: %s' % module)
        self.add_line('    :noindex:')  # To avoid duplicate ID in index
        self.add_line('\n')
        self.add_line('.. autoclass:: %s' % driver_cls.__name__)
        self.add_line('    :members: do_pull,send_measurements')
        self.add_line('\n')
        # self.add_line('    .. automethod:: __init__')
        # self.add_line('\n')
        # self.add_line('    .. autoattribute::')
        # self.add_line('\n')


def setup(app):
    app.add_directive('drivers-doc', DriversDoc)

    return {'version': version_info.version_string()}
