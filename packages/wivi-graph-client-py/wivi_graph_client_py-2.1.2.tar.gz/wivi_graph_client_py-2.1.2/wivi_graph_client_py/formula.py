class Formula_Query:
    load_formula_query = """
        query LoadFormula($input: LoadFormulaArgs) {
            formula(input: $input) {
                id
                name
                source
                unit
                time
                formula
                fun
            }
        }
    """

    calculate_formula_query = '''
        query CalculateFormula($input: CalculateFormulaArgs) {
            calculateFormula(input: $input) {
                vehicleId
                data {
                    value
                    time
                }
            }
        }
    '''

class Formula_Mutation:
    upsert_formula_mutation = """
        mutation UpsertFormula($input: UpsertFormulaInput) {
            upsertFormula(input: $input) {
                id
                name
                source
                unit
                time
                formula
                fun
            }
        }
    """

    upsert_formula_constant_mutation = """
        mutation UpsertFormulaConstant($input: UpsertFormulaConstantInput) {
            upsertFormulaConstant(input: $input) {
                id
                name
                value
            }
        }
    """

