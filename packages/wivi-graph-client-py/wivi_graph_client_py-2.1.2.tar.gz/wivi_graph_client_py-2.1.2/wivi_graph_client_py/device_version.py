class Device_Version_Query:
    get_device_version_query = """
        query deviceVersion($input: DeviceVersionFilterInput) {
            deviceVersion(input: $input) {
                vehicleId
                deviceVersion {
                    name
                    time
                    value
                }
            }
        }
    """
class Device_Version_Mutation:
    upsert_device_version_mutation = '''
        mutation UpsertDeviceVersion($input: UpsertDeviceVersionInput) {
            upsertDeviceVersion(input: $input) {
                configurationId
            }
        }
    '''

    delete_device_version_mutation = '''
        mutation DeleteDeviceVersion($input: DeleteDeviceVersionInput) {
            deleteDeviceVersion(input: $input) {
                configurations
            }
        }
    '''