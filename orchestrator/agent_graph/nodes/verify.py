"""
Verification gate node — checks the latest tool result and decides
whether to pass, fail (triggering retry), or escalate.

This is the core differentiator of the Setu pipeline: every output
passes through this gate before being allowed to reach the user.
"""
from orchestrator.agent_graph.state import AgentState
from datetime import datetime, timezone


def verify_node(state: AgentState) -> dict:
    """Check the latest tool result and set verification status."""
    task_type = state.get("task_type", "drafting")
    tool_results = state.get("tool_results", [])
    task_id = state.get("task_id", "unknown")
    retry_count = state.get("retry_count", 0)
    trace_events = list(state.get("trace_events", []))

    latest_result = (
        tool_results[-1] if tool_results
        else {"success": False, "data": {}, "error": "No tool results available"}
    )

    passed = False
    detail = ""

    try:
        if not latest_result.get("success"):
            passed = False
            detail = latest_result.get("error", "Tool execution failed")
        else:
            data = latest_result.get("data", {})

            if task_type == "extraction":
                # Check that fields were actually extracted
                fields = data.get("fields", data.get("extracted_fields", {}))
                if fields and len(fields) > 0:
                    passed = True
                    detail = f"Extracted {len(fields)} fields successfully"
                else:
                    passed = False
                    detail = "No fields extracted from document"

            elif task_type in ["code_generation", "codegen"]:
                # Check sandbox test result
                if data.get("passed", False):
                    passed = True
                    detail = f"Code tests passed (exit code: {data.get('exit_code', 0)})"
                else:
                    passed = False
                    stderr = data.get("stderr", "Unknown test failure")
                    detail = f"Code tests failed: {stderr[:200]}"

            elif task_type == "numeric_verify":
                if data.get("passed", False):
                    passed = True
                    computed = data.get("computed_value", "?")
                    expected = data.get("expected", "?")
                    detail = f"Numeric check passed: {computed} within tolerance of {expected}"
                else:
                    passed = False
                    detail = f"Numeric check failed: deviation {data.get('deviation', '?')} exceeds tolerance"

            elif task_type in ["document_generation", "drafting"]:
                import os
                artifact = data.get("artifact", {})
                path = data.get("path") or data.get("file_path") or artifact.get("path")
                filename = data.get("filename") or artifact.get("filename", "document.docx")

                if path and os.path.exists(path) and os.path.getsize(path) > 0:
                    passed = True
                    size_kb = round(os.path.getsize(path) / 1024, 1)
                    sop_note = " (SOP aligned)" if data.get("sop_used") else ""
                    detail = f"Verified {filename} ({size_kb} KB) generated successfully{sop_note}"
                else:
                    # Fallback check for raw text draft
                    generated = data.get("generated_text", data.get("draft", ""))
                    if generated:
                        passed = True
                        detail = f"Draft generated successfully ({len(generated)} chars)"
                    else:
                        passed = False
                        detail = latest_result.get("error", "Failed to generate document artifact")

            elif task_type in ["spreadsheet_generation"]:
                import os
                artifact = data.get("artifact", {})
                path = data.get("path") or data.get("file_path") or artifact.get("path")
                filename = data.get("filename") or artifact.get("filename", "spreadsheet.xlsx")

                if path and os.path.exists(path) and os.path.getsize(path) > 0:
                    passed = True
                    size_kb = round(os.path.getsize(path) / 1024, 1)
                    detail = f"Verified {filename} ({size_kb} KB) generated successfully"
                else:
                    passed = False
                    detail = latest_result.get("error", "Failed to generate spreadsheet artifact")

            elif task_type == "conversational":
                # Check that the LLM generated a response
                response = data.get("response", data.get("generated_text", ""))
                if response:
                    passed = True
                    detail = f"Response generated ({len(response)} chars)"
                else:
                    passed = False
                    detail = "Failed to generate response — LLM may be unavailable"

            else:
                passed = latest_result.get("success", False)
                detail = "Generic verification passed" if passed else latest_result.get("error", "Verification failed")

    except Exception as e:
        passed = False
        detail = f"Verification error: {str(e)}"

    if passed:
        verification_status = "passed"
        step = "verify_pass"
    else:
        verification_status = "failed"
        step = "verify_fail"
        retry_count += 1

    payload = {
        "detail": detail,
        "verification_type": task_type,
        "retry_count": retry_count
    }
    
    # Check if sandbox_mode is in the latest tool result's data
    tool_data = latest_result.get("data", {})
    if isinstance(tool_data, dict) and "sandbox_mode" in tool_data:
        payload["sandbox_mode"] = tool_data["sandbox_mode"]

    trace_events.append({
        "task_id": task_id,
        "step": step,
        "payload": payload,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

    # On failure, also emit a retry event if we'll be retrying
    max_retries = state.get("max_retries", 2)
    if not passed and retry_count < max_retries:
        trace_events.append({
            "task_id": task_id,
            "step": "retry",
            "payload": {
                "attempt": retry_count,
                "max_retries": max_retries,
                "reason": detail
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

    return {
        "verification_status": verification_status,
        "retry_count": retry_count,
        "trace_events": trace_events
    }
