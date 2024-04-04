class FailProcessingQuery:
    get_failed_processing_query = """
        query failedProcessing($input: FailedProcessingFilterInput) {
            failedProcessing(input: $input) {
                configuration {
                    id
                    deviceId
                    fleetId
                    organizationId
                    vehicleId
                }
                dbExists
                pipelineStatus
                uploadId
                xmlExists
            }
        }
    """

class FailProcessingMutation:
    upsert_failed_processing_mutation = '''
        mutation upsertFailedProcessing($input: UpsertFailedProcessingInput) {
            upsertFailedProcessing(input: $input) {
                configuration {
                    id
                    vehicleId
                    fleetId
                    organizationId
                    vehicleId
                }
                uploadId
                dbExists
                xmlExists
                pipelineStatus
            }
        }
    '''

    delete_failed_processing_mutation = '''
        mutation DeleteFailedProcessing($input: DeleteFailedProcessingInput) {
            deleteFailedProcessing(input: $input) {
                configurations
            }
        }
    '''