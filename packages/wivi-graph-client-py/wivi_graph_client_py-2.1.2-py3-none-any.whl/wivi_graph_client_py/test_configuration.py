import unittest
from faker import Faker
from wivi_graph_client_py.client import GraphQL_Client

client = GraphQL_Client("http://localhost:8092/graphql")

class TestCreateConfiguration(unittest.TestCase):
    def setUp(self):
        self.fake = Faker()

    def test_simple(self):
        configuration = {
            "vehicleId": self.fake.random_int(),
            "fleetId": self.fake.random_int(),
            "organizationId": self.fake.random_int(),
            "deviceId": self.fake.random_int()
        }
        created_config = client.create_configuration({"input":configuration})
        upserted_data = created_config.get('data', {}).get('createConfiguration', {})
        self.assertIsInstance(upserted_data, dict)
        self.assertIn("id", upserted_data)
        self.assertEqual(upserted_data["vehicleId"], configuration["vehicleId"])
        self.assertEqual(upserted_data["fleetId"], configuration["fleetId"])
        self.assertEqual(upserted_data["organizationId"], configuration["organizationId"])
        self.assertEqual(upserted_data["deviceId"], configuration["deviceId"])

    def test_idempotent(self):
        configuration = {
            "vehicleId": self.fake.random_int(),
            "fleetId": self.fake.random_int(),
            "organizationId": self.fake.random_int(),
            "deviceId": self.fake.random_int()
        }

        created_config = client.create_configuration({"input":configuration})
        upserted_data = created_config.get('data', {}).get('createConfiguration', {})
        created_config2 = client.create_configuration({"input":configuration})
        upserted_data2 = created_config2.get('data', {}).get('createConfiguration', {})

        self.assertIsInstance(upserted_data, dict)
        self.assertIsInstance(upserted_data2, dict)
        self.assertIn("id", upserted_data)
        self.assertIn("id", upserted_data2)
        self.assertEqual(upserted_data["id"], upserted_data2["id"])

    def test_error_missing_vehicle_id(self):
        configuration = {
            "fleetId": self.fake.random_int(),
            "organizationId": self.fake.random_int(),
            "deviceId": self.fake.random_int()
        }

        try:
            response = client.create_configuration({"input": configuration})
            if response.get('errors'):
                error_message = response['errors'][0]['message']
                self.assertIn("Field \"vehicleId\" of required type \"Int!\" was not provided.", error_message)
            else:
                self.fail("Expected exception not raised")
        except Exception as e:
            self.assertIsInstance(e, AssertionError)
if __name__ == "__main__":
    unittest.main()
