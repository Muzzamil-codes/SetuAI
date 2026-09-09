import uuid
import asyncio
import json
from datetime import datetime, timezone
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from backend.gateway.schemas import TaskInput, TaskResult, TraceEvent
from backend.gateway.websocket_manager import manager
from backend.db import task_store

router = APIRouter()


async def run_orchestrator(task_id: str, task_input_dict: dict):
    """Runs the real orchestrator agent graph, streaming TraceEvents via WebSocket.
    
    Falls back to mock trace generator if the orchestrator is not available.
    """
    try:
        from orchestrator.agent_graph.graph import run_agent
        
        async for event_dict in run_agent(task_input_dict):
            event_dict["task_id"] = task_id
            
            event = TraceEvent(
                task_id=task_id,
                step=event_dict.get("step", "error"),
                payload=event_dict.get("payload", {}),
                timestamp=event_dict.get("timestamp", datetime.now(timezone.utc).isoformat())
            )
            event_json = event.model_dump_json()
            await manager.broadcast_event(task_id, event_json)
            
            await asyncio.sleep(0.3)
            
            if event.step == "done":
                payload = event.payload
                task_store.update_task_result(
                    task_id=task_id,
                    status="done",
                    summary=payload.get("summary", "Task completed successfully."),
                    artifacts=payload.get("artifacts", [])
                )
            elif event.step == "error":
                task_store.update_task_result(
                    task_id=task_id,
                    status="error",
                    summary="",
                    error=event.payload.get("error", "Unknown error")
                )
                
    except ImportError:
        await mock_trace_generator(task_id)
    except Exception as e:
        error_event = TraceEvent(
            task_id=task_id,
            step="error",
            payload={"error": str(e)},
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        await manager.broadcast_event(task_id, error_event.model_dump_json())
        task_store.update_task_result(
            task_id=task_id,
            status="error",
            summary="",
            error=str(e)
        )


async def mock_trace_generator(task_id: str):
    """Simulates agent steps with 1-second sleeps for self-testing until Muzzamil's orchestrator is ready."""
    steps = [
        ("classify", {"task_type": "drafting", "confidence": 0.94}),
        ("plan", {"summary": "Extract fields, verify numeric values, draft note"}),
        ("tool_call", {"tool_name": "extract_from_image", "input": {"image_path": "uploads/scan_001.jpg"}}),
        ("verify_pass", {"tool_name": "verify_numeric", "detail": "within tolerance"}),
        ("generate", {"artifact_type": "docx"}),
        ("done", {"artifacts": [{"type": "docx", "filename": "approval_note.docx", "path": "outputs/approval_note.docx"}], "summary": "Task finished successfully."})
    ]

    for step, payload in steps:
        await asyncio.sleep(1)
        timestamp = datetime.now(timezone.utc).isoformat()
        event = TraceEvent(task_id=task_id, step=step, payload=payload, timestamp=timestamp)
        event_json = event.model_dump_json()

        # Stream event live over WebSocket
        await manager.broadcast_event(task_id, event_json)

        # Update database on completion
        if step == "done":
            task_store.update_task_result(
                task_id=task_id,
                status="done",
                summary=payload.get("summary", ""),
                artifacts=payload.get("artifacts", [])
            )


@router.post("/task")
async def create_task(task_input: TaskInput):
    """Creates a new task and returns a UUID task_id."""
    task_id = str(uuid.uuid4())
    task_input.task_id = task_id
    task_store.save_task(task_id=task_id, status="running")

    task_input_dict = {
        "task_id": task_id,
        "modality": task_input.modality,
        "content": task_input.content,
        "context": task_input.context,
        "model_override": task_input.model_override or "auto"
    }

    asyncio.create_task(run_orchestrator(task_id, task_input_dict))

    return {"task_id": task_id}


@router.get("/task/{task_id}", response_model=TaskResult)
async def get_task(task_id: str):
    """Retrieves current task state and artifacts from SQLite."""
    task_data = task_store.get_task(task_id)
    if not task_data:
        raise HTTPException(status_code=404, detail="Task not found")

    return TaskResult(
        task_id=task_data["task_id"],
        status=task_data["status"],
        summary=task_data["summary"],
        artifacts=task_data["artifacts"],
        error=task_data["error"]
    )


@router.websocket("/trace/{task_id}")
async def websocket_trace(websocket: WebSocket, task_id: str):
    """Streams TraceEvent messages live to connected clients."""
    await manager.connect(task_id, websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep socket alive
    except WebSocketDisconnect:
        manager.disconnect(task_id, websocket)