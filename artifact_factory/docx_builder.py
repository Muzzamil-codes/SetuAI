"""
Word Document (.docx) Generator for Setu Artifact Factory.
Generates institutional approval notes with findings tables and embedded scans.
Follows API_CONTRACTS.md Section 3.4.
Owned by Parvez.
"""
import os
import re
import zipfile
import datetime
from typing import Dict, Any, Optional
from verification.schemas import ToolResult

# Try importing python-docx if available
try:
    import docx
    from docx import Document
    from docx.shared import Inches, Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.table import WD_TABLE_ALIGNMENT
    HAS_PYTHON_DOCX = True
except ImportError:
    HAS_PYTHON_DOCX = False


def _sanitize_filename(name: str) -> str:
    """Replaces spaces and illegal characters for clean filesystem names."""
    clean = re.sub(r'[^a-zA-Z0-9_\-]', '_', name.strip().lower())
    return clean.strip('_') or "artifact"


def _build_docx_with_python_docx(data: Dict[str, Any], output_path: str):
    """Builds document using python-docx library."""
    doc = Document()

    # Title
    title_text = data.get("title", "Approval Note — Technical Review")
    title_p = doc.add_heading(title_text, level=1)
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Metadata / Header Block
    meta_table = doc.add_table(rows=3, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_table.style = 'Table Grid'

    today_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M UTC")
    meta_data = [
        ("Date & Time:", today_str),
        ("Facility / Unit:", str(data.get("unit", "Refinery Unit-2"))),
        ("Status:", str(data.get("overall_status", "PENDING_APPROVAL")))
    ]
    for idx, (label, val) in enumerate(meta_data):
        row = meta_table.rows[idx]
        row.cells[0].text = label
        row.cells[1].text = val
        row.cells[0].paragraphs[0].runs[0].font.bold = True

    doc.add_paragraph()  # Spacing

    # Executive Summary / Context
    doc.add_heading("1. Executive Summary", level=2)
    summary_text = data.get(
        "summary",
        "This note documents the automated engineering verification of operating parameters "
        "and physical readings against sovereign standards and SOP limits."
    )
    doc.add_paragraph(summary_text)

    # Findings Table
    doc.add_heading("2. Technical Findings & Inspection Parameters", level=2)
    findings = data.get("findings", [])

    if findings:
        table = doc.add_table(rows=1 + len(findings), cols=3)
        table.style = 'Light Shading Accent 1' if 'Light Shading Accent 1' in doc.styles else 'Table Grid'
        
        # Header Row
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = "Parameter / Equipment"
        hdr_cells[1].text = "Observed Reading"
        hdr_cells[2].text = "Compliance Status"
        for cell in hdr_cells:
            for p in cell.paragraphs:
                for run in p.runs:
                    run.font.bold = True

        # Data Rows
        for i, finding in enumerate(findings, start=1):
            row_cells = table.rows[i].cells
            row_cells[0].text = str(finding.get("field", "N/A"))
            row_cells[1].text = str(finding.get("value", "N/A"))
            row_cells[2].text = str(finding.get("status", "OK"))
    else:
        doc.add_paragraph("No specific inspection anomalies reported.")

    # Embedded Image (if provided)
    source_image = data.get("source_image")
    if source_image and os.path.exists(source_image):
        doc.add_heading("3. Evidence & Source Scan", level=2)
        doc.add_paragraph(f"Source file: {os.path.basename(source_image)}")
        try:
            doc.add_picture(source_image, width=Inches(5.0))
        except Exception:
            doc.add_paragraph(f"[Image placeholder: {source_image}]")

    # Sign-off Block
    doc.add_heading("4. Sign-off & Recommendation", level=2)
    doc.add_paragraph("Reviewed and verified by: Sovereign AI Agent Gatekeeper")
    doc.add_paragraph("Final Approval: ___________________________ (Competent Authority)")

    doc.save(output_path)


def _build_docx_native_openxml(data: Dict[str, Any], output_path: str):
    """
    Zero-dependency pure-Python OpenXML generator.
    Creates a 100% valid Microsoft Word .docx ZIP package when python-docx is not installed.
    """
    title = data.get("title", "Approval Note — Technical Review")
    findings = data.get("findings", [])
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")

    # Construct word/document.xml content
    body_xml = [
        f'<w:p><w:pPr><w:jc w:val="center"/></w:pPr><w:r><w:rPr><w:b/><w:sz w:val="36"/></w:rPr><w:t>{title}</w:t></w:r></w:p>',
        f'<w:p><w:r><w:rPr><w:i/></w:rPr><w:t>Generated on {today_str} | Air-Gapped Sovereign Verification</w:t></w:r></w:p>',
        '<w:p><w:r><w:rPr><w:b/><w:sz w:val="28"/></w:rPr><w:t>1. Executive Summary</w:t></w:r></w:p>',
        '<w:p><w:r><w:t>Automated review of physical readings against operating limits.</w:t></w:r></w:p>',
        '<w:p><w:r><w:rPr><w:b/><w:sz w:val="28"/></w:rPr><w:t>2. Inspection Findings Table</w:t></w:r></w:p>',
    ]

    # Build Table in XML
    table_xml = ['<w:tbl><w:tblPr><w:tblBorders><w:top w:val="single"/><w:bottom w:val="single"/><w:insideH w:val="single"/></w:tblBorders></w:tblPr>']
    # Header
    table_xml.append(
        '<w:tr><w:tc><w:p><w:r><w:rPr><w:b/></w:rPr><w:t>Parameter / Equipment</w:t></w:r></w:p></w:tc>'
        '<w:tc><w:p><w:r><w:rPr><w:b/></w:rPr><w:t>Reading</w:t></w:r></w:p></w:tc>'
        '<w:tc><w:p><w:r><w:rPr><w:b/></w:rPr><w:t>Status</w:t></w:r></w:p></w:tc></w:tr>'
    )
    # Rows
    for f in findings:
        field = f.get("field", "N/A")
        val = f.get("value", "N/A")
        status = f.get("status", "OK")
        table_xml.append(
            f'<w:tr><w:tc><w:p><w:r><w:t>{field}</w:t></w:r></w:p></w:tc>'
            f'<w:tc><w:p><w:r><w:t>{val}</w:t></w:r></w:p></w:tc>'
            f'<w:tc><w:p><w:r><w:t>{status}</w:t></w:r></w:p></w:tc></w:tr>'
        )
    table_xml.append('</w:tbl>')
    body_xml.append(''.join(table_xml))

    body_xml.append('<w:p><w:r><w:rPr><w:b/><w:sz w:val="28"/></w:rPr><w:t>3. Recommendation</w:t></w:r></w:p>')
    body_xml.append('<w:p><w:r><w:t>Approved for operational processing.</w:t></w:r></w:p>')

    full_document_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        f'<w:body>{"".join(body_xml)}</w:body></w:document>'
    )

    content_types_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
        '</Types>'
    )

    rels_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
        '</Relationships>'
    )

    # Write ZIP archive with .docx extension
    with zipfile.ZipFile(output_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('[Content_Types].xml', content_types_xml)
        zf.writestr('_rels/.rels', rels_xml)
        zf.writestr('word/document.xml', full_document_xml)


def generate_docx(template_name: str, data: Dict[str, Any], output_dir: str = "outputs") -> ToolResult:
    """
    Generates a formatted Word (.docx) approval note.
    Strictly follows API_CONTRACTS.md Section 3.4.
    """
    if not isinstance(data, dict):
        return ToolResult(success=False, error=f"Expected 'data' to be a dict, got {type(data).__name__}")

    try:
        # Create output directory relative to repo root
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        target_dir = os.path.join(project_root, output_dir)
        os.makedirs(target_dir, exist_ok=True)

        title = data.get("title", "approval_note")
        safe_title = _sanitize_filename(title)
        filename = f"{safe_title}.docx"
        file_path = os.path.join(target_dir, filename)

        # Build document
        if HAS_PYTHON_DOCX:
            _build_docx_with_python_docx(data, file_path)
        else:
            _build_docx_native_openxml(data, file_path)

        # Relative path for contract compliance
        relative_path = os.path.join(output_dir, filename)

        return ToolResult(
            success=True,
            data={
                "file_path": relative_path,
                "filename": filename
            },
            error=None
        )

    except Exception as e:
        # Contract Rule #0: Catch internally, never raise across boundary
        return ToolResult(
            success=False,
            error=f"DOCX generation failed: {str(e)}"
        )
