"""
Artifact generation node — produces the final deliverable.

Calls into the artifact factory tools (docx, xlsx) via the tool registry,
or writes code files directly for codegen tasks. Emits 'generate' and
'done' trace events.

Falls back gracefully if artifact tools aren't available yet (other
team members' code) by writing a plain text output.
"""
from orchestrator.agent_graph.state import AgentState
from datetime import datetime, timezone
import os
import json
from artifact_factory.docx_builder import generate_docx
from artifact_factory.xlsx_builder import generate_xlsx


def _should_produce_artifact(task_input: dict, task_type: str) -> bool:
    """Determine whether the task explicitly requests a file artifact.

    Only produce a file when the user's instructions clearly ask for a
    document, report, note, spreadsheet, etc.  Regular prompts like
    'write code for X' or 'explain Y' should NOT produce a file.
    """
    content = task_input.get("content", "").lower()
    context = task_input.get("context", {})
    original = str(context.get("original_instructions", "")).lower()
    combined = content + " " + original

    # Extraction from an uploaded file always produces a report
    modality = task_input.get("modality", "text")
    if modality in ("image", "file"):
        return True

    artifact_keywords = [
        "generate report", "draft note", "approval note", "create document",
        "write report", "produce file", "export", "download",
        "save as", ".docx", "docx", ".xlsx", "xlsx", ".pdf", "pdf", "spreadsheet_generation",
        "draft approval", "draft document", "word document", "word doc", "excel",
        "slides", "presentation", ".pptx", "powerpoint", "deck"
    ]
    return any(kw in combined for kw in artifact_keywords)


def _wants_slides(task_input: dict) -> bool:
    content = task_input.get("content", "").lower()
    context = task_input.get("context", {})
    original = str(context.get("original_instructions", "")).lower()
    combined = content + " " + original
    return any(kw in combined for kw in ["slides", "presentation", ".pptx", "powerpoint", "deck", "ppt"])


async def _generate_document_summary(state: AgentState, latest_data: dict, artifact: dict, stream_callback=None) -> str:
    """Produces and streams a professional final summary and conclusion for the generated document."""
    doc_data = latest_data.get("doc_data", {})
    title = doc_data.get("title", artifact.get("filename", "Official Document"))
    doc_type = doc_data.get("doc_type", "document").capitalize()
    filename = artifact.get("filename", "")
    sop_used = latest_data.get("sop_used", False)
    sop_chunks = latest_data.get("sop_chunks", [])
    action_items = doc_data.get("action_items_or_recommendations", [])

    sop_status_desc = (
        "Complies with Standard Operating Procedures found in knowledge base."
        if sop_used else
        "Drafted in accordance with standard industrial maintenance protocols (no specific SOP overrides attached)."
    )

    actions_bullets = "\n".join([f"- {item}" for item in action_items[:4]]) if action_items else "- Direct operational review required"

    fallback_summary = (
        f"I have successfully drafted the official **{title}** and generated the formatted `{filename}` document.\n\n"
        f"### Summary of Document Provisions:\n"
        f"- **Document Category:** {doc_type}\n"
        f"- **Subject:** {title}\n"
        f"- **SOP Alignment:** {sop_status_desc}\n"
        f"- **Key Directives & Precautions:**\n{actions_bullets}\n\n"
        f"The official Word document is available for download below."
    )

    try:
        from orchestrator.agent_graph.nodes.tool_call import _get_model_config, _call_llm_async
        model_config = _get_model_config(state)

        system_prompt = (
            "You are SetuAI, an elite industrial operations assistant. "
            "A technical document artifact has just been drafted and verified by the pipeline. "
            "Your task is to present an articulate, professional final summary and conclusion to the user "
            "explaining what was written inside the document, key sections, timeline, safety rules, "
            "and SOP compliance status. "
            "Format cleanly with Markdown. Do NOT include chat greetings like 'Hello' or 'Certainly'."
        )

        user_prompt = (
            f"Document Title: {title}\n"
            f"Document Type: {doc_type}\n"
            f"Output File: {filename}\n"
            f"SOP Status: {sop_status_desc}\n"
            f"Key Actions/Directives: {', '.join(action_items[:4])}\n\n"
            "Provide the final summary and conclusion of the document for the user:"
        )

        summary = await _call_llm_async(
            model_config=model_config,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            timeout=45,
            stream_callback=stream_callback
        )
        if summary and len(summary.strip()) > 30:
            return summary.strip()
    except Exception as e:
        print(f"[generate_node] LLM summary generation notice: {e}")

    if stream_callback:
        await stream_callback(fallback_summary)
    return fallback_summary


async def generate_node(state: AgentState) -> dict:
    """Generate final artifacts (only when explicitly requested) and emit done event."""
    task_type = state.get("task_type", "document_generation")
    task_id = state.get("task_id", "unknown")
    task_input = state.get("task_input", {})
    trace_events = list(state.get("trace_events", []))
    artifacts = list(state.get("artifacts", []))
    tool_results = state.get("tool_results", [])
    verification_status = state.get("verification_status", "pending")

    # Setup stream_callback for streaming the final conclusion
    from backend.gateway.websocket_manager import manager
    async def stream_callback(chunk: str):
        if chunk:
            payload = {
                "task_id": task_id,
                "step": "stream_chunk",
                "payload": {"chunk": chunk},
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            await manager.broadcast_event(task_id, json.dumps(payload))

    # Get latest tool result data
    latest_data = {}
    if tool_results:
        latest = tool_results[-1]
        latest_data = latest.get("data", {}) if isinstance(latest, dict) else {}

    needs_review = verification_status == "failed"
    content = task_input.get("content", "")

    # Check if artifact was already created by tool_call_node
    existing_artifact = latest_data.get("artifact")
    if existing_artifact and existing_artifact not in artifacts:
        artifacts.append(existing_artifact)

    # -------------------------------------------------------------------
    # Path A: An artifact was produced by the tool call
    # -------------------------------------------------------------------
    if artifacts:
        artifact = artifacts[-1]

        # Emit 'generate' event for artifact creation
        trace_events.append({
            "task_id": task_id,
            "step": "generate",
            "payload": {
                "artifact_type": artifact.get("type", "unknown"),
                "filename": artifact.get("filename", "")
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

        if task_type in ["document_generation", "drafting", "spreadsheet_generation"]:
            summary = await _generate_document_summary(state, latest_data, artifact, stream_callback)
        else:
            review_tag = " [NEEDS HUMAN REVIEW]" if needs_review else ""
            summary = f"Generated {artifact.get('type', 'file')}: {artifact.get('filename', 'unknown')}{review_tag}"

    # -------------------------------------------------------------------
    # Path B: Fallback artifact generation if explicitly requested
    # -------------------------------------------------------------------
    elif _should_produce_artifact(task_input, task_type):
        outputs_dir = os.path.join(os.getcwd(), "outputs")
        os.makedirs(outputs_dir, exist_ok=True)

        try:
            artifact = None
            findings = []
            fields = latest_data.get("fields", latest_data.get("extracted_fields", {}))
            if not isinstance(fields, dict):
                fields = {"Result": str(fields)}

            for k, v in fields.items():
                if k != "raw_response":
                    findings.append({"field": k, "value": v, "status": "Extracted"})
            if "raw_response" in fields:
                findings.append({"field": "Raw Output", "value": fields["raw_response"], "status": "Text"})

            if task_type in ["extraction", "document_generation"]:
                draft_content = latest_data.get("draft", latest_data.get("generated_text", ""))
                if "raw_response" in fields and not findings and not draft_content:
                    draft_content = fields["raw_response"]

                data = {
                    "doc_type": "report" if task_type == "extraction" else "notice",
                    "title": f"Report — {content[:80]}" if task_type == "document_generation" else "Image Extraction Report",
                    "company_or_org": "Setu Industrial Corporation",
                    "department": "Extraction Services" if task_type == "extraction" else "Operations & Maintenance Division",
                    "findings": findings,
                    "body_content": draft_content,
                    "action_items_or_recommendations": []
                }
                result = generate_docx(data, outputs_dir)
                if result.get("success"):
                    artifact = {
                        "type": "docx",
                        "filename": result.get("filename"),
                        "path": result.get("path")
                    }
            elif task_type in ["numeric_verify", "spreadsheet_generation"]:
                # Carry through LLM-generated tables from doc_data if available
                doc_data = latest_data.get("doc_data", {})
                data = {
                    "title": doc_data.get("title", f"Spreadsheet Report" if task_type == "spreadsheet_generation" else f"Verification Report - {content[:60]}"),
                    "findings": findings if findings else doc_data.get("findings", []),
                }
                # Preserve tables so xlsx_builder uses the structured-data branch
                if doc_data.get("tables"):
                    data["tables"] = doc_data["tables"]
                result = generate_xlsx(data, outputs_dir)
                if result.get("success"):
                    artifact = {
                        "type": "xlsx",
                        "filename": result.get("filename"),
                        "path": result.get("path")
                    }
            elif task_type == "code_generation":
                filename = f"{task_id}_code.py"
                path = os.path.join(outputs_dir, filename)
                code = latest_data.get("generated_code", "# No code generated\n")
                with open(path, "w") as f:
                    f.write(code)
                artifact = {
                    "type": "py",
                    "filename": filename,
                    "path": path
                }

            if artifact:
                artifacts.append(artifact)
                trace_events.append({
                    "task_id": task_id,
                    "step": "generate",
                    "payload": {
                        "artifact_type": artifact.get("type", "unknown"),
                        "filename": artifact.get("filename", "")
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
                summary = await _generate_document_summary(state, latest_data, artifact, stream_callback)
            else:
                summary = "Failed to generate artifact."

        except Exception as e:
            summary = f"Failed to generate artifact: {str(e)}"

    # -------------------------------------------------------------------
    # Path C: No artifact requested — return inline conversational results
    # -------------------------------------------------------------------
    else:
        review_tag = " [NEEDS HUMAN REVIEW]" if needs_review else ""

        if task_type == "code_generation":
            code = latest_data.get("generated_code", "")
            test_log = latest_data.get("stdout", "")
            summary = f"Code generation complete.{review_tag}"
            if code:
                summary += f"\n\n```python\n{code}\n```"
            if test_log:
                summary += f"\n\n**Test output:**\n```\n{test_log[:300]}\n```"
        elif task_type == "extraction":
            fields = latest_data.get("fields", latest_data.get("extracted_fields", {}))
            summary = f"Extracted {len(fields)} fields.{review_tag}"
            if fields:
                summary += "\n\n| Field | Value |\n|---|---|\n"
                summary += "\n".join(f"| {k} | {v} |" for k, v in fields.items())
        elif task_type == "numeric_verify":
            computed = latest_data.get("computed_value", "?")
            expected = latest_data.get("expected", "?")
            passed = latest_data.get("passed", False)
            status_badge = "🟩 PASSED" if passed else "🟥 FAILED"
            summary = (
                f"Numeric verification **{status_badge}**{review_tag}\n\n"
                f"• **Computed:** `{computed}`\n"
                f"• **Expected:** `{expected}`"
            )
        elif task_type in ["document_generation", "drafting"]:
            generated = latest_data.get("generated_text", latest_data.get("draft", ""))
            summary = generated or "Drafting completed."
        elif task_type == "conversational":
            response = latest_data.get("response", latest_data.get("generated_text", ""))
            summary = response or "I'm sorry, I couldn't generate a response. The LLM service may be unavailable."
        else:
            summary = f"Task complete.{review_tag}"

    # Emit 'done' event
    trace_events.append({
        "task_id": task_id,
        "step": "done",
        "payload": {
            "summary": summary,
            "artifacts": artifacts
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

    return {
        "artifacts": artifacts,
        "final_summary": summary,
        "trace_events": trace_events
    }



