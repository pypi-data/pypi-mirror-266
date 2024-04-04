class Ecu_Query:
    get_ecu_query = """
        query GetECUData($input: ECUFilterArgs) {
            ecu(input: $input) {
                id
                code
                name
            }
        }
    """
