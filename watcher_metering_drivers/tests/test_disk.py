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

import os
import platform

from freezegun import freeze_time
from mock import Mock
from mock import patch
from posix import statvfs_result
from watcher_metering.agent.measurement import Measurement
from watcher_metering_drivers import disk
from watcher_metering_drivers.tests.base import BaseTestCase


class TestDiskDrivers(BaseTestCase):

    fake_statvfs = statvfs_result((
        4096,  # bsize
        4096,  # frsize
        236216421,  # blocks
        231166945,  # bfree
        219162081,  # bavail
        60006400,  # files
        59315784,  # ffree
        59315784,  # favail
        4096,  # flag
        255,  # namemax
    ))

    scenarios = (
        ("disk.DiskTotalSpacePuller", {
            "puller_factory": disk.DiskTotalSpacePuller,
            "disk_patch": patch.object(
                os, "statvfs", Mock(return_value=fake_statvfs)),
            "expected_data": Measurement(
                name="compute.node.disk.total",
                timestamp="2015-08-04T15:15:45.703542+00:00",
                unit="bytes",
                type_="gauge",
                value=4096 * 236216421,
                resource_id="test_node",
                host="test_node",
                resource_metadata={
                    "host": "test_node",
                    "title": "disk_total"
                }
            )
        }),
        ("disk.DiskFreeSpacePuller", {
            "puller_factory": disk.DiskFreeSpacePuller,
            "disk_patch": patch.object(
                os, "statvfs", Mock(return_value=fake_statvfs)),
            "expected_data": Measurement(
                name="compute.node.disk.free",
                timestamp="2015-08-04T15:15:45.703542+00:00",
                unit="bytes",
                type_="gauge",
                value=4096 * 219162081,
                resource_id="test_node",
                host="test_node",
                resource_metadata={
                    "host": "test_node",
                    "title": "disk_free"
                }
            )
        }),
        ("disk.DiskUsedSpacePuller", {
            "puller_factory": disk.DiskUsedSpacePuller,
            "disk_patch": patch.object(
                os, "statvfs", Mock(return_value=fake_statvfs)),
            "expected_data": Measurement(
                name="compute.node.disk.used",
                timestamp="2015-08-04T15:15:45.703542+00:00",
                unit="bytes",
                type_="gauge",
                value=(236216421 - 231166945) * 4096,
                resource_id="test_node",
                host="test_node",
                resource_metadata={
                    "host": "test_node",
                    "title": "disk_used"
                }
            )
        }),
    )

    @freeze_time("2015-08-04T15:15:45.703542+00:00")
    @patch.object(platform, "node", Mock(return_value="test_node"))
    def test_disk(self):
        data_puller = self.puller_factory(
            self.puller_factory.get_name(),
            self.puller_factory.get_default_probe_id(),
            self.puller_factory.get_default_interval(),
        )

        with self.disk_patch:
            pulled_data = data_puller.do_pull()

        self.assertEqual(
            [measurement.as_dict() for measurement in pulled_data],
            [self.expected_data.as_dict()]
        )
