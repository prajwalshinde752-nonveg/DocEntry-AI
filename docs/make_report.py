"""
Builds the DocEntry-AI project report as a PDF, with no LibreOffice needed.

    python docs/make_report.py

Writes:
    docs/DocEntry-AI_Project_Report.pdf
    docs/architecture.png
"""

from pathlib import Path

from PIL import Image as PILImage, ImageDraw, ImageFont
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    HRFlowable,
    Image,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

OUT = Path(__file__).resolve().parent
PDF = OUT / "Project-Report.pdf"
DIAGRAM = OUT / "architecture.png"

PAGE_W, PAGE_H = A4
M_LEFT, M_RIGHT, M_TOP, M_BOTTOM = 2.2 * cm, 2.0 * cm, 2.3 * cm, 2.1 * cm
CONTENT_W = PAGE_W - M_LEFT - M_RIGHT

NAVY = colors.HexColor("#1F3B57")
ACCENT = colors.HexColor("#1F6F8B")
GREY = colors.HexColor("#5B6B7A")
LIGHT = colors.HexColor("#F1F6F9")
BORDER = colors.HexColor("#C9D6DF")

REPO = "https://github.com/prajwalshinde752-nonveg/DocEntry-AI"


# --------------------------------------------------------------------------
# Diagram
# --------------------------------------------------------------------------

def _font(size, bold=False):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(f"/usr/share/fonts/truetype/dejavu/{name}", size)


def _box(draw, x, y, w, h, title, sub, fill, border, text_color="white"):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=18, fill=fill, outline=border, width=3)
    draw.multiline_text(
        (x + w / 2, y + (h - 14) / 2 - 26),
        title,
        font=_font(24, True),
        fill=text_color,
        anchor="mm",
        align="center",
    )
    draw.multiline_text(
        (x + w / 2, y + h - 46),
        sub,
        font=_font(20),
        fill=text_color,
        anchor="mm",
        align="center",
        spacing=6,
    )


def _arrow(draw, points, color="#1F6F8B", width=4):
    draw.line(points, fill=color, width=width, joint="curve")
    (x1, y1), (x2, y2) = points[-2], points[-1]
    dx, dy = x2 - x1, y2 - y1
    length = max((dx * dx + dy * dy) ** 0.5, 1)
    ux, uy = dx / length, dy / length
    px, py = -uy, ux
    tip = (x2, y2)
    left = (x2 - ux * 22 + px * 11, y2 - uy * 22 + py * 11)
    right = (x2 - ux * 22 - px * 11, y2 - uy * 22 - py * 11)
    draw.polygon([tip, left, right], fill=color)


def _label(draw, x, y, text, color="#1F6F8B"):
    draw.text((x, y), text, font=_font(18, True), fill=color, anchor="mm")


def build_diagram() -> Path:
    W, H = 1400, 820
    img = PILImage.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)

    d.text((50, 24), "DocEntry-AI  ·  system architecture", font=_font(28, True), fill="#1F3B57")

    bw, bh = 300, 190
    xs = [50, 383, 716, 1049]
    row1, row2 = 100, 520

    def box(col, y, title, sub, fill, border, text_color="white"):
        _box(d, xs[col], y, bw, bh, title, sub, fill, border, text_color)

    box(0, row1, "1 · Input", "PDF · image · DOCX\nTXT · pasted text", "#EAF3F8", "#1F6F8B", "#123")
    box(1, row1, "2 · documents.py", "file  →  text\nor page images", "#1F6F8B", "#1F6F8B")
    box(2, row1, "3 · extractor.py", "prompt · model call\nJSON parsing", "#1F6F8B", "#1F6F8B")
    box(3, row1, "4 · Gemini API", "gemini-3.1-flash-lite\nfree tier", "#B45309", "#B45309")

    box(0, row2, "schemas.py", "field definitions\nper document type", "#EAF3F8", "#1F6F8B", "#123")
    box(1, row2, "5 · app.py", "UI · editable\nreview grid", "#1F6F8B", "#1F6F8B")
    box(2, row2, "6 · excel_writer.py", "openpyxl\ncreate / append", "#1F6F8B", "#1F6F8B")
    box(3, row2, "7 · Excel .xlsx", "one row per item\n+ audit columns", "#2E7D32", "#2E7D32")

    mid1 = row1 + bh // 2
    mid2 = row2 + bh // 2

    for i in range(3):
        _arrow(d, [(xs[i] + bw, mid1), (xs[i + 1] - 5, mid1)])
        _arrow(d, [(xs[i] + bw, mid2), (xs[i + 1] - 5, mid2)])

    # Gemini -> app.py
    _arrow(d, [(xs[3] + bw // 2, row1 + bh), (xs[3] + bw // 2, 430),
               (xs[1] + bw // 2, 430), (xs[1] + bw // 2, row2 - 6)])
    _label(d, 1040, 410, "JSON reply")

    # schemas.py -> extractor.py
    _arrow(d, [(xs[0] + bw // 2, row2 - 6), (xs[0] + bw // 2, 330),
               (xs[2] + bw // 2, 330), (xs[2] + bw // 2, row1 + bh + 6)], color="#8C9AA8")
    _label(d, 560, 312, "field keys used in the prompt", "#5B6B7A")

    img.save(DIAGRAM)
    return DIAGRAM


# --------------------------------------------------------------------------
# Styles
# --------------------------------------------------------------------------

def esc(text: str) -> str:
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


STYLES = {
    "body": ParagraphStyle(
        "body", fontName="Helvetica", fontSize=10, leading=14.8,
        alignment=TA_JUSTIFY, spaceAfter=8,
    ),
    "bullet": ParagraphStyle(
        "bullet", fontName="Helvetica", fontSize=10, leading=14.4,
        alignment=TA_LEFT, leftIndent=15, bulletIndent=4, spaceAfter=4,
    ),
    "h1": ParagraphStyle(
        "h1", fontName="Helvetica-Bold", fontSize=15, leading=19,
        textColor=NAVY, spaceBefore=13, spaceAfter=7,
    ),
    "h2": ParagraphStyle(
        "h2", fontName="Helvetica-Bold", fontSize=11.5, leading=15,
        textColor=ACCENT, spaceBefore=9, spaceAfter=3,
    ),
    "title": ParagraphStyle(
        "title", fontName="Helvetica-Bold", fontSize=38, leading=44,
        textColor=NAVY, alignment=TA_CENTER, spaceAfter=10,
    ),
    "subtitle": ParagraphStyle(
        "subtitle", fontName="Helvetica", fontSize=15, leading=21,
        textColor=ACCENT, alignment=TA_CENTER,
    ),
    "kind": ParagraphStyle(
        "kind", fontName="Helvetica-Bold", fontSize=11, leading=15,
        textColor=GREY, alignment=TA_CENTER,
    ),
    "small": ParagraphStyle(
        "small", fontName="Helvetica-Oblique", fontSize=8, leading=11,
        textColor=GREY, alignment=TA_CENTER,
    ),
    "note": ParagraphStyle(
        "note", fontName="Helvetica-Oblique", fontSize=10, leading=14.5,
        textColor=NAVY, alignment=TA_LEFT,
    ),
    "code": ParagraphStyle(
        "code", fontName="Courier", fontSize=7.9, leading=10.6,
        backColor=colors.HexColor("#F2F5F7"), borderPadding=7,
        leftIndent=4, spaceBefore=3, spaceAfter=10,
    ),
    "cell": ParagraphStyle(
        "cell", fontName="Helvetica", fontSize=8.6, leading=11.2,
    ),
    "cell_head": ParagraphStyle(
        "cell_head", fontName="Helvetica-Bold", fontSize=8.6, leading=11.2,
        textColor=colors.white,
    ),
    "toc": ParagraphStyle(
        "toc", fontName="Helvetica", fontSize=10.5, leading=17, leftIndent=8,
    ),
}


def P(text, style="body"):
    return Paragraph(text, STYLES[style])


def body(text):
    return P(esc(text), "body")


def bullets(items):
    out = []
    for item in items:
        if isinstance(item, tuple):
            lead, rest = item
            out.append(Paragraph(f"<b>{esc(lead)}</b>{esc(rest)}", STYLES["bullet"], bulletText="•"))
        else:
            out.append(Paragraph(esc(item), STYLES["bullet"], bulletText="•"))
    return out


def numbered(items):
    out = []
    for i, item in enumerate(items, start=1):
        out.append(Paragraph(esc(item), STYLES["bullet"], bulletText=f"{i}."))
    return out


def h1(text):
    return [Spacer(1, 2), P(esc(text), "h1"), HRFlowable(width="100%", thickness=0.8, color=BORDER, spaceAfter=9)]


def h2(text):
    return P(esc(text), "h2")


def table(headers, rows, widths):
    scale = CONTENT_W / (sum(widths) * cm)
    data = [[Paragraph(esc(h), STYLES["cell_head"]) for h in headers]]
    for row in rows:
        data.append([Paragraph(esc(v), STYLES["cell"]) for v in row])

    t = Table(data, colWidths=[w * cm * scale for w in widths], repeatRows=1, hAlign="CENTER")
    style = [
        ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
    ]
    for r in range(1, len(data)):
        if r % 2 == 0:
            style.append(("BACKGROUND", (0, r), (-1, r), LIGHT))
    t.setStyle(TableStyle(style))
    return [t, Spacer(1, 10)]


def note_box(text):
    t = Table([[Paragraph(esc(text), STYLES["note"])]], colWidths=[CONTENT_W])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EAF3F8")),
        ("LINEBEFORE", (0, 0), (0, -1), 3, ACCENT),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return [Spacer(1, 2), t, Spacer(1, 10)]


def code(text):
    return [Paragraph(esc(text).replace("\n", "<br/>").replace(" ", "&nbsp;"), STYLES["code"])]


# --------------------------------------------------------------------------
# Page decoration
# --------------------------------------------------------------------------

def decorate(canvas, doc):
    if doc.page == 1:
        return
    canvas.saveState()
    canvas.setFont("Helvetica", 7.8)
    canvas.setFillColor(GREY)
    canvas.drawRightString(PAGE_W - M_RIGHT, PAGE_H - 1.35 * cm, "DocEntry-AI  ·  Project Report")
    canvas.setStrokeColor(colors.HexColor("#D5DEE5"))
    canvas.setLineWidth(0.6)
    canvas.line(M_LEFT, PAGE_H - 1.55 * cm, PAGE_W - M_RIGHT, PAGE_H - 1.55 * cm)
    canvas.drawCentredString(PAGE_W / 2, 1.15 * cm, f"Page {doc.page}")
    canvas.restoreState()


# --------------------------------------------------------------------------
# Story
# --------------------------------------------------------------------------

def cover():
    story = [Spacer(1, 3.4 * cm), P("DocEntry-AI", "title"),
             P("AI-Powered Document Data Extraction<br/>for the Import &amp; Export Industry", "subtitle"),
             Spacer(1, 0.7 * cm),
             HRFlowable(width="62%", thickness=1.2, color=ACCENT, hAlign="CENTER"),
             Spacer(1, 0.5 * cm),
             P("PROJECT REPORT", "kind"),
             Spacer(1, 2.6 * cm)]

    details = [
        ("Submitted by", "Prajwal Shinde"),
        ("Project type", "College project · individual"),
        ("Academic year", "2026–27"),
        ("Technology", "Python · Streamlit · Google Gemini API"),
        ("Repository", REPO),
        ("Live demo", "Streamlit Community Cloud"),
    ]
    data = [[Paragraph(esc(k), ParagraphStyle("k", fontName="Helvetica-Bold", fontSize=10, textColor=NAVY, leading=16)),
             Paragraph(esc(v), ParagraphStyle("v", fontName="Helvetica", fontSize=10, leading=16))]
            for k, v in details]
    t = Table(data, colWidths=[4.1 * cm, 11.2 * cm], hAlign="CENTER")
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LINEBELOW", (0, 0), (-1, -2), 0.3, colors.HexColor("#E3EAF0")),
    ]))
    story.append(t)
    story.append(PageBreak())
    return story


def contents():
    story = h1("Contents")
    items = [
        ("1", "Abstract"), ("2", "Introduction and Background"), ("3", "Problem Statement"),
        ("4", "Objectives"), ("5", "Proposed Solution and Scope"), ("6", "System Architecture"),
        ("7", "Technology Stack"), ("8", "Implementation"), ("9", "Workflow and Supported Inputs"),
        ("10", "Results"), ("11", "Testing"), ("12", "Expected Outcome"),
        ("13", "Security and Privacy"), ("14", "Limitations"), ("15", "Future Scope"),
        ("16", "Conclusion"), ("17", "How to Run and Deploy"), ("", "References"),
        ("", "Appendix A — Field Schemas"),
    ]
    for number, name in items:
        prefix = f'<font color="#1F6F8B"><b>{number}.</b></font>&nbsp;&nbsp;' if number else "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
        story.append(Paragraph(prefix + esc(name), STYLES["toc"]))
    story.append(PageBreak())
    return story


def abstract():
    story = h1("1.  Abstract")
    story += [
        body("Every import and export shipment produces a trail of trade documents — tax invoices, "
             "shipping bills, bills of entry, purchase orders and delivery challans. Customs "
             "compliance, DGFT scheme reconciliation, GST filing and bank submissions all require "
             "the contents of those documents to be recorded in Excel registers, and today that "
             "transfer is done by hand: one operator reads a PDF on one screen and re-types each "
             "value into a spreadsheet on the other. It is slow, repetitive and prone to "
             "transposed digits, lost leading zeros and values placed in the wrong column."),
        body("DocEntry-AI removes the typing step. A user uploads one or many documents — a "
             "digital PDF, a phone photo or scan, a Word file, a CSV export, or plain text pasted "
             "directly into the app — chooses the columns required for the register, and the "
             "application reads the document with a multimodal large language model, maps the "
             "values to a document-specific schema, and presents them in an editable grid. One "
             "click exports the approved rows to a fresh Excel file or appends them to an existing "
             "master register."),
        body("The application is written entirely in Python and uses Streamlit for the interface, "
             "PyMuPDF, Pillow and python-docx for document handling, the OpenAI-compatible Gemini "
             "API for extraction, and openpyxl for Excel output. The operator's role shifts from "
             "data entry to data review: instead of producing the data, they confirm it."),
    ]
    return story


def introduction():
    story = h1("2.  Introduction and Background")
    story += [
        body("A single export consignment can generate a dozen documents: a commercial invoice, a "
             "packing list, a shipping bill, a bill of lading, a bank realisation certificate and "
             "supporting declarations. Each arrives as a PDF or a scan from a different source — a "
             "customs portal, a freight forwarder, a bank, an overseas buyer — and each has its own "
             "layout. There is no shared template, so a fixed extraction rule or a simple "
             "copy-paste workflow does not survive contact with real documents."),
        body("The system of record in most trading houses is nevertheless simple: an Excel "
             "register. Auditors, customs officers and bank officials ask for that register, not "
             "the original PDFs. The gap between the two is currently bridged by a person reading "
             "and retyping."),
    ]
    story += note_box("The bottleneck is not a lack of data. It is the manual effort required to "
                      "move data from a document into a structured row.")
    return story


def problem():
    story = h1("3.  Problem Statement")
    story.append(body(
        "Import and export businesses still depend on manual data entry to move information from "
        "trade documents into Excel. The process is slow, repetitive and error-prone, it does not "
        "scale with shipment volume, and the resulting registers are unreliable precisely where "
        "accuracy matters most — customs compliance, scheme reconciliation and audit."))
    story.append(h2("3.1  Current process"))
    story += table(
        ["Step", "How it is done today"],
        [
            ("1. Receive", "Documents arrive as PDFs or scanned images, in many different layouts."),
            ("2. Read", "An operator manually locates each required field inside the document."),
            ("3. Type", "Each value is keyed into the matching Excel column by hand."),
            ("4. Repeat", "The same cycle repeats for every document, every day."),
            ("5. Verify", "A second person re-checks entries, or errors surface later during audit."),
        ],
        [3.2, 12.6],
    )
    story.append(h2("3.2  Pain points"))
    story += bullets([
        ("Time consuming. ", "A single multi-item document can take 15–30 minutes to key in."),
        ("High error rate. ", "Typing introduces transposed digits, stripped leading zeros, values in the wrong column and misread scans."),
        ("Costly consequences. ", "A wrong invoice value, IGST amount or licence number surfaces later as a customs query, a rejected claim or a reconciliation mismatch."),
        ("Does not scale. ", "More shipments means proportionally more operators; experience does not increase throughput."),
        ("Format fragmentation. ", "Every port, bank and buyer issues documents in a different layout, so no fixed template works."),
        ("Low-value work. ", "Skilled documentation staff spend the day typing instead of checking compliance."),
    ])
    return story


def objectives():
    story = h1("4.  Objectives")
    story += numbered([
        "Accept any common document format an exporter actually receives: digital PDF, scanned PDF, phone photo, Word file or pasted text.",
        "Extract the required fields with a free multimodal language model, without OCR templates or fixed coordinates.",
        "Support several trade document types through per-type field schemas that can be extended by editing one dictionary.",
        "Produce one Excel row per line item, so a multi-item invoice becomes a usable register rather than a single summary row.",
        "Keep a human review step before export, so the operator confirms values instead of trusting them blindly.",
        "Export to a new register or append to an existing master file, and run with zero infrastructure cost.",
    ])
    return story


def solution():
    story = h1("5.  Proposed Solution and Scope")
    story.append(body(
        "DocEntry-AI is a single Python web application. The user adds documents, selects the "
        "columns wanted in the register, reviews the extracted values and downloads Excel. The AI "
        "is used only for reading and field matching; all file handling, validation and Excel "
        "writing is ordinary Python, which keeps the output predictable."))
    story += table(
        ["In scope", "Out of scope (first version)"],
        [
            ("Extraction from tax invoices, shipping bills, purchase orders, bills of entry and delivery challans", "Direct filing to customs, DGFT or banking portals"),
            ("Per-type column schemas with user-selectable columns", "Replacing accounting or ERP software"),
            ("Digital PDFs, scanned PDFs, photos, Word, TXT, CSV and pasted text", "Legal or regulatory interpretation of document contents"),
            ("One row per line item, editable before export", "Handwritten documents and non-Latin scripts"),
            ("Fresh Excel register or append to an existing one", "Multi-user accounts, database storage or an audit trail"),
        ],
        [8.0, 7.8],
    )
    return story


def architecture(diagram: Path):
    story = h1("6.  System Architecture")
    story.append(body(
        "The application is deliberately small: five Python modules and one external API. The "
        "diagram below shows the path a document takes from upload to Excel."))
    img_w = CONTENT_W
    img_h = img_w * 800 / 1960
    story.append(Spacer(1, 4))
    story.append(Image(str(diagram), width=img_w, height=img_h))
    story.append(Spacer(1, 5))
    story.append(P("Figure 1 — Document flow through DocEntry-AI", "small"))
    story.append(Spacer(1, 10))

    story.append(h2("6.1  Path of one document"))
    story += numbered([
        "Read. documents.py converts the uploaded file into text, or into JPEG images when the content is a scan or a photo.",
        "Prompt. extractor.py combines the document type, the selected field keys and the document content into one prompt.",
        "Extract. The prompt is sent to gemini-3.1-flash-lite through the OpenAI-compatible endpoint. The model returns JSON only.",
        "Parse. The reply is cleaned, parsed and normalised so every requested key exists with a confidence level.",
        "Review. app.py shows one editable table row per line item. Nothing is written until the user approves.",
        "Export. excel_writer.py writes a new workbook or appends rows below the existing data of a master file.",
    ])
    story.append(h2("6.2  Design decisions"))
    story += bullets([
        ("Text first, images only when needed. ", "A digital PDF is sent as text because it is cheaper and more accurate than rendering pages. Pages are rendered only when the PDF has almost no extractable text."),
        ("One request per document. ", "Batch handling lives in the app loop, so one failure does not abort the rest of the batch."),
        ("JSON contract. ", "The model is instructed to return a fixed JSON shape, which removes guesswork from parsing."),
        ("Schema-driven columns. ", "Adding a new document type means adding one entry to DOCUMENT_TYPES in schemas.py; no other file changes."),
    ])
    return story


def tech_stack():
    story = h1("7.  Technology Stack")
    story.append(body(
        "Python is the only programming language used. There is no HTML, CSS or JavaScript written "
        "by hand — Streamlit generates the page from Python."))
    story += table(
        ["Layer", "Technology", "Purpose in this project"],
        [
            ("Language", "Python 3.12 (cloud), 3.14 (local)", "All application logic"),
            ("Interface", "Streamlit", "Sidebar, tabs, uploader, editable table, download button"),
            ("AI model", "Google Gemini — gemini-3.1-flash-lite", "Reads documents and returns field values as JSON"),
            ("AI client", "openai Python SDK", "Calls Gemini's OpenAI-compatible endpoint"),
            ("PDF", "PyMuPDF", "Text extraction; rendering scanned pages to images"),
            ("Images", "Pillow", "Opens photos, applies EXIF rotation, downscales to 1600 px"),
            ("Word", "python-docx", "Reads paragraphs and tables from .docx files"),
            ("Excel", "openpyxl", "Creates and appends to .xlsx registers, with header styling"),
            ("Config", "python-dotenv", "Loads API settings from .env locally"),
            ("Hosting", "Streamlit Community Cloud", "Free public deployment from GitHub"),
        ],
        [2.8, 5.4, 7.6],
    )
    story.append(body(
        "The free tier of the AI model was a hard requirement, so the model was chosen after "
        "timing real requests: gemini-3.1-flash-lite answers in roughly 2–4 seconds per document, "
        "where a larger model either timed out or was unavailable to new accounts."))
    return story


def implementation():
    story = h1("8.  Implementation")
    story.append(body(
        "The project contains five Python modules totalling about 1,020 lines, plus configuration "
        "and sample documents."))
    story += table(
        ["File", "Lines", "Responsibility"],
        [
            ("app.py", "453", "All UI: sidebar, the four steps, tabs, progress, review grid, download"),
            ("extractor.py", "232", "Prompt construction, model call, JSON parsing, error reporting"),
            ("documents.py", "150", "Any supported file → text or images"),
            ("schemas.py", "101", "Field definitions for the five document types"),
            ("excel_writer.py", "84", "Workbook creation and append-to-master logic"),
        ],
        [3.2, 1.8, 10.8],
    )

    story.append(h2("8.1  documents.py — one reader for every format"))
    story.append(body(
        "Each file type is converted into a small Document object holding either text or a list "
        "of JPEG images. A PDF is opened with PyMuPDF and its text is joined across pages. If "
        "fewer than 40 characters are found, the file is treated as a scan: the first five pages "
        "are rendered at 150 dpi and re-encoded as JPEG. Photos are EXIF-rotated, converted to RGB "
        "and downscaled to 1600 px wide, which keeps phone photos within a sensible request size. "
        "Word files are read paragraph by paragraph, including table cells joined with pipe "
        "characters. A CSV export is read with Python's csv module, auto-detecting comma, "
        "semicolon or tab separators, and is written out one pipe-separated line per row so the "
        "model sees the header and the values together. Files larger than 200 rows are cut at the "
        "200th row, with a note shown in the preview."))

    story.append(h2("8.2  extractor.py — prompt, call, parse"))
    story.append(body(
        "The prompt states the document type, the exact field keys and labels, and the required "
        "JSON shape. The reply is parsed leniently: code fences are stripped, and if the model "
        "wraps the JSON in extra text, the outermost braces are recovered. Both the current "
        '{"records": [...]} shape and the older {"fields": {...}} shape are accepted, so an old '
        "cached module cannot break the page."))
    story += code(
        '{\n  "records": [\n    {"fields": {"invoice_no": "INV/2026/0100", "hsn_code": "5208", "quantity": "500"},\n'
        '     "confidence": {"invoice_no": "high", "hsn_code": "high", "quantity": "high"}}\n  ]\n}'
    )
    story.append(body(
        "If the provider rejects JSON mode or returns a 400 that is not an authentication "
        "problem, the request is retried once without response_format. Every requested key is "
        "guaranteed to exist in the result, with an empty value and low confidence when the "
        "document does not contain it."))

    story.append(h2("8.3  schemas.py — the column contract"))
    story.append(body(
        "DOCUMENT_TYPES maps each document type to a list of (key, label) pairs. The keys are used "
        "in the prompt and in Excel; the labels are what the user sees. Two audit columns, Source "
        "File and Extracted At, are appended automatically so every exported row can be traced "
        "back to its document."))

    story.append(h2("8.4  excel_writer.py — the register"))
    story.append(body(
        "Rows are written with openpyxl. A fresh workbook gets a styled header row, a frozen top "
        "pane and sensible column widths. When a master file is supplied, the existing header is "
        "inspected, missing columns are added, and new rows are appended below the last used row "
        "without disturbing the existing data."))

    story.append(h2("8.5  app.py — the four-step interface"))
    story.append(body(
        "The page is a linear flow: add documents, choose columns, extract and review, download. "
        "The upload tab and the paste-text tab feed the same list of sources, so a pasted document "
        "is processed exactly like a file. Extraction runs in a loop with a progress bar; each "
        "line item becomes a row. Low-confidence fields are listed under the table so the operator "
        "knows what to check first."))
    return story


def workflow():
    story = h1("9.  Workflow and Supported Inputs")
    story += table(
        ["Step", "What the user does", "What the application does"],
        [
            ("1  Add documents", "Uploads one or many files, or pastes text", "Queues each source and shows a preview of the first one"),
            ("2  Choose columns", "Selects the columns needed in the register", "Maps labels to schema keys for the chosen document type"),
            ("3  Extract and review", "Presses Extract fields, then corrects cells", "Calls the model, creates one row per line item, flags low confidence"),
            ("4  Download", "Optionally uploads an existing master register", "Builds or appends the workbook and offers it as a download"),
        ],
        [3.4, 5.2, 7.2],
    )
    story.append(h2("9.1  Supported input formats"))
    story += table(
        ["Input", "How it is read", "Best for"],
        [
            ("Digital PDF", "Text extracted directly with PyMuPDF", "Portal-generated invoices and bills"),
            ("Scanned PDF", "First 5 pages rendered to JPEG and read visually", "Scanned customs paperwork"),
            ("JPG / PNG / WEBP / BMP / TIFF", "Pillow load, EXIF rotation, downscale to 1600 px", "Phone photos of documents"),
            ("DOCX", "Paragraphs and table cells via python-docx", "Documents received in Word"),
            ("TXT", "Decoded as UTF-8 with replacement for bad bytes", "Exported text from other systems"),
            ("CSV", "Parsed with Python's csv module; comma, semicolon or tab separated", "Exports from Excel, Tally or a portal"),
            ("Pasted text", "Used as-is, with a user-supplied row name", "Emails and portal pages"),
        ],
        [4.6, 7.2, 4.0],
    )
    story.append(h2("9.2  Supported document types"))
    story += table(
        ["Document type", "Fields"],
        [
            ("Tax Invoice", "19 fields — invoice no, date, seller/buyer, GSTIN, place of supply, HSN, description, quantity, unit, rate, taxable value, IGST, CGST, SGST, total, currency"),
            ("Shipping Bill", "17 fields — bill no, date, exporter, IEC, GSTIN, invoice, ports, vessel, HSN, description, quantity, FOB value, currency, scheme"),
            ("Purchase Order", "12 fields — PO no, date, buyer, supplier, HSN, description, quantity, unit, rate, total, currency, delivery terms"),
            ("Bill of Entry", "14 fields — BE no, date, importer, IEC, GSTIN, invoice, ports, HSN, description, quantity, assessable value, duty, currency"),
            ("Delivery Challan", "10 fields — challan no, date, consignor, consignee, HSN, description, quantity, unit, value, vehicle no"),
        ],
        [3.6, 12.2],
    )
    return story


def results():
    story = h1("10.  Results")
    story.append(body(
        "The same test invoice was supplied in three different formats and produced identical "
        "values, confirming that the text path and the vision path agree."))
    story += table(
        ["Field", "Text PDF", "Scanned JPG", "DOCX"],
        [
            ("Invoice number", "INV/2026/0042", "INV/2026/0042", "INV/2026/0042"),
            ("Invoice date", "15-10-2026", "15-10-2026", "15-10-2026"),
            ("Seller GSTIN", "27ABCDE1234F1Z5", "27ABCDE1234F1Z5", "27ABCDE1234F1Z5"),
            ("HSN code", "5208", "5208", "5208"),
            ("Quantity", "1500", "1500", "1500"),
            ("Total invoice value", "371700.00", "371700.00", "371700.00"),
        ],
        [4.4, 4.0, 4.0, 3.4],
    )
    story.append(h2("10.1  Multi-item extraction"))
    story.append(body(
        "A three-item invoice (INV/2026/0100) produced three rows in one pass, each carrying the "
        "invoice-level values so it can stand alone in the register."))
    story += table(
        ["Row", "HSN", "Description", "Quantity", "Rate", "Invoice no."],
        [
            ("1", "5208", "Cotton Fabric 40s", "500", "238.00", "INV/2026/0100"),
            ("2", "5205", "Cotton Yarn 20s", "300", "150.00", "INV/2026/0100"),
            ("3", "5402", "Polyester Thread", "200", "210.00", "INV/2026/0100"),
        ],
        [1.4, 2.2, 5.4, 2.4, 2.2, 4.2],
    )
    story.append(h2("10.2  Timing"))
    story += table(
        ["Operation", "Measured time"],
        [
            ("Text PDF → fields", "2.3 – 2.4 s"),
            ("Scanned image → fields", "4.3 s"),
            ("DOCX → fields", "2.3 s"),
            ("Connection test (one short reply)", "about 1 s"),
        ],
        [9.4, 6.4],
    )
    return story


def testing():
    story = h1("11.  Testing")
    story += table(
        ["#", "Test case", "Input", "Expected", "Result"],
        [
            ("1", "Digital PDF, single item", "sample_tax_invoice.pdf", "1 row, all fields", "Pass"),
            ("2", "Scanned image", "sample_tax_invoice_scan.jpg", "1 row, values match PDF", "Pass"),
            ("3", "Word document", "sample_tax_invoice.docx", "1 row, values match PDF", "Pass"),
            ("4", "Pasted text", "Invoice text pasted in the tab", "1 row named by the user", "Pass"),
            ("5", "Multi-item invoice", "sample_tax_invoice_multi.pdf", "3 rows, 3 products", "Pass"),
            ("6", "Batch upload", "PDF + JPG + DOCX together", "3 rows in one register", "Pass"),
            ("7", "CSV export, three line items", "sample_tax_invoice.csv", "3 rows, values match the file", "Pass"),
            ("8", "Invalid API key", "Wrong key in secrets", "Clear error, no crash", "Pass"),
            ("9", "Unsupported file", "e.g. .xlsx used as input", "Readable message, file skipped", "Pass"),
        ],
        [1.0, 4.6, 4.6, 3.4, 2.2],
    )
    story.append(body(
        "The interface was also exercised headlessly with Streamlit's AppTest: text was placed in "
        "the paste box, the extract button was pressed, and the resulting session rows were "
        "checked programmatically. That test is what caught the original one-row-only behaviour."))
    return story


def outcome():
    story = h1("12.  Expected Outcome")
    story += table(
        ["Parameter", "Manual process", "With DocEntry-AI"],
        [
            ("Time per document", "15–30 minutes", "Seconds"),
            ("Error rate", "High — typing and transposition", "Low — extraction plus human review"),
            ("Scalability", "More volume needs more staff", "Batch processing with the same staff"),
            ("Staff role", "Data entry", "Verification and compliance"),
            ("Auditability", "No trace of who typed what", "Source file and timestamp on every row"),
        ],
        [4.0, 6.2, 5.6],
    )
    return story


def security():
    story = h1("13.  Security and Privacy")
    story += bullets([
        ("Key handling. ", "The API key lives in .env locally and in Streamlit Cloud Secrets when deployed. Both are excluded from Git, so the public repository contains no credentials."),
        ("No storage. ", "Uploaded documents are processed in memory and are not written to disk or to a database."),
        ("Provider exposure. ", "Document text or page images are sent to Google's Gemini API for extraction; this is the only third party involved."),
        ("Review before export. ", "Nothing is committed to a register until the user presses download."),
    ])
    return story


def limitations():
    story = h1("14.  Limitations")
    story += bullets([
        "One document type per run: all files in a batch must belong to the type selected in the sidebar.",
        "Scanned PDFs: only the first five pages are read, to control request size.",
        "CSV files: only the first 200 rows are read.",
        "Multi-item documents are capped at 50 rows per document.",
        "Photos are downscaled to 1600 px, which is enough for print but not for very small print.",
        "Handwritten text, stamps and non-Latin scripts are not reliably read.",
        "Values are copied, not validated: GSTIN checksums, date arithmetic and total reconciliation are not checked.",
        "The free tier has request-rate limits, so very large batches may need to be split.",
    ])
    return story


def future():
    story = h1("15.  Future Scope")
    story += bullets([
        "Automatic document-type detection, so a mixed batch no longer needs the sidebar selection.",
        "Splitting a scanned batch PDF into separate documents by page.",
        "Validation rules: GSTIN checksum, quantity × rate = taxable value, tax arithmetic, date sanity.",
        "Persistent master register with a database and a searchable history.",
        "Highlighting low-confidence cells directly in the Excel file.",
        "Multi-language OCR and handwriting support.",
        "User accounts, roles and a full audit trail.",
        "Direct export connectors for accounting software and ERP systems.",
    ])
    return story


def conclusion():
    story = h1("16.  Conclusion")
    story += [
        body("The bottleneck in trade documentation is not a lack of data but the manual effort "
             "required to transfer it. DocEntry-AI removes that effort: documents of any common "
             "format are read by a multimodal model, mapped to a per-type schema, reviewed in an "
             "editable grid, and written to an Excel register with one row per line item. The "
             "operator moves from typing to checking, which is where their knowledge actually adds "
             "value."),
        body("The implementation is deliberately small — five Python modules and one external API "
             "— which keeps it maintainable for a college project while still demonstrating the "
             "full pipeline of file handling, prompt engineering, structured output parsing and "
             "spreadsheet generation."),
    ]
    return story


def how_to_run():
    story = h1("17.  How to Run and Deploy")
    story.append(h2("17.1  Local"))
    story += code(
        "cd DocEntry-AI\npython -m venv .venv\n.venv/bin/pip install -r requirements.txt\n"
        ".venv/bin/streamlit run app.py        # http://localhost:8501"
    )
    story.append(body(
        "The key is placed in .env as AI_API_KEY, with AI_BASE_URL pointed at the Gemini "
        "OpenAI-compatible endpoint and AI_MODEL set to gemini-3.1-flash-lite. The sidebar shows "
        "the model, a masked key fingerprint and a Test connection button."))
    story.append(h2("17.2  Public link"))
    story.append(body(
        "The repository is public on GitHub. Streamlit Community Cloud builds it directly from the "
        "main branch using runtime.txt (Python 3.12) and requirements.txt. The same three settings "
        "are stored in the app's Secrets panel as TOML, so no key is ever committed. Every push to "
        "main triggers an automatic rebuild."))
    story += code(
        'AI_API_KEY = "..."\nAI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"\n'
        'AI_MODEL = "gemini-3.1-flash-lite"'
    )
    return story


def references():
    story = h1("References")
    refs = [
        "Streamlit documentation — https://docs.streamlit.io",
        "Google AI Studio and Gemini API — https://ai.google.dev",
        "OpenAI Python SDK — https://github.com/openai/openai-python",
        "PyMuPDF documentation — https://pymupdf.readthedocs.io",
        "python-docx documentation — https://python-docx.readthedocs.io",
        "openpyxl documentation — https://openpyxl.readthedocs.io",
        "Pillow documentation — https://pillow.readthedocs.io",
        "Streamlit Community Cloud — https://share.streamlit.io",
        f"Project repository — {REPO}",
    ]
    story += numbered(refs)
    return story


def appendix():
    story = h1("Appendix A — Field Schemas")
    story.append(body(
        "Each document type maps to a list of (key, label) pairs in schemas.py. The keys are used "
        "in the prompt and in Excel; the labels are shown to the user."))
    story += table(
        ["Document type", "Field keys"],
        [
            ("Tax Invoice", "invoice_no, invoice_date, seller_name, seller_gstin, buyer_name, buyer_gstin, buyer_address, place_of_supply, hsn_code, description, quantity, unit, rate, taxable_value, igst_amount, cgst_amount, sgst_amount, total_value, currency"),
            ("Shipping Bill", "shipping_bill_no, shipping_bill_date, exporter_name, iec_code, gstin, invoice_no, invoice_date, port_of_loading, port_of_discharge, vessel_name, hsn_code, description, quantity, unit, fob_value, currency, scheme"),
            ("Purchase Order", "po_no, po_date, buyer_name, supplier_name, hsn_code, description, quantity, unit, rate, total_value, currency, delivery_terms"),
            ("Bill of Entry", "be_no, be_date, importer_name, iec_code, gstin, invoice_no, port_of_loading, port_of_discharge, hsn_code, description, quantity, assessable_value, total_duty, currency"),
            ("Delivery Challan", "challan_no, challan_date, consignor, consignee, hsn_code, description, quantity, unit, value, vehicle_no"),
            ("Audit columns", "source_file, extracted_at (added to every type automatically)"),
        ],
        [3.6, 12.2],
    )
    return story


# --------------------------------------------------------------------------

def build() -> Path:
    diagram = build_diagram()

    doc = BaseDocTemplate(
        str(PDF),
        pagesize=A4,
        leftMargin=M_LEFT,
        rightMargin=M_RIGHT,
        topMargin=M_TOP,
        bottomMargin=M_BOTTOM,
        title="DocEntry-AI — Project Report",
        author="Prajwal Shinde",
        subject="AI-powered document data extraction for import/export trade documents",
    )

    frame = Frame(M_LEFT, M_BOTTOM, CONTENT_W, PAGE_H - M_TOP - M_BOTTOM, id="body")
    doc.addPageTemplates([PageTemplate(id="all", frames=[frame], onPage=decorate)])

    story = []
    story += cover()
    story += contents()
    story += abstract()
    story += introduction()
    story += problem()
    story += objectives()
    story += solution()
    story += architecture(diagram)
    story += tech_stack()
    story += implementation()
    story += workflow()
    story += results()
    story += testing()
    story += outcome()
    story += security()
    story += limitations()
    story += future()
    story += conclusion()
    story += how_to_run()
    story += references()
    story += appendix()

    doc.build(story)
    return PDF


if __name__ == "__main__":
    path = build()
    print("wrote", path)
    print("wrote", DIAGRAM)
