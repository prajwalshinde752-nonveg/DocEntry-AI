"""
Reads any supported document into one of two things:

  * text   — digital PDFs, Word files, plain text
  * images — photos/scans (JPG, PNG) and scanned PDFs

The extractor then sends whichever one it got to the AI model.

Supported: pdf, png, jpg/jpeg, webp, bmp, tiff, docx, txt, csv
"""

import csv
import io
from dataclasses import dataclass, field
from pathlib import Path

import docx
import pymupdf
from PIL import Image, ImageOps

SUPPORTED_TYPES = [
    "pdf",
    "png",
    "jpg",
    "jpeg",
    "webp",
    "bmp",
    "tif",
    "tiff",
    "docx",
    "txt",
    "csv",
]

IMAGE_TYPES = {"png", "jpg", "jpeg", "webp", "bmp", "tif", "tiff"}

MAX_IMAGE_PAGES = 5     # only the first N pages of a scanned PDF
MAX_WIDTH = 1600        # downscale big phone photos before sending
JPEG_QUALITY = 85
MAX_CSV_ROWS = 200      # keep a spreadsheet-sized export within one request


@dataclass
class Document:
    kind: str
    text: str = ""
    images: list[bytes] = field(default_factory=list)
    note: str = ""

    @property
    def is_empty(self) -> bool:
        return not self.text.strip() and not self.images

    @property
    def has_images(self) -> bool:
        return bool(self.images)


def _extension(filename: str) -> str:
    return Path(filename).suffix.lower().lstrip(".")


def _to_jpeg(img: Image.Image) -> bytes:
    img = ImageOps.exif_transpose(img)
    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")
    if img.width > MAX_WIDTH:
        height = round(img.height * MAX_WIDTH / img.width)
        img = img.resize((MAX_WIDTH, height), Image.LANCZOS)
    out = io.BytesIO()
    img.save(out, format="JPEG", quality=JPEG_QUALITY, optimize=True)
    return out.getvalue()


def _read_pdf(data: bytes) -> Document:
    with pymupdf.open(stream=data, filetype="pdf") as pdf:
        pages = list(pdf)
        text = "\n".join(page.get_text() for page in pages).strip()

        # Enough text -> it is a digital PDF, no need for vision.
        if len(text) >= 40:
            return Document(kind="pdf", text=text)

        # Otherwise it is a scan: render pages as images.
        images = []
        for page in pages[:MAX_IMAGE_PAGES]:
            pix = page.get_pixmap(dpi=150, alpha=False)
            img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
            images.append(_to_jpeg(img))

        note = ""
        if len(pages) > MAX_IMAGE_PAGES:
            note = f"Only the first {MAX_IMAGE_PAGES} pages were read."

        return Document(kind="pdf-scan", text=text, images=images, note=note)


def _read_image(data: bytes) -> Document:
    img = Image.open(io.BytesIO(data))
    return Document(kind="image", images=[_to_jpeg(img)])


def _read_docx(data: bytes) -> Document:
    document = docx.Document(io.BytesIO(data))
    parts = [p.text for p in document.paragraphs]
    for table in document.tables:
        for row in table.rows:
            parts.append(" | ".join(cell.text.strip() for cell in row.cells))
    return Document(kind="docx", text="\n".join(p for p in parts if p.strip()))


def _read_csv(data: bytes) -> Document:
    """Turn a spreadsheet export into lines the model can read as a table."""
    text = data.decode("utf-8-sig", errors="replace")

    # Commas are normal, but exports from Excel on some machines use ; or tabs.
    try:
        dialect = csv.Sniffer().sniff(text[:4096], delimiters=",;\t|")
    except csv.Error:
        dialect = csv.excel

    rows = [row for row in csv.reader(io.StringIO(text), dialect) if any(row)]
    lines = [" | ".join(cell.strip() for cell in row) for row in rows[:MAX_CSV_ROWS]]

    note = ""
    if len(rows) > MAX_CSV_ROWS:
        note = f"Only the first {MAX_CSV_ROWS} rows were read."

    return Document(kind="csv", text="\n".join(lines), note=note)



def read_document(data: bytes, filename: str) -> Document:
    ext = _extension(filename)

    if ext not in SUPPORTED_TYPES:
        raise ValueError(
            f"Unsupported file type '.{ext}'. "
            f"Try one of: {', '.join(SUPPORTED_TYPES)}"
        )

    if ext == "pdf":
        return _read_pdf(data)
    if ext in IMAGE_TYPES:
        return _read_image(data)
    if ext == "docx":
        return _read_docx(data)
    if ext == "csv":
        return _read_csv(data)
    return Document(kind="txt", text=data.decode("utf-8", errors="replace"))
