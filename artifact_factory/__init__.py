"""
Artifact Factory Module for Setu.
Generates production-grade Word (docx) and Excel (xlsx) deliverables.
Owned by Parvez.
"""
from .docx_builder import generate_docx
from .xlsx_builder import generate_xlsx

__all__ = ["generate_docx", "generate_xlsx"]
