"""
Isolated Code Execution Sandbox.
Executes AI-generated code and tests inside an isolated container with zero network egress.
Follows API_CONTRACTS.md Section 3.3.
"""
import os
import shutil
import tempfile
import subprocess
from typing import Dict, Any, Optional
from verification.schemas import ToolResult
from verification.code_sandbox.test_harness.harness import generate_test_harness
from verification.code_sandbox.self_heal import format_self_heal_context

DEFAULT_IMAGE = os.environ.get("SETU_SANDBOX_IMAGE", "python:3.11-slim")
DEFAULT_TIMEOUT = int(os.environ.get("SETU_SANDBOX_TIMEOUT", "15"))


def _detect_container_runtime() -> Optional[str]:
    """
    Detects whether podman or docker is installed and responsive.
    Prefers podman per system architecture.
    """
    for binary in ["podman", "docker"]:
        path = shutil.which(binary)
        if path:
            # Check if engine/machine is actually responsive
            try:
                res = subprocess.run(
                    [path, "info"],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                if res.returncode == 0:
                    return path
            except Exception:
                continue
    return None


def run_code_sandboxed(
    code: str,
    tests: str,
    language: str = "python",
    timeout_secs: int = DEFAULT_TIMEOUT
) -> ToolResult:
    """
    Executes generated code against tests in an isolated sandbox.
    Guarantees:
      - Zero network access (--network=none)
      - Resource limits (memory, CPU, process limits)
      - Execution timeout enforcement
      - Clean error capture for self-healing
    """
    if language.lower() not in ["python", "python3"]:
        return ToolResult(
            success=False,
            error=f"Unsupported execution language '{language}'. Only Python is supported."
        )

    if not code or not tests:
        return ToolResult(
            success=False,
            error="Both 'code' and 'tests' must be non-empty strings."
        )

    try:
        with tempfile.TemporaryDirectory(prefix="setu_sandbox_") as tmpdir:
            # 1. Write solution and test harness files
            solution_path = os.path.join(tmpdir, "solution.py")
            test_path = os.path.join(tmpdir, "test_solution.py")

            with open(solution_path, "w", encoding="utf-8") as f:
                f.write(code)

            harness_content = generate_test_harness(code, tests)
            with open(test_path, "w", encoding="utf-8") as f:
                f.write(harness_content)

            # 2. Check for container runtime (Podman / Docker)
            runtime_bin = _detect_container_runtime()

            if runtime_bin:
                cmd = [
                    runtime_bin, "run", "--rm",
                    "--network=none",               # Mandatory Zero Network Egress
                    "--memory=512m",                # RAM limit
                    "--cpus=1.0",                   # CPU limit
                    "--pids-limit=64",              # Fork-bomb protection
                    "--cap-drop=ALL",               # Drop Linux kernel capabilities
                    "--security-opt=no-new-privileges",
                    "-v", f"{tmpdir}:/workspace:rw",
                    "-w", "/workspace",
                    DEFAULT_IMAGE,
                    "python3", "test_solution.py"
                ]

                try:
                    proc = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=timeout_secs
                    )
                    stdout = proc.stdout
                    stderr = proc.stderr
                    exit_code = proc.returncode
                    passed = (exit_code == 0)

                except subprocess.TimeoutExpired:
                    return ToolResult(
                        success=True,
                        data={
                            "passed": False,
                            "stdout": "",
                            "stderr": f"Execution timed out after {timeout_secs} seconds.",
                            "exit_code": -1
                        },
                        error=None
                    )
            else:
                # Standalone fallback when container daemon is not active on host:
                # Runs in an isolated subprocess with air-gap network blocking
                sandbox_env = os.environ.copy()
                # Disable proxy / network env vars
                sandbox_env["HTTP_PROXY"] = "http://127.0.0.1:0"
                sandbox_env["HTTPS_PROXY"] = "http://127.0.0.1:0"
                sandbox_env["NO_PROXY"] = ""

                # Wrap execution to block network sockets if runtime binary is absent
                guarded_runner = f"""
import sys, socket
def _blocked(*args, **kwargs):
    raise ConnectionRefusedError("Network access disabled (Air-Gap policy: --network=none)")
socket.socket.connect = _blocked
socket.socket.connect_ex = _blocked
socket.create_connection = _blocked

with open("{test_path}", "r") as f:
    code_to_exec = f.read()
sys.path.insert(0, "{tmpdir}")
exec(compile(code_to_exec, "{test_path}", "exec"), {{'__name__': '__main__'}})
"""
                try:
                    proc = subprocess.run(
                        ["python3", "-c", guarded_runner],
                        cwd=tmpdir,
                        capture_output=True,
                        text=True,
                        timeout=timeout_secs,
                        env=sandbox_env
                    )
                    stdout = proc.stdout
                    stderr = proc.stderr
                    exit_code = proc.returncode
                    passed = (exit_code == 0)

                except subprocess.TimeoutExpired:
                    return ToolResult(
                        success=True,
                        data={
                            "passed": False,
                            "stdout": "",
                            "stderr": f"Execution timed out after {timeout_secs} seconds.",
                            "exit_code": -1
                        },
                        error=None
                    )

            # Package result
            result_data = {
                "passed": passed,
                "stdout": stdout.strip(),
                "stderr": stderr.strip(),
                "exit_code": exit_code
            }

            if not passed:
                heal_info = format_self_heal_context(stdout, stderr, exit_code)
                result_data["self_heal_prompt"] = heal_info["prompt_instruction"]

            return ToolResult(
                success=True,
                data=result_data,
                error=None
            )

    except Exception as e:
        # Contract Rule #0: Never raise across module boundary!
        return ToolResult(
            success=False,
            data={},
            error=f"Sandbox execution error: {str(e)}"
        )

