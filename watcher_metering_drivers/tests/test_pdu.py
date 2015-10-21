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

from collections import OrderedDict
import platform

from freezegun import freeze_time
from mock import Mock
from mock import patch
from watcher_metering.agent.measurement import Measurement
from watcher_metering_drivers import pdu
from watcher_metering_drivers.tests.base import BaseTestCase
from watcher_metering_drivers.wrappers.pdu_raritan import PDURaritanWrapper


class TestPduDrivers(BaseTestCase):

    scenarios = (
        ("PduRmsCurrentPuller", {
            "pdu_puller_factory": pdu.PduRmsCurrentPuller,
            "expected_data": {
                "title": "energy_rms_current",
                "probe_id": "energy.rmsCurrent",
                "interval": 1,
                "unit": "A",
                "type": "gauge",
            }
        }),
        ("PduRmsVoltagePuller", {
            "pdu_puller_factory": pdu.PduRmsVoltagePuller,
            "expected_data": {
                "title": "energy_rms_voltage",
                "probe_id": "energy.rmsVoltage",
                "interval": 1,
                "unit": "V",
                "type": "gauge",
            }
        }),
        ("PduActivePowerPuller", {
            "pdu_puller_factory": pdu.PduActivePowerPuller,
            "expected_data": {
                "title": "energy_active_power",
                "probe_id": "energy.activePower",
                "interval": 1,
                "unit": "W",
                "type": "gauge",
            }
        }),
        ("PduApparentPowerPuller", {
            "pdu_puller_factory": pdu.PduApparentPowerPuller,
            "expected_data": {
                "title": "energy_apparent_power",
                "probe_id": "energy.apparentPower",
                "interval": 1,
                "unit": "VA",
                "type": "gauge",
            }
        }),
        ("PduPowerFactorPuller", {
            "pdu_puller_factory": pdu.PduPowerFactorPuller,
            "expected_data": {
                "title": "energy_power_factor",
                "probe_id": "energy.powerFactor",
                "interval": 1,
                "unit": "",
                "type": "gauge",
            }
        }),
        ("PduActiveEnergyPuller", {
            "pdu_puller_factory": pdu.PduActiveEnergyPuller,
            "expected_data": {
                "title": "energy_active_energy",
                "probe_id": "energy.activeEnergy",
                "interval": 1,
                "unit": "kWh",
                "type": "cumulative",
            }
        }),
        ("PduOnOffPuller", {
            "pdu_puller_factory": pdu.PduOnOffPuller,
            "expected_data": {
                "title": "energy_on_off",
                "probe_id": "energy.onOff",
                "interval": 1,
                "unit": "",
                "type": "gauge",
            }
        }),
        ("PduFrequencyPuller", {
            "pdu_puller_factory": pdu.PduFrequencyPuller,
            "expected_data": {
                "title": "energy_frequency",
                "probe_id": "energy.frequency",
                "interval": 1,
                "unit": "V",
                "type": "gauge",
            }
        }),
    )

    @freeze_time("2015-08-04T15:15:45.703542+00:00")
    @patch.object(platform, "node", Mock(return_value="test_node"))
    @patch.object(PDURaritanWrapper, "get_snmpv2", Mock(return_value=13.37))
    def test_pdu_drivers(self):
        data_puller = self.pdu_puller_factory(
            self.pdu_puller_factory.get_name(),
            self.pdu_puller_factory.get_default_probe_id(),
            self.pdu_puller_factory.get_default_interval(),
            pdu_servers=OrderedDict(
                [("PDU_1", "127.0.0.1"), ("PDU_2", "192.168.1.1")]
            ),
            mapping=[
                {"PDU_1": [{"serv1.hostname": 1}, {"serv2.hostname": 2}]},
                {"PDU_2": [{"serv3.hostname": 1}]},
            ],
        )

        expected_measurements = [
            Measurement(
                name=self.expected_data["probe_id"],
                host="serv1.hostname",
                resource_id="serv1.hostname",
                resource_metadata={
                    "epoch": "1438701345703",
                    "host": "serv1.hostname",
                    "title": self.expected_data["title"]
                },
                timestamp="2015-08-04T15:15:45.703542+00:00",
                type_=self.expected_data["type"],
                unit=self.expected_data["unit"],
                value=13.37,
            ),
            Measurement(
                name=self.expected_data["probe_id"],
                host="serv2.hostname",
                resource_id="serv2.hostname",
                resource_metadata={
                    "epoch": "1438701345703",
                    "host": "serv2.hostname",
                    "title": self.expected_data["title"]
                },
                timestamp="2015-08-04T15:15:45.703542+00:00",
                type_=self.expected_data["type"],
                unit=self.expected_data["unit"],
                value=13.37,
            ),
            Measurement(
                name=self.expected_data["probe_id"],
                host="serv3.hostname",
                resource_id="serv3.hostname",
                resource_metadata={
                    "epoch": "1438701345703",
                    "host": "serv3.hostname",
                    "title": self.expected_data["title"]
                },
                timestamp="2015-08-04T15:15:45.703542+00:00",
                type_=self.expected_data["type"],
                unit=self.expected_data["unit"],
                value=13.37,
            ),
        ]

        pulled_data = data_puller.do_pull()

        self.assertEqual(data_puller.title, self.expected_data["title"])
        self.assertEqual(data_puller.probe_id, self.expected_data["probe_id"])
        self.assertEqual(data_puller.interval, self.expected_data["interval"])
        self.assertEqual(data_puller.unit, self.expected_data["unit"])
        self.assertEqual(data_puller.type, self.expected_data["type"])
        self.assertEqual(
            [measurement.as_dict() for measurement in pulled_data],
            [measurement.as_dict() for measurement in expected_measurements],
        )
