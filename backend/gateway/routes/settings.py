from fastapi import APIRouter, HTTPException, Body
import json
import os
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

REGISTRY_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 
    "orchestrator", "models_registry"
)
MODELS_JSON_PATH = os.path.join(REGISTRY_DIR, "models.json")
SETTINGS_JSON_PATH = os.path.join(REGISTRY_DIR, "settings.json")

class ModelEntry(BaseModel):
    name: str
    modality: str
    role: str
    quant: str
    vram_mb: int
    endpoint: str
    is_manager: Optional[bool] = False

class ManagerModelConfig(BaseModel):
    manager_model: str

@router.get("/models", response_model=List[ModelEntry])
async def get_models():
    """Retrieve the current models configuration."""
    try:
        if not os.path.exists(MODELS_JSON_PATH):
            return []
        with open(MODELS_JSON_PATH, "r") as f:
            data = json.load(f)
        
        # Check active manager model from settings.json
        manager_model = "deepseek-r1:8b"
        if os.path.exists(SETTINGS_JSON_PATH):
            try:
                with open(SETTINGS_JSON_PATH, "r") as f:
                    s_data = json.load(f)
                    manager_model = s_data.get("manager_model", manager_model)
            except Exception:
                pass

        for entry in data:
            entry["is_manager"] = (entry.get("name") == manager_model) or (entry.get("role") == "manager")

        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/models")
async def update_models(models: List[ModelEntry] = Body(...)):
    """Update the models configuration JSON file."""
    try:
        os.makedirs(REGISTRY_DIR, exist_ok=True)
        dumped = [model.model_dump() for model in models]
        
        # Check if a model was marked as manager
        manager_to_set = None
        for m in dumped:
            if m.get("is_manager") or m.get("role") == "manager":
                manager_to_set = m.get("name")
                break

        with open(MODELS_JSON_PATH, "w") as f:
            json.dump(dumped, f, indent=2)

        if manager_to_set:
            s_data = {}
            if os.path.exists(SETTINGS_JSON_PATH):
                try:
                    with open(SETTINGS_JSON_PATH, "r") as f:
                        s_data = json.load(f)
                except Exception:
                    pass
            s_data["manager_model"] = manager_to_set
            with open(SETTINGS_JSON_PATH, "w") as f:
                json.dump(s_data, f, indent=2)

        return {"status": "success", "message": "Models configuration updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/settings/manager-model")
async def get_manager_model():
    """Retrieve the designated SetuAI Manager Agent model."""
    try:
        if os.path.exists(SETTINGS_JSON_PATH):
            with open(SETTINGS_JSON_PATH, "r") as f:
                data = json.load(f)
                if "manager_model" in data:
                    return {"manager_model": data["manager_model"]}
        
        # Fallback: check models.json for role == 'manager' or 'reasoning'
        if os.path.exists(MODELS_JSON_PATH):
            with open(MODELS_JSON_PATH, "r") as f:
                models = json.load(f)
            for m in models:
                if m.get("role") == "manager":
                    return {"manager_model": m.get("name")}
            for m in models:
                if "deepseek" in m.get("name", "") or "reasoning" in m.get("role", ""):
                    return {"manager_model": m.get("name")}
    except Exception:
        pass
    return {"manager_model": "deepseek-r1:8b"}

@router.post("/settings/manager-model")
async def update_manager_model(config: ManagerModelConfig = Body(...)):
    """Set the designated SetuAI Manager Agent model."""
    try:
        os.makedirs(REGISTRY_DIR, exist_ok=True)
        data = {}
        if os.path.exists(SETTINGS_JSON_PATH):
            try:
                with open(SETTINGS_JSON_PATH, "r") as f:
                    data = json.load(f)
            except Exception:
                data = {}
        data["manager_model"] = config.manager_model
        with open(SETTINGS_JSON_PATH, "w") as f:
            json.dump(data, f, indent=2)
        return {"status": "success", "manager_model": config.manager_model}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
