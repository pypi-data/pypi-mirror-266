class AfasFilter:
    EQUAL_TO = 1
    GREATER_THAN_OR_EQUAL_TO = 2
    LESS_THAN_OR_EQUAL_TO = 3
    GREATER_THAN = 4
    LESS_THAN = 5
    CONTAINS_TEXT = 6
    NOT_EQUAL_TO = 7
    IS_EMPTY = 8
    IS_NOT_EMPTY = 9
    STARTS_WITH = 10
    DOES_NOT_CONTAIN_TEXT = 11
    DOES_NOT_START_WITH = 12
    ENDS_WITH = 13
    DOES_NOT_END_WITH = 14
    QUICK_FILTER = 15

    def __init__(self, field: str, value: any, operator: int = 1):
        """
        Initializes an instance of the AfasFilter class.

        Args:
            field (str): The field to filter on.
            value (any): The value(s) to filter on. Can be a single value or a list of values.
            operator (int, optional): The operator to use for the filter. Defaults to EQUAL_TO.

        Raises:
            ValueError: If the operator is invalid.
            ValueError: If the value is a list but the operator is not a list.
            ValueError: If the length of the value and operator lists are not equal.
        """

        # If value is a list, operator should be a list too and of equal length
        if isinstance(value, list):
            if not isinstance(operator, list):
                raise ValueError("Operator should be a list if value is a list")
            if len(value) != len(operator):
                raise ValueError("Value and operator should be of equal length")

        # Check if operators are valid
        if isinstance(operator, list):
            for op in operator:
                if not self.operator_is_valid(op):
                    raise ValueError("Invalid operator")
        else:
            if not self.operator_is_valid(operator):
                raise ValueError("Invalid operator")
        
        
        # Set the filter properties
        self.field = field
        self.value = value
        self.operator = operator

    def operator_is_valid(self, operator):
        if operator not in [
            self.EQUAL_TO,
            self.GREATER_THAN_OR_EQUAL_TO,
            self.LESS_THAN_OR_EQUAL_TO,
            self.GREATER_THAN,
            self.LESS_THAN,
            self.CONTAINS_TEXT,
            self.NOT_EQUAL_TO,
            self.IS_EMPTY,
            self.IS_NOT_EMPTY,
            self.STARTS_WITH,
            self.DOES_NOT_CONTAIN_TEXT,
            self.DOES_NOT_START_WITH,
            self.ENDS_WITH,
            self.DOES_NOT_END_WITH,
            self.QUICK_FILTER
        ]:
            return False
        
        return True

def afas_filters_to_query(filters: list[AfasFilter]):
    """
    Converts a list of AfasFilter objects to a query string.

    Args:
        filters (list[AfasFilter]): A list of AfasFilter objects.

    Returns:
        str: The query string.
    """
    OR_SEPARATOR = "%3B"
    AND_SEPARATOR = "%2C"

    # Initialize variables
    filterfieldids = ""
    filtervalues = ""
    operatortypes = ""

    # Add filters to the query
    for filter in filters:

        if isinstance(filter.value, list):
            # Add OR Statements to the query
            for i in range(len(filter.value)):
                filterfieldids += f'{filter.field}{OR_SEPARATOR}'
                filtervalues += f'{filter.value[i]}{OR_SEPARATOR}'
                operatortypes += f'{filter.operator[i]}{OR_SEPARATOR}'

            # Remove final %3B
            filterfieldids = filterfieldids[:-len(OR_SEPARATOR)]
            filtervalues = filtervalues[:-len(OR_SEPARATOR)]
            operatortypes = operatortypes[:-len(OR_SEPARATOR)]
        else:
            filterfieldids += f'{filter.field}'
            filtervalues += f'{filter.value}'
            operatortypes += f'{filter.operator}'

        # Add separator
        filterfieldids += AND_SEPARATOR
        filtervalues += AND_SEPARATOR
        operatortypes += AND_SEPARATOR

    # Remove final separator
    filterfieldids = filterfieldids[:-len(AND_SEPARATOR)]
    filtervalues = filtervalues[:-len(AND_SEPARATOR)]
    operatortypes = operatortypes[:-len(AND_SEPARATOR)]
    
    # Add filters to the URL
    query = f'&filterfieldids={filterfieldids}&filtervalues={filtervalues}&operatortypes={operatortypes}'

    return query