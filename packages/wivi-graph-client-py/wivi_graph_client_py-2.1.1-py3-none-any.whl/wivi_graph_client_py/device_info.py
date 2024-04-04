class Device_Info_Query:
    get_device_info_query = """
        query GetDeviceInfo($input: DeviceInfoFilterInput) {
            deviceInfo(input: $input) {
                vehicleId
                deviceInfoData {
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

class Device_Info_Mutation:
    create_device_info_mutation = '''
        mutation CreateDeviceStatus($input: CreateDeviceStatusInput) {
            CreateDeviceStatus(input: $input) {
                configurationId
            }
        }
    '''

    delete_device_info_mutation = '''
        mutation deleteDeviceStatus($input: DeleteDeviceStatusInput) {
            deleteDeviceInfo(input: $input) {
                configurations
        }
    '''
