"""
Builds the Excel register.

You can either start a fresh workbook, or upload an existing master sheet and
the new rows are appended to it. Columns are matched by their heading, so an
old register keeps working even if you change the field order.

A batch with several document types becomes one workbook with one sheet per
type. Cells flagged by validation.py are highlighted, and a "Checks" sheet
lists every issue.
"""

import csv
import json
import re
from datetime import datetime
from io import BytesIO, StringIO

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from validation import to_number

HEADER_FILL = PatternFill("solid", fgColor="1F4E78")
HEADER_FONT = Font(color="FFFFFF", bold=True, size=11)
HEADER_ALIGN = Alignment(horizontal="center", vertical="center", wrap_text=True)
BORDER = Border(bottom=Side(style="thin", color="D9D9D9"))
ERROR_FILL = PatternFill("solid", fgColor="F8D7DA")
WARNING_FILL = PatternFill("solid", fgColor="FFF2CC")
INFO_FILL = PatternFill("solid", fgColor="DDEBF7")

MONEY_FORMAT = '#,##0.00'
QUANTITY_FORMAT = '#,##0.####'

MONEY_KEYS = {
    "rate",
    "amount",
    "value",
    "taxable_value",
    "assessable_value",
    "igst_amount",
    "cgst_amount",
    "sgst_amount",
    "fob_value",
    "total_duty",
    "total_value",
}
QUANTITY_KEYS = {
    "quantity",
    "packages",
    "net_weight",
    "gross_weight",
    "distance_km",
}

# Kept deliberately narrow: names, GSTINs and document numbers stay text.
TEXT_KEYS = {
    "invoice_no",
    "po_no",
    "challan_no",
    "be_no",
    "shipping_bill_no",
    "ewb_no",
    "packing_list_no",
    "hsn_code",
    "iec_code",
    "vehicle_no",
    "transporter_id",
}

COLUMN_WIDTHS = {
    "description": 42,
    "buyer_address": 32,
    "seller_name": 28,
    "buyer_name": 28,
    "exporter_name": 28,
    "supplier_name": 28,
    "importer_name": 28,
    "consignor": 24,
    "consignee": 24,
    "source_file": 30,
    "marks": 24,
    "place_of_supply": 18,
    "port_of_loading": 18,
    "port_of_discharge": 18,
    "country_of_origin": 18,
    "country_of_destination": 20,
}


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def _clean_sheet_name(name: str, used: set[str]) -> str:
    base = re.sub(r"[\[\]:*?/\\]", " ", name or "Register").strip() or "Register"
    base = base[:31]
    candidate, n = base, 2
    while candidate.lower() in used:
        suffix = f" {n}"
        candidate = base[: 31 - len(suffix)] + suffix
        n += 1
    used.add(candidate.lower())
    return candidate


def _style_header(ws, headers: list[str]) -> None:
    ws.row_dimensions[1].height = 30
    for index, _ in enumerate(headers, start=1):
        cell = ws.cell(row=1, column=index)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = HEADER_ALIGN
    ws.freeze_panes = "A2"


def _set_filter(ws, headers: list[str]) -> None:
    """Filter the full used range, not just the header row."""
    last_row = max(ws.max_row, 2)
    ws.auto_filter.ref = f"A1:{get_column_letter(max(len(headers), 1))}{last_row}"


def _autosize(ws, key_for_label: dict[str, str]) -> None:
    for col in range(1, ws.max_column + 1):
        header = str(ws.cell(row=1, column=col).value or "")
        key = key_for_label.get(header, "")
        if key in COLUMN_WIDTHS:
            width = COLUMN_WIDTHS[key]
        elif key in MONEY_KEYS or key in QUANTITY_KEYS:
            width = 15
        elif key.endswith("_date") or key in {"extracted_at", "valid_until"}:
            width = 14
        else:
            longest = 0
            for cell in ws[get_column_letter(col)]:
                longest = max(longest, len(str(cell.value or "")))
            width = min(max(longest + 3, 10), 45)
        ws.column_dimensions[get_column_letter(col)].width = width


def _write_value(ws, row: int, column: int, key: str | None, value) -> None:
    cell = ws.cell(row=row, column=column)
    if key and key not in TEXT_KEYS and (key in MONEY_KEYS or key in QUANTITY_KEYS):
        number = to_number(value)
        if number is not None:
            cell.value = number
            cell.number_format = MONEY_FORMAT if key in MONEY_KEYS else QUANTITY_FORMAT
        else:
            cell.value = value
    else:
        cell.value = value
    cell.border = BORDER
    if key in MONEY_KEYS:
        cell.alignment = Alignment(horizontal="right")
    elif key in QUANTITY_KEYS:
        cell.alignment = Alignment(horizontal="right")
    else:
        cell.alignment = Alignment(vertical="top", wrap_text=key in COLUMN_WIDTHS)


def _highlight(
    ws,
    row_offset: int,
    key_for_label: dict[str, str],
    headers: list[str],
    issues: list[dict],
) -> None:
    """Colour the cells mentioned by validation issues."""
    column_for_key = {
        key_for_label[header]: column
        for column, header in enumerate(headers, start=1)
        if header in key_for_label
    }
    for issue in issues:
        column = column_for_key.get(issue.get("key"))
        if not column:
            continue
        row = row_offset + issue["row"] + 1
        cell = ws.cell(row=row, column=column)
        fill = {
            "error": ERROR_FILL,
            "warning": WARNING_FILL,
            "info": INFO_FILL,
        }.get(issue.get("level", "warning"), WARNING_FILL)
        cell.fill = fill


def _append_rows(ws, rows, columns, start_row: int, issues=None) -> None:
    key_for_label = {label: key for key, label in columns}
    headers = [str(ws.cell(row=1, column=i).value or "") for i in range(1, ws.max_column + 1)]
    for offset, row in enumerate(rows):
        excel_row = start_row + offset
        for column, header in enumerate(headers, start=1):
            key = key_for_label.get(header)
            _write_value(ws, excel_row, column, key, row.get(key, "") if key else "")
    if issues:
        _highlight(ws, start_row - 1, key_for_label, headers, issues)


def _validation_sheet(wb, entries: list[dict]) -> None:
    if not entries:
        return
    ws = wb.create_sheet("Checks")
    headers = ["Sheet", "Row", "Column", "Level", "Message"]
    ws.append(headers)
    _style_header(ws, headers)
    for entry in entries:
        ws.append(
            [
                entry["sheet"],
                entry["row"],
                entry["column"],
                entry["level"],
                entry["message"],
            ]
        )
    for row in ws.iter_rows(min_row=2):
        row[3].fill = {
            "error": ERROR_FILL,
            "warning": WARNING_FILL,
            "info": INFO_FILL,
        }.get(str(row[3].value), WARNING_FILL)
    ws.column_dimensions["A"].width = 20
    ws.column_dimensions["B"].width = 8
    ws.column_dimensions["C"].width = 22
    ws.column_dimensions["D"].width = 10
    ws.column_dimensions["E"].width = 70
    ws.freeze_panes = "A2"


# --------------------------------------------------------------------------
# Public API
# --------------------------------------------------------------------------

def build_workbook(sections: list[dict], master_bytes: bytes | None = None) -> bytes:
    """Return an .xlsx file as bytes.

    sections: list of dicts with keys
        name     — sheet / document type name
        columns  — list of (key, label)
        rows     — list of dicts keyed by the field keys
        issues   — optional list of validation issues for these rows
    master_bytes: append to this workbook instead of creating a new one. Only
        used when there is exactly one section; otherwise it is ignored.
    """
    if not sections:
        raise ValueError("Nothing to export.")

    check_entries: list[dict] = []
    single = len(sections) == 1

    if master_bytes and single:
        wb = load_workbook(BytesIO(master_bytes))
        ws = wb.active
        headers = [
            str(ws.cell(row=1, column=i).value or "")
            for i in range(1, ws.max_column + 1)
        ]
        if not any(headers):
            headers = [label for _, label in sections[0]["columns"]]
            for index, header in enumerate(headers, start=1):
                ws.cell(row=1, column=index, value=header)
        _style_header(ws, headers)
        start_row = ws.max_row + 1
        _append_rows(
            ws,
            sections[0]["rows"],
            sections[0]["columns"],
            start_row,
            sections[0].get("issues"),
        )
        _autosize(ws, {label: key for key, label in sections[0]["columns"]})
        _set_filter(ws, headers)
        _collect_checks(check_entries, sections[0], start_row)
    else:
        wb = Workbook()
        wb.remove(wb.active)
        used: set[str] = set()
        for section in sections:
            ws = wb.create_sheet(_clean_sheet_name(section.get("name", "Register"), used))
            columns = section["columns"]
            headers = [label for _, label in columns]
            for index, header in enumerate(headers, start=1):
                ws.cell(row=1, column=index, value=header)
            _style_header(ws, headers)
            _append_rows(ws, section["rows"], columns, 2, section.get("issues"))
            _autosize(ws, {label: key for key, label in columns})
            _set_filter(ws, headers)
            _collect_checks(check_entries, section, 2)
        _validation_sheet(wb, check_entries)

    wb.properties.title = "DocEntry-AI register"
    wb.properties.creator = "DocEntry-AI"
    out = BytesIO()
    wb.save(out)
    return out.getvalue()


def _collect_checks(entries: list[dict], section: dict, start_row: int) -> None:
    labels = {key: label for key, label in section["columns"]}
    for issue in section.get("issues") or []:
        entries.append(
            {
                "sheet": section.get("name", "Register"),
                "row": start_row + issue["row"],
                "column": labels.get(issue.get("key"), issue.get("key", "")),
                "level": issue.get("level", "warning"),
                "message": issue.get("message", ""),
            }
        )


def build_excel(
    rows: list[dict],
    columns: list[tuple[str, str]],
    master_bytes: bytes | None = None,
    sheet_name: str = "Register",
    issues: list[dict] | None = None,
) -> bytes:
    """Backwards-compatible single-sheet wrapper around build_workbook."""
    return build_workbook(
        [
            {
                "name": sheet_name,
                "columns": columns,
                "rows": rows,
                "issues": issues or [],
            }
        ],
        master_bytes=master_bytes,
    )


def build_csv(sections: list[dict]) -> bytes:
    """One flat CSV, with a Document Type column when there are several."""
    out = StringIO()
    writer = csv.writer(out)
    multi = len(sections) > 1

    for section in sections:
        columns = section["columns"]
        headers = [label for _, label in columns]
        if multi:
            headers = ["Document Type"] + headers
        writer.writerow(headers)
        for row in section["rows"]:
            values = [row.get(key, "") for key, _ in columns]
            if multi:
                values = [section.get("name", "")] + values
            writer.writerow(values)

    return out.getvalue().encode("utf-8-sig")


def build_json(sections: list[dict]) -> bytes:
    payload = [
        {
            "document_type": section.get("name", ""),
            "rows": section["rows"],
        }
        for section in sections
    ]
    if len(payload) == 1:
        payload = payload[0]["rows"]  # keep the simple shape for a single run
    return json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")


def default_filename(prefix: str = "DocEntry_Register") -> str:
    return f"{prefix}_{datetime.now():%Y%m%d_%H%M}.xlsx"
