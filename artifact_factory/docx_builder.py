import os
import json
from datetime import datetime
from typing import Dict, Any

try:
    from docx import Document
    from docx.shared import Pt, Inches
    from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False


def generate_docx(data: dict, output_dir: str = "outputs") -> Dict[str, Any]:
    """Generate a professional .docx approval note from structured data.
    
    Args:
        data: dict with keys: title, company, reviewer, department, findings, recommendations
        output_dir: directory to write the output file
    
    Returns:
        dict with keys: success, filename, path, error
    """
    os.makedirs(output_dir, exist_ok=True)
    
    if not HAS_DOCX:
        # Fallback to plain text
        filename = f"approval_note_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        path = os.path.join(output_dir, filename)
        with open(path, "w") as f:
            f.write(f"{data.get('title', 'Approval Note')}\n")
            f.write(f"Company: {data.get('company', 'N/A')}\n")
            f.write(f"Reviewer: {data.get('reviewer', 'N/A')}\n")
            f.write(f"Department: {data.get('department', 'N/A')}\n\n")
            f.write("Findings:\n")
            for item in data.get("findings", []):
                f.write(f"  - {item.get('field', '')}: {item.get('value', '')} [{item.get('status', '')}]\n")
            f.write("\nRecommendations:\n")
            for rec in data.get("recommendations", []):
                f.write(f"  - {rec}\n")
        return {"success": True, "filename": filename, "path": path, "error": None}
    
    try:
        doc = Document()
        
        # Cover Page
        title = doc.add_paragraph()
        title.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        run = title.add_run(data.get("title", "Approval Note"))
        run.bold = True
        run.font.size = Pt(24)
        
        doc.add_paragraph(f"Company: {data.get('company', 'N/A')}")
        doc.add_paragraph(f"Reviewer: {data.get('reviewer', 'N/A')}")
        doc.add_paragraph(f"Department: {data.get('department', 'N/A')}")
        
        subtitle = doc.add_paragraph()
        subtitle.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        subtitle.add_run(f"\nGenerated: {datetime.now().strftime('%d %B %Y')}")
        
        doc.add_page_break()
        
        # Executive Summary
        doc.add_heading("Executive Summary", level=1)
        findings = data.get("findings", [])
        doc.add_paragraph(f"Total Findings: {len(findings)}")
        
        # Findings Table
        doc.add_heading("Findings", level=1)
        table = doc.add_table(rows=1, cols=3)
        table.style = "Table Grid"
        header = table.rows[0].cells
        header[0].text = "Field"
        header[1].text = "Value"
        header[2].text = "Status"
        
        for item in findings:
            row = table.add_row().cells
            row[0].text = str(item.get("field", ""))
            row[1].text = str(item.get("value", ""))
            row[2].text = str(item.get("status", ""))
        
        # Try to add chart if it exists
        try:
            from artifact_factory.chart_generator import generate_chart
            chart_path = generate_chart(data, output_dir)
            if chart_path and os.path.exists(chart_path):
                doc.add_heading("Status Distribution", level=1)
                doc.add_picture(chart_path, width=Inches(4.5))
        except Exception:
            pass
        
        # Recommendations
        recommendations = data.get("recommendations", [])
        if recommendations:
            doc.add_heading("Recommendations", level=1)
            for rec in recommendations:
                doc.add_paragraph(rec, style="List Bullet")
        
        # Signature
        doc.add_page_break()
        doc.add_heading("Approval", level=1)
        doc.add_paragraph("\n\n")
        doc.add_paragraph("________________________")
        doc.add_paragraph("Authorized Signatory")
        
        filename = f"approval_note_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
        path = os.path.join(output_dir, filename)
        doc.save(path)
        
        return {"success": True, "filename": filename, "path": path, "error": None}
    except Exception as e:
        return {"success": False, "filename": "", "path": "", "error": str(e)}


if __name__ == "__main__":
    with open("data.json", "r") as f:
        data = json.load(f)
    result = generate_docx(data, "output")
    print(f"DOCX Generated: {result}")