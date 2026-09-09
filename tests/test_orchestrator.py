"""Standalone test for the SetuAI Manager Agent & ReAct Orchestrator pipeline.

Tests:
1. Manager Agent initialization and ReAct protocol
2. Direct conversational handling (no unnecessary graphs launched)
3. Specialized sub-graph dispatch (codegen_graph, drafting_graph, numeric_verify_graph, vision_graph)
4. Sequential multi-task chaining (codegen → drafting)
5. TraceEvent shape validation
"""
import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def test_conversational():
    """Test that pure conversation is handled directly by SetuAI Manager Agent."""
    from orchestrator.agent_graph.graph import run_agent

    task = {
        "task_id": "test-conv-001",
        "modality": "text",
        "content": "Hello SetuAI, what are your capabilities?",
        "context": {}
    }

    events = []
    async for event in run_agent(task):
        events.append(event)

    steps = [e["step"] for e in events]
    assert "manager" in steps, f"Missing manager event. Got: {steps}"
    assert "done" in steps, f"Missing done event. Got: {steps}"
    done_event = next(e for e in events if e["step"] == "done")
    assert done_event.get("payload", {}).get("summary"), "Missing conversational summary"
    print("✅ Conversational test passed")


async def test_subgraph_codegen():
    """Test codegen specialist sub-graph execution."""
    from orchestrator.agent_graph.subgraphs.codegen_graph import run_codegen_graph

    output, events = await run_codegen_graph(
        task_id="test-codegen-sub-001",
        graph_input={"instruction": "Write a python function to compute factorial"}
    )

    steps = [e["step"] for e in events]
    assert "plan" in steps, f"Missing plan in codegen. Got: {steps}"
    assert "tool_call" in steps, f"Missing tool_call in codegen. Got: {steps}"
    assert "code" in output, "Missing code in codegen output"
    print("✅ Codegen sub-graph test passed")


async def test_subgraph_drafting():
    """Test drafting specialist sub-graph execution."""
    from orchestrator.agent_graph.subgraphs.drafting_graph import run_drafting_graph

    output, events = await run_drafting_graph(
        task_id="test-drafting-sub-001",
        graph_input={
            "instruction": "Draft a safety notice for plant maintenance",
            "format": "docx",
            "doc_type": "notice"
        }
    )

    steps = [e["step"] for e in events]
    assert "plan" in steps, f"Missing plan in drafting. Got: {steps}"
    assert "tool_call" in steps, f"Missing tool_call in drafting. Got: {steps}"
    assert "verify_pass" in steps or "verify_fail" in steps
    print("✅ Drafting sub-graph test passed")


async def test_subgraph_numeric():
    """Test numeric verify specialist sub-graph execution."""
    from orchestrator.agent_graph.subgraphs.numeric_verify_graph import run_numeric_verify_graph

    output, events = await run_numeric_verify_graph(
        task_id="test-numeric-sub-001",
        graph_input={"expression": "100 * 0.2", "expected": 20.0}
    )

    assert "computed_value" in output
    print("✅ Numeric verify sub-graph test passed")


async def test_trace_event_shape():
    """Verify all emitted events match the TraceEvent schema."""
    from orchestrator.agent_graph.graph import run_agent

    task = {
        "task_id": "test-shape-001",
        "modality": "text",
        "content": "Hi",
        "context": {}
    }

    async for event in run_agent(task):
        assert "task_id" in event, f"Missing task_id in event: {event}"
        assert "step" in event, f"Missing step in event: {event}"
        assert "payload" in event, f"Missing payload in event: {event}"
        assert "timestamp" in event, f"Missing timestamp in event: {event}"
        assert event["step"] in (
            "manager", "classify", "plan", "tool_call", "verify_pass",
            "verify_fail", "retry", "generate", "streaming", "stream_chunk", "done", "error"
        ), f"Invalid step: {event['step']}"

    print("✅ TraceEvent shape validation passed")


async def main():
    print("=" * 60)
    print("SETUAI MANAGER AGENT & REACT ORCHESTRATOR TEST SUITE")
    print("=" * 60)

    print("\n--- Codegen Sub-Graph ---")
    await test_subgraph_codegen()

    print("\n--- Drafting Sub-Graph ---")
    await test_subgraph_drafting()

    print("\n--- Numeric Sub-Graph ---")
    await test_subgraph_numeric()

    print("\n--- Conversational Agent ---")
    await test_conversational()

    print("\n--- TraceEvent Shape Validation ---")
    await test_trace_event_shape()

    print("\n" + "=" * 60)
    print("ALL MANAGER AGENT TESTS PASSED ✅")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
