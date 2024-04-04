import unittest
from faker import Faker
from wivi_graph_client_py.client import GraphQL_Client

class TestCreateFailedProcessing(unittest.TestCase):
    def setUp(self):
        self.fake = Faker()
        self.client = GraphQL_Client("http://localhost:8092/graphql")
        self.configurationDto = None

        # Create a configuration and store its DTO for later use
        configuration = {
            "vehicleId": self.fake.random_int(),
            "fleetId": self.fake.random_int(),
            "organizationId": self.fake.random_int(),
            "deviceId": self.fake.random_int()
        }
        response = self.client.create_configuration({"input": configuration})
        self.configurationDto = response.get('data', {}).get('createConfiguration', {}).get('configuration', {})

    async def test_basic(self):
        await self.setUp()
        print(self.configurationDto)
        failed_processing = {
            "configuration": {
                "deviceId": self.configurationDto.get('deviceId'),
                "fleetId": self.configurationDto.get('fleetId'),
                "organizationId": self.configurationDto.get('organizationId'),
                "vehicleId": self.configurationDto.get('vehicleId')
            },
            "dbExists": self.fake.boolean(),
            "pipelineStatus": self.fake.random_element(["FINISHED", "STARTED", "NEW","CANCELLED","LATER","ERROR","NOT_FOUND"]),
            "uploadId": self.fake.random_int(),
            "xmlExists": self.fake.boolean()
        }
        response = self.client.upsert_failed_processing({"input": failed_processing})
        print(response)
        results = response.get('data', {}).get('upsertFailedProcessing', {})

        self.assertIsInstance(results, dict)
        self.assertIsInstance(results.get('configuration'), dict)
        self.assertEqual(results['configuration']['deviceId'], failed_processing['configuration']['deviceId'])
        self.assertEqual(results['configuration']['fleetId'], failed_processing['configuration']['fleetId'])
        self.assertEqual(results['configuration']['organizationId'], failed_processing['configuration']['organizationId'])
        self.assertEqual(results['configuration']['vehicleId'], failed_processing['configuration']['vehicleId'])
        self.assertIsInstance(results.get('dbExists'), bool)
        self.assertIsInstance(results.get('pipelineStatus'), str)
        self.assertIsInstance(results.get('uploadId'), str)
        self.assertIsInstance(results.get('xmlExists'), bool)

if __name__ == "__main__":
    unittest.main()
