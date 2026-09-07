import uuid
import asyncio
import json
from datetime import datetime, timezone
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from backend.gateway.schemas import TaskInput, TaskResult, TraceEvent
from backend.gateway.websocket_manager import manager
from backend.db import task_store

router = APIRouter()


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

    # Background execution using mock generator
    asyncio.create_task(mock_trace_generator(task_id))

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