"""
Builds the Excel register.

You can either start a fresh workbook, or upload an existing master sheet and
the new rows are appended to it. Columns are matched by their heading, so an
old register keeps working even if you change the field order.
"""

from datetime import datetime
from io import BytesIO

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter


HEADER_FILL = PatternFill("solid", fgColor="1F4E78")
HEADER_FONT = Font(color="FFFFFF", bold=True)


def _write_headers(ws, headers: list[str]) -> None:
    ws.append(headers)
    for cell in ws[1]:
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.freeze_panes = "A2"


def _read_headers(ws) -> list[str]:
    if ws.max_row == 0:
        return []
    return [c.value for c in ws[1] if c.value is not None]


def _autosize(ws) -> None:
    for col in range(1, ws.max_column + 1):
        longest = 0
        for cell in ws[get_column_letter(col)]:
            longest = max(longest, len(str(cell.value or "")))
        ws.column_dimensions[get_column_letter(col)].width = min(longest + 3, 45)


def build_excel(
    rows: list[dict],
    columns: list[tuple[str, str]],
    master_bytes: bytes | None = None,
    sheet_name: str = "Register",
) -> bytes:
    """Return an .xlsx file as bytes.

    rows      : list of dicts, keyed by the field keys in `columns`
    columns   : list of (key, label)
    master    : optional existing .xlsx to append to
    """
    key_for_label = {label: key for key, label in columns}

    if master_bytes:
        wb = load_workbook(BytesIO(master_bytes))
        ws = wb.active
        headers = _read_headers(ws)
    else:
        wb = Workbook()
        ws = wb.active
        ws.title = sheet_name
        headers = [label for _, label in columns]
        _write_headers(ws, headers)

    for row in rows:
        values = []
        for label in headers:
            key = key_for_label.get(label)
            values.append(row.get(key, "") if key else "")
        ws.append(values)

    _autosize(ws)

    out = BytesIO()
    wb.save(out)
    return out.getvalue()


def default_filename() -> str:
    return f"DocEntry_Register_{datetime.now():%Y%m%d_%H%M}.xlsx"
