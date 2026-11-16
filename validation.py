"""
Checks the extracted values before they reach Excel.

These are deliberately conservative: they catch the mistakes that hurt a
register (bad GSTIN, impossible totals, duplicate invoice numbers) without
pretending to be a tax engine.

Every issue is a dict:
    {"row": 0-based row index, "key": field key or "", "message": str,
     "level": "error" | "warning" | "info"}
"""

from __future__ import annotations

import re
from datetime import datetime
from io import BytesIO

from openpyxl import load_workbook

ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
GSTIN_RE = re.compile(r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][0-9A-Z]Z[0-9A-Z]$")
HSN_RE = re.compile(r"^[0-9]{4}(?:[0-9]{2}){0,2}$|^[0-9]{4}(?:\.[0-9]{2}){1,2}$")

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
GSTIN_KEYS = {
    "gstin",
    "seller_gstin",
    "buyer_gstin",
    "supplier_gstin",
    "recipient_gstin",
}
NUMBER_KEYS = {
    "invoice_no",
    "po_no",
    "challan_no",
    "be_no",
    "shipping_bill_no",
    "ewb_no",
    "packing_list_no",
}
DATE_FORMATS = (
    "%Y-%m-%d",
    "%d-%m-%Y",
    "%d/%m/%Y",
    "%d.%m.%Y",
    "%Y/%m/%d",
    "%d %b %Y",
    "%d %B %Y",
    "%b %d, %Y",
    "%B %d, %Y",
    "%d-%b-%Y",
    "%d-%b-%y",
)


# --------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------

def gstin_checksum(gstin: str) -> str | None:
    """Return the expected 15th character, or None if the input is unusable."""
    gstin = (gstin or "").strip().upper()
    if len(gstin) < 14:
        return None
    total = 0
    for index, char in enumerate(gstin[:14]):
        value = ALPHABET.find(char)
        if value < 0:
            return None
        product = value * (2 if index % 2 else 1)
        total += product // 36 + product % 36
    return ALPHABET[(36 - total % 36) % 36]


def is_valid_gstin(value: str) -> bool:
    value = (value or "").strip().upper()
    if not GSTIN_RE.match(value):
        return False
    return gstin_checksum(value) == value[-1]


def is_valid_hsn(value: str) -> bool:
    return bool(HSN_RE.match((value or "").strip()))


def to_number(value) -> float | None:
    """Read '1,234.50', '₹ 1234', '(500)' and similar into a float."""
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    negative = text.startswith("(") and text.endswith(")")
    text = text.strip("()")
    text = re.sub(r"[^0-9.\-]", "", text)
    if text in {"", "-", ".", "-."}:
        return None
    try:
        number = float(text)
    except ValueError:
        return None
    return -number if negative else number


def parse_date(value: str) -> datetime | None:
    text = (value or "").strip()
    if not text:
        return None
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def _money(value) -> str:
    number = to_number(value)
    if number is None:
        return str(value)
    return f"{number:,.2f}"


# --------------------------------------------------------------------------
# Master-register duplicates
# --------------------------------------------------------------------------

def _invoice_column(headers: list) -> int | None:
    for index, header in enumerate(headers):
        text = str(header or "").strip().lower()
        if "invoice" in text and ("no" in text or "number" in text):
            return index
    return None


def master_invoice_numbers(master_bytes: bytes | None) -> set[str]:
    """Invoice numbers already present in an uploaded master register."""
    if not master_bytes:
        return set()
    try:
        workbook = load_workbook(BytesIO(master_bytes), read_only=True, data_only=True)
    except Exception:  # noqa: BLE001 - a broken master is reported elsewhere
        return set()

    numbers: set[str] = set()
    try:
        sheet = workbook.active
        rows = sheet.iter_rows(values_only=True)
        headers = list(next(rows, []))
        column = _invoice_column(headers)
        if column is None:
            return set()
        for row in rows:
            if column < len(row):
                value = str(row[column] or "").strip()
                if value:
                    numbers.add(value.lower())
    finally:
        workbook.close()
    return numbers


# --------------------------------------------------------------------------
# Row checks
# --------------------------------------------------------------------------

def _check_gstin(row_index: int, key: str, value: str) -> list[dict]:
    if not str(value or "").strip():
        return []
    if is_valid_gstin(value):
        return []
    return [
        {
            "row": row_index,
            "key": key,
            "level": "error",
            "message": f"'{value}' is not a valid GSTIN (checksum/format failed).",
        }
    ]


def _check_hsn(row_index: int, value: str) -> list[dict]:
    text = str(value or "").strip()
    if not text or is_valid_hsn(text):
        return []
    return [
        {
            "row": row_index,
            "key": "hsn_code",
            "level": "warning",
            "message": f"HSN '{text}' is not 4, 6 or 8 digits.",
        }
    ]


def _check_totals(row_index: int, row: dict) -> list[dict]:
    taxable = to_number(row.get("taxable_value"))
    total = to_number(row.get("total_value"))
    taxes = [to_number(row.get(key)) for key in ("igst_amount", "cgst_amount", "sgst_amount")]
    taxes = [value for value in taxes if value is not None]

    if taxable is None or total is None or not taxes:
        return []

    expected = taxable + sum(taxes)
    # Registered invoices may round the grand total to the nearest rupee.
    if abs(expected - total) <= 1.0:
        return []

    return [
        {
            "row": row_index,
            "key": "total_value",
            "level": "warning",
            "message": (
                f"Totals do not add up: taxable {_money(taxable)} + taxes "
                f"{_money(sum(taxes))} = {_money(expected)}, but total is "
                f"{_money(total)}."
            ),
        }
    ]


def _check_date(row_index: int, key: str, value: str) -> list[dict]:
    text = str(value or "").strip()
    if not text or parse_date(text):
        return []
    return [
        {
            "row": row_index,
            "key": key,
            "level": "info",
            "message": f"Date '{text}' was not recognised — kept exactly as extracted.",
        }
    ]


def validate_rows(
    rows: list[dict],
    master_bytes: bytes | None = None,
) -> list[dict]:
    """Check every row and return a flat list of issues."""
    issues: list[dict] = []
    known_invoices = master_invoice_numbers(master_bytes)

    seen_invoices: dict[str, int] = {}
    seen_sources: dict[str, str] = {}

    for index, row in enumerate(rows):
        for key, value in row.items():
            if key in GSTIN_KEYS:
                issues.extend(_check_gstin(index, key, value))
            elif key == "hsn_code":
                issues.extend(_check_hsn(index, value))
            elif key.endswith("_date") or key in {"valid_until"}:
                issues.extend(_check_date(index, key, value))

        issues.extend(_check_totals(index, row))

        for key in NUMBER_KEYS & row.keys():
            if not str(row.get(key) or "").strip():
                issues.append(
                    {
                        "row": index,
                        "key": key,
                        "level": "warning",
                        "message": "Document number is empty.",
                    }
                )
                break

        invoice = str(row.get("invoice_no") or "").strip().lower()
        if invoice:
            if invoice in known_invoices:
                issues.append(
                    {
                        "row": index,
                        "key": "invoice_no",
                        "level": "warning",
                        "message": "Invoice already exists in the master register.",
                    }
                )
            source = str(row.get("source_file") or "")
            if invoice in seen_invoices and seen_sources.get(invoice) != source:
                issues.append(
                    {
                        "row": index,
                        "key": "invoice_no",
                        "level": "info",
                        "message": (
                            "Same invoice number appears in more than one source "
                            "document — check for a duplicate upload."
                        ),
                    }
                )
            seen_invoices.setdefault(invoice, index)
            seen_sources.setdefault(invoice, source)

    return issues


def issues_per_row(issues: list[dict]) -> dict[int, list[dict]]:
    grouped: dict[int, list[dict]] = {}
    for issue in issues:
        grouped.setdefault(issue["row"], []).append(issue)
    return grouped


def summarise(issues: list[dict]) -> str:
    errors = sum(1 for issue in issues if issue["level"] == "error")
    warnings = sum(1 for issue in issues if issue["level"] == "warning")
    infos = sum(1 for issue in issues if issue["level"] == "info")
    parts = []
    if errors:
        parts.append(f"{errors} error(s)")
    if warnings:
        parts.append(f"{warnings} warning(s)")
    if infos:
        parts.append(f"{infos} note(s)")
    return ", ".join(parts) or "no issues found"
