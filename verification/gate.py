"""
Single unified verification gatekeeper for the orchestrator.
Dispatches to numeric verification (SymPy) or code execution sandbox (Podman).
Follows Setu architecture gatekeeper design.
"""
from typing import Dict, Any
from verification.schemas import ToolResult
from verification.numeric.sympy_checker import verify_numeric
from verification.code_sandbox.podman_runner import run_code_sandboxed


def verify(verification_type: str, payload: Dict[str, Any]) -> ToolResult:
    """
    Unified entrypoint for all verification tasks.
    Parameters:
      - verification_type: "numeric" | "code"
      - payload: input dictionary matching the target tool's contract.
    """
    try:
        vtype = verification_type.strip().lower()

        if vtype == "numeric":
            expression = payload.get("expression", "")
            constraints = payload.get("constraints", {})
            return verify_numeric(expression=expression, constraints=constraints)

        elif vtype in ["code", "sandbox", "code_sandbox"]:
            code = payload.get("code", "")
            tests = payload.get("tests", "")
            language = payload.get("language", "python")
            return run_code_sandboxed(code=code, tests=tests, language=language)

        else:
            return ToolResult(
                success=False,
                error=f"Unknown verification type '{verification_type}'. Supported: 'numeric', 'code'."
            )

    except Exception as e:
        # Contract Rule #0: Catch internal errors and return cleanly
        return ToolResult(
            success=False,
            error=f"Verification gate error: {str(e)}"
        )
