"""
Codegen Graph — specialist sub-graph for code generation and sandbox verification.
Executed as a discrete tool/sub-graph by the SetuAI Manager Agent.
"""
from datetime import datetime, timezone
import json
import os
import threading
from typing import AsyncGenerator, Tuple, Dict, Any

from orchestrator.agent_graph.nodes.tool_call import (
    _get_model_config,
    _call_llm_async,
    _run_tool,
    _llm_generate_code,
    _llm_generate_tests
)


def _get_coder_model() -> dict:
    """Finds qwen2.5-coder or falls back to first available model."""
    try:
        models_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "models_registry", "models.json"
        )
        with open(models_path, "r") as f:
            manifest = json.load(f)
        for m in manifest:
            if "coder" in m.get("role", "") or "coder" in m.get("name", ""):
                return m
        if manifest:
            return manifest[0]
    except Exception:
        pass
    return {"name": "qwen2.5-coder:7b", "endpoint": "http://localhost:11434/v1"}


async def run_codegen_graph(
    task_id: str,
    graph_input: dict,
    cancel_event: threading.Event = None
) -> Tuple[Dict[str, Any], list]:
    """
    Executes the codegen graph:
    1. Plan step
    2. Code generation (qwen2.5-coder)
    3. Test suite generation
    4. Sandbox execution
    5. Verification gate
    
    Returns (result_dict, trace_events).
    """
    trace_events = []
    instruction = graph_input.get("instruction", "") or graph_input.get("prompt", "")
    coder_model = _get_coder_model()

    # Step 1: Plan
    plan_text = f"Generate Python code for: {instruction[:90]} → execute in sandbox → verify tests pass"
    plan_event = {
        "task_id": task_id,
        "step": "plan",
        "payload": {
            "plan": plan_text,
            "task_type": "code_generation",
            "retry_count": 0
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    trace_events.append(plan_event)

    # Step 2: Generate code
    code = await _llm_generate_code(
        model_config=coder_model,
        user_request=instruction,
        stream_callback=None,
        cancel_event=cancel_event
    )

    # Step 3: Tool call (sandbox)
    tool_event = {
        "task_id": task_id,
        "step": "tool_call",
        "payload": {
            "tool_name": "sandbox",
            "input_summary": {"language": "python", "code_preview": code[:100]},
            "success": True
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    trace_events.append(tool_event)

    # Step 4: Generate tests and run in sandbox
    test_code = await _llm_generate_tests(coder_model, instruction, code)
    sandbox_input = {
        "verification_type": "code",
        "code": code,
        "tests": test_code,
        "timeout": 30,
        "language": "python"
    }
    sandbox_result = _run_tool("sandbox", sandbox_input)
    
    data = sandbox_result.get("data", {})
    passed = data.get("passed", False)
    exit_code = data.get("exit_code", 0 if passed else 1)
    stdout = data.get("stdout", "")
    stderr = data.get("stderr", "")

    # Step 5: Verify
    if passed:
        verify_event = {
            "task_id": task_id,
            "step": "verify_pass",
            "payload": {
                "detail": f"Code verified in sandbox (exit code: {exit_code})",
                "verification_type": "code_generation",
                "retry_count": 0
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    else:
        err_snippet = (stderr or stdout or "Execution error")[:150]
        verify_event = {
            "task_id": task_id,
            "step": "verify_fail",
            "payload": {
                "detail": f"Code verification failed: {err_snippet}",
                "verification_type": "code_generation",
                "retry_count": 0
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    trace_events.append(verify_event)

    output = {
        "success": passed,
        "code": code,
        "test_code": test_code,
        "passed": passed,
        "stdout": stdout,
        "stderr": stderr,
        "exit_code": exit_code
    }
    return output, trace_events
