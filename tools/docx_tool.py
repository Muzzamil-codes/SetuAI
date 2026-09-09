"""
DOCX Tool wrapper for the LangGraph tool registry.
Wraps artifact_factory/docx_builder.py.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from verification.schemas import ToolResult

DESCRIPTION = (
    "Generates an official, professionally styled Microsoft Word document (.docx). "
    "Use this tool when the user requests a notice, memorandum, official letter, standard operating procedure (SOP), "
    "compliance report, or documentation file in Word format. "
    "The input must contain clean markdown body content without conversational greetings or chat commentary."
)

SCHEMA = {
    "name": "docx",
    "description": DESCRIPTION,
    "parameters": {
        "type": "object",
        "properties": {
            "doc_type": {
                "type": "string",
                "enum": ["notice", "letter", "memo", "report", "standard"],
                "description": "The category of document. Use 'notice' for plant/work/maintenance notices, 'letter' or 'memo' for official correspondence, 'report' for technical reports."
            },
            "title": {
                "type": "string",
                "description": "The concise, official title of the document or notice subject."
            },
            "company_or_org": {
                "type": "string",
                "description": "Issuing company, facility, or organization name."
            },
            "department": {
                "type": "string",
                "description": "Issuing division or department (e.g. Plant Maintenance & Engineering Division)."
            },
            "date": {
                "type": "string",
                "description": "Date of issue (e.g. '10 September 2026')."
            },
            "recipient_or_target": {
                "type": "string",
                "description": "Target audience, affected parties, or recipient (e.g. 'All Facility Personnel and Shift Supervisors')."
            },
            "body_content": {
                "type": "string",
                "description": "Thorough, professional markdown text for the body of the document. Include sections with ## headings, detailed explanations, affected equipment/locations, timeline, and safety directives. MUST NOT contain conversational preamble like 'Here is the notice'."
            },
            "action_items_or_recommendations": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of key action items, mandatory safety precautions, or operational directives."
            },
            "signatory": {
                "type": "string",
                "description": "Name and official title of the signing authority."
            }
        },
        "required": ["title", "body_content"]
    }
}


def run(input: dict) -> ToolResult:
    """Universal tool signature: run(input: dict) -> ToolResult."""
    if not isinstance(input, dict):
        return ToolResult(success=False, error=f"Invalid input type: expected dict, got {type(input).__name__}")
    
    data = input.get("data", input)
    
    try:
        from artifact_factory.docx_builder import generate_docx
        result = generate_docx(data=data, output_dir="outputs")
        if result.get("success"):
            return ToolResult(
                success=True,
                data={
                    "filename": result["filename"],
                    "path": result["path"],
                    "file_path": result["path"],
                    "doc_type": result.get("doc_type", "document"),
                    "title": data.get("title", ""),
                    "artifact": {
                        "type": "docx",
                        "filename": result["filename"],
                        "path": result["path"]
                    }
                }
            )
        else:
            return ToolResult(success=False, error=result.get("error", "DOCX generation failed"))
    except Exception as e:
        return ToolResult(success=False, error=f"DOCX tool error: {str(e)}")
