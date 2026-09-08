"""
Self-heal error packager for code verification.
Formats stderr and tracebacks into structured diagnostics for Muzzamil's retry node.
"""
import re
from typing import Dict, Any

def format_self_heal_context(stdout: str, stderr: str, exit_code: int) -> Dict[str, Any]:
    """
    Parses test failure outputs and extracts actionable error information for LLM self-healing.
    """
    error_summary = ""
    failure_details = []

    output_text = stderr if stderr.strip() else stdout

    # Look for pytest failure summaries or tracebacks
    lines = output_text.splitlines()
    capturing_failure = False
    captured_lines = []

    for line in lines:
        if "FAILURES" in line or "AssertionError" in line or "Error:" in line or "Traceback" in line:
            capturing_failure = True
        if capturing_failure:
            captured_lines.append(line)

    if captured_lines:
        error_summary = "\n".join(captured_lines[-15:])  # Keep the most relevant trailing error lines
    else:
        error_summary = output_text[-500:] if len(output_text) > 500 else output_text

    return {
        "exit_code": exit_code,
        "error_summary": error_summary.strip(),
        "prompt_instruction": (
            f"The generated code failed verification with the following error:\n\n"
            f"```\n{error_summary.strip()}\n```\n\n"
            f"Please inspect the failure and rewrite the code to satisfy the tests."
        )
    }
