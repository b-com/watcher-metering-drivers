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
from mock import MagicMock
from mock import patch
from watcher_metering_drivers.instance_cpu import InstanceCpuNodePuller
from watcher_metering_drivers.tests.base import BaseTestCase
from watcher_metering_drivers.wrappers.cpu import CpuTimeRecord
from watcher_metering_drivers.wrappers.cpu import Instance
from watcher_metering_drivers.wrappers.cpu import InstanceCpuWrapper


class TestInstanceCpuDrivers(BaseTestCase):

    scenarios = (
        ("single_CPU", {
            "patches": patch.multiple(
                InstanceCpuWrapper,
                get_instances=MagicMock(return_value=[
                    Instance("fake", "fakeUUID")]),
                get_cpu_count=MagicMock(return_value=1),
                get_cpu_time=MagicMock(return_value=495470000000),
                get_sys_time=MagicMock(return_value=14044.78222455),
                get_last_record=MagicMock(return_value=CpuTimeRecord(
                    cpu_time=495350000000,
                    sys_time=14042.771235722,
                    cpu_count=1,
                )),
            ),
            "expected_measurements": [{
                "resource_metadata": {
                    "title": "instance_cpu_used",
                    "display_name": "fake",
                    "host": platform.node(),
                },
                "value": 6.0,
                "host": platform.node(),
                "name": "cpu_util",
                "resource_id": "fakeUUID",
                "unit": "%",
                "timestamp": "2015-08-04T15:15:45.703542+00:00",
                "type": "gauge"
            }],
        }),
        ("2_CPUs", {
            "patches": patch.multiple(
                InstanceCpuWrapper,
                get_instances=MagicMock(return_value=[
                    Instance("fake", "fakeUUID")]),
                get_cpu_count=MagicMock(return_value=2),
                get_cpu_time=MagicMock(return_value=495470000000),
                get_sys_time=MagicMock(return_value=14044.78222455),
                get_last_record=MagicMock(return_value=CpuTimeRecord(
                    cpu_time=495350000000,
                    sys_time=14042.771235722,
                    cpu_count=2,
                )),
            ),
            "expected_measurements": [{
                "resource_metadata": {
                    "title": "instance_cpu_used",
                    "display_name": "fake",
                    "host": platform.node(),
                },
                "value": 3.0,
                "host": platform.node(),
                "name": "cpu_util",
                "resource_id": "fakeUUID",
                "unit": "%",
                "timestamp": "2015-08-04T15:15:45.703542+00:00",
                "type": "gauge"
            }],
        }),
    )

    @freeze_time("2015-08-04T15:15:45.703542+00:00")
    def test_instance_cpu(self):
        data_puller = InstanceCpuNodePuller(
            InstanceCpuNodePuller.get_name(),
            InstanceCpuNodePuller.get_default_probe_id(),
            InstanceCpuNodePuller.get_default_interval(),
            libvirt_type="qemu",
            connection_uri=None,
        )

        with self.patches:
            measurements = data_puller.do_pull()

        self.assertEqual(len(measurements), len(self.expected_measurements))
        for measurement, expected in zip(
                measurements, self.expected_measurements):
            self.assertEqual(measurement.as_dict(), expected)


# class TestBench(BaseTestCase):

#     def test_instance_cpu_bench(self):
#         data_puller = InstanceCpuNodePuller(
#             InstanceCpuNodePuller.get_name(),
#             InstanceCpuNodePuller.get_default_probe_id(),
#             InstanceCpuNodePuller.get_default_interval(),
#             libvirt_type="qemu",
#             connection_uri=None,
#         )
#         print("")
#         for _ in range(100):
#             time.sleep(1)
#             print([metric.value for metric in data_puller.do_pull()])
