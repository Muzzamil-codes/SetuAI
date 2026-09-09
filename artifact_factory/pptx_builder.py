import os
import json
from typing import Dict, Any

try:
    from pptx import Presentation
    HAS_PPTX = True
except ImportError:
    HAS_PPTX = False


def generate_pptx(data: dict, output_dir: str = "outputs") -> Dict[str, Any]:
    """Generate a .pptx presentation from structured data.
    
    Args:
        data: dict with keys: title, company, reviewer, department, findings, recommendations
        output_dir: directory to write the output file
    
    Returns:
        dict with keys: success, filename, path, error
    """
    os.makedirs(output_dir, exist_ok=True)
    
    if not HAS_PPTX:
        return {"success": False, "filename": "", "path": "", "error": "python-pptx not installed"}
    
    try:
        prs = Presentation()
        
        # Slide 1: Title
        slide = prs.slides.add_slide(prs.slide_layouts[0])
        slide.shapes.title.text = data.get("title", "Presentation")
        slide.placeholders[1].text = (
            f"Company: {data.get('company_or_org', data.get('company', 'N/A'))}\n"
            f"Presenter: {data.get('signatory', data.get('reviewer', 'N/A'))}\n"
            f"Department: {data.get('department', 'N/A')}"
        )
        
        custom_slides = data.get("slides", [])
        if custom_slides:
            for s_data in custom_slides:
                slide = prs.slides.add_slide(prs.slide_layouts[1])
                slide.shapes.title.text = s_data.get("title", "Topic")
                content = s_data.get("content", s_data.get("bullets", []))
                text_box = slide.placeholders[1]
                text_box.text = ""
                if isinstance(content, list):
                    for pt in content:
                        text_box.text += f"\u2022 {pt}\n"
                else:
                    text_box.text = str(content)
        else:
            # Fallback structure
            findings = data.get("findings", [])
            if findings:
                slide = prs.slides.add_slide(prs.slide_layouts[1])
                slide.shapes.title.text = "Executive Summary"
                slide.placeholders[1].text = f"Total Items Reviewed: {len(findings)}"
            
            recommendations = data.get("action_items_or_recommendations", data.get("recommendations", []))
            if recommendations:
                slide = prs.slides.add_slide(prs.slide_layouts[1])
                slide.shapes.title.text = "Recommendations & Directives"
                text_box = slide.placeholders[1]
                text_box.text = ""
                for rec in recommendations:
                    text_box.text += f"\u2022 {rec}\n"
        
        from datetime import datetime
        import re
        safe_title = re.sub(r'[^a-zA-Z0-9_\-]', '_', data.get('title', 'presentation')[:30]).strip('_').lower()
        filename = f"presentation_{safe_title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pptx"
        path = os.path.join(output_dir, filename)
        prs.save(path)
        
        return {"success": True, "filename": filename, "path": path, "error": None}
    except Exception as e:
        return {"success": False, "filename": "", "path": "", "error": str(e)}


if __name__ == "__main__":
    with open("data.json", "r") as f:
        data = json.load(f)
    result = generate_pptx(data, "output")
    print(f"PPTX Generated: {result}")