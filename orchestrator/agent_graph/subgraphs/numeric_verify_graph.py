"""
Numeric Verify Graph — specialist sub-graph for engineering calculation verification.
Executed as a discrete tool/sub-graph by the SetuAI Manager Agent.
"""
from datetime import datetime, timezone
import threading
from typing import Tuple, Dict, Any

from orchestrator.agent_graph.nodes.tool_call import _run_tool


async def run_numeric_verify_graph(
    task_id: str,
    graph_input: dict,
    cancel_event: threading.Event = None
) -> Tuple[Dict[str, Any], list]:
    """
    Executes the numeric verify graph:
    1. Plan step
    2. Sandbox numeric verification execution
    3. Verification gate
    
    Returns (result_dict, trace_events).
    """
    trace_events = []
    expr = graph_input.get("expression", "") or graph_input.get("prompt", "")
    expected = graph_input.get("expected", None)
    tolerance = graph_input.get("tolerance", 0.05)

    trace_events.append({
        "task_id": task_id,
        "step": "plan",
        "payload": {
            "plan": "Verify engineering calculation against specified tolerances in sandbox",
            "task_type": "numeric_verify",
            "retry_count": 0
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

    tool_input_data = {
        "verification_type": "numeric",
        "expression": expr,
        "expected": expected,
        "tolerance": tolerance
    }
    tool_res = _run_tool("sandbox", tool_input_data)
    success = tool_res.get("success", False)

    trace_events.append({
        "task_id": task_id,
        "step": "tool_call",
        "payload": {
            "tool_name": "sandbox",
            "input_summary": {"expression": expr[:60], "expected": str(expected)},
            "success": success
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

    data = tool_res.get("data", {})
    passed = data.get("passed", False)
    computed = data.get("computed_value", "?")

    if passed:
        trace_events.append({
            "task_id": task_id,
            "step": "verify_pass",
            "payload": {
                "detail": f"Numeric verification passed: {computed} matches expected {expected}",
                "verification_type": "numeric_verify",
                "retry_count": 0
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    else:
        trace_events.append({
            "task_id": task_id,
            "step": "verify_fail",
            "payload": {
                "detail": f"Numeric verification failed: computed {computed} vs expected {expected}",
                "verification_type": "numeric_verify",
                "retry_count": 0
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

    output = {
        "success": passed,
        "passed": passed,
        "computed_value": computed,
        "expected": expected,
        "data": data
    }
    return output, trace_events
