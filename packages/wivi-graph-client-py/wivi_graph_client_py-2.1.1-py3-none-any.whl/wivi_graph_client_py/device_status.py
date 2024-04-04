class Device_Status_Query:
    get_device_status_query = """
        query GetDeviceStatus($input: DeviceStatusFilterInput) {
            DeviceStatus(input: $input) {
                vehicleId
                DeviceStatusData {
                    name
                    data {
                        time
                        svalue
                        value
                    }
                }
            }
        }
    """

class Device_Status_Mutation:
    create_device_status_mutation = '''
        mutation createDeviceStatus($input: CreateDeviceStatusInput) {
            createDeviceStatus(input: $input) {
                configuration {
                    deviceId
                    vehicleId
                    organizationId
                    fleetId
                }
            }
        }
    '''

    delete_device_status_mutation = '''
        mutation DeleteDeviceStatus($input: DeleteDeviceStatusInput) {
            deleteDeviceStatus(input: $input) {
                configurations
            }
        }
    '''
