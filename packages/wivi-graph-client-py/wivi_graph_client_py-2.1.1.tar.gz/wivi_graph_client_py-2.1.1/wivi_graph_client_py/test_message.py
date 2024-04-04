import unittest
from faker import Faker
from wivi_graph_client_py.client import GraphQL_Client

class TestCreateMessage(unittest.TestCase):
    def setUp(self):
        self.fake = Faker()
        self.client = GraphQL_Client("http://localhost:8092/graphql")
        self.messages = {
            "messages": [{
                "uploadId": self.fake.random_int(),
                "networkName": str(self.fake.random_number(digits=3)),
                "ecuId": self.fake.word(),
                "name": self.fake.word(),
                "requestCode": self.fake.word(),
                "arbId": str(self.fake.random_number(digits=3))
            }]
        }

    def test_simple(self):
        response = self.client.create_message({"input": self.messages})
        results = response.get('data', {}).get('createMessage', [])

        self.assertIsInstance(results, list)

    def test_idempotent(self):
        response = self.client.create_message({"input": self.messages})
        results = response.get('data', {}).get('createMessage', [])

        response2 = self.client.create_message({"input": self.messages})
        results2 = response2.get('data', {}).get('createMessage', [])
        self.assertIsInstance(results, list)
        self.assertIsInstance(results2, list)
        self.assertEqual(results[0]['id'], results2[0]['id'])

    def test_idempotent_across_arbId(self):
        self.messages['messages'][0]['arbId'] = None  # Set arbId to None to simulate missing value
        response = self.client.create_message({"input": self.messages})
        results = response.get('data', {}).get('createMessage', [])

        response2 = self.client.create_message({"input": self.messages})
        results2 = response2.get('data', {}).get('createMessage', [])

        self.assertIsInstance(results, list)
        self.assertIsInstance(results2, list)
        self.assertEqual(results[0]['id'], results2[0]['id'])

if __name__ == "__main__":
    unittest.main()
