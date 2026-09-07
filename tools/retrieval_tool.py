from __future__ import annotations
from typing import Optional
from pydantic import BaseModel
from grounding.retrieval import retrieve as do_retrieve
from grounding.retrieval import verify_claim as do_verify_claim

class ToolResult(BaseModel):
    success: bool
    data: dict = {}
    error: Optional[str] = None

def run(input: dict) -> ToolResult:
    """
    Universal entry point for Muzzamil's LangGraph orchestrator.
    Handles retrieve() and verify_claim() with complete exception safety.
    """
    try:
        if "claim" in input:
            claim = input.get("claim", "")
            chunks = input.get("chunks", [])
            data = do_verify_claim(claim, chunks)
            return ToolResult(success=True, data=data)

        elif "query" in input:
            query = input.get("query", "")
            top_k = input.get("top_k", 5)
            data = do_retrieve(query, top_k=top_k)
            return ToolResult(success=True, data=data)

        else:
            return ToolResult(
                success=False,
                error="Invalid input: must contain either 'query' or 'claim'"
            )
    except Exception as e:
        return ToolResult(success=False, error=f"Retrieval error: {str(e)}")