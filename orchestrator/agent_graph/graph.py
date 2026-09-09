"""
Setu Agent Graph — LangGraph state machine with SimpleGraph fallback.

Defines the agentic pipeline: classify → plan → tool_call → verify → generate
with a conditional retry loop when verification fails (max 2 retries).

Exposes `run_agent(task_input_dict) -> AsyncGenerator[dict, None]` for the
backend to consume. Each yielded dict is a TraceEvent-shaped dict.
"""
from orchestrator.agent_graph.state import AgentState
from orchestrator.classifier.infer import classify_task_with_confidence, select_model, select_model_by_name
from orchestrator.agent_graph.nodes.plan import plan_node
from orchestrator.agent_graph.nodes.tool_call import tool_call_node
from orchestrator.agent_graph.nodes.verify import verify_node
from orchestrator.agent_graph.nodes.generate import generate_node
from datetime import datetime, timezone
import traceback
from typing import AsyncGenerator


class SimpleGraph:
    """Lightweight state machine that replaces LangGraph when it's not installed.

    Walks nodes in sequence, following edges and conditional edges, and
    yields every *new* trace event produced by each node — not just the last.
    """

    def __init__(self):
        self.nodes: dict[str, callable] = {}
        self.edges: dict[str, str] = {}
        self.conditional_edges: dict[str, tuple] = {}
        self._entry_point: str | None = None

    def add_node(self, name: str, func: callable):
        self.nodes[name] = func
        if self._entry_point is None:
            self._entry_point = name

    def add_edge(self, from_node: str, to_node: str):
        self.edges[from_node] = to_node

    def add_conditional_edge(self, from_node: str, condition_func: callable,
                             mapping: dict[str, str]):
        self.conditional_edges[from_node] = (condition_func, mapping)

    def set_entry_point(self, name: str):
        self._entry_point = name

    async def run(self, initial_state: AgentState) -> AsyncGenerator[dict, None]:
        state = dict(initial_state)  # mutable working copy
        current_node = self._entry_point or "classify"
        events_yielded = 0  # track how many events we've already sent

        while current_node and current_node != "END":
            func = self.nodes.get(current_node)
            if not func:
                break

            try:
                import asyncio
                if asyncio.iscoroutinefunction(func):
                    updates = await func(state)
                else:
                    updates = func(state)
                
                state.update(updates)

                # Yield every NEW trace event (not just the last one)
                all_events = state.get("trace_events", [])
                while events_yielded < len(all_events):
                    yield all_events[events_yielded]
                    events_yielded += 1

            except Exception as e:
                yield {
                    "task_id": state.get("task_id", "unknown"),
                    "step": "error",
                    "payload": {"error": str(e),
                                "traceback": traceback.format_exc()},
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                break

            # Determine next node
            if current_node in self.conditional_edges:
                cond_func, mapping = self.conditional_edges[current_node]
                next_key = cond_func(state)
                current_node = mapping.get(next_key, "END")
            else:
                current_node = self.edges.get(current_node, "END")


# ---------------------------------------------------------------------------
# Classify node (lives here rather than in nodes/ because it directly calls
# the classifier and populates the top-level routing fields)
# ---------------------------------------------------------------------------

def classify_node(state: AgentState) -> dict:
    """Classifies the incoming task and selects the specialist model."""
    task_input = state.get("task_input", {})
    task_id = state.get("task_id", "unknown")
    content = task_input.get("content", "")
    modality = task_input.get("modality", "text")

    task_type, confidence, method = classify_task_with_confidence(content, modality)
    model_override = task_input.get("model_override", "auto")

    if model_override and model_override != "auto":
        # User explicitly chose a model — skip classifier
        model = select_model_by_name(model_override)
        # Still classify to determine task_type for pipeline routing
        task_type, confidence, method = classify_task_with_confidence(content, modality)
        method = f"user_override({model_override})"
        confidence = 1.0
    else:
        task_type, confidence, method = classify_task_with_confidence(content, modality)
        model = select_model(task_type)

    trace_events = list(state.get("trace_events", []))
    trace_events.append({
        "task_id": task_id,
        "step": "classify",
        "payload": {
            "task_type": task_type,
            "confidence": confidence,
            "classification_method": method,
            "selected_model": model
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

    return {
        "task_type": task_type,
        "selected_model": model,
        "trace_events": trace_events
    }


# ---------------------------------------------------------------------------
# Graph construction
# ---------------------------------------------------------------------------

try:
    from langgraph.graph import StateGraph, END
    HAS_LANGGRAPH = True
except ImportError:
    HAS_LANGGRAPH = False
    END = "END"


def build_graph():
    """Builds the agent state graph using LangGraph or the SimpleGraph fallback."""
    if HAS_LANGGRAPH:
        workflow = StateGraph(AgentState)
    else:
        workflow = SimpleGraph()

    workflow.add_node("classify", classify_node)
    workflow.add_node("plan", plan_node)
    workflow.add_node("tool_call", tool_call_node)
    workflow.add_node("verify", verify_node)
    workflow.add_node("generate", generate_node)

    def classify_condition(state: AgentState) -> str:
        if state.get("task_type") == "conversational":
            return "conversational"
        return "complex"

    workflow.add_conditional_edge(
        "classify",
        classify_condition,
        {
            "conversational": "tool_call",
            "complex": "plan"
        }
    )
    workflow.add_edge("plan", "tool_call")
    workflow.add_edge("tool_call", "verify")

    def verify_condition(state: AgentState) -> str:
        status = state.get("verification_status")
        retries = state.get("retry_count", 0)
        max_retries = state.get("max_retries", 2)
        task_type = state.get("task_type", "")

        if status == "passed":
            return "passed"
        
        # Do not blindly retry conversational/drafting tasks if the LLM is just down/empty.
        # Retries are meant for things like code execution failing or numeric verification failing.
        if task_type in ["conversational", "drafting"] and status == "failed":
            return "exhausted"

        elif status == "failed" and retries < max_retries:
            return "retry"
        else:
            return "exhausted"

    workflow.add_conditional_edge(
        "verify",
        verify_condition,
        {
            "passed": "generate",
            "retry": "plan",
            "exhausted": "generate"
        }
    )

    workflow.add_edge("generate", END)

    if HAS_LANGGRAPH:
        return workflow.compile()
    return workflow


# ---------------------------------------------------------------------------
# Public API — the single function the backend imports
# ---------------------------------------------------------------------------

async def run_agent(task_input_dict: dict) -> AsyncGenerator[dict, None]:
    """Run the full agent pipeline for a task.

    Yields TraceEvent-shaped dicts as the agent progresses through
    classify → plan → tool_call → verify → generate.

    Args:
        task_input_dict: A dict matching the TaskInput schema:
            {task_id, modality, content, context}

    Yields:
        dict with keys: task_id, step, payload, timestamp
    """
    initial_state: AgentState = {
        "task_id": task_input_dict.get(
            "task_id",
            f"task_{int(datetime.now(timezone.utc).timestamp())}"
        ),
        "task_input": task_input_dict,
        "task_type": "",
        "modality": task_input_dict.get("modality", "text"),
        "selected_model": {},
        "messages": task_input_dict.get("context", {}).get("chat_history", []),
        "plan": "",
        "tool_calls": [],
        "tool_results": [],
        "verification_status": "pending",
        "retry_count": 0,
        "max_retries": 2,
        "artifacts": [],
        "trace_events": [],
        "error": None,
        "final_summary": ""
    }

    graph = build_graph()

    try:
        if HAS_LANGGRAPH:
            async for output in graph.astream(initial_state):
                for _node_name, state_update in output.items():
                    events = state_update.get("trace_events", [])
                    for event in events:
                        yield event
        else:
            async for event in graph.run(initial_state):
                yield event
    except Exception as e:
        yield {
            "task_id": initial_state["task_id"],
            "step": "error",
            "payload": {"error": str(e),
                        "traceback": traceback.format_exc()},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
