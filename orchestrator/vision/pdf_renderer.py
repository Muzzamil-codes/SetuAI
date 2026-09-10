"""
PDF page rendering utility for the vision pipeline.

Converts PDF pages to PNG images using PyMuPDF (fitz), which is already
a project dependency (used in grounding/vector_store/ingest.py and
backend/gateway/routes/knowledge.py).
"""
import os
import tempfile
from typing import List


def is_pdf(path: str) -> bool:
    """Check if a file path points to a PDF."""
    return path.lower().endswith(".pdf")


def render_pdf_pages(pdf_path: str, dpi: int = 150, max_pages: int = 10) -> List[str]:
    """Render PDF pages to temporary PNG files.

    Args:
        pdf_path: Absolute or relative path to the PDF file.
        dpi: Resolution for rasterization. 150 DPI provides crisp text legibility while keeping token count efficient.
        max_pages: Cap to avoid sending too many images to the VLM.

    Returns:
        List of paths to the rendered PNG files.

    Raises:
        ImportError: If PyMuPDF is not installed.
        FileNotFoundError: If the PDF does not exist.
        ValueError: If the PDF has zero pages.
    """
    try:
        import pymupdf as fitz
    except ImportError:
        import fitz

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    doc = fitz.open(pdf_path)
    if doc.page_count == 0:
        doc.close()
        raise ValueError(f"PDF has zero pages: {pdf_path}")

    page_count = min(doc.page_count, max_pages)
    rendered_paths: List[str] = []

    # Create a temp directory that persists for the duration of the request
    tmp_dir = tempfile.mkdtemp(prefix="setu_pdf_")
    zoom = dpi / 72.0
    matrix = fitz.Matrix(zoom, zoom)

    for i in range(page_count):
        page = doc[i]
        pix = page.get_pixmap(matrix=matrix)
        out_path = os.path.join(tmp_dir, f"page_{i + 1}.png")
        pix.save(out_path)
        rendered_paths.append(out_path)

    doc.close()
    return rendered_paths
