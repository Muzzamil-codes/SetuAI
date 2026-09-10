"""
Regression test suite for code sandbox verification, traceback parsing,
and codegen subgraph verification events.
Follows API_CONTRACTS.md.
"""
import sys
import os
import pytest
import asyncio

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from verification.code_sandbox.self_heal import parse_verification_error
from verification.code_sandbox.podman_runner import run_code_sandboxed
from orchestrator.agent_graph.subgraphs.codegen_graph import run_codegen_graph


def test_traceback_parser_assertion_error():
    """Verifies that standard Python AssertionError traceback is parsed concisely."""
    stderr = """Traceback (most recent call last):
  File "/tmp/sandbox/test_solution.py", line 37, in <module>
    test_fn()
  File "/tmp/sandbox/test_solution.py", line 13, in test_knapsack
    assert knapsack([1, 2, 3], [10, 20, 30], 5) == 10
AssertionError: Test case 2 failed"""

    parsed = parse_verification_error(stderr)
    assert parsed["exc_type"] == "AssertionError"
    assert parsed["exc_msg"] == "Test case 2 failed"
    assert "test_solution.py:13 in test_knapsack" in parsed["location"]
    assert "AssertionError: Test case 2 failed" in parsed["concise_summary"]
    assert "test_solution.py:13" in parsed["concise_summary"]


def test_traceback_parser_syntax_error():
    """Verifies that Python SyntaxError is correctly extracted with location."""
    stderr = """  File "/tmp/sandbox/solution.py", line 5
    def broken_func(
                   ^
SyntaxError: unexpected EOF while parsing"""

    parsed = parse_verification_error(stderr)
    assert parsed["exc_type"] == "SyntaxError"
    assert "unexpected EOF" in parsed["exc_msg"]
    assert "solution.py:5" in parsed["location"]
    assert "SyntaxError:" in parsed["concise_summary"]


def test_traceback_parser_runtime_error():
    """Verifies that ZeroDivisionError and line numbers are correctly extracted."""
    stderr = """Traceback (most recent call last):
  File "/tmp/sandbox/test_solution.py", line 15, in <module>
    compute()
  File "/tmp/sandbox/solution.py", line 4, in compute
    return 100 / 0
ZeroDivisionError: division by zero"""

    parsed = parse_verification_error(stderr)
    assert parsed["exc_type"] == "ZeroDivisionError"
    assert parsed["exc_msg"] == "division by zero"
    assert "solution.py:4 in compute" in parsed["location"]
    assert "ZeroDivisionError: division by zero (solution.py:4 in compute)" == parsed["concise_summary"]


def test_traceback_parser_timeout():
    """Verifies that sandbox timeouts produce clean TimeoutError."""
    stderr = "Execution timed out after 15 seconds."
    parsed = parse_verification_error(stderr)
    assert parsed["exc_type"] == "TimeoutError"
    assert "15s" in parsed["exc_msg"]
    assert parsed["location"] == "sandbox"


def test_valid_knapsack_passes_sandbox():
    """Verifies that valid 0/1 knapsack code passes sandbox verification."""
    code = '''def knapsack(weights, values, capacity):
    n = len(weights)
    dp = [[0 for _ in range(capacity + 1)] for _ in range(n + 1)]
    for i in range(1, n + 1):
        for w in range(1, capacity + 1):
            if weights[i-1] <= w:
                dp[i][w] = max(values[i-1] + dp[i-1][w - weights[i-1]], dp[i-1][w])
            else:
                dp[i][w] = dp[i-1][w]
    return dp[n][capacity]
'''
    tests = '''def test_knapsack():
    assert callable(knapsack)
    assert knapsack([], [], 0) == 0
    assert knapsack([1, 2, 3], [10, 20, 30], 0) == 0
    assert knapsack([1], [10], 1) == 10
    assert knapsack([5], [10], 1) == 0
    res = knapsack([1, 2, 3], [10, 20, 30], 5)
    assert isinstance(res, int)
    assert res == 50
'''
    res = run_code_sandboxed(code=code, tests=tests, language="python")
    assert res.success is True
    assert res.data["passed"] is True
    assert res.data["exit_code"] == 0
    assert "ALL_TESTS_PASSED" in res.data["stdout"]


def test_invalid_code_fails_with_parsed_error():
    """Verifies that failing code fails verification with non-zero exit code and structured error."""
    code = '''def divide(a, b):
    return a / b
'''
    tests = '''def test_divide():
    assert divide(10, 2) == 5
    divide(10, 0)
'''
    res = run_code_sandboxed(code=code, tests=tests, language="python")
    assert res.success is True
    assert res.data["passed"] is False
    assert res.data["exit_code"] != 0
    assert "parsed_error" in res.data
    parsed = res.data["parsed_error"]
    assert parsed["exc_type"] == "ZeroDivisionError"
    assert "division by zero" in parsed["exc_msg"]
    assert "ZeroDivisionError: division by zero" in parsed["concise_summary"]


def test_assertion_failure_fails_with_clean_error():
    """Verifies that failing assertions produce clean error details and exit code != 0."""
    code = '''def add(a, b):
    return a + b
'''
    tests = '''def test_add():
    assert add(2, 2) == 5, "Math broke"
'''
    res = run_code_sandboxed(code=code, tests=tests, language="python")
    assert res.success is True
    assert res.data["passed"] is False
    assert res.data["exit_code"] != 0
    assert "parsed_error" in res.data
    parsed = res.data["parsed_error"]
    assert parsed["exc_type"] == "AssertionError"
    assert "Math broke" in parsed["exc_msg"]


@pytest.mark.asyncio
async def test_codegen_subgraph_execution(monkeypatch):
    """Verifies that codegen_graph handles both pass and fail with trace events and structured logs."""
    from orchestrator.agent_graph.subgraphs import codegen_graph

    # Mock coder model to return valid knapsack implementation
    async def mock_generate_code(*args, **kwargs):
        return '''def knapsack(weights, values, capacity):
    n = len(weights)
    dp = [[0 for _ in range(capacity + 1)] for _ in range(n + 1)]
    for i in range(1, n + 1):
        for w in range(1, capacity + 1):
            if weights[i-1] <= w:
                dp[i][w] = max(values[i-1] + dp[i-1][w - weights[i-1]], dp[i-1][w])
            else:
                dp[i][w] = dp[i-1][w]
    return dp[n][capacity]
'''
    async def mock_generate_tests(*args, **kwargs):
        return '''def test_knapsack():
    assert callable(knapsack)
    assert knapsack([1, 2, 3], [10, 20, 30], 5) == 50
'''
    monkeypatch.setattr(codegen_graph, "_llm_generate_code", mock_generate_code)
    monkeypatch.setattr(codegen_graph, "_llm_generate_tests", mock_generate_tests)

    output, trace_events = await codegen_graph.run_codegen_graph(
        task_id="test_task_pass",
        graph_input={"instruction": "Write knapsack"}
    )
    assert output["passed"] is True
    assert output["exit_code"] == 0
    verify_events = [e for e in trace_events if e["step"] == "verify_pass"]
    assert len(verify_events) == 1
    assert "Code verified in sandbox" in verify_events[0]["payload"]["detail"]


@pytest.mark.asyncio
async def test_codegen_subgraph_failure_event(monkeypatch):
    """Verifies that codegen_graph failure produces verify_fail with concise message."""
    from orchestrator.agent_graph.subgraphs import codegen_graph

    async def mock_generate_code(*args, **kwargs):
        return 'def bad_func():\n    raise ValueError("Explicit test error")\n'

    async def mock_generate_tests(*args, **kwargs):
        return 'def test_bad():\n    bad_func()\n'

    monkeypatch.setattr(codegen_graph, "_llm_generate_code", mock_generate_code)
    monkeypatch.setattr(codegen_graph, "_llm_generate_tests", mock_generate_tests)

    output, trace_events = await codegen_graph.run_codegen_graph(
        task_id="test_task_fail",
        graph_input={"instruction": "Trigger error"}
    )
    assert output["passed"] is False
    assert output["exit_code"] != 0
    verify_fails = [e for e in trace_events if e["step"] == "verify_fail"]
    self_heals = [e for e in trace_events if e["step"] == "self_heal"]
    # Initial failure + 2 self-healing retries = 3 verify_fail events
    assert len(verify_fails) == 3
    assert len(self_heals) == 2
    payload = verify_fails[-1]["payload"]
    assert "Code verification failed: ValueError: Explicit test error" in payload["detail"]
    assert payload["exception_type"] == "ValueError"
    assert payload["exception_message"] == "Explicit test error"
