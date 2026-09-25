import unittest
from GoodWe import GoodWe
from GoodWe import PowerStation
from GoodWe import Inverter
from GoodWe import GoodWeSEMSPlus
import logging
from unittest.mock import patch


class BasicInverterTest(unittest.TestCase):
    inverter = None
    inverterApi = None

    def setUp(self):
        # inverter API data is part of the GetMonitorDetailByPowerstationId API data
        self.inverterApi = {
            "sn": "sn_simple",
            "name": "name_simple",
            "change_num": 0,
            "change_type": 0,
            "relation_sn": None,
            "relation_name": None,
            "status": -1,
        }
        self.inverter = Inverter(self.inverterApi)

    def test_invSerial(self):
        self.assertEqual(self.inverter.serialNumber, "sn_simple")

    def test_invType(self):
        self.assertEqual(self.inverter.type, "name_simple")


class PowerStationTest(unittest.TestCase):
    powerStation = None
    powerStationSingle = None
    powerStationDouble = None
    powerStationApiDataSingle = None
    powerStationApiDataDouble = None

    def setUp(self):
        print("starting the test")
        logging.info("starting the test")

    def test_starting_out(self):
        self.assertEqual(1, 1)

    def test_powerStationId(self):
        stationId = "a73d66f6-aa49-428e-9f93-bdd781f04b7a"
        self.powerStation = PowerStation(id=stationId)
        self.assertEqual(self.powerStation.id, "a73d66f6-aa49-428e-9f93-bdd781f04b7a")
        self.assertEqual(self.powerStation.name, "")
        self.assertEqual(self.powerStation.firstFreeDeviceNum, 0)

    def test_singlePowerStation(self):
        # power station api data is part of the QueryPowerStationByHistory api data
        # this is a single PS
        self.powerStationApiDataSingle = {
            "info": {
                "powerstation_id": "a73d66f6-aa49-428e-9f93-bdd781f04b7e",
                "stationname": "pw_name_1",
                "address": "pw_address_1",
                "status": 1,
            },
            "inverter": [
                {
                    "sn": "inverter_SN1",
                    "name": "inverter_name1",
                    "change_num": 0,
                    "change_type": 0,
                    "relation_sn": None,
                    "relation_name": None,
                    "status": 1,
                }
            ],
        }
        self.powerStationSingle = PowerStation(
            stationData=self.powerStationApiDataSingle
        )
        print("Created power station: '" + str(self.powerStationSingle) + "'")
        logging.info("Created power station: '" + str(self.powerStationSingle) + "'")
        self.assertEqual(
            self.powerStationSingle.id,
            "a73d66f6-aa49-428e-9f93-bdd781f04b7e",
            msg="Single PS ID fail",
        )
        self.assertEqual(
            self.powerStationSingle.name, "pw_name_1", msg="Single PS name fail"
        )
        self.assertEqual(
            self.powerStationSingle.numInverters,
            1,
            msg="Single PS num inv fail: " + str(self.powerStationSingle.numInverters),
        )

    def test_doublePowerStation(self):
        self.powerStationApiDataDouble = {
            "info": {
                "powerstation_id": "a73d66f6-aa49-428e-9f93-bdd781f04b7d",
                "stationname": "pw_name_2",
                "address": "pw_address_2",
                "status": 1,
            },
            "inverter": [
                {
                    "sn": "inverter_SN21",
                    "name": "inverter_name21",
                    "change_num": 0,
                    "change_type": 0,
                    "relation_sn": None,
                    "relation_name": None,
                    "status": 1,
                },
                {
                    "sn": "inverter_SN22",
                    "name": "inverter_name22",
                    "change_num": 0,
                    "change_type": 0,
                    "relation_sn": None,
                    "relation_name": None,
                    "status": 1,
                },
            ],
        }
        self.powerStationDouble = PowerStation(
            stationData=self.powerStationApiDataDouble
        )
        logging.info("Created power station: '" + str(self.powerStationDouble) + "'")
        print("Created power station: '" + str(self.powerStationDouble) + "'")
        self.assertEqual(
            self.powerStationDouble.id,
            "a73d66f6-aa49-428e-9f93-bdd781f04b7d",
            msg="Double PS ID fail",
        )
        self.assertEqual(
            self.powerStationDouble.name, "pw_name_2", msg="Double PS name fail"
        )
        self.assertEqual(
            self.powerStationDouble.numInverters,
            2,
            msg="Double PS num inv fail: " + str(self.powerStationDouble.numInverters),
        )

    # def test_doublePowerStation(self):

    def tearDown(self):
        logging.info("tearing down the house")
        print("tearing down the house")
        self.powerStationSingle = None
        self.powerStationDouble = None
        self.powerStation = None


class GoodWeSEMSPlusWebDataTest(unittest.TestCase):
    class _MockResponse:
        def __init__(self, payload, status_code=200, url="https://example.invalid"):
            self._payload = payload
            self.status_code = status_code
            self.url = url
            self.text = str(payload)

        def json(self):
            return self._payload

        def raise_for_status(self):
            if self.status_code >= 400:
                raise Exception("HTTP {}".format(self.status_code))

    def setUp(self):
        self.account = GoodWeSEMSPlus("eu-gateway.semsportal.com", "443", "user", "password")
        self.account.base_url = "https://eu-gateway.semsportal.com/web/sems"
        self.account.token = {
            "uid": "uid1",
            "timestamp": 1,
            "token": "secret-token",
            "client": "semsPlusWeb",
            "version": "",
            "language": "en",
            "region": "eu",
        }

    @patch("GoodWe.requests.post")
    def test_station_data_web_fallback_is_wrapped_with_code_and_data(self, mock_post):
        mock_post.return_value = self._MockResponse(
            {"code": "00000", "data": {"inverter": []}}
        )
        with patch.object(
            self.account,
            "getWebData",
            return_value={
                "info": {"powerstation_id": "station-1", "stationname": "", "address": "", "status": 0},
                "inverter": [{"sn": "INV1", "status": 1}],
            },
        ):
            result = self.account.stationDataRequest("station-1")

        self.assertEqual(result["code"], 0)
        self.assertIn("data", result)
        self.assertEqual(result["data"]["inverter"][0]["sn"], "INV1")

    @patch("GoodWe.requests.post")
    def test_centralized_page_response_is_normalized(self, mock_post):
        mock_post.return_value = self._MockResponse(
            {
                "code": "00000",
                "data": {
                    "dataList": [
                        {
                            "id": "station-1",
                            "children": [
                                {
                                    "deviceType": "INVERTER",
                                    "sn": "INV1",
                                    "status": 1,
                                    "faultMessage": "",
                                    "temperature": "22.5",
                                    "fac": "50.1",
                                    "Iac": "1.5",
                                    "Vac": "230.4",
                                    "pAc": "2.3",
                                    "Vpv1": "350",
                                    "Ipv1": "4.2",
                                    "proToday": "5.1",
                                    "proTotal": "1234.5",
                                }
                            ],
                        }
                    ]
                },
            }
        )

        result = self.account.getWebCentralizedPageInverters("station-1")

        self.assertEqual(len(result), 1)
        inverter = result[0]
        self.assertEqual(inverter["sn"], "INV1")
        self.assertEqual(inverter["status"], 1)
        self.assertEqual(inverter["output_power"], 2300.0)
        self.assertEqual(inverter["pv_input_1"], "350.0V/4.2A")
        self.assertEqual(inverter["etotal"], 1234.5)

    @patch("GoodWe.requests.post")
    def test_centralized_page_pagination_merges_multiple_pages(self, mock_post):
        mock_post.side_effect = [
            self._MockResponse(
                {
                    "code": "00000",
                    "data": {
                        "total": 60,
                        "records": 50,
                        "dataList": [
                            {
                                "id": "station-1",
                                "children": [
                                    {"deviceType": "INVERTER", "sn": "INV-A", "status": 1}
                                ],
                            }
                        ],
                    },
                }
            ),
            self._MockResponse(
                {
                    "code": "00000",
                    "data": {
                        "total": 60,
                        "records": 10,
                        "dataList": [
                            {
                                "id": "station-1",
                                "children": [
                                    {"deviceType": "INVERTER", "sn": "INV-B", "status": 0}
                                ],
                            }
                        ],
                    },
                }
            ),
        ]

        result = self.account.getWebCentralizedPageInverters("station-1")

        self.assertEqual([inv["sn"] for inv in result], ["INV-A", "INV-B"])
        self.assertEqual(mock_post.call_count, 2)
        first_payload = mock_post.call_args_list[0].kwargs["json"]
        self.assertEqual(first_payload["powerStationId"], "station-1")

    def test_web_data_falls_back_to_legacy_web_endpoints(self):
        with patch.object(
            self.account, "getWebCentralizedPageInverters", return_value=[]
        ), patch.object(
            self.account,
            "getWebInverterDevices",
            return_value=[{"sn": "INV2", "deviceType": "INVERTER", "status": 1}],
        ), patch.object(
            self.account,
            "getWebInverterTelemetry",
            return_value={
                "tempperature": 23.0,
                "d": {"fac1": 50.0},
                "output_current": 2.0,
                "output_voltage": 230.0,
                "output_power": 2000.0,
                "pv_input_1": "100.0V/1.0A",
            },
        ), patch.object(
            self.account, "getWebInverterTelecounting", return_value={"etotal": 10.0}
        ):
            result = self.account.getWebData("station-1")

        self.assertEqual(result["inverter"][0]["sn"], "INV2")
        self.assertEqual(result["inverter"][0]["etotal"], 10.0)
        self.assertEqual(result["info"]["powerstation_id"], "station-1")

    def test_web_data_falls_back_when_centralized_request_fails(self):
        with patch("GoodWe.requests.post", side_effect=Exception("network error")), patch.object(
            self.account,
            "getWebInverterDevices",
            return_value=[{"sn": "INV3", "deviceType": "INVERTER", "status": 1}],
        ), patch.object(
            self.account,
            "getWebInverterTelemetry",
            return_value={"output_power": 1200.0, "pv_input_1": "120.0V/2.0A"},
        ), patch.object(
            self.account, "getWebInverterTelecounting", return_value={"etotal": 20.0}
        ):
            result = self.account.getWebData("station-1")

        self.assertEqual(result["inverter"][0]["sn"], "INV3")
        self.assertIn("info", result)

    def test_web_data_keeps_centralized_results_without_pv_input(self):
        with patch.object(
            self.account,
            "getWebCentralizedPageInverters",
            return_value=[{"sn": "INV4", "status": 1, "output_power": 1000.0}],
        ), patch.object(
            self.account,
            "getWebInverterDevices",
            return_value=[{"sn": "INV4", "deviceType": "INVERTER", "status": 1}],
        ) as mock_legacy_devices:
            result = self.account.getWebData("station-1")

        self.assertEqual(result["inverter"][0]["sn"], "INV4")
        self.assertNotIn("pv_input_1", result["inverter"][0])
        self.assertEqual(result["info"]["powerstation_id"], "station-1")
        mock_legacy_devices.assert_not_called()


def main():
    logging.basicConfig(format='%(asctime)s - %(levelname)-8s - %(filename)-18s - %(message)s', filename="goodwe_test.log",level=logging.DEBUG)
    logging.info("==== starting test run ====")
    unittest.main()
    logging.info("==== finished test run ====")


if __name__ == "__main__":
    main()
