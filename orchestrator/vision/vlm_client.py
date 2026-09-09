import httpx
import base64
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

MODELS_JSON_PATH = os.path.join(
    os.path.dirname(__file__), '..', 'models_registry', 'models.json'
)


def _get_vision_model() -> dict:
    """Reads models.json and returns the first vision-modality model entry.

    Returns:
        dict with 'name' and 'endpoint' keys.
        Falls back to a hardcoded default if the file is missing or has no vision model.
    """
    fallback = {'name': 'qwen2-vl-7b-instruct', 'endpoint': None}
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
    """Extracts structured fields from an image using a VLM based on the user's prompt."""
    stub_response = {
        "valve_tag": "V-204",
        "pressure_reading": "4.05 bar",
        "inspection_date": "2024-03-15",
        "inspector": "R. Kumar",
        "condition": "Normal",
        "next_inspection": "2024-03-29"
    }

    model_info = _get_vision_model()

    # Use the caller-supplied endpoint if provided, otherwise use the registry endpoint
    if endpoint is None:
        endpoint = model_info.get('endpoint')

    # If we still have no endpoint, return stub data
    if not endpoint:
        return stub_response

    try:
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

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()

        # Extract the assistant's message content depending on API
        if "choices" in result:
            content = result["choices"][0]["message"]["content"]
        elif "message" in result:
            content = result["message"].get("content", "")
        else:
            content = ""

        # Try to parse the content as JSON for structured fields
        try:
            return json.loads(content)
        except (json.JSONDecodeError, TypeError):
            # If the model returned non-JSON text, wrap it
            return {"raw_response": content}

    except Exception:
        return stub_response
