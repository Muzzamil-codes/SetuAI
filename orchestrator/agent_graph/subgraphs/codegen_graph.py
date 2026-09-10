"""
Codegen Graph — specialist sub-graph for code generation and sandbox verification.
Executed as a discrete tool/sub-graph by the SetuAI Manager Agent.
"""
from datetime import datetime, timezone
import json
import os
import threading
import logging
from typing import Tuple, Dict, Any, Optional
from verification.code_sandbox.self_heal import (
    parse_verification_error,
    is_recoverable_error,
    format_self_heal_prompt
)

logger = logging.getLogger("codegen_graph")

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


def _log_sandbox_failure(exit_code: int, exc_type: str, exc_msg: str, location: str, code: str, test_code: str, stdout: str, stderr: str):
    failure_log = (
        "\n" + "=" * 70 + "\n"
        "❌ CODE VERIFICATION FAILED\n"
        f"Exit Code: {exit_code}\n"
        f"Exception Type: {exc_type}\n"
        f"Exception Message: {exc_msg}\n"
        f"Location: {location}\n"
        + "-" * 30 + " GENERATED CODE " + "-" * 30 + "\n"
        f"{code}\n"
        + "-" * 32 + " TEST CODE " + "-" * 34 + "\n"
        f"{test_code}\n"
        + "-" * 30 + " SANDBOX STDOUT " + "-" * 30 + "\n"
        f"{stdout if stdout.strip() else '(empty)'}\n"
        + "-" * 30 + " SANDBOX STDERR " + "-" * 30 + "\n"
        f"{stderr if stderr.strip() else '(empty)'}\n"
        + "=" * 70
    )
    logger.error(failure_log)
    print(failure_log)


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
    5. Verification gate with bounded self-healing loop (max 2 repairs)
    
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

    # Step 5: Verify & Self-Heal Loop
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
        trace_events.append(verify_event)
    else:
        parsed_err = data.get("parsed_error") or parse_verification_error(stderr, stdout)
        concise_err = parsed_err.get("concise_summary") or "Execution error"
        exc_type = parsed_err.get("exc_type") or "Error"
        exc_msg = parsed_err.get("exc_msg") or ""
        location = parsed_err.get("location") or "unknown"

        # Log COMPLETE failure details to backend console
        _log_sandbox_failure(exit_code, exc_type, exc_msg, location, code, test_code, stdout, stderr)

        verify_event = {
            "task_id": task_id,
            "step": "verify_fail",
            "payload": {
                "detail": f"Code verification failed: {concise_err}",
                "verification_type": "code_generation",
                "exception_type": exc_type,
                "exception_message": exc_msg,
                "location": location,
                "exit_code": exit_code,
                "retry_count": 0
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        trace_events.append(verify_event)

        # Attempt bounded self-healing if recoverable (max 2 repairs)
        max_repairs = 2
        if is_recoverable_error(exc_type, exc_msg, stderr):
            for attempt in range(1, max_repairs + 1):
                if cancel_event and cancel_event.is_set():
                    break

                # Self-heal trace event
                self_heal_event = {
                    "task_id": task_id,
                    "step": "self_heal",
                    "payload": {
                        "detail": f"Repairing code (attempt {attempt}/{max_repairs}): {concise_err}",
                        "attempt": attempt,
                        "max_attempts": max_repairs,
                        "error": concise_err,
                        "exception_type": exc_type,
                        "exception_message": exc_msg,
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                trace_events.append(self_heal_event)

                # Generate repaired code
                repair_prompt = format_self_heal_prompt(
                    instruction=instruction,
                    previous_code=code,
                    exc_type=exc_type,
                    exc_msg=exc_msg,
                    location=location,
                    stderr=stderr,
                    attempt=attempt
                )
                repaired_code = await _llm_generate_code(
                    model_config=coder_model,
                    user_request=repair_prompt,
                    stream_callback=None,
                    cancel_event=cancel_event
                )
                code = repaired_code

                # Tool call (sandbox retry)
                tool_event = {
                    "task_id": task_id,
                    "step": "tool_call",
                    "payload": {
                        "tool_name": "sandbox",
                        "input_summary": {"language": "python", "code_preview": code[:100], "attempt": attempt},
                        "success": True
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                trace_events.append(tool_event)

                # Re-run sandbox with repaired code
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

                if passed:
                    verify_event = {
                        "task_id": task_id,
                        "step": "verify_pass",
                        "payload": {
                            "detail": f"Code verified in sandbox after self-healing (attempt {attempt}, exit code: {exit_code})",
                            "verification_type": "code_generation",
                            "retry_count": attempt
                        },
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                    trace_events.append(verify_event)
                    break
                else:
                    parsed_err = data.get("parsed_error") or parse_verification_error(stderr, stdout)
                    concise_err = parsed_err.get("concise_summary") or "Execution error"
                    exc_type = parsed_err.get("exc_type") or "Error"
                    exc_msg = parsed_err.get("exc_msg") or ""
                    location = parsed_err.get("location") or "unknown"

                    _log_sandbox_failure(exit_code, exc_type, exc_msg, location, code, test_code, stdout, stderr)

                    verify_event = {
                        "task_id": task_id,
                        "step": "verify_fail",
                        "payload": {
                            "detail": f"Code verification failed: {concise_err}",
                            "verification_type": "code_generation",
                            "exception_type": exc_type,
                            "exception_message": exc_msg,
                            "location": location,
                            "exit_code": exit_code,
                            "retry_count": attempt
                        },
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                    trace_events.append(verify_event)

                    if not is_recoverable_error(exc_type, exc_msg, stderr):
                        break

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
