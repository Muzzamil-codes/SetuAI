"""
DOCX Tool wrapper for Muzzamil's LangGraph tool registry.
Wraps artifact_factory/docx_builder.py.
Follows API_CONTRACTS.md Section 1.4 & 3.4.
Owned by Parvez.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from verification.schemas import ToolResult
from artifact_factory.docx_builder import generate_docx


def run(input: dict) -> ToolResult:
    """
    Universal tool signature: run(input: dict) -> ToolResult.
    Accepts {"template_name": str, "data": dict}.
    """
    if not isinstance(input, dict):
        return ToolResult(
            success=False,
            error=f"Invalid input type: expected dict, got {type(input).__name__}"
        )

    template_name = input.get("template_name", "approval_note")
    data = input.get("data", {})

    return generate_docx(template_name=template_name, data=data)
