# -*- encoding: utf-8 -*-
# Copyright (c) 2015 b<>com
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

from __future__ import unicode_literals

import platform

from freezegun import freeze_time
from mock import Mock
from mock import patch
import psutil
from psutil._pslinux import svmem
from watcher_metering.agent.measurement import Measurement
from watcher_metering_drivers import memory
from watcher_metering_drivers.tests.base import BaseTestCase


class TestMemoryDrivers(BaseTestCase):

    fake_svmem = svmem(
        total=16749080576,
        available=15042203648,
        percent=10.2,
        used=3770953728,
        free=12978126848,
        active=2177314816,
        inactive=1093963776,
        buffers=322965504,
        cached=1741111296)

    scenarios = (
        ("TotalMemoryPuller", {
            "puller_factory": memory.TotalMemoryPuller,
            "memory_patch": patch.object(psutil, "virtual_memory",
                                         Mock(return_value=fake_svmem)),
            "expected_data": Measurement(
                name="compute.node.memory.total",
                timestamp="2015-08-04T15:15:45.703542+00:00",
                unit="bytes",
                type_="gauge",
                value=16749080576,
                resource_id="test_node",
                host="test_node",
                resource_metadata={
                    "host": "test_node",
                    "title": "memory_total"
                }
            )
        }),
        ("FreeMemoryPuller", {
            "puller_factory": memory.FreeMemoryPuller,
            "memory_patch": patch.object(psutil, "virtual_memory",
                                         Mock(return_value=fake_svmem)),
            "expected_data": Measurement(
                name="compute.node.memory.free",
                timestamp="2015-08-04T15:15:45.703542+00:00",
                unit="bytes",
                type_="gauge",
                value=12978126848,
                resource_id="test_node",
                host="test_node",
                resource_metadata={
                    "host": "test_node",
                    "title": "memory_free"
                }
            )
        }),
        ("UsedMemoryPuller", {
            "puller_factory": memory.UsedMemoryPuller,
            "memory_patch": patch.object(psutil, "virtual_memory",
                                         Mock(return_value=fake_svmem)),
            "expected_data": Measurement(
                name="compute.node.memory.used",
                timestamp="2015-08-04T15:15:45.703542+00:00",
                unit="bytes",
                type_="gauge",
                value=3770953728,
                resource_id="test_node",
                host="test_node",
                resource_metadata={
                    "host": "test_node",
                    "title": "memory_used"
                }
            )
        }),
    )

    @freeze_time("2015-08-04T15:15:45.703542+00:00")
    @patch.object(platform, "node", Mock(return_value="test_node"))
    def test_memory(self):
        data_puller = self.puller_factory(
            self.puller_factory.get_name(),
            self.puller_factory.get_default_probe_id(),
            self.puller_factory.get_default_interval(),
        )

        with self.memory_patch:
            pulled_data = data_puller.do_pull()

        self.assertEqual(
            [measurement.as_dict() for measurement in pulled_data],
            [self.expected_data.as_dict()]
        )
