from __future__ import annotations
import asyncio
from typing import Optional
import os
from pydantic import BaseModel
from orchestrator.vision.tiling import tile_image
from orchestrator.vision.vlm_client import extract_fields_vlm, resolve_image_path
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
    raw_path = input_data.get("image_path")
    user_prompt = input_data.get("user_prompt")
    
    if not raw_path:
        return ToolResult(success=False, error="image_path is required")
        
    image_path = resolve_image_path(raw_path)
    if not os.path.exists(image_path):
        return ToolResult(success=False, error=f"Vision pipeline error: Image not found at path: {raw_path}")

    try:
        # Run tiling
        tiles = tile_image(image_path)
        
        # Run the async vlm_client cleanly using ThreadPoolExecutor if inside a running loop
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                extracted_fields = executor.submit(
                    lambda: asyncio.run(extract_fields_vlm(image_path, user_prompt))
                ).result()
        else:
            extracted_fields = asyncio.run(extract_fields_vlm(image_path, user_prompt))

        if not isinstance(extracted_fields, dict):
            return ToolResult(
                success=False,
                error=f"Vision extraction failed: expected dict from VLM, got {type(extracted_fields).__name__}"
            )

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
