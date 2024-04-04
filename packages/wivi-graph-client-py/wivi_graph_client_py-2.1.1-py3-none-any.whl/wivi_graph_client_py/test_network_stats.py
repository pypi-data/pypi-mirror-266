import unittest
from faker import Faker
from wivi_graph_client_py.client import GraphQL_Client
from datetime import datetime

client = GraphQL_Client("http://localhost:8092/graphql")

class TestCreateNetworkStats(unittest.TestCase):
    def setUp(self):
        self.fake = Faker()
        self.network_stats = {
            "errorMessages": self.fake.random_int(),
            "longMessageParts": self.fake.random_int(),
            "matchedMessages": self.fake.random_int(),
            "maxTime":  datetime.utcnow().isoformat(), 
            "minTime":  datetime.utcnow().isoformat(),
            "name": self.fake.word(),
            "rate": self.fake.random_int(),
            "totalMessages": self.fake.random_int(),
            "unmatchedMessages": self.fake.random_int(),
            "uploadId": self.fake.random_int(),
            "vehicleId": self.fake.random_int()
        }

    def test_basic(self):
        self.setUp()
        response = client.create_network_stats({"input":self.network_stats})
        results = response.get('data', {}).get('createNetworkStats', [])
        
        self.assertIsInstance(results, dict)
        self.assertIn("name", results)
        self.assertIn("vehicleId", results)
        self.assertIn("uploadId", results)
        self.assertIn("totalMessages", results)
        self.assertIn("matchedMessages", results)
        self.assertIn("unmatchedMessages", results)
        self.assertIn("errorMessages", results)
        self.assertIn("longMessageParts", results)
        self.assertIn("minTime", results)
        self.assertIn("maxTime", results)
        self.assertIn("rate", results)

        self.assertEqual(results["name"], self.network_stats["name"])
        self.assertEqual(results["vehicleId"], self.network_stats["vehicleId"])
        self.assertEqual(results["uploadId"], self.network_stats["uploadId"])
        self.assertEqual(results["totalMessages"], self.network_stats["totalMessages"])
        self.assertEqual(results["matchedMessages"], self.network_stats["matchedMessages"])
        self.assertEqual(results["unmatchedMessages"], self.network_stats["unmatchedMessages"])
        self.assertEqual(results["errorMessages"], self.network_stats["errorMessages"])
        self.assertEqual(results["longMessageParts"], self.network_stats["longMessageParts"])
        self.assertEqual(results["rate"], self.network_stats["rate"])

if __name__ == "__main__":
    unittest.main()
