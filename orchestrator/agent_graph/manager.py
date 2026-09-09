"""
SetuAI Manager Agent — Central ReAct Orchestrator Protocol.

Replaces the old classifier system with an intelligent Manager Agent (DeepSeek-R1)
that serves as SetuAI. It converses directly with users and dynamically orchestrates
specialist sub-graphs (codegen_graph, drafting_graph, vision_graph, numeric_verify_graph)
using a sequential ReAct (Reasoning + Acting) loop.
"""
import os
import json
import re
import asyncio
from datetime import datetime, timezone
from typing import AsyncGenerator, Dict, Any, List, Optional
import threading

from orchestrator.agent_graph.nodes.tool_call import (
    _get_model_config,
    _call_llm_async,
    _extract_json_from_text,
    _get_cancel_event,
    _cleanup_cancel_event
)
from orchestrator.agent_graph.subgraphs.codegen_graph import run_codegen_graph
from orchestrator.agent_graph.subgraphs.drafting_graph import run_drafting_graph
from orchestrator.agent_graph.subgraphs.vision_graph import run_vision_graph
from orchestrator.agent_graph.subgraphs.numeric_verify_graph import run_numeric_verify_graph


# System prompt defining the SetuAI persona and specialist sub-graph capabilities
MANAGER_SYSTEM_PROMPT = """You are SetuAI, an elite AI operating system for industrial engineering, plant operations, code generation, technical document drafting, and verification.

You can converse naturally, professionally, and helpful with users.
When the user asks you to perform technical tasks, you act as the Manager Agent and can execute specialist sub-graphs to carry out technical operations.

AVAILABLE SPECIALIST SUB-GRAPHS:
1. codegen_graph:
   - Purpose: Generates and rigorously tests Python code inside an isolated sandbox environment.
   - Input format: {"instruction": "<what python code to write and test>"}
   - Returns: Verified python code, test suite execution results, and pass/fail status.

2. drafting_graph:
   - Purpose: Creates official, professionally styled Microsoft Word (.docx), Excel (.xlsx), or PowerPoint (.pptx) documents. Checks SOP knowledge base, applies official formatting (notices, letters, reports, memos), and verifies creation on disk.
   - Input format: {
       "instruction": "<what document to draft>",
       "doc_type": "notice" | "letter" | "memo" | "report" | "standard",
       "format": "docx" | "xlsx" | "pptx",
       "title": "<optional title>",
       "data": "<optional attached code, data, or prior graph results to include in document>"
     }
   - Returns: Downloadable file artifact details (filename, path, doc_type, sop_used).

3. visual_extraction_graph:
   - Purpose: Analyzes uploaded engineering drawings, plant images, or documents using Vision-Language Models (Qwen2.5-VL) and OCR.
   - Input format: {"prompt": "<what to extract or analyze>", "image_path": "<path to image>"}
   - Returns: Extracted fields and visual analysis.

4. numeric_verify_graph:
   - Purpose: Verifies engineering calculations, unit conversions, and formulas against tolerances in sandbox.
   - Input format: {"expression": "<calculation>", "expected": <numeric value>}
   - Returns: Verification pass/fail status.

HOW YOU OPERATE (ReAct Protocol):
- If the user's message is conversational (greetings, general inquiry, explanations that do not require running code or producing files), respond with:
  {"action": "respond", "thought": "This is conversational."}
- If the user asks for a technical task (writing code, generating a document/report/notice, analyzing an image, verifying numbers), choose the FIRST required graph and output ONLY a JSON action block:
  ```json
  {
    "thought": "<your reasoning on why this graph is needed first>",
    "action": "run_graph",
    "graph_name": "<codegen_graph | drafting_graph | visual_extraction_graph | numeric_verify_graph>",
    "graph_input": { ... }
  }
  ```
- MULTI-STEP SEQUENTIAL CHAINING:
  If the user asks for a composite task (e.g. "write python code for X and produce a report of that code in a docx file"):
  1. First call `codegen_graph` to generate and verify the code.
  2. You will receive the verified code in an Observation.
  3. Then call `drafting_graph` passing the verified code in the `data` field to produce the .docx report.
  4. Once all graphs finish, finalize with `{"action": "respond"}`.

RULES:
- Always output a valid JSON action block during planning.
- Do NOT output markdown code fences around your JSON if possible, or use standard ```json ... ```.
"""


def _get_manager_model(task_input: dict) -> dict:
    """Finds configured manager model from settings.json, user model override, or deepseek-r1."""
    override = task_input.get("model_override")
    registry_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "models_registry"
    )
    models_path = os.path.join(registry_dir, "models.json")
    settings_path = os.path.join(registry_dir, "settings.json")

    manifest = []
    try:
        if os.path.exists(models_path):
            with open(models_path, "r") as f:
                manifest = json.load(f)
    except Exception:
        pass

    # 1. User task override
    if override and override != "auto":
        for m in manifest:
            if m.get("name") == override:
                return m
        return {"name": override, "endpoint": "http://localhost:11434/v1"}

    # 2. Configured manager_model in settings.json
    configured_manager = ""
    try:
        if os.path.exists(settings_path):
            with open(settings_path, "r") as f:
                s_data = json.load(f)
                configured_manager = s_data.get("manager_model", "")
    except Exception:
        pass

    if configured_manager:
        for m in manifest:
            if m.get("name") == configured_manager:
                return m
        return {"name": configured_manager, "endpoint": "http://localhost:11434/v1"}

    # 3. Model explicitly assigned role "manager" or is_manager flag
    for m in manifest:
        if m.get("role") == "manager" or m.get("is_manager"):
            return m

    # 4. Fallback: reasoning / deepseek
    for m in manifest:
        if "deepseek" in m.get("name", "") or "reasoning" in m.get("role", ""):
            return m

    if manifest:
        return manifest[0]

    return {"name": "deepseek-r1:8b", "endpoint": "http://localhost:11434/v1"}


async def run_manager_agent(task_input: dict) -> AsyncGenerator[dict, None]:
    """
    Main entrypoint for the SetuAI ReAct Manager Agent.
    Yields TraceEvents as it reasons, calls specialist sub-graphs, and streams responses.
    """
    task_id = task_input.get("task_id", f"task_{int(datetime.now(timezone.utc).timestamp())}")
    user_content = task_input.get("content", "").strip()
    modality = task_input.get("modality", "text")
    context = task_input.get("context", {})
    chat_history = context.get("chat_history", [])
    manager_model = _get_manager_model(task_input)

    cancel_event = _get_cancel_event(task_id)

    # 1. Emit manager initialization event (compatible with frontend trace & model badge)
    yield {
        "task_id": task_id,
        "step": "manager",
        "payload": {
            "selected_model": manager_model,
            "agent": "SetuAI Manager",
            "protocol": "ReAct"
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    # Setup WebSocket streaming helper
    from backend.gateway.websocket_manager import manager as ws_manager
    async def stream_chunk_callback(chunk: str):
        if chunk and not cancel_event.is_set():
            payload = {
                "task_id": task_id,
                "step": "stream_chunk",
                "payload": {"chunk": chunk},
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            await ws_manager.broadcast_event(task_id, json.dumps(payload))

    # Check if this is an image extraction request from modality
    image_path = ""
    if modality in ["image", "file"] and os.path.exists(user_content):
        image_path = user_content

    # ReAct state tracking
    observations: List[Dict[str, Any]] = []
    collected_artifacts: List[Dict[str, Any]] = []
    max_steps = 4
    step_num = 0

    while step_num < max_steps:
        if cancel_event.is_set():
            break

        step_num += 1

        # Format past observations for the manager
        obs_text = ""
        if observations:
            obs_lines = []
            for i, obs in enumerate(observations, 1):
                graph = obs.get("graph_name", "unknown")
                data = obs.get("output", {})
                obs_lines.append(f"Observation {i} [from {graph}]:\n{json.dumps(data, indent=2)}")
            obs_text = "\n\nPREVIOUS SUB-GRAPH OBSERVATIONS:\n" + "\n\n".join(obs_lines)

        user_prompt = f"User Request: {user_content}"
        if image_path:
            user_prompt += f"\nUploaded image path: {image_path}"
        if obs_text:
            user_prompt += obs_text
            user_prompt += "\n\nBased on the observations above, decide your next action: run another graph or respond to the user."
        else:
            user_prompt += "\n\nDecide your action: respond conversationally or run a specialist sub-graph."

        # Query manager agent for decision
        raw_decision = await _call_llm_async(
            model_config=manager_model,
            system_prompt=MANAGER_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            timeout=60,
            chat_history=chat_history if step_num == 1 else None,
            cancel_event=cancel_event
        )

        decision_json = _extract_json_from_text(raw_decision)
        action = "respond"
        graph_name = ""
        graph_input = {}
        thought = ""

        if decision_json and isinstance(decision_json, dict):
            action = decision_json.get("action", "respond")
            graph_name = decision_json.get("graph_name", "")
            graph_input = decision_json.get("graph_input", {})
            thought = decision_json.get("thought", "")

        # Auto-detect intent if LLM was indecisive on step 1
        if step_num == 1 and action != "run_graph":
            lower_req = user_content.lower()
            needs_doc = any(k in lower_req for k in [".docx", "docx", "word doc", "notice", "letter", "memorandum", ".xlsx", "spreadsheet", "excel", ".pptx", "slides", "presentation"])
            needs_code = any(k in lower_req for k in ["python code", "write a script", "write code", "code for", "program that"])
            has_image = bool(image_path or modality in ["image", "file"])

            if has_image:
                action = "run_graph"
                graph_name = "visual_extraction_graph"
                graph_input = {"prompt": user_content, "image_path": image_path}
                thought = "Uploaded image detected. Delegating to visual_extraction_graph."
            elif needs_code and needs_doc:
                # Sequential multi-step request: start with code
                action = "run_graph"
                graph_name = "codegen_graph"
                graph_input = {"instruction": user_content}
                thought = "User requested both code and a document. Executing codegen_graph first to get verified code."
            elif needs_code:
                action = "run_graph"
                graph_name = "codegen_graph"
                graph_input = {"instruction": user_content}
                thought = "Code generation requested. Delegating to codegen_graph."
            elif needs_doc:
                fmt = "xlsx" if any(k in lower_req for k in ["xlsx", "spreadsheet", "excel"]) else ("pptx" if any(k in lower_req for k in ["pptx", "slides", "presentation"]) else "docx")
                doc_type = "notice" if "notice" in lower_req else ("letter" if "letter" in lower_req else ("report" if "report" in lower_req else "standard"))
                action = "run_graph"
                graph_name = "drafting_graph"
                graph_input = {"instruction": user_content, "format": fmt, "doc_type": doc_type}
                thought = f"Document generation requested. Delegating to drafting_graph for {fmt}."

        # If action is to run a graph
        if action == "run_graph" and graph_name:
            yield {
                "task_id": task_id,
                "step": "plan",
                "payload": {
                    "plan": f"SetuAI Manager: {thought or f'Executing {graph_name}'}",
                    "task_type": graph_name,
                    "retry_count": 0
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

            sub_res = {}
            sub_events = []

            # Execute the chosen sub-graph
            if graph_name == "codegen_graph":
                sub_res, sub_events = await run_codegen_graph(task_id, graph_input, cancel_event)
            elif graph_name == "drafting_graph":
                sub_res, sub_events = await run_drafting_graph(task_id, graph_input, cancel_event)
            elif graph_name in ["vision_graph", "visual_extraction_graph"]:
                sub_res, sub_events = await run_vision_graph(task_id, graph_input, cancel_event)
            elif graph_name == "numeric_verify_graph":
                sub_res, sub_events = await run_numeric_verify_graph(task_id, graph_input, cancel_event)

            # Yield each event from the sub-graph live to the frontend
            for evt in sub_events:
                yield evt

            # Collect any generated artifact
            if isinstance(sub_res, dict) and sub_res.get("artifact"):
                art = sub_res["artifact"]
                if art not in collected_artifacts:
                    collected_artifacts.append(art)

            observations.append({
                "graph_name": graph_name,
                "output": sub_res
            })

            # Check if user requested code AND document and we just finished codegen
            lower_req = user_content.lower()
            wants_both = any(k in lower_req for k in [".docx", "docx", "word doc", "report"]) and \
                         any(k in lower_req for k in ["python code", "write a script", "write code", "code for"])
            
            if wants_both and graph_name == "codegen_graph" and sub_res.get("code"):
                # Automatically chain to drafting_graph with verified code
                code_text = sub_res.get("code", "")
                test_status = "PASSED" if sub_res.get("passed") else "FAILED"
                doc_title = f"Technical Report: Code Implementation"
                
                chain_input = {
                    "instruction": f"Generate a technical engineering report for the user request: '{user_content}'. Include detailed architecture, operational principles, and the verified Python code.",
                    "doc_type": "report",
                    "format": "docx",
                    "title": doc_title,
                    "data": f"Verified Python Code ({test_status}):\n```python\n{code_text}\n```"
                }

                yield {
                    "task_id": task_id,
                    "step": "plan",
                    "payload": {
                        "plan": "SetuAI Manager: Code generation and verification complete. Now executing drafting_graph to produce the official Word document report.",
                        "task_type": "drafting_graph",
                        "retry_count": 0
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }

                doc_res, doc_events = await run_drafting_graph(task_id, chain_input, cancel_event)
                for evt in doc_events:
                    yield evt

                if isinstance(doc_res, dict) and doc_res.get("artifact"):
                    art = doc_res["artifact"]
                    if art not in collected_artifacts:
                        collected_artifacts.append(art)

                observations.append({
                    "graph_name": "drafting_graph",
                    "output": doc_res
                })
                break

            # If user only requested a single task (and not a composite multi-task), proceed to synthesis
            if not wants_both:
                break

            continue

        # If action is respond or no more graphs to run, break to final response
        break

    # -------------------------------------------------------------------
    # Final Response Synthesis (Streamed to User)
    # -------------------------------------------------------------------
    if cancel_event.is_set():
        yield {
            "task_id": task_id,
            "step": "done",
            "payload": {"summary": "Task was cancelled.", "artifacts": []},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        _cleanup_cancel_event(task_id)
        return

    # Prepare synthesis prompt for the Manager
    synthesis_system = (
        "You are SetuAI, an elite AI operating system for industrial engineering, plant operations, code generation, and verification. "
        "Provide a comprehensive, authoritative, beautifully structured final response to the user. "
        "Present any code in clean Markdown blocks, summarize test verification results, and reference any generated files. "
        "Speak directly and professionally as SetuAI."
    )

    if observations:
        synthesis_prompt = f"User Request: {user_content}\n\nCompleted Sub-Graph Results:\n"
        for obs in observations:
            g_name = obs.get("graph_name")
            out = obs.get("output", {})
            if g_name == "codegen_graph":
                synthesis_prompt += f"\n- Codegen Result: Sandbox tests {'PASSED' if out.get('passed') else 'FAILED'}.\nCode:\n```python\n{out.get('code', '')}\n```\n"
            elif g_name == "drafting_graph":
                synthesis_prompt += f"\n- Document Generated: `{out.get('filename')}` (Title: {out.get('title')}, SOP Aligned: {out.get('sop_used')}).\n"
            elif g_name in ["vision_graph", "visual_extraction_graph"]:
                synthesis_prompt += f"\n- Visual Findings: {out.get('analysis', '')}\nFields: {json.dumps(out.get('fields', {}))}\n"
            elif g_name == "numeric_verify_graph":
                synthesis_prompt += f"\n- Numeric Check: {'PASSED' if out.get('passed') else 'FAILED'} (Computed: {out.get('computed_value')}, Expected: {out.get('expected')})\n"
        synthesis_prompt += "\nSynthesize the complete final answer for the user now:"
    else:
        synthesis_prompt = user_content

    final_response = await _call_llm_async(
        model_config=manager_model,
        system_prompt=synthesis_system,
        user_prompt=synthesis_prompt,
        timeout=90,
        chat_history=chat_history,
        stream_callback=stream_chunk_callback,
        cancel_event=cancel_event
    )

    if not final_response or len(final_response.strip()) < 5:
        # Fallback summary
        if collected_artifacts:
            art = collected_artifacts[0]
            final_response = f"I have processed your request and generated `{art.get('filename')}`. You can download the file below."
        elif observations:
            final_response = "I have completed the requested operations successfully."
        else:
            final_response = "Hello! I am SetuAI, your AI engineering and plant operations assistant. How may I assist you today?"
        await stream_chunk_callback(final_response)

    # Emit final 'done' event
    yield {
        "task_id": task_id,
        "step": "done",
        "payload": {
            "summary": final_response,
            "artifacts": collected_artifacts
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    _cleanup_cancel_event(task_id)
