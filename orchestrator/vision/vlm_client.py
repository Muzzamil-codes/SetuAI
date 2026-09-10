import httpx
import base64
import json
import os
import re
import sys
import unicodedata

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

MODELS_JSON_PATH = os.path.join(
    os.path.dirname(__file__), '..', 'models_registry', 'models.json'
)


def resolve_image_path(path: str) -> str:
    """Resolves image paths across relative paths, workspace root, and unicode space variations (e.g. Mac screenshot NFKC)."""
    if not path:
        return path
    if os.path.exists(path):
        return path

    workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    candidates = [
        path,
        os.path.join(workspace_root, path),
        os.path.join("uploads", os.path.basename(path)),
        os.path.join(workspace_root, "uploads", os.path.basename(path))
    ]

    for cand in candidates:
        if os.path.exists(cand):
            return cand
        d = os.path.dirname(cand) or "."
        if os.path.exists(d) and os.path.isdir(d):
            base_norm = unicodedata.normalize("NFKC", os.path.basename(cand))
            try:
                for f in os.listdir(d):
                    if unicodedata.normalize("NFKC", f) == base_norm:
                        return os.path.join(d, f)
            except Exception:
                pass

    return path


def _get_vision_model() -> dict:
    """Reads models.json and returns the first vision-modality model entry.

    Returns:
        dict with 'name' and 'endpoint' keys.
        Falls back to a default if the file is missing or has no vision model.
    """
    fallback = {'name': 'qwen2.5vl:7b', 'endpoint': 'http://localhost:11434/v1'}
    try:
        with open(MODELS_JSON_PATH, 'r') as f:
            models = json.load(f)
        for model in models:
            if model.get('modality') == 'vision':
                return {'name': model['name'], 'endpoint': model['endpoint']}
    except Exception:
        pass
    return fallback


async def extract_fields_vlm(image_path: str, user_prompt: str = None, endpoint: str = None) -> dict:
    """Extracts structured fields from an image (or PDF) using a VLM based on the user's prompt."""
    image_path = resolve_image_path(image_path)
    if not image_path or not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found at path: {image_path}")

    # --- PDF handling: render pages to images, process each, merge results ---
    from orchestrator.vision.pdf_renderer import is_pdf
    if is_pdf(image_path):
        from orchestrator.vision.pdf_renderer import render_pdf_pages
        page_images = render_pdf_pages(image_path)
        if not page_images:
            raise ValueError(f"PDF rendered zero page images: {image_path}")

        merged: dict = {}
        for i, page_img in enumerate(page_images):
            page_prompt = user_prompt
            if len(page_images) > 1:
                # Tell the VLM which page it's looking at
                page_note = f"(This is page {i + 1} of {len(page_images)} from a PDF document.) "
                page_prompt = page_note + (user_prompt or "")
            page_result = await extract_fields_vlm(page_img, page_prompt, endpoint)
            if isinstance(page_result, dict):
                if len(page_images) == 1:
                    merged = page_result
                else:
                    # Prefix keys with page number to avoid collisions
                    for k, v in page_result.items():
                        if k == "raw_response":
                            prev = merged.get("raw_response", "")
                            merged["raw_response"] = (prev + f"\n\n--- Page {i + 1} ---\n" + v).strip()
                        else:
                            merged[f"page_{i + 1}_{k}"] = v

        # Clean up temporary rendered images
        import shutil
        if page_images:
            tmp_dir = os.path.dirname(page_images[0])
            shutil.rmtree(tmp_dir, ignore_errors=True)

        return merged if merged else {"raw_response": "No content extracted from PDF pages."}

    model_info = _get_vision_model()

    # Use the caller-supplied endpoint if provided, otherwise use the registry endpoint
    if endpoint is None:
        endpoint = model_info.get('endpoint')

    if not endpoint:
        raise ValueError("No vision model endpoint configured.")

    with open(image_path, "rb") as f:
        raw_b64 = base64.b64encode(f.read()).decode('utf-8')

    default_prompt = "Extract fields as JSON: valve_tag, pressure_reading, inspection_date, inspector, condition, next_inspection"
    actual_prompt = f"Analyze the image and return a JSON object with the requested information: {user_prompt}" if user_prompt else default_prompt
    
    is_ollama = "11434" in endpoint
    url = endpoint.replace("/v1", "/api/chat") if is_ollama else f"{endpoint.rstrip('/')}/chat/completions"

    if is_ollama:
        payload = {
            "model": model_info['name'],
            "messages": [
                {
                    "role": "user",
                    "content": actual_prompt,
                    "images": [raw_b64]
                }
            ],
            "stream": False,
            "options": {
                "num_ctx": 16384,
                "num_predict": 4096
            }
        }
    else:
        payload = {
            "model": model_info['name'],
            "messages": [
                {"role": "user", "content": [
                    {"type": "text", "text": actual_prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{raw_b64}"}}
                ]}
            ],
            "max_tokens": 4096,
            "options": {
                "num_ctx": 16384,
                "num_predict": 4096
            }
        }
    
    print(f"[vlm_client] Extraction Request (Native Ollama: {is_ollama}):")
    print(f"  - Model: {model_info['name']}")
    if is_ollama:
        print(f"  - Context Limit (num_ctx): {payload['options']['num_ctx']}")
        print(f"  - Gen Limit (num_predict): {payload['options']['num_predict']}")
    else:
        print(f"  - Gen Limit (max_tokens): {payload['max_tokens']}")

    async with httpx.AsyncClient(timeout=180.0) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        result = response.json()

    # Extract the assistant's message content depending on API
    if "choices" in result and result["choices"]:
        content = result["choices"][0]["message"]["content"]
    elif "message" in result:
        content = result["message"].get("content", "")
    else:
        content = ""

    if not content:
        raise ValueError("Qwen2.5-VL returned empty content.")

    # Try to parse the content as JSON for structured fields
    clean_content = content.strip()
    if "```" in clean_content:
        fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", clean_content)
        if fence_match:
            clean_content = fence_match.group(1).strip()

    try:
        parsed = json.loads(clean_content)
        if isinstance(parsed, dict):
            return parsed
    except (json.JSONDecodeError, TypeError):
        # Fallback to finding outermost { and }
        start = clean_content.find("{")
        end = clean_content.rfind("}")
        if start != -1 and end > start:
            try:
                parsed = json.loads(clean_content[start:end + 1])
                if isinstance(parsed, dict):
                    return parsed
            except Exception:
                pass

    # If the model returned non-JSON text, wrap it in a dict with raw_response
    return {"raw_response": content}
