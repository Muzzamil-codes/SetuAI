"""
XLSX Tool wrapper for the LangGraph tool registry.
Wraps artifact_factory/xlsx_builder.py.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from verification.schemas import ToolResult

DESCRIPTION = (
    "Generates a styled Excel workbook (.xlsx) with tables, headers, and dashboard summaries. "
    "Use this tool when the user requests an Excel sheet, spreadsheet, data table, or numerical inspection export."
)

SCHEMA = {
    "name": "xlsx",
    "description": DESCRIPTION,
    "parameters": {
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "Spreadsheet title or dashboard name"},
            "company_or_org": {"type": "string", "description": "Company or facility name"},
            "department": {"type": "string", "description": "Issuing department"},
            "tables": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Sheet/table name"},
                        "headers": {"type": "array", "items": {"type": "string"}, "description": "Column header titles"},
                        "rows": {"type": "array", "items": {"type": "array"}, "description": "Row data matching headers"}
                    }
                },
                "description": "Custom sheets and structured data tables"
            },
            "findings": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "field": {"type": "string"},
                        "value": {"type": "string"},
                        "status": {"type": "string", "enum": ["Approved", "Review", "Rejected", "Normal"]}
                    }
                },
                "description": "Optional status findings list"
            }
        },
        "required": ["title"]
    }
}


def run(input: dict) -> ToolResult:
    """Universal tool signature: run(input: dict) -> ToolResult."""
    if not isinstance(input, dict):
        return ToolResult(success=False, error=f"Invalid input type: expected dict, got {type(input).__name__}")
    
    data = input.get("data", input)
    
    try:
        from artifact_factory.xlsx_builder import generate_xlsx
        result = generate_xlsx(data=data, output_dir="outputs")
        if result.get("success"):
            return ToolResult(
                success=True,
                data={
                    "filename": result["filename"],
                    "path": result["path"],
                    "file_path": result["path"],
                    "artifact": {
                        "type": "xlsx",
                        "filename": result["filename"],
                        "path": result["path"]
                    }
                }
            )
        else:
            return ToolResult(success=False, error=result.get("error", "XLSX generation failed"))
    except Exception as e:
        return ToolResult(success=False, error=f"XLSX tool error: {str(e)}")
