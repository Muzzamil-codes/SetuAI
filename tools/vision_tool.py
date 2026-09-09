from __future__ import annotations
import asyncio
from typing import Optional
from pydantic import BaseModel
from orchestrator.vision.tiling import tile_image
from orchestrator.vision.vlm_client import extract_fields_vlm
from orchestrator.vision.ocr_client import extract_text_ocr
from orchestrator.vision.provenance import link_provenance

class ToolResult(BaseModel):
    success: bool
    data: dict = {}
    error: Optional[str] = None

def run(input_data: dict) -> ToolResult:
    """
    Runs the vision extraction pipeline.
    Expects input_data to have:
      - 'image_path': Path to the image
      - 'extract_mode': 'both' (default), 'vlm', or 'ocr'
    """
    image_path = input_data.get("image_path")
    user_prompt = input_data.get("user_prompt")
    
    if not image_path:
        return ToolResult(success=False, error="image_path is required")
        
    try:
        # Run tiling
        tiles = tile_image(image_path)
        
        # In a real async environment we would await this if run() was async,
        # but since tool_registry specifies run(input: dict) as sync,
        # we run the async vlm_client via asyncio.run (or get_event_loop)
        try:
            loop = asyncio.get_running_loop()
            if loop.is_running():
                extracted_fields = extract_fields_vlm(image_path, user_prompt).__await__().send(None)
            else:
                extracted_fields = asyncio.run(extract_fields_vlm(image_path, user_prompt))
        except StopIteration as e:
            extracted_fields = e.value
        except Exception:
            extracted_fields = asyncio.run(extract_fields_vlm(image_path, user_prompt))

        ocr_results = extract_text_ocr(image_path)
        provenance = link_provenance(extracted_fields, ocr_results, tiles)
        
        return ToolResult(
            success=True,
            data={
                "fields": extracted_fields,
                "provenance": provenance
            }
        )
    except Exception as e:
        return ToolResult(success=False, error=f"Vision pipeline error: {str(e)}")
