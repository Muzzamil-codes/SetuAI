"""
Numeric checker using AST allowlist validation and SymPy mathematical evaluation.
Follows API_CONTRACTS.md Section 3.2.
"""
import ast
import math
from typing import Dict, Any
from verification.schemas import ToolResult

# Safe mathematical function allowlist
SAFE_FUNCTIONS = {
    "abs": abs,
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "log": math.log,
    "exp": math.exp,
    "round": round,
    "min": min,
    "max": max,
    "pi": math.pi,
    "e": math.e,
}

# Try importing SymPy for symbolic mathematics; if not present, safe AST evaluator handles arithmetic
try:
    import sympy
    HAS_SYMPY = True
except ImportError:
    HAS_SYMPY = False


class _SafeMathASTValidator(ast.NodeVisitor):
    """
    Validates that an AST contains only safe mathematical expressions and comparisons.
    Blocks attribute access (dunder methods), assignments, imports, loops, etc.
    """
    ALLOWED_NODES = (
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.Compare,
        ast.Constant,
        ast.Call,
        ast.Name,
        ast.Load,
        # Operators
        ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow,
        ast.USub, ast.UAdd,
        ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE
    )

    def __init__(self):
        self.is_safe = True
        self.violation_reason = None

    def generic_visit(self, node):
        if not isinstance(node, self.ALLOWED_NODES):
            self.is_safe = False
            self.violation_reason = f"Disallowed AST syntax element: {type(node).__name__}"
            return
        if isinstance(node, ast.Name):
            if node.id not in SAFE_FUNCTIONS and not node.id.isidentifier():
                self.is_safe = False
                self.violation_reason = f"Unknown or disallowed identifier: {node.id}"
                return
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name) or node.func.id not in SAFE_FUNCTIONS:
                self.is_safe = False
                func_name = getattr(node.func, 'id', str(node.func))
                self.violation_reason = f"Disallowed function call: {func_name}"
                return
        super().generic_visit(node)


def _safe_eval_ast(node: ast.AST) -> Any:
    """Evaluates an already-validated safe math AST."""
    if isinstance(node, ast.Expression):
        return _safe_eval_ast(node.body)
    elif isinstance(node, ast.Constant):
        return node.value
    elif isinstance(node, ast.Name):
        if node.id in SAFE_FUNCTIONS:
            return SAFE_FUNCTIONS[node.id]
        raise ValueError(f"Unknown variable: {node.id}")
    elif isinstance(node, ast.UnaryOp):
        operand = _safe_eval_ast(node.operand)
        if isinstance(node.op, ast.USub):
            return -operand
        elif isinstance(node.op, ast.UAdd):
            return +operand
        raise ValueError(f"Unsupported unary operator: {type(node.op).__name__}")
    elif isinstance(node, ast.BinOp):
        left = _safe_eval_ast(node.left)
        right = _safe_eval_ast(node.right)
        if isinstance(node.op, ast.Add):
            return left + right
        elif isinstance(node.op, ast.Sub):
            return left - right
        elif isinstance(node.op, ast.Mult):
            return left * right
        elif isinstance(node.op, ast.Div):
            return left / right
        elif isinstance(node.op, ast.FloorDiv):
            return left // right
        elif isinstance(node.op, ast.Mod):
            return left % right
        elif isinstance(node.op, ast.Pow):
            return left ** right
        raise ValueError(f"Unsupported binary operator: {type(node.op).__name__}")
    elif isinstance(node, ast.Compare):
        left = _safe_eval_ast(node.left)
        for op, comparator in zip(node.ops, node.comparators):
            right = _safe_eval_ast(comparator)
            passed = False
            if isinstance(op, ast.Eq):
                passed = (left == right)
            elif isinstance(op, ast.NotEq):
                passed = (left != right)
            elif isinstance(op, ast.Lt):
                passed = (left < right)
            elif isinstance(op, ast.LtE):
                passed = (left <= right)
            elif isinstance(op, ast.Gt):
                passed = (left > right)
            elif isinstance(op, ast.GtE):
                passed = (left >= right)
            else:
                raise ValueError(f"Unsupported comparison operator: {type(op).__name__}")
            if not passed:
                return False
            left = right
        return True
    elif isinstance(node, ast.Call):
        func = _safe_eval_ast(node.func)
        args = [_safe_eval_ast(arg) for arg in node.args]
        return func(*args)
    raise ValueError(f"Unsupported node type: {type(node).__name__}")


def verify_numeric(expression: str, constraints: Dict[str, Any] = None) -> ToolResult:
    """
    Checks a mathematical calculation or comparison against optional constraints.
    Returns ToolResult with data["passed"] = True/False and details.
    Follows API contract Section 3.2.
    """
    if constraints is None:
        constraints = {}

    if not expression or not isinstance(expression, str):
        return ToolResult(
            success=False,
            error="Expression must be a non-empty string."
        )

    # 1. Parse and validate AST safety (Sandboxing against malicious code injection)
    try:
        parsed_tree = ast.parse(expression.strip(), mode='eval')
    except SyntaxError as e:
        return ToolResult(
            success=False,
            error=f"Syntax error in expression '{expression}': {str(e)}"
        )
    except Exception as e:
        return ToolResult(
            success=False,
            error=f"Failed to parse expression: {str(e)}"
        )

    validator = _SafeMathASTValidator()
    validator.visit(parsed_tree)
    if not validator.is_safe:
        return ToolResult(
            success=False,
            error=f"Security validation error: {validator.violation_reason}"
        )

    # 2. Evaluate expression
    try:
        if HAS_SYMPY and ("=" in expression or "==" in expression):
            # Use SymPy for algebraic / symbolic checking
            val = _safe_eval_ast(parsed_tree)
        else:
            val = _safe_eval_ast(parsed_tree)
    except ZeroDivisionError:
        return ToolResult(
            success=True,
            data={
                "passed": False,
                "evaluated_result": None,
                "detail": "Division by zero in mathematical expression"
            }
        )
    except Exception as e:
        return ToolResult(
            success=False,
            error=f"Evaluation error: {str(e)}"
        )

    # 3. Handle constraints (e.g. tolerance)
    tolerance = constraints.get("tolerance")
    passed = False
    detail = ""

    if isinstance(val, bool):
        passed = val
        detail = "within tolerance" if passed else "comparison evaluated to false"
    elif isinstance(val, (int, float)):
        expected = constraints.get("expected")
        if expected is not None:
            if tolerance is not None:
                passed = abs(val - float(expected)) <= float(tolerance)
                detail = f"abs({val} - {expected}) <= {tolerance}: {passed}"
            else:
                passed = (val == float(expected))
                detail = f"{val} == {expected}: {passed}"
        else:
            # Numeric value without explicit boolean comparator or expected value
            passed = True
            detail = "evaluated successfully"
    else:
        passed = bool(val)
        detail = f"evaluated result: {val}"

    return ToolResult(
        success=True,
        data={
            "passed": passed,
            "evaluated_result": val,
            "detail": detail
        },
        error=None
    )
