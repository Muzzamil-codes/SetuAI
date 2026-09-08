"""
Test harness injector for code sandbox execution.
Wraps assertions and imports into a test module compatible with both pytest and python3.
"""

def generate_test_harness(code: str, tests: str) -> str:
    """
    Generates test file content that executes tests against solution.py.
    Compatible with both pytest and direct python execution.
    """
    lines = tests.strip().splitlines()
    has_test_functions = any(line.strip().startswith("def test_") for line in lines)

    if has_test_functions:
        test_body = tests
    else:
        # Indent raw assertions inside a test function
        indented_lines = "\n".join("    " + line if line.strip() else "" for line in lines)
        test_body = f"def test_solution():\n{indented_lines}"

    harness = f"""# Auto-generated sandbox test harness
import sys

try:
    import pytest
except ImportError:
    pytest = None

from solution import *

{test_body}

if __name__ == '__main__':
    # Auto-execute all test functions if executed directly with python
    test_funcs = [obj for name, obj in list(globals().items()) if name.startswith('test_') and callable(obj)]
    for test_fn in test_funcs:
        test_fn()
    print("ALL_TESTS_PASSED")
"""
    return harness
