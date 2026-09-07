from __future__ import annotations
import importlib
from typing import Any, Optional
from pydantic import BaseModel

class ToolResult(BaseModel):
    success: bool
    data: dict = {}
    error: Optional[str] = None

TOOL_MAPPINGS = {
    "retrieval": "tools.retrieval_tool",
    "sandbox": "tools.sandbox_tool",
    "verify": "tools.sandbox_tool",
    "docx": "tools.docx_tool",
    "xlsx": "tools.xlsx_tool",
    "vision": "tools.vision_tool"
}

def get_tool(name: str) -> Any:
    """Returns the module for the requested tool name."""
    if name not in TOOL_MAPPINGS:
        return _get_stub_tool(f"Tool '{name}' not found in registry.")
    
    module_name = TOOL_MAPPINGS[name]
    try:
        module = importlib.import_module(module_name)
        if not hasattr(module, "run"):
            return _get_stub_tool(f"Tool module '{module_name}' missing 'run' function.")
        return module
    except ImportError as e:
        return _get_stub_tool(f"Failed to import tool '{name}': {e}")

def list_tools() -> list[str]:
    """Returns a list of available tool names."""
    return list(TOOL_MAPPINGS.keys())

def _get_stub_tool(error_message: str):
    """Returns a dummy module that returns a failure ToolResult."""
    class StubTool:
        @staticmethod
        def run(input: dict) -> ToolResult:
            return ToolResult(success=False, error=error_message)
    return StubTool()
