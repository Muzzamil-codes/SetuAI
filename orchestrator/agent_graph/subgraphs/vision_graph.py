"""
Vision Graph — specialist sub-graph for image analysis and visual document extraction.
Executed as a discrete tool/sub-graph by the SetuAI Manager Agent.
"""
from datetime import datetime, timezone
import os
import threading
from typing import Tuple, Dict, Any

from orchestrator.agent_graph.nodes.tool_call import (
    _run_tool,
    _llm_vision_response
)


def _get_vision_model() -> dict:
    """Finds qwen2.5-vl or falls back to first available vision model."""
    try:
        models_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "models_registry", "models.json"
        )
        with open(models_path, "r") as f:
            manifest = json.load(f)
        for m in manifest:
            if "vision" in m.get("modality", "") or "vl" in m.get("name", ""):
                return m
        if manifest:
            return manifest[0]
    except Exception:
        pass
    return {"name": "qwen2.5-vl", "endpoint": "http://localhost:11434/v1"}


from orchestrator.vision.vlm_client import resolve_image_path


async def run_vision_graph(
    task_id: str,
    graph_input: dict,
    cancel_event: threading.Event = None
) -> Tuple[Dict[str, Any], list]:
    """
    Executes the vision graph:
    1. Plan step
    2. Vision VLM / OCR call
    3. Verification gate
    
    Returns (result_dict, trace_events).
    """
    trace_events = []
    raw_path = graph_input.get("image_path", "")
    image_path = resolve_image_path(raw_path) if raw_path else ""
    prompt = graph_input.get("prompt", "") or graph_input.get("instruction", "Extract all key information from this image")

    # 1. Plan
    trace_events.append({
        "task_id": task_id,
        "step": "plan",
        "payload": {
            "plan": "Analyze visual input with Qwen2.5-VL → extract structured fields and findings",
            "task_type": "extraction",
            "retry_count": 0
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

    # 2. Tool call
    tool_input_data = {
        "image_path": image_path,
        "extract_mode": "both",
        "user_prompt": prompt
    }
    tool_res = _run_tool("vision", tool_input_data)
    success = tool_res.get("success", False)

    trace_events.append({
        "task_id": task_id,
        "step": "tool_call",
        "payload": {
            "tool_name": "vision",
            "input_summary": {"image_path": image_path, "prompt": prompt[:80]},
            "success": success
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

    data = tool_res.get("data", {})
    fields = data.get("fields", data.get("extracted_fields", {}))
    analysis = data.get("response", data.get("raw_response", ""))

    if isinstance(fields, dict) and not analysis:
        if "raw_response" in fields:
            analysis = fields["raw_response"]
        else:
            analysis = "\n".join(f"- {k}: {v}" for k, v in fields.items())

    # 3. Verification
    if success and (fields or analysis):
        field_count = len(fields) if isinstance(fields, dict) else 1
        trace_events.append({
            "task_id": task_id,
            "step": "verify_pass",
            "payload": {
                "detail": f"Extracted visual findings successfully ({field_count} fields)",
                "verification_type": "extraction",
                "retry_count": 0
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        output = {
            "success": True,
            "fields": fields,
            "analysis": analysis,
            "status": "extracted"
        }
        return output, trace_events
    else:
        err = tool_res.get("error", "Vision analysis failed")
        trace_events.append({
            "task_id": task_id,
            "step": "verify_fail",
            "payload": {
                "detail": err,
                "verification_type": "extraction",
                "retry_count": 0
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        return {"success": False, "error": err}, trace_events
