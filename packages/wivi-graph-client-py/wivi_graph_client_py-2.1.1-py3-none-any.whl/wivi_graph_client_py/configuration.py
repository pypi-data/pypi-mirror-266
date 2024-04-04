class Configuration_Query:
    get_configuration_query = """
        query configurations($input: ConfigurationFilterInput) {
            configuration(input: $input) {
                id
                deviceId
                fleetId
                organizationId
                vehicleId
            }
        }
    """
    configurationsMetaQuery = """
        query configurations($input: ConfigurationFilterInput) {
            configuration(input: $input) {
                id
                deviceId
                fleetId
                organizationId
                vehicleId
                signals {
                    name
                }
                ecus {
                    name
                }
                messages {
                    name
                }
                network {
                    name
                }
            }
        }
    """
class Configuration_Mutation:
    create_configuration_mutation = """
        mutation createConfiguration($input: CreateConfigurationInput!) {
            createConfiguration(input: $input) {
                id
                deviceId
                vehicleId
                organizationId
                fleetId
            }
    """
