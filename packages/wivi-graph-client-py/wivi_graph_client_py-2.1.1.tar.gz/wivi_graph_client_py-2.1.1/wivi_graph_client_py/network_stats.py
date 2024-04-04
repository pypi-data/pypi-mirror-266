class Network_Stats_Query:
    get_network_stats_query = """
        query networkStatusQuery($input: NetworkStatsFilter) {
            networkStats(input: $input) {
                errorMessages
                longMessageParts
                matchedMessages
                maxTime
                minTime
                name
                uploadId
                vehicleId
                unmatchedMessages
                totalMessages
            }
        }
    """

class Network_Stats_Mutation:
    create_network_stats_mutation = """
        mutation createNetworkStats($input: CreateNetworkStatsInput!) {
            createNetworkStats(input: $input) {
                name
                vehicleId
                uploadId
                totalMessages
                matchedMessages
                unmatchedMessages
                errorMessages
                longMessageParts
                minTime
                maxTime
                rate
            }
        }
    """
