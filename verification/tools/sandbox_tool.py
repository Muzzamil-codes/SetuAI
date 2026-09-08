"""
Thin tool wrapper exposing run(input: dict) -> ToolResult.
Wraps verification/gate.py for Muzzamil's LangGraph tool registry.
Follows API_CONTRACTS.md Section 1.4, 3.2, and 3.3.
"""
from typing import Dict, Any
import sys
import os

# Ensure setu root is in path if imported from tools/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from verification.schemas import ToolResult
from verification.gate import verify


def run(input: Dict[str, Any]) -> ToolResult:
    """
    Universal tool signature: run(input: dict) -> ToolResult
    Inspects input keys to dispatch to numeric or code verification.
    """
    if not isinstance(input, dict):
        return ToolResult(
            success=False,
            error=f"Invalid input type: expected dict, got {type(input).__name__}"
        )

    try:
        # Determine verification target based on contract shapes
        if "expression" in input:
            return verify(verification_type="numeric", payload=input)
        elif "code" in input:
            return verify(verification_type="code", payload=input)
        elif "verification_type" in input:
            return verify(
                verification_type=input.get("verification_type", ""),
                payload=input.get("payload", {})
            )
        else:
            return ToolResult(
                success=False,
                error="Unrecognized verification input: payload must contain either 'expression' or 'code'."
            )
    except Exception as e:
        # Contract Rule #0: Catch internally, never raise across boundary
        return ToolResult(
            success=False,
            error=f"Sandbox tool wrapper error: {str(e)}"
        )
