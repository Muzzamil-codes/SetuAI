"""
PPTX Tool wrapper for the LangGraph tool registry.
Wraps artifact_factory/pptx_builder.py.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from verification.schemas import ToolResult


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
                    "file_path": result["path"]
                }
            )
        else:
            return ToolResult(success=False, error=result.get("error", "PPTX generation failed"))
    except Exception as e:
        return ToolResult(success=False, error=f"PPTX tool error: {str(e)}")
