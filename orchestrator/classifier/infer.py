import json
import os

try:
    import torch
    from transformers import AutoTokenizer, AutoModel
    HAS_MODERNBERT = True
except ImportError:
    HAS_MODERNBERT = False

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    import urllib.request
    import urllib.error

# Lazy loading of ModernBERT
_tokenizer = None
_model = None

def _load_modernbert():
    global _tokenizer, _model
    if not HAS_MODERNBERT:
        return
    if _model is None:
        try:
            model_id = "answerdotai/ModernBERT-base"
            _tokenizer = AutoTokenizer.from_pretrained(model_id)
            _model = AutoModel.from_pretrained(model_id)
            _model.eval()
        except Exception as e:
            print(f"ModernBERT load error: {e}")

def get_embedding(text: str):
    if not HAS_MODERNBERT:
        return None
    if _model is None or _tokenizer is None:
        _load_modernbert()
    if _model is None:
        return None
        
    with torch.no_grad():
        inputs = _tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        outputs = _model(**inputs)
        attention_mask = inputs['attention_mask']
        token_embeddings = outputs.last_hidden_state
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
        sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
        return sum_embeddings / sum_mask

def _get_llm_endpoint():
    models_manifest_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models_registry", "models.json")
    try:
        with open(models_manifest_path, "r") as f:
            manifest = json.load(f)
            for m in manifest:
                if m.get("name") == "deepseek-r1":
                    return m.get("endpoint")
    except Exception:
        pass
    return None

def classify_task_with_confidence(content: str, modality: str) -> tuple[str, float, str]:
    if modality in ["image", "file"]:
        return "extraction", 1.0, "modality_rule"

    # Tier 1: Local LLM structured classification
    endpoint = _get_llm_endpoint()
    if endpoint:
        url = f"{endpoint}/chat/completions"
        system_prompt = (
            "Classify the text into one of these 4 categories: codegen, numeric_verify, extraction, drafting.\n"
            "Categories:\n"
            "- codegen: writing or debugging code, software architecture.\n"
            "- numeric_verify: verifying calculations, checking numeric values, tolerances.\n"
            "- extraction: extracting data from tables, documents, or logs.\n"
            "- drafting: writing reports, emails, summaries, non-code text.\n"
            "Return JSON only with keys: 'task_type' (str), 'confidence' (float 0-1), 'reasoning' (str)."
        )
        
        payload = {
            "model": "deepseek-r1",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content}
            ],
            "response_format": {"type": "json_object"}
        }
        
        try:
            if HAS_REQUESTS:
                resp = requests.post(url, json=payload, timeout=5)
                if resp.status_code == 200:
                    data = resp.json()
                    content_str = data['choices'][0]['message']['content']
                    res = json.loads(content_str)
                    task_type = res.get('task_type')
                    if task_type in ["codegen", "numeric_verify", "extraction", "drafting"]:
                        return task_type, float(res.get('confidence', 0.9)), "llm"
            else:
                req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'),
                                             headers={'Content-Type': 'application/json'},
                                             method='POST')
                with urllib.request.urlopen(req, timeout=5) as resp:
                    if resp.status == 200:
                        data = json.loads(resp.read().decode('utf-8'))
                        content_str = data['choices'][0]['message']['content']
                        res = json.loads(content_str)
                        task_type = res.get('task_type')
                        if task_type in ["codegen", "numeric_verify", "extraction", "drafting"]:
                            return task_type, float(res.get('confidence', 0.9)), "llm"
        except Exception as e:
            print(f"LLM classification failed: {e}")

    # Tier 2: Enhanced keyword heuristics
    content_lower = content.lower()
    categories = {
        "codegen": {
            "pos": ["python", "function", "script", "code", "debug", "program", "algorithm", "c++", "java", "implement", "coding", "dynamic programming", "sorting", "recursion", "class", "api", "backend", "frontend"],
            "neg": ["document", "report", "draft", "note", "memo", "approval", "summary"]
        },
        "numeric_verify": {
            "pos": ["verify", "calculate", "tolerance", "check", "numeric", "math", "computation", "value", "formula"],
            "neg": []
        },
        "extraction": {
            "pos": ["extract", "scan", "ocr", "parse", "invoice", "image", "structured data", "table", "fields"],
            "neg": []
        },
        "drafting": {
            "pos": ["draft", "approval", "note", "write", "document", "email", "report", "summarize", "compose", "letter", "memo"],
            "neg": ["python", "function", "algorithm", "debug", "code", "implement"]
        }
    }
    
    scores = {}
    for cat, kws in categories.items():
        score = sum(1 for kw in kws["pos"] if kw in content_lower)
        score -= sum(1 for kw in kws["neg"] if kw in content_lower)
        scores[cat] = score
        
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    best_cat, best_score = sorted_scores[0]
    second_best_score = sorted_scores[1][1] if len(sorted_scores) > 1 else 0
    
    if best_score > 0:
        confidence = min(0.9, 0.5 + 0.1 * (best_score - second_best_score))
        return best_cat, confidence, "heuristics"

    # Tier 3: ModernBERT (last resort)
    try:
        content_emb = get_embedding(content)
        if content_emb is not None:
            bert_categories = {
                "codegen": "write code program function algorithm implement debug software python java C++ javascript rust dynamic programming sorting",
                "numeric_verify": "verify calculate math tolerance pressure number computation check numeric value formula",
                "extraction": "extract fields from scanned document image OCR structured data table parse invoice",
                "drafting": "draft approval note write document email report summarize compose letter memo"
            }
            
            best_bert_cat = "drafting"
            best_bert_score = -1.0
            
            content_emb = torch.nn.functional.normalize(content_emb, p=2, dim=1)
            
            for cat, desc in bert_categories.items():
                cat_emb = get_embedding(desc)
                cat_emb = torch.nn.functional.normalize(cat_emb, p=2, dim=1)
                score = torch.mm(content_emb, cat_emb.transpose(0, 1)).item()
                
                if score > best_bert_score:
                    best_bert_score = score
                    best_bert_cat = cat
                    
            if best_bert_score > -1.0:
                return best_bert_cat, float(best_bert_score), "modernbert"
    except Exception as e:
        print(f"ModernBERT classification failed: {e}")
        
    return "drafting", 0.1, "fallback"

def classify_task(content: str, modality: str) -> str:
    """Classifies a task into extraction, codegen, drafting, or numeric_verify."""
    task_type, _, _ = classify_task_with_confidence(content, modality)
    return task_type

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
