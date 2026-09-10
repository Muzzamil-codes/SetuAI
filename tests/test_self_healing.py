"""
Regression test suite for SetuAI self-healing code execution loop in codegen_graph.
Follows API_CONTRACTS.md and test specifications.
"""
import sys
import os
import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from verification.code_sandbox.self_heal import (
    parse_verification_error,
    is_recoverable_error,
    format_self_heal_prompt
)
from orchestrator.agent_graph.subgraphs import codegen_graph


@pytest.mark.asyncio
async def test_first_try_pass_no_self_heal(monkeypatch):
    """TEST 1: Valid code passes on the first try with ZERO self_heal overhead."""
    async def mock_generate_code(*args, **kwargs):
        return '''def add(a, b):
    return a + b
'''

    async def mock_generate_tests(*args, **kwargs):
        return '''def test_add():
    assert add(2, 3) == 5
'''

    monkeypatch.setattr(codegen_graph, "_llm_generate_code", mock_generate_code)
    monkeypatch.setattr(codegen_graph, "_llm_generate_tests", mock_generate_tests)

    output, trace_events = await codegen_graph.run_codegen_graph(
        task_id="task_pass_first_try",
        graph_input={"instruction": "Add two numbers"}
    )

    assert output["passed"] is True
    assert output["exit_code"] == 0

    steps = [e["step"] for e in trace_events]
    assert steps == ["plan", "tool_call", "verify_pass"]
    assert "self_heal" not in steps
    assert "verify_fail" not in steps


@pytest.mark.asyncio
async def test_self_heal_success_on_first_repair(monkeypatch):
    """TEST 2: Code fails once, self-healing repairs it on attempt 1 -> verify_pass."""
    call_count = 0

    async def mock_generate_code(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            # Buggy code on first run: off-by-one error
            return '''def add(a, b):
    return a + b + 1
'''
        # Repaired code on attempt 1
        return '''def add(a, b):
    return a + b
'''

    async def mock_generate_tests(*args, **kwargs):
        return '''def test_add():
    assert add(2, 3) == 5
'''

    monkeypatch.setattr(codegen_graph, "_llm_generate_code", mock_generate_code)
    monkeypatch.setattr(codegen_graph, "_llm_generate_tests", mock_generate_tests)

    output, trace_events = await codegen_graph.run_codegen_graph(
        task_id="task_heal_success",
        graph_input={"instruction": "Add two numbers"}
    )

    assert output["passed"] is True
    assert output["exit_code"] == 0
    assert call_count == 2

    steps = [e["step"] for e in trace_events]
    assert steps == [
        "plan",
        "tool_call",    # initial sandbox run
        "verify_fail",  # initial failure
        "self_heal",    # repair attempt 1
        "tool_call",    # sandbox retry
        "verify_pass"   # passed after repair
    ]

    self_heal_evts = [e for e in trace_events if e["step"] == "self_heal"]
    assert len(self_heal_evts) == 1
    assert self_heal_evts[0]["payload"]["attempt"] == 1
    assert self_heal_evts[0]["payload"]["max_attempts"] == 2


@pytest.mark.asyncio
async def test_self_heal_success_on_second_repair(monkeypatch):
    """TEST 3: Code fails twice, self-healing succeeds on attempt 2 -> verify_pass."""
    call_count = 0

    async def mock_generate_code(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return 'def compute():\n    return 1 / 0\n'
        elif call_count == 2:
            return 'def compute():\n    return "not a number"\n'
        else:
            return 'def compute():\n    return 42\n'

    async def mock_generate_tests(*args, **kwargs):
        return 'def test_compute():\n    assert compute() == 42\n'

    monkeypatch.setattr(codegen_graph, "_llm_generate_code", mock_generate_code)
    monkeypatch.setattr(codegen_graph, "_llm_generate_tests", mock_generate_tests)

    output, trace_events = await codegen_graph.run_codegen_graph(
        task_id="task_heal_attempt_2",
        graph_input={"instruction": "Return 42"}
    )

    assert output["passed"] is True
    assert output["exit_code"] == 0
    assert call_count == 3

    steps = [e["step"] for e in trace_events]
    assert steps == [
        "plan",
        "tool_call",    # initial
        "verify_fail",  # fail 1
        "self_heal",    # attempt 1
        "tool_call",    # sandbox retry 1
        "verify_fail",  # fail 2
        "self_heal",    # attempt 2
        "tool_call",    # sandbox retry 2
        "verify_pass"   # passed!
    ]


@pytest.mark.asyncio
async def test_self_heal_stops_after_max_repairs(monkeypatch):
    """TEST 4: Code persistently fails -> exactly 2 repairs -> returns final verify_fail."""
    call_count = 0

    async def mock_generate_code(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        return 'def bad():\n    raise RuntimeError("Permanent failure")\n'

    async def mock_generate_tests(*args, **kwargs):
        return 'def test_bad():\n    bad()\n'

    monkeypatch.setattr(codegen_graph, "_llm_generate_code", mock_generate_code)
    monkeypatch.setattr(codegen_graph, "_llm_generate_tests", mock_generate_tests)

    output, trace_events = await codegen_graph.run_codegen_graph(
        task_id="task_heal_exhausted",
        graph_input={"instruction": "Fail persistently"}
    )

    assert output["passed"] is False
    assert output["exit_code"] != 0
    # 1 initial call + 2 repair calls = 3 calls total
    assert call_count == 3

    steps = [e["step"] for e in trace_events]
    assert steps == [
        "plan",
        "tool_call",    # initial
        "verify_fail",  # initial failure
        "self_heal",    # repair attempt 1
        "tool_call",    # retry 1
        "verify_fail",  # failure 1
        "self_heal",    # repair attempt 2
        "tool_call",    # retry 2
        "verify_fail"   # final failure (stopped at max 2)
    ]

    self_heals = [e for e in trace_events if e["step"] == "self_heal"]
    assert len(self_heals) == 2
    assert self_heals[0]["payload"]["attempt"] == 1
    assert self_heals[1]["payload"]["attempt"] == 2


def test_module_not_found_prompt_forbids_pip_and_instructs_stdlib():
    """TEST 5: Dependency errors explain air-gap policy and demand standard library."""
    prompt = format_self_heal_prompt(
        instruction="Read Modbus registers",
        previous_code="import pymodbus\n...",
        exc_type="ModuleNotFoundError",
        exc_msg="No module named 'pymodbus'",
        location="solution.py:1",
        stderr="ModuleNotFoundError: No module named 'pymodbus'",
        attempt=1
    )

    assert "pymodbus" in prompt
    assert "DO NOT attempt to pip install" in prompt
    assert "air-gapped" in prompt
    assert "standard library" in prompt
    assert "socket" in prompt


def test_recoverability_classification():
    """Verifies that is_recoverable_error properly distinguishes recoverable vs non-recoverable."""
    assert is_recoverable_error("ModuleNotFoundError", "No module named 'pymodbus'") is True
    assert is_recoverable_error("AssertionError", "Expected 10 got 20") is True
    assert is_recoverable_error("NameError", "name 'foo' is not defined") is True
    assert is_recoverable_error("TypeError", "unsupported operand type") is True
    assert is_recoverable_error("IndexError", "list index out of range") is True
    assert is_recoverable_error("KeyError", "'key'") is True
    assert is_recoverable_error("ZeroDivisionError", "division by zero") is True
    assert is_recoverable_error("ValueError", "invalid literal") is True
    assert is_recoverable_error("AttributeError", "'int' object has no attribute 'get'") is True
    assert is_recoverable_error("SystemExit", "exit") is False
    assert is_recoverable_error("MemoryError", "out of memory") is False
