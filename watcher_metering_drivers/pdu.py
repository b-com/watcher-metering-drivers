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

import time

from enum import Enum
from oslo_config import cfg
from oslo_config import types
from oslo_log import log
from watcher_metering.agent.measurement import Measurement
from watcher_metering.agent.puller import MetricPuller
from watcher_metering_drivers.wrappers.pdu_raritan import PDURaritanWrapper

LOG = log.getLogger(__name__)


class PduPullerBase(MetricPuller):

    class Metrics(Enum):
        rmsCurrent = 1
        rmsVoltage = 4
        activePower = 5
        apparentPower = 6
        powerFactor = 7
        activeEnergy = 8
        onOff = 14
        frequency = 23

    class Units(Enum):
        none = -1
        other = 0
        volt = 1
        amp = 2
        watt = 3
        voltamp = 4
        wattHour = 5
        voltampHour = 6
        degreeC = 7

    def __init__(self, title, probe_id, interval,
                 pdu_servers, mapping):
        super(PduPullerBase, self).__init__(title, probe_id, interval)
        self.pdu_servers = pdu_servers
        self.mapping = self._normalize_mapping(mapping)

        self.wrapper = PDURaritanWrapper()
        self._check_config()

    @classmethod
    def _get_pdu_opts(cls):
        return [
            cfg.Opt(
                name="pdu_servers",
                type=types.Dict(
                    value_type=types.String(),
                ),
                help="A mapping between PDU names and their endpoint "
                     "(IP/FQDN)",
                sample_default=(
                    "[my_data_puller]\n"
                    "#pdu_servers=PDU_1:127.0.0.1,PDU_2:192.168.1.1")
            ),
            cfg.MultiOpt(
                name="mapping",
                item_type=types.Dict(
                    value_type=types.List(
                        bounds=True,
                        item_type=types.Dict(
                            value_type=types.Integer()
                        ),
                    ),
                ),
                help="Each entry specified here should be an entry mapping a "
                     "PDU name to a list of servers. Each server is a pair "
                     "between its endpoint and its related outlet ID.",
                sample_default=(
                    "[my_data_puller]\n"
                    "#mapping = PDU_1:[serv1.hostname:1,serv2.hostname:2]\n"
                    "#mapping = PDU_2:[serv3.hostname:1,serv4.hostname:2]"
                ),

            ),
        ]

    def _normalize_mapping(self, mapping):
        normalized_mapping = {}
        for entry in mapping:
            for pdu_name, server_outlet_pairs in entry.items():
                if pdu_name in normalized_mapping:
                    raise ValueError(
                        "Duplicated `%s` value in mapping!" % pdu_name)
                for pair_dict in server_outlet_pairs:
                    for pair_key, pair_value, in pair_dict.items():
                        normalized_mapping.setdefault(pdu_name, []).append(
                            (pair_key, pair_value)
                        )

        return normalized_mapping

    def _check_config(self):
        for pdu_name, pdu_endpoint in self.pdu_servers.items():
            if pdu_name not in self.mapping:
                raise ValueError(
                    "Missing PDU entry for `%s`->`%s` in `pdu_to_servers` "
                    "config" % (pdu_name, pdu_endpoint))

    @classmethod
    def get_config_opts(cls):
        return cls.get_base_opts() + cls._get_pdu_opts()

    @property
    def metric(self):
        raise NotImplementedError

    @property
    def unit(self):
        raise NotImplementedError

    @property
    def type(self):
        raise NotImplementedError

    def _do_pull_for_server(self, pdu, server_endpoint, outlet):
        try:
            LOG.debug(
                "PDU address is %s | server is %s | plugged on outlet %s",
                pdu, server_endpoint, outlet)
            value = self.wrapper.get_snmpv2(
                pdu, self.metric, outlet
            )
            milliseconds_since_epoch = int(time.time() * 1000)
            resource_metadata = {
                "host": server_endpoint,
                "title": self.title,
                "epoch": str(milliseconds_since_epoch)
            }

            measurement = Measurement(
                name=self.probe_id,
                unit=self.unit,
                type_=self.type,
                value=float(value),
                resource_id=server_endpoint,
                host=server_endpoint,
                resource_metadata=resource_metadata,
            )

            LOG.debug("[PDU] Message = %r", measurement.as_dict())
            return measurement

        except Exception as exc:
            LOG.warning(
                "Sorry, we have not received a response of PDU (%s) "
                "for getting the OID(%s) "
                "on the server `%s` thrown Exception is <%s>",
                pdu, self.metric, server_endpoint, exc.args[0]
            )

    def do_pull(self):
        LOG.info("[%s] Pulling measurements...", self.key)
        measurements = []
        for pdu_name, pdu_endpoint in self.pdu_servers.items():
            mapping_entry = self.mapping[pdu_name]
            for server_endpoint, server_outlet in mapping_entry:
                # server_endpoint, server_outlet = server_outlet_pair
                measurement = self._do_pull_for_server(
                    pdu_endpoint, server_endpoint, server_outlet
                )
                if measurement:
                    measurements.append(measurement)

        LOG.info("[%s] Measurements collected.", self.key)
        return measurements


class PduRmsCurrentPuller(PduPullerBase):

    @classmethod
    def get_name(cls):
        return "energy_rms_current"

    @classmethod
    def get_default_probe_id(cls):
        return "energy.rmsCurrent"

    @classmethod
    def get_default_interval(cls):
        return 1  # 1 second

    @property
    def metric(self):
        return self.Metrics.activePower.value

    @property
    def unit(self):
        return "A"  # Ampere

    @property
    def type(self):
        return "gauge"  # To be confirmed


class PduRmsVoltagePuller(PduPullerBase):

    @classmethod
    def get_name(cls):
        return "energy_rms_voltage"

    @classmethod
    def get_default_probe_id(cls):
        return "energy.rmsVoltage"

    @classmethod
    def get_default_interval(cls):
        return 1  # 1 second

    @property
    def metric(self):
        return self.Metrics.rmsVoltage.value

    @property
    def unit(self):
        return "V"  # Volt

    @property
    def type(self):
        return "gauge"  # To be confirmed


class PduActivePowerPuller(PduPullerBase):

    @classmethod
    def get_name(cls):
        return "energy_active_power"

    @classmethod
    def get_default_probe_id(cls):
        return "energy.activePower"

    @classmethod
    def get_default_interval(cls):
        return 1  # 1 second

    @property
    def metric(self):
        return self.Metrics.activePower.value

    @property
    def unit(self):
        return "W"  # Watt

    @property
    def type(self):
        return "gauge"  # To be confirmed


class PduApparentPowerPuller(PduPullerBase):

    @classmethod
    def get_name(cls):
        return "energy_apparent_power"

    @classmethod
    def get_default_probe_id(cls):
        return "energy.apparentPower"

    @classmethod
    def get_default_interval(cls):
        return 1  # 1 second

    @property
    def metric(self):
        return self.Metrics.apparentPower.value

    @property
    def unit(self):
        return "VA"  # Volt-Ampere

    @property
    def type(self):
        return "gauge"  # To be confirmed


class PduPowerFactorPuller(PduPullerBase):

    @classmethod
    def get_name(cls):
        return "energy_power_factor"

    @classmethod
    def get_default_probe_id(cls):
        return "energy.powerFactor"

    @classmethod
    def get_default_interval(cls):
        return 1  # 1 second

    @property
    def metric(self):
        return self.Metrics.powerFactor.value

    @property
    def unit(self):
        return ""  # No unit: ratio

    @property
    def type(self):
        return "gauge"  # To be confirmed


class PduActiveEnergyPuller(PduPullerBase):

    @classmethod
    def get_name(cls):
        return "energy_active_energy"

    @classmethod
    def get_default_probe_id(cls):
        return "energy.activeEnergy"

    @classmethod
    def get_default_interval(cls):
        return 1  # 1 second

    @property
    def metric(self):
        return self.Metrics.activeEnergy.value

    @property
    def unit(self):
        return "kWh"

    @property
    def type(self):
        return "cumulative"


class PduOnOffPuller(PduPullerBase):

    @classmethod
    def get_name(cls):
        return "energy_on_off"

    @classmethod
    def get_default_probe_id(cls):
        return "energy.onOff"

    @classmethod
    def get_default_interval(cls):
        return 1  # 1 second

    @property
    def metric(self):
        return self.Metrics.onOff.value

    @property
    def unit(self):
        return ""  # Boolean

    @property
    def type(self):
        return "gauge"  # To be confirmed


class PduFrequencyPuller(PduPullerBase):

    @classmethod
    def get_name(cls):
        return "energy_frequency"

    @classmethod
    def get_default_probe_id(cls):
        return "energy.frequency"

    @classmethod
    def get_default_interval(cls):
        return 1  # 1 second

    @property
    def metric(self):
        return self.Metrics.frequency.value

    @property
    def unit(self):
        return "V"  # To be confirmed

    @property
    def type(self):
        return "gauge"  # To be confirmed
