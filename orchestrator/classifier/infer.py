import json
import os

def classify_task(content: str, modality: str) -> str:
    """Classifies a task into extraction, codegen, drafting, or numeric_verify."""
    if modality in ["image", "file"]:
        return "extraction"
    
    content_lower = content.lower()
    
    code_keywords = ["python", "function", "script", "code", "modbus", "plc", "sql", "debug", "implement"]
    if any(keyword in content_lower for keyword in code_keywords):
        return "codegen"
        
    numeric_keywords = ["verify", "calculate", "tolerance", "pressure", "check", "math", "number"]
    if any(keyword in content_lower for keyword in numeric_keywords):
        if "verify" in content_lower or "calculate" in content_lower or "check" in content_lower:
            return "numeric_verify"
            
    return "drafting"

def select_model(task_type: str, models_manifest: list = None) -> dict:
    """Selects the appropriate model from the manifest based on the task type."""
    if not models_manifest:
        models_manifest_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models_registry", "models.json")
        try:
            with open(models_manifest_path, "r") as f:
                models_manifest = json.load(f)
        except Exception:
            models_manifest = []
            
    role_map = {
        "extraction": "extraction",
        "codegen": "codegen",
        "drafting": "reasoning",
        "numeric_verify": "reasoning"
    }
    
    target_role = role_map.get(task_type, "reasoning")
    
    for model in models_manifest:
        if model.get("role") == target_role:
            return model
            
    return {}
