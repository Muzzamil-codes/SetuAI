import os
import sys
import pytest
import asyncio

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from tools.vision_tool import run as run_vision_tool
from orchestrator.agent_graph.subgraphs.vision_graph import run_vision_graph
from orchestrator.agent_graph.manager import run_manager_agent

_CANDIDATE_IMAGES = [
    "/Users/nafey/.gemini/antigravity/brain/3dc5a401-aec3-4b44-8022-aee67aca295b/.user_uploaded/media_1788985710070.png",
    os.path.join(PROJECT_ROOT, "uploads", "Screenshot 2026-09-09 at 7.53.16 PM.png"),
]
TEST_IMAGE = next((p for p in _CANDIDATE_IMAGES if os.path.exists(p)), _CANDIDATE_IMAGES[0])


@pytest.mark.asyncio
async def test_vision_pipeline_success_regression():
    """
    Regression test:
    image -> vision tool -> Qwen2.5-VL result -> structured result
    -> visual extraction graph completes successfully with verify_pass.
    """
    assert os.path.exists(TEST_IMAGE), f"Test image not found at {TEST_IMAGE}"

    # 1. Direct tool test
    tool_input = {
        "image_path": TEST_IMAGE,
        "user_prompt": "Extract document information and technical details from this pipeline notice as JSON"
    }
    tool_res = run_vision_tool(tool_input)
    assert tool_res.success is True, f"Vision tool failed: {tool_res.error}"
    assert isinstance(tool_res.data, dict)
    fields = tool_res.data.get("fields")
    assert isinstance(fields, dict) and len(fields) > 0, f"Expected non-empty dict fields, got {fields}"
    assert "NoneType" not in str(tool_res.error)

    # 2. Visual extraction graph test
    graph_input = {
        "image_path": TEST_IMAGE,
        "prompt": "Extract technical details from the pipeline notice"
    }
    result, trace_events = await run_vision_graph(
        task_id="test_vision_success_task",
        graph_input=graph_input
    )

    # Verify steps in trace
    step_names = [e["step"] for e in trace_events]
    assert "plan" in step_names
    assert "tool_call" in step_names
    assert "verify_pass" in step_names
    assert "verify_fail" not in step_names

    # Verify structured result
    assert result["success"] is True
    assert result["status"] == "extracted"
    assert isinstance(result["fields"], dict) and len(result["fields"]) > 0


@pytest.mark.asyncio
async def test_vision_pipeline_actual_failure_produces_verify_fail():
    """
    Failure test:
    Proves that an actual vision failure (e.g. non-existent image)
    produces verify_fail with the real error instead of fake/mock fields.
    """
    non_existent_image = "/path/to/non_existent_pipeline_image_12345.png"

    # 1. Direct tool test with invalid image
    tool_input = {
        "image_path": non_existent_image,
        "user_prompt": "Extract pipeline details"
    }
    tool_res = run_vision_tool(tool_input)
    assert tool_res.success is False
    assert "Vision pipeline error" in tool_res.error
    assert "Image not found" in tool_res.error or "No such file" in tool_res.error

    # 2. Graph execution with invalid image
    graph_input = {
        "image_path": non_existent_image,
        "prompt": "Extract pipeline details"
    }
    result, trace_events = await run_vision_graph(
        task_id="test_vision_fail_task",
        graph_input=graph_input
    )

    # Verify verify_fail is recorded with real error
    step_names = [e["step"] for e in trace_events]
    assert "verify_fail" in step_names
    assert "verify_pass" not in step_names
    assert result["success"] is False

    fail_event = next(e for e in trace_events if e["step"] == "verify_fail")
    fail_detail = fail_event["payload"]["detail"]
    assert "Vision pipeline error" in fail_detail
    assert "Image not found" in fail_detail or "No such file" in fail_detail


@pytest.mark.asyncio
async def test_source_mode_image_only():
    """
    SOURCE MODE: IMAGE_ONLY
    User requests: 'Draft a report based on the attached image.'
    - Vision executes
    - Retrieval does NOT execute (no SOP requested)
    - Output does NOT contain 'SOP Aligned: False' or forced industrial engineering framing
    """
    assert os.path.exists(TEST_IMAGE), f"Test image not found at {TEST_IMAGE}"
    task_input = {
        "task_id": "test_image_only_mode",
        "modality": "image",
        "content": "Draft a report based on the attached image.",
        "image_path": TEST_IMAGE,
        "context": {}
    }
    events = []
    async for evt in run_manager_agent(task_input):
        events.append(evt)

    step_names = [e.get("step") for e in events]
    assert "manager" in step_names
    assert "done" in step_names

    tool_calls = [e.get("payload", {}).get("tool_name") for e in events if e.get("step") == "tool_call"]
    assert "retrieval" not in tool_calls, "Retrieval should NOT be invoked for IMAGE_ONLY mode"

    done_evt = next(e for e in events if e.get("step") == "done")
    summary = done_evt["payload"]["summary"]
    assert "SOP Aligned: False" not in summary
    assert "SOP Aligned: ❌" not in summary


@pytest.mark.asyncio
async def test_source_mode_knowledge_base():
    """
    SOURCE MODE: KNOWLEDGE_BASE
    User requests: 'According to our SOPs, what is the pressure tolerance for Valve V-204?'
    - Retrieval executes
    - Vision does NOT execute
    - Output is grounded in retrieved SOP evidence
    """
    task_input = {
        "task_id": "test_kb_mode",
        "modality": "text",
        "content": "According to our SOPs, what is the pressure tolerance for Valve V-204?",
        "context": {}
    }
    events = []
    async for evt in run_manager_agent(task_input):
        events.append(evt)

    tool_calls = [e.get("payload", {}).get("tool_name") for e in events if e.get("step") == "tool_call"]
    assert "retrieval" in tool_calls, f"Expected retrieval in tool calls, got {tool_calls}"
    assert "vision" not in tool_calls
    assert "vision_tool" not in tool_calls

    done_evt = next(e for e in events if e.get("step") == "done")
    summary = done_evt["payload"]["summary"]
    assert "0.1" in summary or "V-204" in summary


@pytest.mark.asyncio
async def test_source_mode_image_plus_knowledge():
    """
    SOURCE MODE: IMAGE_PLUS_KNOWLEDGE
    User requests: 'According to our SOPs, analyze the attached image.'
    - Both Vision and Retrieval execute
    - Output does not contain 'SOP Aligned: False'
    """
    assert os.path.exists(TEST_IMAGE), f"Test image not found at {TEST_IMAGE}"
    task_input = {
        "task_id": "test_image_plus_kb_mode",
        "modality": "image",
        "content": "According to our SOPs, analyze the attached image.",
        "image_path": TEST_IMAGE,
        "context": {}
    }
    events = []
    async for evt in run_manager_agent(task_input):
        events.append(evt)

    tool_calls = [e.get("payload", {}).get("tool_name") for e in events if e.get("step") == "tool_call"]
    assert "retrieval" in tool_calls, "Retrieval should be executed when SOPs are requested"
    assert any("vision" in tc for tc in tool_calls if tc), "Vision should be executed for image"

    done_evt = next(e for e in events if e.get("step") == "done")
    summary = done_evt["payload"]["summary"]
    assert "SOP Aligned: False" not in summary

