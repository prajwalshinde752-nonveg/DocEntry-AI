"""
Field definitions for each supported document type.

Each entry is:  (key, label)
  key   = internal name used in the code and the Excel file
  label = the column heading a human sees

To add a new document type, just add another entry to DOCUMENT_TYPES.
"""

DOCUMENT_TYPES = {
    "Tax Invoice": [
        ("invoice_no", "Invoice No."),
        ("invoice_date", "Invoice Date"),
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
}


# These two columns are added automatically so every exported register is auditable.
AUDIT_COLUMNS = [
    ("source_file", "Source File"),
    ("extracted_at", "Extracted At"),
]
