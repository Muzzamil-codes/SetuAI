"""
Cross-module schema definitions for verification and tool results.
Strictly follows API_CONTRACTS.md (Section 1.3, 3.2, 3.3).
Resilient to environments with or without Pydantic installed.
"""
from typing import Optional, Dict, Any

try:
    from pydantic import BaseModel, Field
    HAS_PYDANTIC = True
except ImportError:
    HAS_PYDANTIC = False

if HAS_PYDANTIC:
    class ToolResult(BaseModel):
        """
        Universal tool return shape.
        Every tool (sandbox, retrieval, docx, vision) returns exactly this.
        """
        success: bool
        data: Dict[str, Any] = Field(default_factory=dict)
        error: Optional[str] = None

    class VerifyNumericInput(BaseModel):
        expression: str
        constraints: Dict[str, Any] = Field(default_factory=dict)

    class RunCodeSandboxInput(BaseModel):
        code: str
        language: str = "python"
        tests: str

else:
    from dataclasses import dataclass, field

    @dataclass
    class ToolResult:
        """Fallback dataclass when Pydantic is not installed."""
        success: bool
        data: Dict[str, Any] = field(default_factory=dict)
        error: Optional[str] = None

        def dict(self) -> Dict[str, Any]:
            return {
                "success": self.success,
                "data": self.data,
                "error": self.error
            }

    @dataclass
    class VerifyNumericInput:
        expression: str
        constraints: Dict[str, Any] = field(default_factory=dict)

    @dataclass
    class RunCodeSandboxInput:
        code: str
        language: str = "python"
        tests: str = ""
