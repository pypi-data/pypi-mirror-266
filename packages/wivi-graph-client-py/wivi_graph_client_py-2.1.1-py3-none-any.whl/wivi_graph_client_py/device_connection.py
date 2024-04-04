class Device_Connections_Query:
    get_device_connection_query = """
        query deviceConnection($input: DeviceConnectionFilterInput) {
            deviceConnection(input: $input) {
                configuration {
                    deviceId
                    vehicleId
                    organizationId
                    fleetId
                }
            }
        }
    """


class Device_Connections_Mutation:

    upsert_device_connection_mutation = '''
        mutation createDeviceConnection($input: CreateDeviceConnectionInput) {
            createDeviceConnection(input: $input) {
                configuration {
                    vehicleId
                    fleetId
                    organizationId
                    deviceId
                }
                bytesReceived
                bytesSent
                networkProvider
                network
                networkType
                version
                startTime
                endTime
                time
            }
        }
    '''

    delete_device_connection_mutation = '''
        mutation DeleteDeviceConnection($input: DeleteDeviceConnectionInput) {
            deleteDeviceConnection(input: $input) {
                DeviceConnection
            }
        }
    '''
