"""
Plan node — generates an execution plan based on the classified task type.

The plan is a human-readable description of the steps the agent will take,
shown in the trace UI so judges can follow the reasoning.
"""
from orchestrator.agent_graph.state import AgentState
from datetime import datetime, timezone


def plan_node(state: AgentState) -> dict:
    """Generate an execution plan based on task type."""
    task_type = state.get("task_type", "drafting")
    task_id = state.get("task_id", "unknown")
    retry_count = state.get("retry_count", 0)
    error_context = ""

    # On retry, include error context from the previous failed attempt
    if retry_count > 0:
        tool_results = state.get("tool_results", [])
        if tool_results:
            last_result = tool_results[-1]
            last_error = last_result.get("error", "")
            if last_error:
                error_context = f" (Retry #{retry_count}: previous attempt failed — {last_error})"

    plans = {
        "extraction": (
            "Extract fields from uploaded document/image using VLM + OCR → "
            "cross-verify extracted values against SOP database → "
            "generate formatted approval note (.docx)"
        ),
        "codegen": (
            "Generate Python code for the requested task → "
            "run code in sandboxed environment with test harness → "
            "verify tests pass → deliver code with test log"
        ),
        "numeric_verify": (
            "Parse numeric expression from request → "
            "verify calculation with SymPy against known tolerances → "
            "generate verification report (.xlsx)"
        ),
        "drafting": (
            "Retrieve relevant context from SOP knowledge base → "
            "draft document using retrieved evidence → "
            "verify all claims are grounded in sources → "
            "generate final approval note (.docx)"
        )
    }

    plan = plans.get(task_type, plans["drafting"]) + error_context

    trace_events = list(state.get("trace_events", []))
    trace_events.append({
        "task_id": task_id,
        "step": "plan",
        "payload": {"plan": plan, "task_type": task_type,
                     "retry_count": retry_count},
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

    return {
        "plan": plan,
        "trace_events": trace_events
    }
