from client import GraphQL_Client

if __name__ == "__main__":
    endpoint = "http://0.0.0.0:8080/graphql"

    client = GraphQL_Client(endpoint)
    variables = {
        "input": {
            "configurationId": 3,
            "info": [
                {
                    "time": "2022-10-09T00:00:00Z",
                    "stats": [
                        {"name": "DevInfoTest", "svalue": "100Km/h", "value": 100}
                    ],
                }
            ],
        }
    }
    response = client.create_device_info(variables)


