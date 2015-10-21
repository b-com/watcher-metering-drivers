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
from psutil._pslinux import scputimes
from watcher_metering.agent.measurement import Measurement
from watcher_metering_drivers import cpu
from watcher_metering_drivers.tests.base import BaseTestCase


class TestCpuDrivers(BaseTestCase):

    fake_scputimes = scputimes(
        user=1.4,
        nice=0.0,
        system=0.6,
        idle=97.9,
        iowait=0.1,
        irq=0.0,
        softirq=0.0,
        steal=0.0,
        guest=0.0,
        guest_nice=0.0)

    scenarios = (
        ("test_CpuCountPuller", {
            "puller_factory": cpu.CpuCountPuller,
            "cpu_patch": patch.object(psutil, "cpu_count",
                                      Mock(return_value=5)),
            "expected_data": Measurement(
                name="compute.node.cpu.count",
                timestamp="2015-08-04T15:15:45.703542+00:00",
                unit="",
                type_="gauge",
                value=5,
                resource_id="test_node",
                host="test_node",
                resource_metadata={
                    "host": "test_node",
                    "title": "cpu_count"
                }
            )
        }),
        ("test_CpuIdlePuller", {
            "puller_factory": cpu.CpuIdlePuller,
            "cpu_patch": patch.object(psutil, "cpu_times_percent",
                                      Mock(return_value=fake_scputimes)),
            "expected_data": Measurement(
                name="compute.node.cpu.idle",
                timestamp="2015-08-04T15:15:45.703542+00:00",
                unit="%",
                type_="gauge",
                value=97.9,
                resource_id="test_node",
                host="test_node",
                resource_metadata={
                    "host": "test_node",
                    "title": "cpu_idle"
                }
            )
        }),
        ("test_CpuUserPuller", {
            "puller_factory": cpu.CpuUserPuller,
            "cpu_patch": patch.object(psutil, "cpu_times_percent",
                                      Mock(return_value=fake_scputimes)),
            "expected_data": Measurement(
                name="compute.node.cpu.user",
                timestamp="2015-08-04T15:15:45.703542+00:00",
                unit="%",
                type_="gauge",
                value=1.4,
                resource_id="test_node",
                host="test_node",
                resource_metadata={
                    "host": "test_node",
                    "title": "cpu_user"
                }
            )
        }),
    )

    @freeze_time("2015-08-04T15:15:45.703542+00:00")
    @patch.object(platform, "node", Mock(return_value="test_node"))
    def test_cpu(self):
        data_puller = self.puller_factory(
            self.puller_factory.get_name(),
            self.puller_factory.get_default_probe_id(),
            self.puller_factory.get_default_interval(),
        )

        with self.cpu_patch:
            pulled_data = data_puller.do_pull()

        self.assertEqual(
            [measurement.as_dict() for measurement in pulled_data],
            [self.expected_data.as_dict()]
        )
