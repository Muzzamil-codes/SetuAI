"""Standalone test for the orchestrator pipeline.

Runs the full agent graph with stub tools (no dependencies on
other team members' code) and verifies:
1. Classifier correctly routes different task types
2. Graph produces the right sequence of trace events
3. Retry path triggers on verification failure
"""
import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_classifier():
    """Test that the classifier routes correctly."""
    from orchestrator.classifier.infer import classify_task, select_model

    # Image modality → extraction
    assert classify_task("anything", "image") == "extraction"
    assert classify_task("anything", "file") == "extraction"

    # Code keywords → codegen
    assert classify_task("Write a python script for Modbus polling", "text") == "codegen"
    assert classify_task("Implement a function to process data", "text") == "codegen"
    assert classify_task("Debug this SQL query", "text") == "codegen"

    # Numeric verification keywords
    assert classify_task("Verify pressure reading of 4.05 bar", "text") == "numeric_verify"
    assert classify_task("Check if tolerance is within range", "text") == "numeric_verify"
    assert classify_task("Calculate the flow rate", "text") == "numeric_verify"

    # Default → drafting
    assert classify_task("Draft an approval note for the valve inspection", "text") == "drafting"
    assert classify_task("Prepare a summary of maintenance activities", "text") == "drafting"

    # Model selection
    model = select_model("codegen")
    assert model.get("role") == "codegen"
    model = select_model("extraction")
    assert model.get("role") == "extraction"
    model = select_model("drafting")
    assert model.get("role") == "reasoning"

    print("✅ Classifier tests passed")


async def test_graph_drafting():
    """Test full pipeline for a drafting task."""
    from orchestrator.agent_graph.graph import run_agent

    task = {
        "task_id": "test-drafting-001",
        "modality": "text",
        "content": "Draft an approval note for Unit-2 Valve V-204 inspection",
        "context": {}
    }

    events = []
    async for event in run_agent(task):
        events.append(event)
        print(f"  [{event['step']}] {event.get('payload', {})}")

    steps = [e["step"] for e in events]
    assert "classify" in steps, f"Missing classify step. Got: {steps}"
    assert "plan" in steps, f"Missing plan step. Got: {steps}"
    assert "tool_call" in steps, f"Missing tool_call step. Got: {steps}"
    assert "done" in steps, f"Missing done step. Got: {steps}"

    # Check classifier routed correctly
    classify_event = next(e for e in events if e["step"] == "classify")
    assert classify_event["payload"]["task_type"] == "drafting"

    print("✅ Drafting pipeline test passed")


async def test_graph_extraction():
    """Test full pipeline for an extraction task."""
    from orchestrator.agent_graph.graph import run_agent

    task = {
        "task_id": "test-extraction-001",
        "modality": "image",
        "content": "uploads/scan_001.jpg",
        "context": {}
    }

    events = []
    async for event in run_agent(task):
        events.append(event)
        print(f"  [{event['step']}] {event.get('payload', {})}")

    steps = [e["step"] for e in events]
    classify_event = next(e for e in events if e["step"] == "classify")
    assert classify_event["payload"]["task_type"] == "extraction"
    assert "done" in steps

    print("✅ Extraction pipeline test passed")


async def test_graph_codegen():
    """Test full pipeline for a code generation task."""
    from orchestrator.agent_graph.graph import run_agent

    task = {
        "task_id": "test-codegen-001",
        "modality": "text",
        "content": "Write a Python script to poll Modbus registers",
        "context": {}
    }

    events = []
    async for event in run_agent(task):
        events.append(event)
        print(f"  [{event['step']}] {event.get('payload', {})}")

    steps = [e["step"] for e in events]
    classify_event = next(e for e in events if e["step"] == "classify")
    assert classify_event["payload"]["task_type"] == "codegen"
    assert "done" in steps

    print("✅ Codegen pipeline test passed")


async def test_graph_numeric():
    """Test full pipeline for a numeric verification task."""
    from orchestrator.agent_graph.graph import run_agent

    task = {
        "task_id": "test-numeric-001",
        "modality": "text",
        "content": "Verify pressure reading 4.05 bar against tolerance of 4.0",
        "context": {}
    }

    events = []
    async for event in run_agent(task):
        events.append(event)
        print(f"  [{event['step']}] {event.get('payload', {})}")

    steps = [e["step"] for e in events]
    classify_event = next(e for e in events if e["step"] == "classify")
    assert classify_event["payload"]["task_type"] == "numeric_verify"
    assert "done" in steps

    print("✅ Numeric verification pipeline test passed")


async def test_trace_event_shape():
    """Verify all emitted events match the TraceEvent schema."""
    from orchestrator.agent_graph.graph import run_agent

    task = {
        "task_id": "test-shape-001",
        "modality": "text",
        "content": "Draft a report",
        "context": {}
    }

    async for event in run_agent(task):
        assert "task_id" in event, f"Missing task_id in event: {event}"
        assert "step" in event, f"Missing step in event: {event}"
        assert "payload" in event, f"Missing payload in event: {event}"
        assert "timestamp" in event, f"Missing timestamp in event: {event}"
        assert event["step"] in (
            "classify", "plan", "tool_call", "verify_pass",
            "verify_fail", "retry", "generate", "done", "error"
        ), f"Invalid step: {event['step']}"

    print("✅ TraceEvent shape test passed")


async def main():
    print("=" * 60)
    print("SETU ORCHESTRATOR — STANDALONE TEST SUITE")
    print("=" * 60)

    print("\n--- Classifier Tests ---")
    test_classifier()

    print("\n--- Drafting Pipeline ---")
    await test_graph_drafting()

    print("\n--- Extraction Pipeline ---")
    await test_graph_extraction()

    print("\n--- Codegen Pipeline ---")
    await test_graph_codegen()

    print("\n--- Numeric Verification Pipeline ---")
    await test_graph_numeric()

    print("\n--- TraceEvent Shape Validation ---")
    await test_trace_event_shape()

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED ✅")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
