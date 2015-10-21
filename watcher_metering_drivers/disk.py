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

from oslo_log import log
from watcher_metering.agent.measurement import Measurement
from watcher_metering.agent.puller import MetricPuller
from watcher_metering_drivers.wrappers.host_monitoring import HostMetric
from watcher_metering_drivers.wrappers.host_monitoring import HostMonitoring

LOG = log.getLogger(__name__)


def get_root_path():
    return os.path.abspath(os.sep)


class BaseDiskNodePuller(MetricPuller):

    def __init__(self, title, probe_id, interval):
        super(BaseDiskNodePuller, self).__init__(
            title=title,
            probe_id=probe_id,
            interval=interval,
        )
        self.wrapper = HostMonitoring()

    @property
    def metric(self):
        raise NotImplementedError  # HostMetric attribute

    @property
    def unit(self):
        raise NotImplementedError  # (unicode string)

    def do_pull(self):
        LOG.info("[%s] Pulling measurements...", self.key)
        value = self.wrapper.disk_usage(get_root_path(), self.metric)

        resource_metadata = {
            "host": platform.node(),
            "title": self.title
        }
        measurement = Measurement(
            name=self.probe_id,
            unit=self.unit,
            type_="gauge",
            value=value,
            resource_id=platform.node(),
            resource_metadata=resource_metadata,
        )
        LOG.info("[%s] Measurements collected.", self.key)
        return [measurement]


class DiskTotalSpacePuller(BaseDiskNodePuller):

    @classmethod
    def get_name(cls):
        return "disk_total"

    @classmethod
    def get_default_probe_id(cls):
        return "compute.node.disk.total"

    @classmethod
    def get_default_interval(cls):
        return 60 * 60  # 1 hour

    @property
    def metric(self):
        return HostMetric.disk_total

    @property
    def unit(self):
        return "bytes"


class DiskFreeSpacePuller(BaseDiskNodePuller):

    @classmethod
    def get_name(cls):
        return "disk_free"

    @classmethod
    def get_default_probe_id(cls):
        return "compute.node.disk.free"

    @classmethod
    def get_default_interval(cls):
        return 5  # 5 seconds

    @property
    def metric(self):
        return HostMetric.disk_free

    @property
    def unit(self):
        return "bytes"


class DiskUsedSpacePuller(BaseDiskNodePuller):

    @classmethod
    def get_name(cls):
        return "disk_used"

    @classmethod
    def get_default_probe_id(cls):
        return "compute.node.disk.used"

    @classmethod
    def get_default_interval(cls):
        return 5  # 5 seconds

    @property
    def metric(self):
        return HostMetric.disk_used

    @property
    def unit(self):
        return "bytes"
