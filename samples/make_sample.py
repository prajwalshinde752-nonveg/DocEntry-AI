"""
Creates a fake but realistic tax invoice PDF so you can test the app.

Run:  .venv/bin/python samples/make_sample.py
"""

import zlib
from pathlib import Path

LINES = [
    "TAX INVOICE",
    "",
    "Sunrise Textiles Pvt Ltd",
    "Plot 12, MIDC, Pune 411019, Maharashtra, India",
    "GSTIN: 27ABCDE1234F1Z5",
    "",
    "Invoice No.: INV/2026/0042          Invoice Date: 15-10-2026",
    "Buyer: Global Traders LLC",
    "Buyer GSTIN: 27XYZAB5678G1Z2",
    "Place of Supply: Maharashtra (27)",
    "",
    "HSN Code: 5208",
    "Description of Goods: Cotton Woven Fabric, 120 GSM",
    "Quantity: 1500        Unit: MTR        Rate: 210.00",
    "",
    "Taxable Value: 315000.00",
    "IGST Amount: 0.00",
    "CGST Amount: 28350.00",
    "SGST Amount: 28350.00",
    "Total Invoice Value: 371700.00",
    "Currency: INR",
]


def _escape(text: str) -> str:
    return text.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")


def make_pdf(path: Path) -> None:
    content = ["BT", "/F1 11 Tf", "50 800 Td", "16 TL"]
    for line in LINES:
        content.append(f"({_escape(line)}) Tj")
        content.append("T*")
    content.append("ET")
    stream = "\n".join(content).encode("latin-1")

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
    ]

    out = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for i, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{i} 0 obj\n".encode() + body + b"\nendobj\n"

    xref_pos = len(out)
    out += f"xref\n0 {len(objects) + 1}\n".encode()
    out += b"0000000000 65535 f \n"
    for off in offsets[1:]:
        out += f"{off:010d} 00000 n \n".encode()
    out += (
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_pos}\n%%EOF\n"
    ).encode()

    path.write_bytes(bytes(out))
    print(f"Wrote {path}")


if __name__ == "__main__":
    make_pdf(Path(__file__).parent / "sample_tax_invoice.pdf")
