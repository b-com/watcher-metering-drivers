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

from watcher_metering_drivers import cpu
from watcher_metering_drivers import disk
from watcher_metering_drivers import instance_cpu
from watcher_metering_drivers import memory
from watcher_metering_drivers import pdu
from watcher_metering_drivers import swap


DRIVERS = [
    cpu.CpuCountPuller,
    cpu.CpuIdlePuller,
    cpu.CpuUserPuller,
    disk.DiskTotalSpacePuller,
    disk.DiskFreeSpacePuller,
    disk.DiskUsedSpacePuller,
    instance_cpu.InstanceCpuNodePuller,
    memory.TotalMemoryPuller,
    memory.FreeMemoryPuller,
    memory.UsedMemoryPuller,
    pdu.PduRmsCurrentPuller,
    pdu.PduRmsVoltagePuller,
    pdu.PduActivePowerPuller,
    pdu.PduApparentPowerPuller,
    pdu.PduPowerFactorPuller,
    pdu.PduActiveEnergyPuller,
    pdu.PduOnOffPuller,
    pdu.PduFrequencyPuller,
    swap.TotalSwapPuller,
    swap.FreeSwapPuller,
    swap.UsedSwapPuller,
]


def list_opts():
    drivers_opts = [
        (driver.get_entry_name(), driver.get_config_opts())
        for driver in DRIVERS
        ]
    return drivers_opts
