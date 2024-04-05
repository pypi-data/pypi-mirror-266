import unittest
from faker import Faker
from wivi_graph_client_py.client import GraphQL_Client

class TestCreateDeviceConnection(unittest.IsolatedAsyncioTestCase):
    async def setUp(self):
        self.fake = Faker()
        self.client = GraphQL_Client("http://localhost:8092/graphql")
        self.configurationDto = None

        # Generate fake configuration data
        configuration = {
            "vehicleId": self.fake.random_int(),
            "fleetId": self.fake.random_int(),
            "organizationId": self.fake.random_int(),
            "deviceId": self.fake.random_int()
        }
        
        # Create configuration and store the response
        response = self.client.create_configuration({"input": configuration})
        self.configurationDto = response.get('data', {}).get('createConfiguration', {})

    async def test_basic(self):
        await self.setUp()
        device_connection = {
            "endTime":  self.fake.date_time_this_decade().isoformat(),
            "startTime":  self.fake.date_time_this_decade().isoformat(),
            "time":  self.fake.date_time_this_decade().isoformat(),
            "bytesReceived": str(self.fake.random_int()),
            "bytesSent": str(self.fake.random_int()),
            "network": self.fake.ipv4(),
            "networkProvider": self.fake.ipv4(),
            "networkType": self.fake.ipv4(),
            "version": self.fake.ipv4(),
            "configuration":  {
                 "deviceId": self.configurationDto.get('deviceId'),
                "fleetId": self.configurationDto.get('fleetId'),
                "organizationId": self.configurationDto.get('organizationId'),
                "vehicleId": self.configurationDto.get('vehicleId')
            }
        }
        response = self.client.create_device_connection({"input":device_connection})
        results = response.get('data', {}).get('createDeviceConnection', {})
        self.assertIsInstance(results.get('bytesReceived'), str)
        self.assertIsInstance(results.get('bytesSent'), str)
        self.assertIsInstance(results.get('configuration').get('deviceId'), int)
        self.assertIsInstance(results.get('configuration').get('fleetId'), int)
        self.assertIsInstance(results.get('configuration').get('organizationId'), int)
        self.assertIsInstance(results.get('configuration').get('vehicleId'), int)
        self.assertIsInstance(results.get('endTime'), str)
        self.assertIsInstance(results.get('time'), str)
        self.assertIsInstance(results.get('version'), str)
        self.assertIsInstance(results.get('startTime'), str)

if __name__ == "__main__":
    unittest.main()
