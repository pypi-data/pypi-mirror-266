import unittest
from faker import Faker
from wivi_graph_client_py.client import GraphQL_Client

class TestUpsertDeviceVersion(unittest.TestCase):
    async def asyncSetUp(self):
        self.fake = Faker()
        self.client = GraphQL_Client("http://localhost:8092/graphql")
        self.configurationDto = None
        configuration = {
            "vehicleId": self.fake.random_int(),
            "fleetId": self.fake.random_int(),
            "organizationId": self.fake.random_int(),
            "deviceId": self.fake.random_int()
        }
        response =  self.client.create_configuration({"input": configuration})
        self.configurationDto = response.get('data', {}).get('createConfiguration', {})

    async def test_create_device_version(self):
        await self.asyncSetUp()
        device_version = {
            "configurationId": self.configurationDto.get('id'),
            "data": [{
                "time": self.fake.date_time_this_decade(),
                "versions": [{
                    "name": self.fake.word(),
                    "version": self.fake.word()
                } for _ in range(3)]
            } for _ in range(3)]
        }
        response = self.client.upsert_version({"input": device_version})
        print(response)
        results = response.get('data', {}).get('upsertDeviceVersion', {})

        self.assertIsInstance(results, dict)

if __name__ == "__main__":
    unittest.main()
