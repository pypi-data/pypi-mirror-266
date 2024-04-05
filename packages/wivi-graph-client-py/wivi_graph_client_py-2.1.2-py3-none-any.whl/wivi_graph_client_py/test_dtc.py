import unittest
from datetime import datetime

from wivi_graph_client_py.client import GraphQL_Client

client = GraphQL_Client("http://0.0.0.0:8092/graphql")

class TestUpsertDtcData(unittest.IsolatedAsyncioTestCase):
    async def setUp(self):
        self.configuration = {
            "input": {
                "deviceId": 1,
                "fleetId": 1,
                "organizationId": 1,
                "vehicleId": 1
            }
        }
        self.messages = {
            "input": {
                "messages": [
                    {
                        "arbId": "67890",
                        "name": "example_name",
                        "networkName": "PS-011",
                        "ecuId": "example_network_name", 
                        "uploadId": 12345
                    }
                ]   
            }
        }
        self.configurationDto = client.create_configuration(self.configuration)
        self.msgDto = client.create_message(self.messages)
        
        self.dtc_data = {
            "dtcId": "ABC1",
            "value": "12345",
            "status": "active",
            "description": "2024-02-18T12:00:00Z",
            "time": datetime.now().isoformat(),
            "snapshot": [
                {"time": "2024-02-18T12:00:00Z", "bytes": "snapshot_bytes_example"}
            ],
            "extension": [
                {"time": "2024-02-18T12:00:00Z", "bytes": "snapshot_bytes_example"}
            ]
        }
        
        self.dtc = {
            "input": {
                "configurationId": self.configurationDto['data']['createConfiguration']['id'],
                "messageId": self.msgDto['data']['createMessage'][0]['id'],
                "uploadId": 12345,
                "messageDate": datetime.now().isoformat(),
                "data": [self.dtc_data]
            }
        }

        self.dtc2 = self.dtc.copy()
        self.dtc2["input"]["data"][0]["dtcId"] = "ABC12"

        self.dtc_multiple = self.dtc.copy()
        self.dtc_multiple["input"]["data"].extend([
            {"dtcId": "ABC1234", **self.dtc_data},
            {"dtcId": "ABC12345", **self.dtc_data}
        ])

    async def test_create_dtc(self):
        await self.setUp()
        result = client.create_dtc(self.dtc)
        self.assertIsInstance(result, dict)

    async def test_prevent_duplicate_dtc_insertion(self):
        await self.setUp()
        result = client.create_dtc(self.dtc)
        result2 = client.create_dtc(self.dtc2)
        self.assertIn('data', result2)
        expected_keys = ['upsertDtcData']
        self.assertTrue(all(key in result2['data'] for key in expected_keys))

    async def test_create_multiple_bytes_for_extension_in_dtc(self):
        await self.setUp()
        result = client.create_dtc(self.dtc_multiple)
        self.assertIsInstance(result, dict)

    async def test_create_multiple_bytes_for_snapshot_in_dtc(self):
        await self.setUp()
        result = client.create_dtc(self.dtc_multiple)
        self.assertIsInstance(result, dict)

    async def test_create_multiple_dtc_values(self):
        await self.setUp()
        result = client.create_dtc(self.dtc2)
        self.assertIsInstance(result, dict)

    async def test_create_multiple_dtc_time_series_values(self):
        await self.setUp()
        result = client.create_dtc(self.dtc_multiple)
        self.assertIsInstance(result, dict)

if __name__ == "__main__":
    unittest.main()
