def link_provenance(extracted_fields: dict, ocr_results: list[dict], tile_info: list[dict]) -> list[dict]:
    """Links extracted fields to source bounding boxes, mapping to global coordinates."""
    provenance = []
    
    for field_name, value in extracted_fields.items():
        matched = False
        if isinstance(value, str):
            value_lower = value.lower()
            
            for ocr in ocr_results:
                ocr_text = ocr.get("text", "").lower()
                
                if value_lower in ocr_text or ocr_text in value_lower:
                    bbox = ocr.get("bbox", [0, 0, 0, 0])
                    tile_idx = ocr.get("tile_idx", 0)
                    
                    # Offset by tile coordinates if applicable
                    if tile_info and tile_idx < len(tile_info):
                        tile = tile_info[tile_idx]
                        offset_x = tile.get("x", 0)
                        offset_y = tile.get("y", 0)
                        bbox = [
                            bbox[0] + offset_x, bbox[1] + offset_y,
                            bbox[2] + offset_x, bbox[3] + offset_y
                        ]
                        
                    provenance.append({
                        "field_name": field_name,
                        "value": value,
                        "bbox": bbox,
                        "tile_idx": tile_idx,
                        "confidence": ocr.get("confidence", 1.0),
                        "source_type": "vlm"
                    })
                    matched = True
                    break
                    
        if not matched:
            provenance.append({
                "field_name": field_name,
                "value": value,
                "bbox": None,
                "tile_idx": -1,
                "confidence": 0.0,
                "source_type": "vlm"
            })
            
    return provenance
