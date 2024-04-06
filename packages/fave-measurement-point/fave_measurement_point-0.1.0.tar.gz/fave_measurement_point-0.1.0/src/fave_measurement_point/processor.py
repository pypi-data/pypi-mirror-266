from fave_measurement_point.formants import FormantArray
import re
import functools

def rgetattr(obj, 
             attr : str, 
             *args):
    """_gets object attribute from string_

    Args:
        obj (_type_): _object_
        attr (_str_): attribute path attr.attr.attr
    """
    def _getattr(obj, attr: str):
        try:
            return getattr(obj, attr, *args)
        except:
            return ''
    return functools.reduce(_getattr, [obj] + attr.split('.'))

def build_expressions()->list[str]:
    """Build a list of valid landmark expressions

    Returns:
        (list[str]): List of landmark regexes
    """
    formant_expr = r"f\d"
    anchors = ["min", "max"]
    times = ["time", "rel_time", "prop_time"]
    
    all_exprs = [
        formant_expr + "." + anchor + "." + time
        for anchor in anchors
        for time in times
    ]

    return all_exprs


def find_vars(expression:str) -> list[str]:
    """Find landmark variables in expression

    Args:
        expression (str):
            An expression defining a landmark location

    Returns:
        (list[str]): List of landmark variables
    """
    all_vars = build_expressions()

    vars = [
        match
        for expr in all_vars
        for match in re.findall(expr, expression)
        if re.search(expr, expression)
    ]

    return vars

def inject_values(
        expression:str,
        formants: FormantArray
        )->str:
    """Replace landmark variable names with
    numeric strings.

    Args:
        expression (str): 
            A landmark expression
        formants (FormantArray): 
            The formant array from which to get 
            the numerc values

    Returns:
        (str): The numeric string
    """
    vars = find_vars(expression)
    for var in vars:
        numeral = rgetattr(formants, var)
        expression = expression.replace(var, str(numeral))

    return expression


def evaluate_math(x:str) -> bool:
    """Ensure the landmark expression is *only*
    valid mathematical expressions.

    Args:
        x (str): The numeric string

    Returns:
        (bool):
            If the string is only valid math, True. Else, False.
    """
    matches = re.match(r'^[\d+-/*()\s]+$', x)
    if matches:
        return True
    return False


def parse_expression(
        expression:str,
        formants: FormantArray
        ) -> float:
    """Parse a landmark expression and return
    the resulting numeric value.

    Args:
        expression (str): A landmark expression
        formants (FormantArray): 
            The formant array with which
            to evaluate the expression

    Returns:
        (float): The resulting value
    """
    
    math_string = inject_values(expression, formants)

    is_math = evaluate_math(math_string)

    if not is_math:
        raise Exception(f"The expression {expression} contains "\
                        "invalid math or landmark variables")
    
    result = eval(math_string, {})

    return result
    

