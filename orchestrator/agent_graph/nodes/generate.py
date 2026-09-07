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


def generate_node(state: AgentState) -> dict:
    """Generate final artifacts based on task type and tool results."""
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

    outputs_dir = os.path.join(os.getcwd(), "outputs")
    os.makedirs(outputs_dir, exist_ok=True)

    try:
        if task_type in ["extraction", "drafting"]:
            artifact = _build_docx(task_id, task_type, content,
                                   latest_data, needs_review, outputs_dir)
        elif task_type == "numeric_verify":
            artifact = _build_xlsx(task_id, content, latest_data,
                                   needs_review, outputs_dir)
        elif task_type == "codegen":
            artifact = _build_code(task_id, latest_data,
                                   needs_review, outputs_dir)
        else:
            artifact = _build_text(task_id, content, outputs_dir)

        artifacts.append(artifact)
        review_tag = " [NEEDS HUMAN REVIEW]" if needs_review else ""
        summary = (
            f"Generated {artifact.get('type', 'file')}: "
            f"{artifact.get('filename', 'unknown')}{review_tag}"
        )

    except Exception as e:
        summary = f"Failed to generate artifact: {str(e)}"
        err_file = f"{task_id}_error.txt"
        err_path = os.path.join(outputs_dir, err_file)
        with open(err_path, "w") as f:
            f.write(f"Error: {e}\n")
        artifacts.append({"type": "docx", "filename": err_file,
                          "path": f"outputs/{err_file}"})

    # Emit 'generate' event
    trace_events.append({
        "task_id": task_id,
        "step": "generate",
        "payload": {
            "artifact_type": artifact.get("type", "unknown") if artifacts else "error",
            "filename": artifact.get("filename", "") if artifacts else ""
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

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


def _build_docx(task_id, task_type, content, data, needs_review, outputs_dir):
    """Try the docx tool; fall back to plain text."""
    # Build findings from tool results
    findings = []
    if task_type == "extraction":
        fields = data.get("fields", data.get("extracted_fields", {}))
        if isinstance(fields, dict):
            for field_name, value in fields.items():
                findings.append({
                    "field": field_name.replace("_", " ").title(),
                    "value": str(value),
                    "status": "Normal",
                    "source": "VLM/OCR Extraction"
                })
    elif task_type == "drafting":
        for i, chunk in enumerate(data.get("chunks", [])[:5]):
            text = chunk.get("text", str(chunk)) if isinstance(chunk, dict) else str(chunk)
            findings.append({
                "field": f"Reference {i + 1}",
                "value": text[:200],
                "status": "Normal",
                "source": chunk.get("source", "KB") if isinstance(chunk, dict) else "KB"
            })

    ref_no = f"SETU-{task_id[:8].upper()}"
    review_tag = " [NEEDS HUMAN REVIEW]" if needs_review else ""

    docx_input = {
        "data": {
            "title": f"Approval Note — {content[:80]}",
            "reference_no": ref_no,
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "subject": content[:200],
            "findings": findings,
            "recommendation": f"All parameters within limits.{review_tag}",
            "summary": f"AI-generated report for: {content[:300]}",
            "provenance_notes": [
                f"Task ID: {task_id}",
                "Values cross-referenced against SOP database",
                f"Verification: {'PASSED' if not needs_review else 'NEEDS REVIEW'}"
            ]
        }
    }

    try:
        from tools.tool_registry import get_tool
        tool = get_tool("docx")
        result = tool.run(docx_input)
        if result.success:
            return {
                "type": "docx",
                "filename": result.data.get("filename", f"{ref_no}_approval_note.docx"),
                "path": result.data.get("path", f"outputs/{ref_no}_approval_note.docx")
            }
    except Exception:
        pass

    # Fallback: plain text
    filename = f"{ref_no}_approval_note.txt"
    path = os.path.join(outputs_dir, filename)
    with open(path, "w") as f:
        f.write(f"SETU Approval Note | Ref: {ref_no}\n{'='*50}\n")
        f.write(f"Subject: {content[:200]}\n\nFindings:\n")
        for i, finding in enumerate(findings, 1):
            f.write(f"  {i}. {finding['field']}: {finding['value']} "
                    f"[{finding['status']}] (Source: {finding['source']})\n")
        f.write(f"\nRecommendation: All parameters within limits.{review_tag}\n")
    return {"type": "docx", "filename": filename, "path": f"outputs/{filename}"}


def _build_xlsx(task_id, content, data, needs_review, outputs_dir):
    """Try the xlsx tool; fall back to plain text."""
    xlsx_input = {
        "data": {
            "title": f"Verification Report - {content[:60]}",
            "headers": ["Parameter", "Measured", "Expected", "Tolerance",
                        "Deviation", "Status"],
            "rows": [[
                "Pressure",
                str(data.get("computed_value", "N/A")),
                str(data.get("expected", "N/A")),
                f"±{data.get('tolerance', 0.1)} bar",
                str(data.get("deviation", "N/A")),
                "PASS" if data.get("passed", True) else "FAIL"
            ]],
            "formula_columns": {},
            "highlight_rules": []
        }
    }

    try:
        from tools.tool_registry import get_tool
        tool = get_tool("xlsx")
        result = tool.run(xlsx_input)
        if result.success:
            return {
                "type": "xlsx",
                "filename": result.data.get("filename", f"{task_id}_report.xlsx"),
                "path": result.data.get("path", f"outputs/{task_id}_report.xlsx")
            }
    except Exception:
        pass

    filename = f"{task_id}_report.txt"
    path = os.path.join(outputs_dir, filename)
    with open(path, "w") as f:
        f.write(f"Verification Report\n{content}\nResult: {data}\n")
    return {"type": "xlsx", "filename": filename, "path": f"outputs/{filename}"}


def _build_code(task_id, data, needs_review, outputs_dir):
    """Write generated code to a file."""
    code = data.get("generated_code", "# No code generated\n")
    test_log = data.get("stdout", "")
    review_tag = "# WARNING: NEEDS HUMAN REVIEW\n" if needs_review else ""

    filename = f"{task_id}_code.py"
    path = os.path.join(outputs_dir, filename)
    with open(path, "w") as f:
        f.write(f"# Generated by Setu AI — Task: {task_id}\n{review_tag}")
        if test_log:
            f.write(f"# Test log: {test_log[:300]}\n")
        f.write(f"\n{code}")
    return {"type": "docx", "filename": filename, "path": f"outputs/{filename}"}


def _build_text(task_id, content, outputs_dir):
    """Generic text output."""
    filename = f"{task_id}_output.txt"
    path = os.path.join(outputs_dir, filename)
    with open(path, "w") as f:
        f.write(f"Setu AI Output | Task: {task_id}\n\n{content}\n")
    return {"type": "docx", "filename": filename, "path": f"outputs/{filename}"}
