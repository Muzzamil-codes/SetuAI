"""
Standalone Test Suite for Nafey's Verification Module.
Tests numeric verification, code execution sandbox, self-healing errors,
and air-gapped network isolation.
Strictly follows API_CONTRACTS.md Section 3.2, 3.3, and 6.
"""
import sys
import os

# Add project root to sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from tools.sandbox_tool import run
from verification.schemas import ToolResult
from verification.numeric.sympy_checker import verify_numeric
from verification.code_sandbox.podman_runner import run_code_sandboxed


def test_verify_numeric_pass_and_fail():
    """Verifies that numeric comparisons evaluate correctly and distinguish success vs passed."""
    ok = run({"expression": "2 + 2 == 4", "constraints": {}})
    assert isinstance(ok, ToolResult)
    assert ok.success is True
    assert ok.data["passed"] is True
    assert ok.error is None

    bad = run({"expression": "2 + 2 == 5", "constraints": {}})
    assert isinstance(bad, ToolResult)
    # Crucial contract distinction:
    # success is True because the tool didn't crash, but data['passed'] is False
    assert bad.success is True
    assert bad.data["passed"] is False
    assert bad.error is None


def test_verify_numeric_inequality_and_tolerance():
    """Tests engineering inequality and tolerance bounds."""
    # Engineering comparison check: 4.2 <= 5.0
    res = run({"expression": "4.2 <= 5.0", "constraints": {"tolerance": 0.05}})
    assert res.success is True
    assert res.data["passed"] is True
    assert "within tolerance" in res.data["detail"]

    # Tolerance calculation on value
    val_check = verify_numeric("10.02", constraints={"expected": 10.0, "tolerance": 0.05})
    assert val_check.success is True
    assert val_check.data["passed"] is True

    # Out of tolerance check
    out_of_bounds = verify_numeric("10.15", constraints={"expected": 10.0, "tolerance": 0.05})
    assert out_of_bounds.success is True
    assert out_of_bounds.data["passed"] is False


def test_verify_numeric_ast_security_injection():
    """Security check: AST parser must block malicious code injection in numeric expressions."""
    malicious_inputs = [
        "__import__('os').system('echo pwned')",
        "open('/etc/passwd').read()",
        "eval('2 + 2')",
        "exec('x = 1')",
    ]
    for bad_expr in malicious_inputs:
        res = verify_numeric(bad_expr)
        # Should be caught by AST validator and rejected cleanly
        assert res.success is False
        assert "Security validation error" in res.error or "Syntax error" in res.error


def test_sandbox_pass_fail_and_isolation():
    """
    Three canonical contract tests:
      1. Clean pass
      2. Bug that fails test and captures AssertionError for self-healing
      3. Air-gap isolation check (network call MUST fail)
    """
    # 1. Clean Pass
    good = run({
        "code": "def f(): return 1",
        "language": "python",
        "tests": "assert f() == 1"
    })
    assert good.success is True
    assert good.data["passed"] is True
    assert good.data["exit_code"] == 0

    # 2. Bug: Fails with AssertionError and populates stderr
    bad = run({
        "code": "def f(): return 2",
        "language": "python",
        "tests": "assert f() == 1"
    })
    assert bad.success is True
    assert bad.data["passed"] is False
    assert "AssertionError" in bad.data["stderr"]
    assert "self_heal_prompt" in bad.data
    assert "AssertionError" in bad.data["self_heal_prompt"]

    # 3. Air-Gap Isolation Check: Network calls must fail
    net = run({
        "code": "import urllib.request\nurllib.request.urlopen('http://example.com')",
        "language": "python",
        "tests": "pass"
    })
    assert net.success is True
    assert net.data["passed"] is False  # Must fail inside sandbox
    assert ("ConnectionRefusedError" in net.data["stderr"] or 
            "URLError" in net.data["stderr"] or 
            "Network access disabled" in net.data["stderr"] or
            "socket.error" in net.data["stderr"])


def test_sandbox_timeout():
    """Verifies that infinite loops are killed without hanging the host."""
    infinite_loop = run({
        "code": "while True:\n    pass",
        "language": "python",
        "tests": "pass"
    })
    # Fast test with 2s timeout
    res = run_code_sandboxed(
        code="while True:\n    pass",
        tests="pass",
        timeout_secs=2
    )
    assert res.success is True
    assert res.data["passed"] is False
    assert "timed out" in res.data["stderr"].lower()


def run_manual_demonstration():
    """Runs a human-readable CLI demonstration of all verification checks."""
    print("=" * 60)
    print("SETU AIR-GAPPED VERIFICATION MODULE — STANDALONE DEMO")
    print("=" * 60)

    # 1. Numeric Check Pass
    r1 = run({"expression": "2 + 2 == 4", "constraints": {}})
    print(f"\n[1] Numeric Check (2 + 2 == 4):")
    print(f"    success: {r1.success} | passed: {r1.data.get('passed')} | detail: {r1.data.get('detail')}")

    # 2. Numeric Check Fail (Distinction check)
    r2 = run({"expression": "2 + 2 == 5", "constraints": {}})
    print(f"\n[2] Numeric Check (2 + 2 == 5):")
    print(f"    success: {r2.success} (Tool ran ok) | passed: {r2.data.get('passed')} (Math failed)")

    # 3. Numeric Security Check
    r3 = run({"expression": "__import__('os').system('ls')", "constraints": {}})
    print(f"\n[3] Numeric Security Injection Block:")
    print(f"    success: {r3.success} | error: {r3.error}")

    # 4. Sandbox Code Pass
    r4 = run({
        "code": "def calculate_head_loss(q, d): return 0.0826 * (q**2) / (d**5)",
        "language": "python",
        "tests": "assert round(calculate_head_loss(2, 1), 3) == 0.330"
    })
    print(f"\n[4] Engineering Code Sandbox Pass:")
    print(f"    passed: {r4.data.get('passed')} | exit_code: {r4.data.get('exit_code')}")

    # 5. Sandbox Code Failure & Self-Heal Prompt
    r5 = run({
        "code": "def calculate_head_loss(q, d): return 0.0826 * (q) / (d)",
        "language": "python",
        "tests": "assert round(calculate_head_loss(2, 1), 3) == 0.330"
    })
    print(f"\n[5] Buggy Code & Self-Heal Extraction:")
    print(f"    passed: {r5.data.get('passed')}")
    print(f"    self-heal prompt excerpt:\n    {r5.data.get('self_heal_prompt', '')[:120]}...")

    # 6. Sovereign Air-Gap Network Check
    r6 = run({
        "code": "import urllib.request\nurllib.request.urlopen('http://1.1.1.1')",
        "language": "python",
        "tests": "pass"
    })
    print(f"\n[6] Sovereign Air-Gap Network Egress Check:")
    print(f"    passed: {r6.data.get('passed')} (False indicates network blocked successfully)")
    print(f"    stderr excerpt: {r6.data.get('stderr', '')[:80]}...")

    print("\n" + "=" * 60)
    print("ALL STANDALONE VERIFICATION CHECKS COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == "__main__":
    test_verify_numeric_pass_and_fail()
    test_verify_numeric_inequality_and_tolerance()
    test_verify_numeric_ast_security_injection()
    test_sandbox_pass_fail_and_isolation()
    test_sandbox_timeout()
    run_manual_demonstration()
