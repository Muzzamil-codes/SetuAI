from fastapi import APIRouter, HTTPException, Body
import json
import os
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

MODELS_JSON_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 
    "orchestrator", "models_registry", "models.json"
)

class ModelEntry(BaseModel):
    name: str
    modality: str
    role: str
    quant: str
    vram_mb: int
    endpoint: str

@router.get("/models", response_model=List[ModelEntry])
async def get_models():
    """Retrieve the current models configuration."""
    try:
        if not os.path.exists(MODELS_JSON_PATH):
            return []
        with open(MODELS_JSON_PATH, "r") as f:
            data = json.load(f)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/models")
async def update_models(models: List[ModelEntry] = Body(...)):
    """Update the models configuration JSON file."""
    try:
        os.makedirs(os.path.dirname(MODELS_JSON_PATH), exist_ok=True)
        # Dump to JSON and write to file
        with open(MODELS_JSON_PATH, "w") as f:
            json.dump([model.model_dump() for model in models], f, indent=2)
        return {"status": "success", "message": "Models configuration updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
