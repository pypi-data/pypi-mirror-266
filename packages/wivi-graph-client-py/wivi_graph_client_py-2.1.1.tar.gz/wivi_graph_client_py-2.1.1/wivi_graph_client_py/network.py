class Network_Query:
    get_network_query = """
        query GetNetworks($input: NetworkFilterArgs) {
            network(input: $input) {
                id
                name
            }
        }
    """
