class GPS_Query:
    get_gps_query = """
        query gpsData($input: GpsDataFilterArgs) {
            gpsData(input: $input) {
                vehicleId
                gpsData {
                    time
                    latitude
                    longitude
                    accuracy
                    altitude
                }
            }
        }
"""

class GPS_Mutation:
    upsert_gps_mutation = """
        mutation UpsertGpsData($input: UpsertGpsDataInput) {
            upsertGpsData(input: $input) {
                deviceId
                fleetId
                vehicleId
                id
                organizationId
            }
        }
    """

    delete_gps_mutation = '''
        mutation DeleteGPSData($input: DeleteGPSDataInput) {
            deleteGpsData(input: $input) {
               
            }
        }
    '''
