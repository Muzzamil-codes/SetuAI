"""Artifact Factory — document and spreadsheet generation."""
from artifact_factory.docx_builder import generate_docx
from artifact_factory.xlsx_builder import generate_xlsx

__all__ = ["generate_docx", "generate_xlsx"]
