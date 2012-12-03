"""Logic for interpreting user provided values.

@author: Sam Pottinger
@license: GNU GPL v2
"""

def safe_int_interpret(target):
    """Interpret a value as an integer.

    @param target: The value to interpret.
    @return: Integer parsed or None if could not be parsed.
    @rtype: int
    """
    try:
        return int(target)
    except ValueError:
        return None

def safe_float_interpret(target):
    """Interpret a value as an floating point value.

    @param target: The value to interpet.
    @return: Float parsed or None if could not be parsed.
    @rtype: float
    """
    try:
        return float(target)
    except ValueError:
        return None

def operator_to_str(operator):
    """Convert a operator abreviation to a code description of it.

    @param operator: The abreviation to convert (ex. "eq")
    @type operator: str
    @return: The code description of operator (ex. "==")
    @rtype: str
    """
    if operator == "eq":
        return "=="
    elif operator == "lt":
        return "<"
    elif operator == "gt":
        return ">"
    elif operator == "neq":
        return "!="
    elif operator == "lteq":
        return "<="
    elif operator == "gteq":
        return ">="
    else:
        return "?"

def filter_to_str(target):
    """Convert a filter to a SQL clause.

    @param target: The filter to convert.
    @type target: models.Filter
    @return: The SQL clause ready string representation of the given filter.
    @rtype: str
    """
    operator_str = operator_to_str(target.operator)
    return "%s %s %s" % (target.field, operator_str, target.operand)