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
        "save as", ".docx", ".xlsx", ".pdf", "spreadsheet",
        "draft approval", "draft document",
        "slides", "presentation", ".pptx", "powerpoint", "deck"
    ]
    return any(kw in combined for kw in artifact_keywords)


def _wants_slides(task_input: dict) -> bool:
    content = task_input.get("content", "").lower()
    context = task_input.get("context", {})
    original = str(context.get("original_instructions", "")).lower()
    combined = content + " " + original
    return any(kw in combined for kw in ["slides", "presentation", ".pptx", "powerpoint", "deck", "ppt"])


def generate_node(state: AgentState) -> dict:
    """Generate final artifacts (only when explicitly requested) and emit done event."""
    task_type = state.get("task_type", "drafting")
    task_id = state.get("task_id", "unknown")
    task_input = state.get("task_input", {})
    trace_events = list(state.get("trace_events", []))
    artifacts = list(state.get("artifacts", []))
    tool_results = state.get("tool_results", [])
    verification_status = state.get("verification_status", "pending")

    # Get latest tool result data
    latest_data = {}
    if tool_results:
        latest = tool_results[-1]
        latest_data = latest.get("data", {}) if isinstance(latest, dict) else {}

    needs_review = verification_status == "failed"
    content = task_input.get("content", "")

    # -------------------------------------------------------------------
    # Only produce a file artifact if the task explicitly asks for one
    # -------------------------------------------------------------------
    if _should_produce_artifact(task_input, task_type):
        outputs_dir = os.path.join(os.getcwd(), "outputs")
        os.makedirs(outputs_dir, exist_ok=True)

        try:
            artifact = None
            if task_type in ["extraction", "drafting"]:
                data = {
                    "title": f"Approval Note — {content[:80]}",
                    "company": "Setu",
                    "reviewer": "AI Agent",
                    "department": "Engineering",
                    "findings": [],
                    "recommendations": []
                }
                result = generate_docx(data, outputs_dir)
                if result.get("success"):
                    artifact = {
                        "type": "docx",
                        "filename": result.get("filename"),
                        "path": result.get("path")
                    }
            elif task_type == "numeric_verify":
                data = {
                    "title": f"Verification Report - {content[:60]}",
                    "findings": []
                }
                result = generate_xlsx(data, outputs_dir)
                if result.get("success"):
                    artifact = {
                        "type": "xlsx",
                        "filename": result.get("filename"),
                        "path": result.get("path")
                    }
            elif task_type == "codegen":
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
            else:
                filename = f"{task_id}_output.txt"
                path = os.path.join(outputs_dir, filename)
                with open(path, "w") as f:
                    f.write(content)
                artifact = {
                    "type": "txt",
                    "filename": filename,
                    "path": path
                }

            if artifact:
                artifacts.append(artifact)
                review_tag = " [NEEDS HUMAN REVIEW]" if needs_review else ""
                summary = (
                    f"Generated {artifact.get('type', 'file')}: "
                    f"{artifact.get('filename', 'unknown')}{review_tag}"
                )

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
            else:
                summary = "Failed to generate artifact."

        except Exception as e:
            summary = f"Failed to generate artifact: {str(e)}"

    else:
        # ----- No file artifact requested — return results inline -----
        review_tag = " [NEEDS HUMAN REVIEW]" if needs_review else ""

        if task_type == "codegen":
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
        elif task_type == "drafting":
            # Show the LLM-generated draft text
            generated = latest_data.get("generated_text", latest_data.get("draft", ""))
            chunks = latest_data.get("chunks", [])
            if generated:
                summary = generated
                if needs_review:
                    summary += "\n\n---\n*[NEEDS HUMAN REVIEW]*"
            else:
                summary = f"Drafting complete — used {len(chunks)} reference chunks.{review_tag}"
                for i, chunk in enumerate(chunks[:3], 1):
                    text = chunk.get("text", str(chunk))[:150] if isinstance(chunk, dict) else str(chunk)[:150]
                    summary += f"\n\n> **Reference {i}:**\n> {text}..."
        elif task_type == "conversational":
            # Show the direct LLM response
            response = latest_data.get("response", latest_data.get("generated_text", ""))
            if response:
                summary = response
            else:
                summary = "I'm sorry, I couldn't generate a response. The LLM service may be unavailable."
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



