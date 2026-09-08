import json
import os

import torch
from transformers import AutoTokenizer, AutoModel

# Lazy loading of ModernBERT
_tokenizer = None
_model = None

def _load_modernbert():
    global _tokenizer, _model
    if _model is None:
        try:
            model_id = "answerdotai/ModernBERT-base"
            _tokenizer = AutoTokenizer.from_pretrained(model_id)
            _model = AutoModel.from_pretrained(model_id)
            _model.eval()
        except Exception as e:
            print(f"ModernBERT load error: {e}")

def get_embedding(text: str) -> torch.Tensor:
    if _model is None or _tokenizer is None:
        _load_modernbert()
    if _model is None:
        return None
        
    with torch.no_grad():
        inputs = _tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        outputs = _model(**inputs)
        # Use CLS token representation or mean pooling. We use mean pooling here.
        attention_mask = inputs['attention_mask']
        token_embeddings = outputs.last_hidden_state
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
        sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
        return sum_embeddings / sum_mask

def classify_task(content: str, modality: str) -> str:
    """Classifies a task into extraction, codegen, drafting, or numeric_verify using ModernBERT."""
    if modality in ["image", "file"]:
        return "extraction"
        
    try:
        content_emb = get_embedding(content)
        if content_emb is None:
            raise RuntimeError("Model not loaded")
            
        categories = {
            "codegen": "write code program function algorithm implement debug software python java C++ javascript rust dynamic programming sorting",
            "numeric_verify": "verify calculate math tolerance pressure number computation check numeric value formula",
            "extraction": "extract fields from scanned document image OCR structured data table parse invoice",
            "drafting": "draft approval note write document email report summarize compose letter memo"
        }
        
        best_cat = "drafting"
        best_score = -1.0
        
        content_emb = torch.nn.functional.normalize(content_emb, p=2, dim=1)
        
        for cat, desc in categories.items():
            cat_emb = get_embedding(desc)
            cat_emb = torch.nn.functional.normalize(cat_emb, p=2, dim=1)
            score = torch.mm(content_emb, cat_emb.transpose(0, 1)).item()
            
            if score > best_score:
                best_score = score
                best_cat = cat

        print(f"[Classifier] ModernBERT result: '{best_cat}' (score: {best_score:.4f}) for: '{content[:80]}'")
        return best_cat
    except Exception as e:
        print(f"ModernBERT classification failed, falling back to heuristics: {e}")
        # Fallback heuristics
        content_lower = content.lower()
        if any(kw in content_lower for kw in [
            "python", "function", "script", "code", "debug", "program",
            "algorithm", "c++", "java", "implement", "coding", "dynamic programming",
            "sorting", "recursion", "class", "api", "backend", "frontend"
        ]):
            return "codegen"
        if any(kw in content_lower for kw in ["verify", "calculate", "tolerance", "check", "numeric"]):
            return "numeric_verify"
        if any(kw in content_lower for kw in ["extract", "scan", "ocr", "parse", "invoice", "image"]):
            return "extraction"
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
