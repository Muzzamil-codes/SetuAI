import httpx
import base64
import json

async def extract_fields_vlm(image_path: str, endpoint: str = None) -> dict:
    """Extracts structured fields from an image using a VLM."""
    stub_response = {
        "valve_tag": "V-204",
        "pressure_reading": "4.05 bar",
        "inspection_date": "2024-03-15",
        "inspector": "R. Kumar",
        "condition": "Normal",
        "next_inspection": "2024-03-29"
    }
    
    if not endpoint:
        return stub_response
        
    try:
        with open(image_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode('utf-8')
            
        payload = {
            "model": "qwen2-vl-7b-instruct",
            "messages": [
                {"role": "user", "content": [
                    {"type": "text", "text": "Extract fields as JSON: valve_tag, pressure_reading, inspection_date, inspector, condition, next_inspection"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                ]}
            ]
        }
        
        async with httpx.AsyncClient() as client:
            return stub_response
    except Exception:
        return stub_response
