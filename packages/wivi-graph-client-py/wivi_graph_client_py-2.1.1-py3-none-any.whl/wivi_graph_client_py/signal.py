class Signals_Query:
    get_signals_query = """
        query signals($input: SignalFilterArgs) {
            signal(input: $input) {
                name
                unit
                paramType
                paramId
                messageName
                configurationId
                messageId
                networkName
            }
        }
    """

    get_signals_data_query = """
        query signalData($input: SignalDataFilterArgs) {
            signalData(input: $input) {
                vehicleId
                data {
                    value
                    signalType
                    time
                    signalId
                    stateId
                    svalue
                }
            }
        }
    """

class Signals_Mutation:
    upsert_signal_data_mutation = """
        mutation UpsertSignalData($input: UpsertSignalDataArgs) {
            upsertSignalData(input: $input) {
                configurationId
                messageId
                messageName
                name
                paramType
                unit
            }
        }
    """

    delete_signal_data_mutation = """
        mutation DeleteSignalData($input: DeleteSignalDataInput) {
            deleteSignalData(input: $input) {
               configurations
            }
        }
    """

