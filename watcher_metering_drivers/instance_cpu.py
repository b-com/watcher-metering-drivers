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

from oslo_config import cfg
from oslo_log import log
from watcher_metering.agent.measurement import Measurement
from watcher_metering.agent.puller import MetricPuller
from watcher_metering_drivers.wrappers.cpu import InstanceCpuWrapper

LOG = log.getLogger(__name__)


class InstanceCpuNodePuller(MetricPuller):

    def __init__(self, title, probe_id, interval,
                 libvirt_type, connection_uri):
        super(InstanceCpuNodePuller, self).__init__(
            title=title,
            probe_id=probe_id,
            interval=interval,
        )
        self.libvirt_type = libvirt_type
        self.connection_uri = connection_uri

        self.uri = self._get_uri()
        self.wrapper = InstanceCpuWrapper(
            libvirt_type=self.libvirt_type,
            libvirt_uri=self.uri,
        )

    def _get_uri(self):
        if self.libvirt_type == 'uml':
            uri = self.connection_uri or 'uml:///system'
        elif self.libvirt_type == 'xen':
            uri = self.connection_uri or 'xen:///'
        elif self.libvirt_type == 'lxc':
            uri = self.connection_uri or 'lxc:///'
        elif self.libvirt_type == 'parallels':
            uri = self.connection_uri or 'parallels:///system'
        else:
            uri = self.connection_uri or 'qemu:///system'
        return uri

    @classmethod
    def get_config_opts(cls):
        # This could also be extrated from the Nova or Ceilometer configuration
        # See --> https://github.com/openstack/nova/blob/stable/liberty
        #   /nova/virt/libvirt/driver.py#L132
        # See --> https://github.com/openstack/ceilometer/blob/stable/liberty
        #   /ceilometer/compute/virt/libvirt/inspector.py#L32
        return cls.get_base_opts() + [
            cfg.StrOpt('libvirt_type',
                       default='kvm',
                       choices=['kvm', 'lxc', 'qemu', 'uml', 'xen'],
                       help='Libvirt domain type.'),
            cfg.StrOpt('connection_uri',
                       default='',
                       help='Override the default libvirt URI '
                            '(which is dependent on libvirt_type).'),
        ]

    def do_pull(self):
        LOG.info("[%s] Pulling measurements...", self.key)
        measurements = []
        for instance in self.wrapper.get_instances():
            value = self.wrapper.instance_cpu_percent(instance)

            resource_metadata = {
                "host": platform.node(),
                "title": self.title,
                "display_name": instance.name
            }
            measurement = Measurement(
                name=self.probe_id,
                unit=self.unit,
                type_="gauge",
                value=value,
                resource_id=instance.id,
                resource_metadata=resource_metadata,
            )
            LOG.info("[%s] Measurements collected.", self.key)
            measurements.append(measurement)

        return measurements

    @classmethod
    def get_name(cls):
        return "instance_cpu_used"

    @classmethod
    def get_default_probe_id(cls):
        return "cpu_util"

    @classmethod
    def get_default_interval(cls):
        return 1

    @property
    def unit(self):
        return "%"
