class Dtc_Query:
    get_dtc_query = """
        query dtcData($input: DtcDataFilterInput) {
            dtcData(input: $input) {
                vehicleId
                dtcs {
                    messageName
                    description
                    uploadId
                    domain
                    code
                    status
                    dtcId
                    value
                    count
                    failure
                    occurances {
                        time
                        state
                        snapshots {
                            time
                            bytes
                        }
                        extensions {
                            time
                            bytes
                        }
                    }
                }
            }
        }
    """

class Dtc_Mutation:
    upsert_dtc_mutation = """
        mutation UpsertDtcData($input: UpsertDtcDataInput) {
            upsertDtcData(input: $input) {
                configurationId
                messageId
            }
        }
    """

    delete_dtc_mutation = """
        mutation DeleteDtcData($input: DeleteDtcDataInput) {
            deleteDtcData(input: $input) {
                configurations
            }
        }
    """
