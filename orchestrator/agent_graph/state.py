from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict):
    task_id: str
    task_input: dict
    task_type: str
    modality: str
    selected_model: dict
    messages: list
    plan: str
    tool_calls: list[dict]
    tool_results: list[dict]
    verification_status: str
    retry_count: int
    max_retries: int
    artifacts: list[dict]
    trace_events: list[dict]
    error: Optional[str]
    final_summary: str
