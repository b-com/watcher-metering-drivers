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

import os

from enum import Enum
import psutil


class HostMetric(Enum):
    mem_free = 1
    mem_total = 2
    mem_used = 3

    disk_free = 4
    disk_total = 5
    disk_used = 6

    swap_free = 7
    swap_total = 8
    swap_used = 9

    cpu_count = 10
    cpu_idle = 11
    cpu_user = 12


class HostMonitoring(object):

    def disk_usage(self, path, usage):
        st = os.statvfs(path)
        if usage == HostMetric.disk_free:
            free = st.f_bavail * st.f_frsize
            return free
        elif usage == HostMetric.disk_total:
            total = st.f_blocks * st.f_frsize
            return total
        else:
            used = (st.f_blocks - st.f_bfree) * st.f_frsize
            return used

    def memory_usage(self, usage):
        m = psutil.virtual_memory()
        if usage == HostMetric.mem_free:
            return m.free
        elif usage == HostMetric.mem_total:
            return m.total
        else:
            return m.used

    def swap_usage(self, usage):
        m = psutil.swap_memory()
        if usage == HostMetric.swap_free:
            return m.free
        elif usage == HostMetric.swap_total:
            return m.total
        else:
            return m.used

    def cpu_usage(self, usage):
        if usage == HostMetric.cpu_count:
            return psutil.cpu_count()
        elif usage == HostMetric.cpu_user:
            return psutil.cpu_times_percent().user
        else:
            return psutil.cpu_times_percent().idle
