"""
Excel Spreadsheet (.xlsx) Generator for Setu Artifact Factory.
Generates comparative statements with real dynamic formulas (SUM, variance).
Follows API_CONTRACTS.md Section 3.5.
Owned by Parvez.
"""
import os
import re
import zipfile
from typing import Dict, Any, List
from verification.schemas import ToolResult
from html import escape as xml_escape

# Try importing openpyxl if available
try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False


def _sanitize_filename(name: str) -> str:
    clean = re.sub(r'[^a-zA-Z0-9_\-]', '_', name.strip().lower())
    return clean.strip('_') or "artifact"


def _build_xlsx_with_openpyxl(data: Dict[str, Any], output_path: str):
    """Builds comparative spreadsheet using openpyxl with real dynamic formulas."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Comparative Statement"

    # Title styling
    title_font = Font(name="Calibri", size=14, bold=True, color="1F4E79")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
    total_font = Font(name="Calibri", size=11, bold=True)
    border_side = Side(style="thin", color="D9D9D9")
    thin_border = Border(left=border_side, right=border_side, top=border_side, bottom=border_side)
    double_bottom_border = Border(top=border_side, bottom=Side(style="double", color="000000"))

    # Title block
    title_text = data.get("title", "Comparative Statement — Technical & Financial Evaluation")
    ws.merge_cells("A1:E1")
    ws["A1"] = title_text
    ws["A1"].font = title_font
    ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 30

    # Headers
    vendors = data.get("vendors", ["Vendor A", "Vendor B"])
    headers = ["Item Description"]
    for v in vendors:
        headers.append(f"{v} (INR)")
    headers.extend(["Variance (Diff)", "Lowest Bidder"])

    ws.row_dimensions[3].height = 24
    for col_idx, header in enumerate(headers, start=1):
        cell = ws.cell(row=3, column=col_idx, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")

    # Data rows with real formulas
    rows_data = data.get("rows", [])
    start_row = 4
    current_row = start_row

    for item in rows_data:
        ws.row_dimensions[current_row].height = 20
        if isinstance(item, (list, tuple)):
            for col_idx, val in enumerate(item, start=1):
                cell = ws.cell(row=current_row, column=col_idx, value=str(val))
                cell.border = thin_border
            current_row += 1
            continue

        # Col A: Item
        ws.cell(row=current_row, column=1, value=str(item.get("item", f"Item {current_row - 3}"))).border = thin_border

        # Vendor columns
        col_letters = []
        for v_idx, v in enumerate(vendors, start=2):
            col_letter = get_column_letter(v_idx)
            col_letters.append(col_letter)
            # Fetch price key, e.g. price_a, price_b or prices list
            price = item.get(f"price_{chr(95 + v_idx)}") or item.get("prices", {}).get(v) or 0
            cell = ws.cell(row=current_row, column=v_idx, value=float(price))
            cell.number_format = '#,##0.00'
            cell.border = thin_border

        # Variance column (Real Excel Formula: =B4 - C4)
        variance_col = len(vendors) + 2
        var_cell = ws.cell(row=current_row, column=variance_col)
        if len(col_letters) >= 2:
            var_cell.value = f"={col_letters[0]}{current_row}-{col_letters[1]}{current_row}"
        else:
            var_cell.value = 0
        var_cell.number_format = '#,##0.00'
        var_cell.border = thin_border

        # Lowest Bidder column (Real Excel Formula: MIN check or label)
        status_col = variance_col + 1
        stat_cell = ws.cell(row=current_row, column=status_col)
        if len(col_letters) >= 2:
            stat_cell.value = f'=IF({col_letters[0]}{current_row}<={col_letters[1]}{current_row}, "{vendors[0]}", "{vendors[1]}")'
        else:
            stat_cell.value = "N/A"
        stat_cell.alignment = Alignment(horizontal="center")
        stat_cell.border = thin_border

        current_row += 1

    # Total row with REAL SUM FORMULA
    total_row = current_row
    ws.row_dimensions[total_row].height = 22
    ws.cell(row=total_row, column=1, value="TOTAL (INR)").font = total_font
    ws.cell(row=total_row, column=1).border = double_bottom_border

    if rows_data:
        end_data_row = total_row - 1
        for v_idx in range(2, len(vendors) + 3):
            col_letter = get_column_letter(v_idx)
            cell = ws.cell(row=total_row, column=v_idx)
            # Enforce REAL formula
            cell.value = f"=SUM({col_letter}{start_row}:{col_letter}{end_data_row})"
            cell.font = total_font
            cell.number_format = '#,##0.00'
            cell.border = double_bottom_border

    # Auto-fit column widths
    for col in ws.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = max(max_len + 4, 16)

    wb.save(output_path)


def _build_xlsx_native_openxml(data: Dict[str, Any], output_path: str):
    """
    Zero-dependency pure-Python OpenXML spreadsheet generator.
    Produces a valid Microsoft Excel .xlsx ZIP package with real formula tags (<f>=SUM(...)</f>).
    """
    title = data.get("title", "Comparative Statement")
    vendors = data.get("vendors", ["Vendor A", "Vendor B"])
    rows_data = data.get("rows", [])

    sheet_xml_rows = []
    # Row 1: Title
    sheet_xml_rows.append(f'<row r="1"><c r="A1" t="inlineStr"><is><t>{title}</t></is></c></row>')

    # Row 3: Headers
    headers = ["Item Description"] + [f"{v} (INR)" for v in vendors] + ["Variance (Diff)"]
    header_cells = []
    for idx, h in enumerate(headers):
        col_char = chr(65 + idx)
        header_cells.append(f'<c r="{col_char}3" t="inlineStr"><is><t>{xml_escape(h)}</t></is></c>')
    sheet_xml_rows.append(f'<row r="3">{"".join(header_cells)}</row>')

    # Data Rows
    start_row = 4
    current_row = start_row
    for r in rows_data:
        if isinstance(r, (list, tuple)):
            row_cells = []
            for col_idx, val in enumerate(r):
                col_char = chr(65 + col_idx)
                row_cells.append(f'<c r="{col_char}{current_row}" t="inlineStr"><is><t>{xml_escape(str(val))}</t></is></c>')
            sheet_xml_rows.append(f'<row r="{current_row}">{"".join(row_cells)}</row>')
            current_row += 1
            continue

        item = xml_escape(str(r.get("item", f"Item {current_row-3}")))
        price_a = float(r.get("price_a", 0))
        price_b = float(r.get("price_b", 0))

        row_cells = [
            f'<c r="A{current_row}" t="inlineStr"><is><t>{item}</t></is></c>',
            f'<c r="B{current_row}"><v>{price_a}</v></c>',
            f'<c r="C{current_row}"><v>{price_b}</v></c>',
            # Real Excel Formula for variance
            f'<c r="D{current_row}"><f>B{current_row}-C{current_row}</f><v>{price_a - price_b}</v></c>'
        ]
        sheet_xml_rows.append(f'<row r="{current_row}">{"".join(row_cells)}</row>')
        current_row += 1

    # Total Row with real =SUM formula
    total_row = current_row
    end_data_row = total_row - 1
    total_cells = [
        f'<c r="A{total_row}" t="inlineStr"><is><t>TOTAL (INR)</t></is></c>',
        f'<c r="B{total_row}"><f>SUM(B{start_row}:B{end_data_row})</f></c>',
        f'<c r="C{total_row}"><f>SUM(C{start_row}:C{end_data_row})</f></c>',
        f'<c r="D{total_row}"><f>SUM(D{start_row}:D{end_data_row})</f></c>'
    ]
    sheet_xml_rows.append(f'<row r="{total_row}">{"".join(total_cells)}</row>')

    sheet_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f'<sheetData>{"".join(sheet_xml_rows)}</sheetData>'
        '</worksheet>'
    )

    workbook_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<sheets><sheet name="Comparative Statement" sheetId="1" r:id="rId1"/></sheets>'
        '</workbook>'
    )

    content_types_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        '</Types>'
    )

    rels_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
        '</Relationships>'
    )

    wb_rels_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
        '</Relationships>'
    )

    with zipfile.ZipFile(output_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('[Content_Types].xml', content_types_xml)
        zf.writestr('_rels/.rels', rels_xml)
        zf.writestr('xl/workbook.xml', workbook_xml)
        zf.writestr('xl/_rels/workbook.xml.rels', wb_rels_xml)
        zf.writestr('xl/worksheets/sheet1.xml', sheet_xml)


def generate_xlsx(template_name: str, data: Dict[str, Any], output_dir: str = "outputs") -> ToolResult:
    """
    Generates a formatted Excel (.xlsx) comparative statement with real formulas.
    Strictly follows API_CONTRACTS.md Section 3.5.
    """
    if not isinstance(data, dict):
        return ToolResult(success=False, error=f"Expected 'data' to be a dict, got {type(data).__name__}")

    try:
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        target_dir = os.path.join(project_root, output_dir)
        os.makedirs(target_dir, exist_ok=True)

        title = data.get("title", "comparative_statement")
        safe_title = _sanitize_filename(title)
        filename = f"{safe_title}.xlsx"
        file_path = os.path.join(target_dir, filename)

        if HAS_OPENPYXL:
            _build_xlsx_with_openpyxl(data, file_path)
        else:
            _build_xlsx_native_openxml(data, file_path)

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
        return ToolResult(
            success=False,
            error=f"XLSX generation failed: {str(e)}"
        )
