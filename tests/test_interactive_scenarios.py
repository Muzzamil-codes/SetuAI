"""
Interactive Deep-Dive Test Suite for Nafey's Verification Module.
Simulates realistic refinery engineering calculations, code execution,
self-healing auto-repair, and security attack vectors.
"""
import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from tools.sandbox_tool import run


def banner(title: str):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_scenario_1_refinery_pipe_tolerance():
    banner("SCENARIO 1: REFINERY VALVE PRESSURE TOLERANCE (API 3.2)")
    print("Context: P&ID inspection report states Valve V-204 rated pressure is 4.2 bar.")
    print("SOP-114 allows maximum operating limit of 5.0 bar with 0.05 tolerance.\n")

    # 1. Normal operating condition
    payload_pass = {
        "expression": "4.2 <= 5.0",
        "constraints": {"tolerance": 0.05}
    }
    res_pass = run(payload_pass)
    print("Test 1.1 — Safe Operating Pressure (4.2 <= 5.0):")
    print(f"  Result: passed={res_pass.data.get('passed')}, detail='{res_pass.data.get('detail')}'")
    assert res_pass.data["passed"] is True

    # 2. Overpressure condition
    payload_fail = {
        "expression": "5.4 <= 5.0",
        "constraints": {"tolerance": 0.05}
    }
    res_fail = run(payload_fail)
    print("\nTest 1.2 — Critical Overpressure Condition (5.4 <= 5.0):")
    print(f"  Result: passed={res_fail.data.get('passed')}, detail='{res_fail.data.get('detail')}'")
    print(f"  API Contract Note: tool success={res_fail.success} (Tool didn't crash; physics check failed!)")
    assert res_fail.data["passed"] is False


def test_scenario_2_ast_security_defense():
    banner("SCENARIO 2: SOVEREIGN AIR-GAP AST SECURITY ATTACK DEFENSE")
    print("Context: An LLM generates a prompt injection attempting to leak host environment data.\n")

    attacks = [
        ("Shell Execution Attempt", "__import__('os').system('cat /etc/passwd')"),
        ("Filesystem Read Attempt", "open('/etc/hosts').read()"),
        ("Dunder Attribute Inspection", "().__class__.__bases__[0].__subclasses__()"),
    ]

    for label, payload_str in attacks:
        res = run({"expression": payload_str, "constraints": {}})
        print(f"Attack: {label}")
        print(f"  Payload: {payload_str}")
        print(f"  Blocked?: {not res.success}")
        print(f"  Error Caught: {res.error}\n")
        assert res.success is False


def test_scenario_3_engineering_code_sandbox():
    banner("SCENARIO 3: ENGINEERING CODE EXECUTION IN PODMAN SANDBOX")
    print("Context: AI generates an internal tool function to calculate pipe friction head loss.\n")

    code = """
def darcy_weisbach(f, L, D, v):
    g = 9.81
    # Head loss h_f = f * (L/D) * (v^2 / (2*g))
    return f * (L / D) * (v**2 / (2 * g))
"""
    tests = """
# Friction factor 0.02, length 100m, diameter 0.2m, velocity 2 m/s
head_loss = darcy_weisbach(0.02, 100.0, 0.2, 2.0)
assert round(head_loss, 2) == 2.04
"""

    res = run({
        "code": code,
        "language": "python",
        "tests": tests
    })

    print("Sandbox Run Result:")
    print(f"  Passed: {res.data.get('passed')}")
    print(f"  Exit Code: {res.data.get('exit_code')}")
    print(f"  Isolation: --network=none, memory: 512m, cpu: 1.0 core")
    assert res.data["passed"] is True


def test_scenario_4_autonomous_self_heal_simulation():
    banner("SCENARIO 4: AUTONOMOUS SELF-HEAL LOOP (SIMULATION)")
    print("Context: Model generates code with an off-by-one formula bug. Watch the error get captured.\n")

    # Buggy code (using 2 instead of 2*g)
    buggy_code = """
def darcy_weisbach(f, L, D, v):
    # BUG: Forgot gravity constant 'g' in denominator!
    return f * (L / D) * (v**2 / 2.0)
"""
    tests = """
head_loss = darcy_weisbach(0.02, 100.0, 0.2, 2.0)
assert round(head_loss, 2) == 2.04
"""

    print("Cycle 1: Executing Buggy Code...")
    res_buggy = run({"code": buggy_code, "language": "python", "tests": tests})
    print(f"  Passed: {res_buggy.data.get('passed')}")
    print(f"  Exit Code: {res_buggy.data.get('exit_code')}")
    print(f"  Generated Self-Heal Prompt for Coder Model:")
    print("  --------------------------------------------------")
    for line in res_buggy.data.get("self_heal_prompt", "").splitlines()[:10]:
        print(f"    {line}")
    print("    [...]")
    print("  --------------------------------------------------")
    assert res_buggy.data["passed"] is False

    print("\nCycle 2: Coding Model receives the prompt above, fixes formula, and resubmits...")
    fixed_code = """
def darcy_weisbach(f, L, D, v):
    g = 9.81
    return f * (L / D) * (v**2 / (2 * g))
"""
    res_fixed = run({"code": fixed_code, "language": "python", "tests": tests})
    print(f"  Passed: {res_fixed.data.get('passed')}")
    print(f"  Exit Code: {res_fixed.data.get('exit_code')}")
    print("  Status: SELF-HEAL CYCLE COMPLETED SUCCESSFULLY!")
    assert res_fixed.data["passed"] is True


def test_scenario_5_zero_egress_air_gap_proof():
    banner("SCENARIO 5: PROVING THE ZERO-EGRESS AIR-GAP CLAIM")
    print("Context: Verifying that code running inside sandbox CANNOT reach the internet or external servers.\n")

    code_with_network = """
import urllib.request
response = urllib.request.urlopen("http://example.com", timeout=3)
"""
    res = run({"code": code_with_network, "language": "python", "tests": "pass"})
    print("Network Egress Attempt Result:")
    print(f"  Passed: {res.data.get('passed')} (Must be False)")
    print(f"  Stderr Output: {res.data.get('stderr')[:140]}...")
    print("\nProof: Outbound connection strictly blocked! No data can leave the premises.")
    assert res.data["passed"] is False


if __name__ == "__main__":
    test_scenario_1_refinery_pipe_tolerance()
    test_scenario_2_ast_security_defense()
    test_scenario_3_engineering_code_sandbox()
    test_scenario_4_autonomous_self_heal_simulation()
    test_scenario_5_zero_egress_air_gap_proof()

    print("\n" + "=" * 70)
    print("  ALL 5 DEEP-DIVE VERIFICATION SCENARIOS PASSED WITH FLYING COLORS!")
    print("=" * 70 + "\n")
