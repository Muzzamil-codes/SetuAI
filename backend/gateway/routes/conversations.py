from fastapi import APIRouter, HTTPException, Body
from typing import List, Dict, Any
from backend.db import task_store

router = APIRouter()

@router.get("/conversations")
async def list_conversations():
    """Retrieve all conversations."""
    try:
        return task_store.get_conversations()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/conversations")
async def save_conversations(conversations: List[Dict[str, Any]] = Body(...)):
    """Save a list of conversations (bulk sync from client)."""
    try:
        # In a real app we'd sync them intelligently, 
        # but for simplicity we can just loop and save.
        # Wait, if we want to delete ones that are removed, we can just clear and insert, 
        # or we just rely on explicit DELETE endpoints.
        for conv in conversations:
            task_store.save_conversation(conv)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/conversations/{conv_id}")
async def save_conversation(conv_id: str, conv: Dict[str, Any] = Body(...)):
    """Save a single conversation."""
    try:
        if conv.get("id") != conv_id:
            raise HTTPException(status_code=400, detail="ID mismatch")
        task_store.save_conversation(conv)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/conversations/{conv_id}")
async def delete_conversation(conv_id: str):
    """Delete a conversation."""
    try:
        task_store.delete_conversation(conv_id)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
