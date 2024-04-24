import ast
import operator
import sys
from typing import Any, Dict, Union


Numeric = Union[int, float]
VariablesType = Dict[str, Numeric]

OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
    ast.Lt: operator.lt,
    ast.LtE: operator.le,
    ast.Gt: operator.gt,
    ast.GtE: operator.ge,
    ast.And: operator.and_,
    ast.Or: operator.or_,
    ast.Not: operator.not_,
}


def eval_expr(expr: str, variables: Dict[str, Numeric]) -> Union[bool, Any]:
    """
    Evaluate a boolean expression string `expr` with given variables.

    Args:
        expr (str): The boolean expression string.
        **variables: Keyword arguments where keys are variable names (as strings)
            and values are numeric values (int or float).

    Returns:
        Union[bool, Any]: The result of evaluating the boolean expression.
    """
    expr_tree = ast.parse(expr, mode='eval')
    return _eval(expr_tree.body, variables)


def _eval(node: ast.AST, variables: Dict[str, Numeric]) -> Union[bool, Any]:
    """
    Recursively evaluate an abstract syntax tree node representing a boolean expression.

    Args:
        node (ast.AST): The AST node to evaluate.
        variables (Dict[str, VariableValue]): Dictionary of variables and their values.

    Returns:
        Union[bool, Any]: The result of evaluating the node.
    """
    # TODO: Add support for more node types
    if isinstance(node, ast.Constant):
        # Handle constant nodes (boolean, numeric, etc.)
        return node.value

    if isinstance(node, ast.Name):
        if node.id in variables:
            return variables[node.id]
        raise NameError(f"Variable '{node.id}' is not defined")

    if isinstance(node, ast.Compare):
        left_value = _eval(node.left, variables)
        right_value = _eval(node.comparators[0], variables)
        op_type = type(node.ops[0])
        return OPERATORS[op_type](left_value, right_value)  # type: ignore

    if isinstance(node, ast.BoolOp):
        left_value = _eval(node.values[0], variables)
        right_value = _eval(node.values[1], variables)
        op_type = type(node.op)  # type: ignore
        return OPERATORS[op_type](left_value, right_value)  # type: ignore

    if isinstance(node, ast.BinOp):
        left_value = _eval(node.left, variables)
        right_value = _eval(node.right, variables)
        op_type = type(node.op)  # type: ignore
        return OPERATORS[op_type](left_value, right_value)  # type: ignore

    if isinstance(node, ast.UnaryOp):
        operand_value = _eval(node.operand, variables)
        op_type = type(node.op)  # type: ignore
        return OPERATORS[op_type](operand_value)  # type: ignore

    raise ValueError(f'Unsupported node type: {type(node).__name__}')


if __name__ == '__main__':
    # Example usage:
    variables: Dict[str, Numeric] = {'x': 42, 'y': 10, 'z': 5.5}

    result = eval_expr('x + y >= z and (z + 60) > 12', variables)
    sys.stdout.write(str(result) + '\n')
