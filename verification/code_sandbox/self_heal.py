"""
Self-heal error packager for code verification.
Formats stderr and tracebacks into structured diagnostics for Muzzamil's retry node.
"""
import re
from typing import Dict, Any

def parse_verification_error(stderr: str, stdout: str = "") -> Dict[str, str]:
    """
    Parses execution output to extract structured error details:
    - exc_type: Exception class name (e.g. AssertionError, ZeroDivisionError, SyntaxError, TimeoutError)
    - exc_msg: Exception message (e.g. division by zero, Test case 2 failed)
    - location: File and line where error occurred (e.g. test_solution.py:13 in test_knapsack)
    - concise_summary: Clean single-line summary for UI trace display
    """
    output = (stderr or "").strip()
    if not output:
        output = (stdout or "").strip()

    if not output:
        return {
            "exc_type": "UnknownError",
            "exc_msg": "Non-zero exit code without error output",
            "location": "unknown",
            "concise_summary": "UnknownError: Non-zero exit code"
        }

    # Check for timeout
    if "timed out" in output.lower():
        timeout_match = re.search(r"timed out after (\d+) seconds", output, re.IGNORECASE)
        secs = timeout_match.group(1) if timeout_match else ""
        msg = f"Timed out after {secs}s" if secs else "Execution timed out"
        return {
            "exc_type": "TimeoutError",
            "exc_msg": msg,
            "location": "sandbox",
            "concise_summary": f"TimeoutError: {msg}"
        }

    lines = [line.rstrip() for line in output.splitlines() if line.strip()]

    exc_type = ""
    exc_msg = ""
    location = ""

    # 1. Look for Python exception line: e.g. "AssertionError: ...", "ZeroDivisionError: ..."
    # Scan from bottom upwards to find the actual exception line
    exc_pattern = re.compile(r"^([A-Z][a-zA-Z0-9_]*(?:Error|Exception|Exit|Interrupt|Warning|AssertionError))(?::\s*(.*))?$")
    for line in reversed(lines):
        line_clean = line.strip()
        # Handle pytest "E   AssertionError: ..." prefix
        if line_clean.startswith("E "):
            line_clean = line_clean[2:].strip()
        m = exc_pattern.match(line_clean)
        if m:
            exc_type = m.group(1)
            exc_msg = (m.group(2) or "").strip()
            break

    # 2. Look for the last frame: File "...", line X, in Y
    frame_pattern = re.compile(r'File "([^"]+)", line (\d+)(?:, in (.+))?')
    for line in reversed(lines):
        fm = frame_pattern.search(line)
        if fm:
            filepath, lineno, func = fm.groups()
            filename = filepath.split("/")[-1]
            if func:
                location = f"{filename}:{lineno} in {func}"
            else:
                location = f"{filename}:{lineno}"
            break

    # 3. Handle pytest summary if not matched: e.g. "test_solution.py:13: AssertionError"
    if not location:
        pytest_loc = re.search(r"([a-zA-Z0-9_\-\.]+):(\d+):\s*([A-Za-z0-9_]+)", output)
        if pytest_loc:
            location = f"{pytest_loc.group(1)}:{pytest_loc.group(2)}"
            if not exc_type:
                exc_type = pytest_loc.group(3)

    if not exc_type:
        last_line = lines[-1] if lines else "Execution failed"
        exc_type = "ExecutionError"
        exc_msg = last_line[:100]

    # Build concise summary
    if exc_msg:
        summary = f"{exc_type}: {exc_msg}"
    else:
        summary = exc_type

    if location:
        concise_summary = f"{summary} ({location})"
    else:
        concise_summary = summary

    return {
        "exc_type": exc_type,
        "exc_msg": exc_msg,
        "location": location or "unknown",
        "concise_summary": concise_summary
    }


def format_self_heal_context(stdout: str, stderr: str, exit_code: int) -> Dict[str, Any]:
    """
    Parses test failure outputs and extracts actionable error information for LLM self-healing.
    """
    error_summary = ""
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


RECOVERABLE_EXCEPTION_TYPES = {
    # Test assertion failures (logic bugs, off-by-one, formula errors)
    "AssertionError",
    # Runtime exceptions that can be fixed by code changes
    "TypeError", "ValueError", "AttributeError", "IndexError", "KeyError",
    "ZeroDivisionError", "UnboundLocalError", "NameError", "OverflowError",
    "NotImplementedError", "FileNotFoundError",
    # Syntax and compilation errors
    "SyntaxError", "IndentationError", "TabError",
    # Dependency errors (missing module that can be rewritten via standard library)
    "ModuleNotFoundError", "ImportError"
}


NON_RECOVERABLE_EXCEPTION_TYPES = {
    "TimeoutError",
    "MemoryError",
    "SystemExit",
    "KeyboardInterrupt",
    "GeneratorExit",
}


def is_recoverable_error(exc_type: str, exc_msg: str = "", stderr: str = "") -> bool:
    """
    Determines whether a code execution failure in the sandbox is potentially recoverable by the LLM.
    
    Recoverable:
      - Logic assertion failures
      - Standard runtime and syntax exceptions
      - Missing modules that can be rewritten with the standard library
      
    Non-recoverable:
      - Execution timeouts (infinite loops, hangs)
      - System resource exhaustion (MemoryError)
      - Process interrupts / exits (SystemExit, KeyboardInterrupt)
      - Empty errors
    """
    if not exc_type:
        return False
    if exc_type in NON_RECOVERABLE_EXCEPTION_TYPES:
        return False
    combined = f"{exc_type} {exc_msg} {stderr}".lower()
    if "timeout" in combined or "timed out" in combined or "out of memory" in combined:
        return False
    if exc_type in RECOVERABLE_EXCEPTION_TYPES:
        return True
    if (exc_type.endswith("Error") or exc_type.endswith("Exception")) and "timeout" not in exc_type.lower():
        return True
    return False


def format_self_heal_prompt(
    instruction: str,
    previous_code: str,
    exc_type: str,
    exc_msg: str,
    location: str,
    stderr: str = "",
    attempt: int = 1
) -> str:
    """
    Builds a targeted, actionable repair prompt for the coding LLM.
    Specifically handles ModuleNotFoundError per the sandbox dependency policy.
    """
    # 1. Dependency Error Handling (e.g. pymodbus)
    if exc_type in ["ModuleNotFoundError", "ImportError"]:
        missing_mod = ""
        mod_match = re.search(r"No module named ['\"]([^'\"]+)['\"]", f"{exc_msg} {stderr}")
        if mod_match:
            missing_mod = mod_match.group(1)
        else:
            missing_mod = exc_msg.strip() or "the requested external library"

        return (
            f"User Task: {instruction}\n\n"
            f"Your previous solution failed execution with:\n"
            f"{exc_type}: {exc_msg} ({location})\n\n"
            f"SANDBOX DEPENDENCY POLICY NOTICE:\n"
            f"The package '{missing_mod}' is NOT installed in this air-gapped, isolated execution sandbox. "
            f"DO NOT attempt to pip install or download packages. Sandbox security strictly prohibits network egress and installing external third-party packages.\n"
            f"You MUST rewrite the implementation using ONLY the Python standard library "
            f"(e.g., standard modules like `socket`, `struct`, `urllib`, `json`, `math`, `sys`) "
            f"without importing '{missing_mod}'.\n\n"
            f"Previous code:\n```python\n{previous_code}\n```\n\n"
            f"Please output ONLY the complete, corrected Python code implementing the functionality using the standard library. "
            f"No explanations, no markdown fences."
        )

    # 2. General Code / Runtime / Test Failure Handling
    lines = [line.strip() for line in (stderr or "").splitlines() if line.strip()]
    relevant_lines = lines[-12:] if lines else [f"{exc_type}: {exc_msg}"]
    error_summary = "\n".join(relevant_lines)

    return (
        f"User Task: {instruction}\n\n"
        f"Your previous Python code failed verification in the sandbox (Repair Attempt {attempt}/2):\n"
        f"Error: {exc_type}: {exc_msg} ({location})\n\n"
        f"Execution Traceback / Diagnostics:\n"
        f"```\n{error_summary}\n```\n\n"
        f"Previous code that failed:\n```python\n{previous_code}\n```\n\n"
        f"Please analyze the failure, correct the bug, and output ONLY the complete, runnable, fixed Python code. "
        f"No explanations, no markdown fences."
    )


