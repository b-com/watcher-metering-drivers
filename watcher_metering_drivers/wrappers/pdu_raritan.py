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

from oslo_log import log
from pysnmp.entity.rfc3413.oneliner import cmdgen

LOG = log.getLogger(__name__)


class PDURaritanWrapper(object):

    def get_snmpv2(self, ip, metric, outlet):
        cmd = cmdgen.CommandGenerator()
        oid = str(
            '.1.3.6.1.4.1.13742.6.5.4.3.1.4.1.{outlet}.{metric_id}'.format(
                outlet=str(outlet).strip(),
                metric_id=str(metric)
            )
        )
        error_indication, error_status, error_index, var_binds = cmd.getCmd(
            cmdgen.CommunityData('public'),
            cmdgen.UdpTransportTarget((ip, 161), timeout=.2, retries=1),
            oid
        )

        # Check for errors and print out results
        if error_indication:
            raise NameError(error_indication)
        else:
            if error_status:
                LOG.error(
                    '%s at %s',
                    error_status.prettyPrint(),
                    error_index and var_binds[int(error_index) - 1] or '?',
                )
                raise NameError(var_binds)
            else:
                for _, val in var_binds:
                    # Trick to unpack the returned value
                    return val
