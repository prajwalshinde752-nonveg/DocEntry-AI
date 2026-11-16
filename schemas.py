"""
Field definitions for each supported document type.

Each entry is:  (key, label)
  key   = internal name used in the code and the Excel file
  label = the column heading a human sees

To add a new document type, just add another entry to DOCUMENT_TYPES.
Users can also create their own document types and columns from the app;
those are stored in the history database and merged in at runtime.
"""

import re

DOCUMENT_TYPES = {
    "Tax Invoice": [
        ("invoice_no", "Invoice No."),
        ("invoice_date", "Invoice Date"),
        ("po_no", "PO No."),
        ("seller_name", "Seller Name"),
        ("seller_gstin", "Seller GSTIN"),
        ("buyer_name", "Buyer Name"),
        ("buyer_gstin", "Buyer GSTIN"),
        ("buyer_address", "Buyer Address"),
        ("place_of_supply", "Place of Supply"),
        ("hsn_code", "HSN Code"),
        ("description", "Description of Goods"),
        ("quantity", "Quantity"),
        ("unit", "Unit"),
        ("rate", "Rate"),
        ("taxable_value", "Taxable Value"),
        ("igst_amount", "IGST Amount"),
        ("cgst_amount", "CGST Amount"),
        ("sgst_amount", "SGST Amount"),
        ("total_value", "Total Invoice Value"),
        ("currency", "Currency"),
    ],
    "Shipping Bill": [
        ("shipping_bill_no", "Shipping Bill No."),
        ("shipping_bill_date", "Shipping Bill Date"),
        ("exporter_name", "Exporter Name"),
        ("iec_code", "IEC Code"),
        ("gstin", "GSTIN"),
        ("invoice_no", "Invoice No."),
        ("invoice_date", "Invoice Date"),
        ("port_of_loading", "Port of Loading"),
        ("port_of_discharge", "Port of Discharge"),
        ("vessel_name", "Vessel Name"),
        ("hsn_code", "HSN Code"),
        ("description", "Description of Goods"),
        ("quantity", "Quantity"),
        ("unit", "Unit"),
        ("fob_value", "FOB Value"),
        ("currency", "Currency"),
        ("scheme", "Scheme / Claim"),
    ],
    "Purchase Order": [
        ("po_no", "PO No."),
        ("po_date", "PO Date"),
        ("buyer_name", "Buyer Name"),
        ("supplier_name", "Supplier Name"),
        ("hsn_code", "HSN Code"),
        ("description", "Description of Goods"),
        ("quantity", "Quantity"),
        ("unit", "Unit"),
        ("rate", "Rate"),
        ("total_value", "Total Value"),
        ("currency", "Currency"),
        ("delivery_terms", "Delivery Terms"),
    ],
    "Bill of Entry": [
        ("be_no", "Bill of Entry No."),
        ("be_date", "Bill of Entry Date"),
        ("importer_name", "Importer Name"),
        ("iec_code", "IEC Code"),
        ("gstin", "GSTIN"),
        ("invoice_no", "Invoice No."),
        ("port_of_loading", "Port of Loading"),
        ("port_of_discharge", "Port of Discharge"),
        ("hsn_code", "HSN Code"),
        ("description", "Description of Goods"),
        ("quantity", "Quantity"),
        ("assessable_value", "Assessable Value"),
        ("total_duty", "Total Duty"),
        ("currency", "Currency"),
    ],
    "Delivery Challan": [
        ("challan_no", "Challan No."),
        ("challan_date", "Challan Date"),
        ("consignor", "Consignor"),
        ("consignee", "Consignee"),
        ("hsn_code", "HSN Code"),
        ("description", "Description of Goods"),
        ("quantity", "Quantity"),
        ("unit", "Unit"),
        ("value", "Value"),
        ("vehicle_no", "Vehicle No."),
    ],
    "E-Way Bill": [
        ("ewb_no", "E-Way Bill No."),
        ("ewb_date", "E-Way Bill Date"),
        ("valid_until", "Valid Until"),
        ("supplier_gstin", "Supplier GSTIN"),
        ("recipient_gstin", "Recipient GSTIN"),
        ("invoice_no", "Invoice No."),
        ("invoice_date", "Invoice Date"),
        ("place_of_supply", "Place of Supply"),
        ("hsn_code", "HSN Code"),
        ("description", "Description of Goods"),
        ("quantity", "Quantity"),
        ("unit", "Unit"),
        ("taxable_value", "Taxable Value"),
        ("total_value", "Total Value"),
        ("vehicle_no", "Vehicle No."),
        ("transporter_id", "Transporter ID"),
        ("distance_km", "Distance (km)"),
        ("currency", "Currency"),
    ],
    "Packing List": [
        ("packing_list_no", "Packing List No."),
        ("packing_list_date", "Packing List Date"),
        ("exporter_name", "Exporter Name"),
        ("invoice_no", "Invoice No."),
        ("buyer_name", "Buyer Name"),
        ("description", "Description of Goods"),
        ("quantity", "Quantity"),
        ("unit", "Unit"),
        ("packages", "No. of Packages"),
        ("net_weight", "Net Weight"),
        ("gross_weight", "Gross Weight"),
        ("marks", "Marks & Numbers"),
        ("port_of_loading", "Port of Loading"),
        ("port_of_discharge", "Port of Discharge"),
    ],
    "Commercial Invoice": [
        ("invoice_no", "Invoice No."),
        ("invoice_date", "Invoice Date"),
        ("exporter_name", "Exporter Name"),
        ("buyer_name", "Buyer Name"),
        ("buyer_address", "Buyer Address"),
        ("country_of_origin", "Country of Origin"),
        ("country_of_destination", "Country of Destination"),
        ("port_of_loading", "Port of Loading"),
        ("port_of_discharge", "Port of Discharge"),
        ("incoterms", "Incoterms"),
        ("hsn_code", "HS Code"),
        ("description", "Description of Goods"),
        ("quantity", "Quantity"),
        ("unit", "Unit"),
        ("rate", "Rate"),
        ("amount", "Amount"),
        ("total_value", "Total Value"),
        ("currency", "Currency"),
    ],
}


# These two columns are added automatically so every exported register is auditable.
AUDIT_COLUMNS = [
    ("source_file", "Source File"),
    ("extracted_at", "Extracted At"),
]


# --------------------------------------------------------------------------
# User-defined columns
# --------------------------------------------------------------------------

def _slug(label: str) -> str:
    """Turn a column heading into a safe internal key."""
    key = re.sub(r"[^a-z0-9]+", "_", label.strip().lower()).strip("_")
    return key or "column"


def parse_custom_columns(text: str) -> list[tuple[str, str]]:
    """Parse lines like ``hsn=HSN Code`` or just ``HSN Code``.

    Blank lines and comments (starting with #) are ignored. Duplicate keys get
    a numeric suffix so they never collide with each other.
    """
    columns: list[tuple[str, str]] = []
    seen: set[str] = set()

    for raw in (text or "").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key_part, label = line.split("=", 1)
            key = _slug(key_part) if key_part.strip() else _slug(label)
            label = label.strip() or key
        else:
            label = line
            key = _slug(label)

        base, n = key, 2
        while key in seen:
            key = f"{base}_{n}"
            n += 1
        seen.add(key)
        columns.append((key, label))

    return columns


def merge_columns(*groups: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """Combine column groups, keeping the first use of each key and label."""
    merged: list[tuple[str, str]] = []
    keys: set[str] = set()
    labels: set[str] = set()

    for group in groups:
        for key, label in group:
            clean_key, clean_label = key, label
            n = 2
            while clean_key in keys:
                clean_key = f"{key}_{n}"
                n += 1
            # A duplicate label would make the Streamlit multiselect ambiguous.
            base_label, n = clean_label, 2
            while clean_label in labels:
                clean_label = f"{base_label} ({n})"
                n += 1
            keys.add(clean_key)
            labels.add(clean_label)
            merged.append((clean_key, clean_label))

    return merged
