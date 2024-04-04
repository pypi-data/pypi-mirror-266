import unittest
from wivi_graph_client_py.client import GraphQL_Client
from datetime import datetime

client = GraphQL_Client("http://localhost:8092/graphql")

class TestUpsertGpsData(unittest.IsolatedAsyncioTestCase):
    async def setUp(self):
        self.configuration = {
            "input": {
                "deviceId": 1,
                "fleetId": 1,
                "organizationId": 1,
                "vehicleId": 1
            }
        } 
        self.configurationDto = client.create_configuration(self.configuration)
        self.gps_data = {
            "time": datetime.utcnow().isoformat(),
            "accuracy": 10,
            "altitude": 100,
            "latitude": 37.7749,
            "longitude": -122.4194,
            "bearing": "North",
            "speed": 50,
            "available": {
                "accuracy": True,
                "time": True,
                "date": True,
                "latlon": True,
                "speed": True,
                "altitude": True,
                "bearing": True
            }
        }
        self.upsert_gps_data_input = {
            "configurationId": self.configurationDto['data']['createConfiguration']['id'],
            "data": [self.gps_data]
        }
    
    async def test_create(self):
        await self.setUp()
        result = client.upsert_gps({"input": self.upsert_gps_data_input})
        upserted_data = result.get('data', {}).get('upsertGpsData', {})
        config_data = self.configurationDto.get('data', {}).get('createConfiguration', {})
        
        self.assertIsInstance(upserted_data, dict)
        self.assertIsInstance(upserted_data.get('id'), int)
        self.assertEqual(upserted_data.get('deviceId'), config_data.get('deviceId'))
        self.assertEqual(upserted_data.get('vehicleId'), config_data.get('vehicleId'))
        self.assertEqual(upserted_data.get('organizationId'), config_data.get('organizationId'))
        self.assertEqual(upserted_data.get('fleetId'), config_data.get('fleetId'))

if __name__ == "__main__":
    unittest.main()
