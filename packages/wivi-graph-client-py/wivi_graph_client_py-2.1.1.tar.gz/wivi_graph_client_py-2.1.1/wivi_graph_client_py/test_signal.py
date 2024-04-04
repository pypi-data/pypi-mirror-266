import unittest
from wivi_graph_client_py.client import GraphQL_Client
from datetime import datetime

client = GraphQL_Client("http://localhost:8092/graphql")

class TestUpsertSignalData(unittest.IsolatedAsyncioTestCase):
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
        self.msgDto = (client.create_message(self.messages))
        self.signal_data = [
            {
                "time":  "2024-02-18T12:00:00Z",
                "svalue": "example_svalue",
                "value": 123,
            }
            for _ in range(50)
        ]
        self.signal_data_large = [
            {
                "time":  "2024-02-18T12:00:00Z",
                "svalue": "example_svalue",
                "value": 123,
            }
            for _ in range(50)
        ]

        self.upsert_signal = {
            "configurationId": self.configurationDto['data']['createConfiguration']['id'],
            "messageId": self.msgDto['data']['createMessage'][0]['id'],
            "data": self.signal_data,
            "paramType": "NUMBER",
            "signalType": "SIGNAL",
            "unit": "km/h",
            "name": "example_name"
        }
        self.upsert_signal_large = {
            "configurationId": self.configurationDto['data']['createConfiguration']['id'],
            "messageId": self.msgDto['data']['createMessage'][0]['id'],
            "data": self.signal_data_large,
            "paramType": "NUMBER",
            "signalType": "SIGNAL",
            "unit": "km/h",
            "name": "example_name"
        }

        self.upsert_signal_data_input = {
            "signals": [self.upsert_signal for _ in range(5)]
        }
        
        self.upsert_signal_data_input_large = {
            "signals": [self.upsert_signal for _ in range(5)]
        }

    async def test_simple(self):
        await self.setUp()
        signal_data_payload = {
            "input": self.upsert_signal_data_input
        }
        response = client.upsert_signal_data(signal_data_payload)
        result = response.get('data', {}).get('upsertSignalData', [])
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 5)  # Ensure 5 signals were upserted
        first_signal = result[0]
        self.assertEqual(first_signal['configurationId'], self.configurationDto['data']['createConfiguration']['id'])
        self.assertEqual(first_signal['messageId'], self.msgDto['data']['createMessage'][0]['id'])


    async def test_upsert(self):
        await self.setUp()
        signal_data_payload = {
            "input": self.upsert_signal_data_input
        }
        response = client.upsert_signal_data(signal_data_payload)
        response2 = client.upsert_signal_data(signal_data_payload)
        result = response.get('data', {}).get('upsertSignalData', [])
        result2 = response2.get('data', {}).get('upsertSignalData', [])
        self.assertIsInstance(result, list)
        self.assertIsInstance(result2, list)
        self.assertEqual(result[0]['configurationId'], result2[0]['configurationId'])
        self.assertEqual(result[0]['messageId'], result2[0]['messageId'])
        self.assertEqual(result[0]['name'], result2[0]['name'])
        self.assertEqual(result[0]['unit'], result2[0]['unit'])
        self.assertEqual(result[0]['paramType'], result2[0]['paramType'])


    async def test_should_upsert_really_large_payload(self):
        await self.setUp()
        signal_data_payload = {
            "input": self.upsert_signal_data_input_large
        }
        response = client.upsert_signal_data(signal_data_payload)
        result = response.get('data', {}).get('upsertSignalData', [])
        self.assertIsInstance(result, list)
        self.assertEqual(result[0]['configurationId'], self.configurationDto['data']['createConfiguration']['id'])
        self.assertEqual(result[0]['messageId'], self.msgDto['data']['createMessage'][0]['id'])

    async def test_can_insert_DID(self):
        await self.setUp()
        signal_data_payload = {
            "input":{
                "signals": [
                    {
                        "configurationId": self.configurationDto['data']['createConfiguration']['id'],
                        "messageId": self.msgDto['data']['createMessage'][0]['id'],
                        "data": self.signal_data,
                        "paramType": "NUMBER",
                        "signalType": "DID",
                        "unit": "km/h",
                        "name": "example_name"
                    }
                ]
            }
        }
        response = client.upsert_signal_data(signal_data_payload)
        result = response.get('data', {}).get('upsertSignalData', [])
        self.assertIsInstance(result, list)
        self.assertEqual(result[0]['configurationId'], self.configurationDto['data']['createConfiguration']['id'])
        self.assertEqual(result[0]['messageId'], self.msgDto['data']['createMessage'][0]['id'])

    async def test_can_insert_DMR(self):
        await self.setUp()
        signal_data_payload = {
            "input":{
                "signals": [
                    {
                        "configurationId": self.configurationDto['data']['createConfiguration']['id'],
                        "messageId": self.msgDto['data']['createMessage'][0]['id'],
                        "data": self.signal_data,
                        "paramType": "NUMBER",
                        "signalType": "DMR",
                        "unit": "km/h",
                        "name": "example_name"
                    }
                ]
            }
        }
        response = client.upsert_signal_data(signal_data_payload)
        result = response.get('data', {}).get('upsertSignalData', [])
        self.assertIsInstance(result, list)
        self.assertEqual(result[0]['configurationId'], self.configurationDto['data']['createConfiguration']['id'])
        self.assertEqual(result[0]['messageId'], self.msgDto['data']['createMessage'][0]['id'])

    async def test_can_insert_PID(self):
        await self.setUp()
        signal_data_payload = {
            "input":{
                "signals": [
                    {
                        "configurationId": self.configurationDto['data']['createConfiguration']['id'],
                        "messageId": self.msgDto['data']['createMessage'][0]['id'],
                        "data": self.signal_data,
                        "paramType": "NUMBER",
                        "signalType": "PID",
                        "unit": "km/h",
                        "name": "example_name"
                    }
                ]
            }
        }
        response = client.upsert_signal_data(signal_data_payload)
        result = response.get('data', {}).get('upsertSignalData', [])
        self.assertIsInstance(result, list)
        self.assertEqual(result[0]['configurationId'], self.configurationDto['data']['createConfiguration']['id'])
        self.assertEqual(result[0]['messageId'], self.msgDto['data']['createMessage'][0]['id'])

    async def test_can_insert_SIGNAL(self):
        await self.setUp()
        signal_data_payload = {
            "input":{
                "signals": [
                    {
                        "configurationId": self.configurationDto['data']['createConfiguration']['id'],
                        "messageId": self.msgDto['data']['createMessage'][0]['id'],
                        "data": self.signal_data,
                        "paramType": "NUMBER",
                        "signalType": "SIGNAL",
                        "unit": "km/h",
                        "name": "example_name"
                    }
                ]
            }
        }
        response = client.upsert_signal_data(signal_data_payload)
        result = response.get('data', {}).get('upsertSignalData', [])
        self.assertIsInstance(result, list)
        self.assertEqual(result[0]['configurationId'], self.configurationDto['data']['createConfiguration']['id'])
        self.assertEqual(result[0]['messageId'], self.msgDto['data']['createMessage'][0]['id'])

if __name__ == "__main__":
    unittest.main()
