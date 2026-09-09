"""
PPTX Tool wrapper for the LangGraph tool registry.
Wraps artifact_factory/pptx_builder.py.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from verification.schemas import ToolResult

DESCRIPTION = (
    "Generates a PowerPoint presentation (.pptx) with formatted title, content slides, and bullet points. "
    "Use this tool when the user requests presentation slides, pitch decks, or meeting slide briefings."
)

SCHEMA = {
    "name": "pptx",
    "description": DESCRIPTION,
    "parameters": {
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "Presentation title"},
            "company_or_org": {"type": "string", "description": "Company or facility name"},
            "department": {"type": "string", "description": "Issuing department"},
            "signatory": {"type": "string", "description": "Presenter name"},
            "slides": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Slide title"},
                        "bullets": {"type": "array", "items": {"type": "string"}, "description": "Bullet points for this slide"}
                    },
                    "required": ["title", "bullets"]
                },
                "description": "List of slide topics and bullet points"
            }
        },
        "required": ["title"]
    }
}


def run(input: dict) -> ToolResult:
    """Universal tool signature: run(input: dict) -> ToolResult."""
    if not isinstance(input, dict):
        return ToolResult(success=False, error=f"Invalid input type: expected dict, got {type(input).__name__}")
    
    data = input.get("data", input)
    
    try:
        from artifact_factory.pptx_builder import generate_pptx
        result = generate_pptx(data=data, output_dir="outputs")
        if result.get("success"):
            return ToolResult(
                success=True,
                data={
                    "filename": result["filename"],
                    "path": result["path"],
                    "file_path": result["path"],
                    "artifact": {
                        "type": "pptx",
                        "filename": result["filename"],
                        "path": result["path"]
                    }
                }
            )
        else:
            return ToolResult(success=False, error=result.get("error", "PPTX generation failed"))
    except Exception as e:
        return ToolResult(success=False, error=f"PPTX tool error: {str(e)}")
