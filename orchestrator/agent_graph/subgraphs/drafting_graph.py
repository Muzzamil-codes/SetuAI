"""
Drafting Graph — specialist sub-graph for document, spreadsheet, and slide generation.
Executed as a discrete tool/sub-graph by the SetuAI Manager Agent.
"""
from datetime import datetime, timezone
import json
import os
import threading
from typing import Tuple, Dict, Any

from orchestrator.agent_graph.nodes.tool_call import (
    _get_model_config,
    _run_tool,
    _try_retrieval,
    _llm_generate_tool_args
)


def _get_manager_model() -> dict:
    """Finds configured manager model from settings.json, models.json, or fallback."""
    try:
        reg_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "models_registry"
        )
        settings_path = os.path.join(reg_dir, "settings.json")
        models_path = os.path.join(reg_dir, "models.json")

        manifest = []
        if os.path.exists(models_path):
            with open(models_path, "r") as f:
                manifest = json.load(f)

        if os.path.exists(settings_path):
            with open(settings_path, "r") as f:
                s_data = json.load(f)
                conf = s_data.get("manager_model", "")
                if conf:
                    for m in manifest:
                        if m.get("name") == conf:
                            return m
                    return {"name": conf, "endpoint": "http://localhost:11434/v1"}

        for m in manifest:
            if m.get("role") == "manager" or m.get("is_manager"):
                return m
        for m in manifest:
            if "deepseek" in m.get("name", "") or "reasoning" in m.get("role", ""):
                return m
        if manifest:
            return manifest[0]
    except Exception:
        pass
    return {"name": "deepseek-r1:8b", "endpoint": "http://localhost:11434/v1"}


async def run_drafting_graph(
    task_id: str,
    graph_input: dict,
    cancel_event: threading.Event = None,
    manager_model: dict = None
) -> Tuple[Dict[str, Any], list]:
    """
    Executes the drafting graph:
    1. Plan step
    2. SOP RAG retrieval & check
    3. Tool schema synthesis (docx / xlsx / pptx)
    4. Tool execution (artifact_factory)
    5. File integrity verification
    6. Generate event
    
    Returns (result_dict, trace_events).
    """
    trace_events = []
    instruction = graph_input.get("instruction", "") or graph_input.get("prompt", "")
    fmt = (graph_input.get("format") or "docx").lower()
    doc_type = graph_input.get("doc_type", "")
    attached_data = graph_input.get("data", "")
    title_hint = graph_input.get("title", "")

    # 1. Determine tool
    if "pptx" in fmt or "slide" in fmt or "presentation" in fmt:
        tool_name = "pptx"
    elif "xlsx" in fmt or "sheet" in fmt or "excel" in fmt:
        tool_name = "xlsx"
    else:
        tool_name = "docx"

    model_config = manager_model or _get_manager_model()

    # 2. Plan event
    lower_inst = instruction.lower()
    needs_sop = any(k in lower_inst for k in ["sop", "sops", "procedure", "standard operating", "knowledge base"])
    plan_text = f"Check SOPs in knowledge base → synthesize parameters for {tool_name} → verify file integrity" if needs_sop else f"Synthesize parameters for {tool_name} from source input → verify file integrity"
    trace_events.append({
        "task_id": task_id,
        "step": "plan",
        "payload": {
            "plan": plan_text,
            "task_type": "document_generation",
            "retry_count": 0
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

    # 3. Check SOPs only if explicitly requested
    sop_chunks = []
    if needs_sop:
        raw_sops = _try_retrieval(instruction)
        sop_chunks = [c for c in raw_sops if c.get("score", 0) >= 0.40]
    sop_used = len(sop_chunks) > 0

    # Combine instruction with attached data (e.g. verified python code)
    combined_prompt = instruction
    if attached_data:
        combined_prompt += f"\n\nATTACHED REFERENCE DATA / CODE TO INCLUDE IN DOCUMENT:\n{attached_data}"
    if title_hint:
        combined_prompt += f"\nDOCUMENT TITLE HINT: {title_hint}"
    if doc_type:
        combined_prompt += f"\nDOCUMENT TYPE HINT: {doc_type}"

    # 4. LLM synthesize structured arguments matching tool schema
    tool_input_data = await _llm_generate_tool_args(
        model_config=model_config,
        user_request=combined_prompt,
        tool_name=tool_name,
        sop_chunks=sop_chunks,
        cancel_event=cancel_event
    )

    if doc_type and "doc_type" in tool_input_data:
        tool_input_data["doc_type"] = doc_type
    if title_hint and not tool_input_data.get("title"):
        tool_input_data["title"] = title_hint

    # 5. Execute tool
    tool_res = _run_tool(tool_name, tool_input_data)
    success = tool_res.get("success", False)

    trace_events.append({
        "task_id": task_id,
        "step": "tool_call",
        "payload": {
            "tool_name": tool_name,
            "input_summary": {
                "title": tool_input_data.get("title", ""),
                "doc_type": tool_input_data.get("doc_type", tool_name)
            },
            "success": success
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

    # 6. Verification gate
    file_path = tool_res.get("data", {}).get("path") or tool_res.get("data", {}).get("file_path")
    filename = tool_res.get("data", {}).get("filename", f"document.{tool_name}")

    if success and file_path and os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        size_kb = round(os.path.getsize(file_path) / 1024, 1)
        sop_note = " (SOP aligned)" if sop_used else ""
        trace_events.append({
            "task_id": task_id,
            "step": "verify_pass",
            "payload": {
                "detail": f"Verified {filename} ({size_kb} KB) generated successfully{sop_note}",
                "verification_type": "document_generation",
                "retry_count": 0
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

        artifact = {
            "type": tool_name,
            "filename": filename,
            "path": file_path
        }

        trace_events.append({
            "task_id": task_id,
            "step": "generate",
            "payload": {
                "artifact_type": tool_name,
                "filename": filename,
                "artifact": artifact
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

        output = {
            "success": True,
            "artifact": artifact,
            "title": tool_input_data.get("title", filename),
            "doc_type": tool_input_data.get("doc_type", tool_name),
            "sop_used": sop_used,
            "filename": filename,
            "path": file_path
        }
        return output, trace_events
    else:
        err = tool_res.get("error", "Failed to verify generated document on disk")
        trace_events.append({
            "task_id": task_id,
            "step": "verify_fail",
            "payload": {
                "detail": err,
                "verification_type": "document_generation",
                "retry_count": 0
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        return {"success": False, "error": err}, trace_events
