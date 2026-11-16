"""
Shared layout, styles, helpers and diagrams for the DocEntry-AI report.

Used by docs/make_report.py. Kept separate so the content file stays readable.
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
    CondPageBreak,
    Frame,
    HRFlowable,
    Image,
    KeepTogether,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

OUT = Path(__file__).resolve().parent
FIG_DIR = OUT / "figures"

PAGE_W, PAGE_H = A4
M_LEFT, M_RIGHT, M_TOP, M_BOTTOM = 2.4 * cm, 2.2 * cm, 2.5 * cm, 2.3 * cm
CONTENT_W = PAGE_W - M_LEFT - M_RIGHT

# ---------------------------------------------------------------- palette
NAVY = colors.HexColor("#1B2A41")
CHARCOAL = colors.HexColor("#33383D")
GREY = colors.HexColor("#5C6369")
MUTED = colors.HexColor("#8A9299")
LIGHT = colors.HexColor("#EFF1F3")
BORDER = colors.HexColor("#C9CED3")
WHITE = colors.white

# ---------------------------------------------------------------- registries
# Captions are declared once here so the List of Tables / Figures and the body
# always agree. Key is the number, value is the caption text.
TABLES = {
    "1.1": "Steps in the manual data-entry process and the weakness of each",
    "1.2": "Scope of the project and what is deliberately left out",
    "1.3": "Expected outcome compared with the present manual process",
    "2.1": "Summary of earlier work on document data extraction",
    "2.2": "Categories of extraction methods and how they compare",
    "3.1": "Modules in the application and what each one does",
    "3.2": "Technology options considered and the reason for the choice",
    "4.1": "Hardware requirements",
    "4.2": "Software requirements",
    "4.3": "Functional requirements",
    "4.4": "Non-functional requirements",
    "5.1": "Source files, size and responsibility",
    "5.2": "Fields extracted for each document type",
    "6.1": "Where the project can be applied and what it saves",
    "7.1": "Advantages of DocEntry-AI over manual data entry",
    "9.1": "Objectives and the evidence that each was met",
    "10.1": "Planned development phases after the first release",
    "A.1": "Tax Invoice schema",
    "A.2": "Shipping Bill schema",
    "A.3": "Field lists for the remaining six document types",
    "B.1": "Values extracted from the three-item sample invoice",
    "C.1": "Test log with inputs, expected results and outcome",
}

FIGURES = {
    "3.1": "Block diagram of the proposed system",
    "3.2": "Document processing workflow",
    "3.3": "Main modules and the data passed between them",
    "3.4": "Deployment view of the application",
    "5.1": "Wireframe of the review screen (schematic, not a screenshot)",
    "5.2": "Sequence of calls for one uploaded document",
    "10.1": "Development timeline for the planned enhancements",
}

# Contents outline. Level 0 = chapter, level 1 = section.
OUTLINE = [
    ("Acknowledgement", 0, "front"),
    ("Abstract", 0, "front"),
    ("List of Tables", 0, "front"),
    ("List of Figures", 0, "front"),
    ("Abbreviations", 0, "front"),
    ("1  Introduction", 0, "body"),
    ("1.1  Background and Motivation", 1, "body"),
    ("1.2  Problem Statement", 1, "body"),
    ("1.3  Objectives of the Project", 1, "body"),
    ("1.4  Scope and Limitations", 1, "body"),
    ("1.5  Expected Outcomes", 1, "body"),
    ("2  Literature Review and Theoretical Background", 0, "body"),
    ("2.1  Review of Previous Work Related to Document Data Extraction", 1, "body"),
    ("2.2  Key Concepts: Document Processing, OCR, and Data Extraction", 1, "body"),
    ("2.3  Review of Existing Systems and Methods", 1, "body"),
    ("2.4  Gap Analysis", 1, "body"),
    ("3  System Overview and Design", 0, "body"),
    ("3.1  Proposed DocEntry-AI System", 1, "body"),
    ("3.2  Block Diagram of the Proposed System", 1, "body"),
    ("3.3  Description of System Components", 1, "body"),
    ("3.4  Document Processing Workflow", 1, "body"),
    ("3.5  Selection Criteria for Components and Tools", 1, "body"),
    ("4  System Specifications", 0, "body"),
    ("4.1  Hardware Requirements", 1, "body"),
    ("4.2  Software Requirements", 1, "body"),
    ("4.3  Functional Requirements", 1, "body"),
    ("4.4  Non-Functional Requirements", 1, "body"),
    ("5  Implementation", 0, "body"),
    ("5.1  Document Upload", 1, "body"),
    ("5.2  Document Type Identification and Data Extraction", 1, "body"),
    ("5.3  Column Selection and Field Mapping", 1, "body"),
    ("5.4  Data Review and Editing", 1, "body"),
    ("5.5  Excel Register Generation and Download", 1, "body"),
    ("6  Applications of the Project", 0, "body"),
    ("6.1  Import and Export Documentation", 1, "body"),
    ("6.2  Customs and Compliance Record Preparation", 1, "body"),
    ("6.3  Reconciliation and Internal Record Keeping", 1, "body"),
    ("7  Advantages", 0, "body"),
    ("8  Limitations", 0, "body"),
    ("9  Conclusion", 0, "body"),
    ("9.1  Project Summary", 1, "body"),
    ("9.2  Outcomes in Relation to Project Objectives", 1, "body"),
    ("9.3  Issues Identified", 1, "body"),
    ("10  Future Work", 0, "body"),
    ("10.1  Planned Enhancements", 1, "body"),
    ("10.2  Development Plan and Timeline", 1, "body"),
    ("10.3  Expected Future Outcomes", 1, "body"),
    ("11  Publications", 0, "body"),
    ("12  References", 0, "body"),
    ("13  Appendices", 0, "body"),
]

# ---------------------------------------------------------------- styles
STYLES = {
    "body": ParagraphStyle(
        "body", fontName="Helvetica", fontSize=10.3, leading=15.6,
        alignment=TA_JUSTIFY, spaceAfter=7,
    ),
    "body_first": ParagraphStyle(
        "body_first", fontName="Helvetica", fontSize=10.3, leading=15.6,
        alignment=TA_JUSTIFY, spaceAfter=7, firstLineIndent=0,
    ),
    "bullet": ParagraphStyle(
        "bullet", fontName="Helvetica", fontSize=10.2, leading=15.0,
        alignment=TA_LEFT, leftIndent=16, bulletIndent=4, spaceAfter=4,
    ),
    "h1": ParagraphStyle(
        "h1", fontName="Helvetica-Bold", fontSize=15.5, leading=20,
        textColor=NAVY, spaceBefore=6, spaceAfter=6,
    ),
    "h2": ParagraphStyle(
        "h2", fontName="Helvetica-Bold", fontSize=11.6, leading=15,
        textColor=colors.HexColor("#3F5C7A"), spaceBefore=11, spaceAfter=4,
    ),
    "front_title": ParagraphStyle(
        "front_title", fontName="Helvetica-Bold", fontSize=17, leading=22,
        textColor=NAVY, spaceAfter=10,
    ),
    "caption": ParagraphStyle(
        "caption", fontName="Helvetica-Oblique", fontSize=8.6, leading=11.6,
        textColor=GREY, alignment=TA_CENTER, spaceBefore=4, spaceAfter=10,
    ),
    "cell": ParagraphStyle("cell", fontName="Helvetica", fontSize=8.5, leading=11.2),
    "cell_head": ParagraphStyle(
        "cell_head", fontName="Helvetica-Bold", fontSize=8.5, leading=11.2,
        textColor=WHITE,
    ),
    "cell_bold": ParagraphStyle(
        "cell_bold", fontName="Helvetica-Bold", fontSize=8.5, leading=11.2,
        textColor=CHARCOAL,
    ),
    "toc": ParagraphStyle("toc", fontName="Helvetica", fontSize=10, leading=16),
    "toc_chapter": ParagraphStyle(
        "toc_chapter", fontName="Helvetica-Bold", fontSize=10, leading=17,
        textColor=NAVY,
    ),
    "toc_page": ParagraphStyle(
        "toc_page", fontName="Helvetica", fontSize=10, leading=16, alignment=TA_RIGHT,
    ),
    "toc_page_bold": ParagraphStyle(
        "toc_page_bold", fontName="Helvetica-Bold", fontSize=10, leading=17,
        alignment=TA_RIGHT, textColor=NAVY,
    ),
    "note": ParagraphStyle(
        "note", fontName="Helvetica-Oblique", fontSize=9.8, leading=14,
        textColor=CHARCOAL, alignment=TA_LEFT,
    ),
    "code": ParagraphStyle(
        "code", fontName="Courier", fontSize=7.5, leading=9.6,
        backColor=colors.HexColor("#EEF0F2"), borderPadding=6,
        leftIndent=4, spaceBefore=4, spaceAfter=10, textColor=colors.HexColor("#22272B"),
    ),
    "ref": ParagraphStyle(
        "ref", fontName="Helvetica", fontSize=9.6, leading=14,
        alignment=TA_LEFT, leftIndent=24, firstLineIndent=-24, spaceAfter=5,
    ),
}


def esc(text: str) -> str:
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def new_page():
    """Start a new page only when the current one already has content.

    A plain PageBreak after a chapter that happens to end exactly at the foot of
    a page produces an empty page. CondPageBreak with almost the full frame
    height breaks mid-page but does nothing when the cursor is already at the
    top of a fresh page.
    """
    return CondPageBreak(24 * cm)


def P(text, style="body"):
    return Paragraph(text, STYLES[style])


def body(text):
    return Paragraph(esc(text), STYLES["body"])


def bullets(items):
    out = []
    for item in items:
        if isinstance(item, tuple):
            lead, rest = item
            out.append(Paragraph(f"<b>{esc(lead)}</b>{esc(rest)}", STYLES["bullet"], bulletText="\u2022"))
        else:
            out.append(Paragraph(esc(item), STYLES["bullet"], bulletText="\u2022"))
    return out


def numbered(items):
    return [
        Paragraph(esc(item), STYLES["bullet"], bulletText=f"{i}.")
        for i, item in enumerate(items, start=1)
    ]


def h1(text):
    p = Paragraph(esc(text), STYLES["h1"])
    p._kind = "h1"
    p._text = text
    return [
        Spacer(1, 4),
        p,
        HRFlowable(width="100%", thickness=0.9, color=BORDER, spaceBefore=1, spaceAfter=10),
    ]


def h2(text):
    p = Paragraph(esc(text), STYLES["h2"])
    p._kind = "h2"
    p._text = text
    return p


def front_title(text):
    p = Paragraph(esc(text), STYLES["front_title"])
    p._kind = "front"
    p._text = text
    return [p, HRFlowable(width="100%", thickness=0.9, color=BORDER, spaceAfter=12)]


def table(key, headers, rows, widths, bold_first=False):
    caption_text = TABLES[key]
    cap = Paragraph(f"Table {key}  {caption_text}", STYLES["caption"])
    cap._kind = "table"
    cap._key = key
    cap.keepWithNext = 1

    scale = CONTENT_W / (sum(widths) * cm)
    data = [[Paragraph(esc(h), STYLES["cell_head"]) for h in headers]]
    for row in rows:
        cells = []
        for i, value in enumerate(row):
            style = "cell_bold" if (bold_first and i == 0) else "cell"
            cells.append(Paragraph(esc(value), STYLES[style]))
        data.append(cells)

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
    return [Spacer(1, 2), cap, t, Spacer(1, 8)]


def figure(key, path, width_cm=15.6):
    caption_text = FIGURES[key]
    cap = Paragraph(f"Figure {key}  {caption_text}", STYLES["caption"])
    cap._kind = "figure"
    cap._key = key
    width = width_cm * cm
    height = width * 0.5  # placeholder, replaced below
    from PIL import Image as _PILImage
    with _PILImage.open(path) as im:
        ratio = im.height / im.width
    height = width * ratio
    max_h = 15.0 * cm
    if height > max_h:
        height = max_h
        width = height / ratio
    img = Image(str(path), width=width, height=height)
    return [Spacer(1, 4), KeepTogether([img, cap]), Spacer(1, 6)]


def note_box(text):
    t = Table([[Paragraph(esc(text), STYLES["note"])]], colWidths=[CONTENT_W])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F1F3F5")),
        ("LINEBEFORE", (0, 0), (0, -1), 3, NAVY),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return [Spacer(1, 2), t, Spacer(1, 10)]


def code(text):
    body_html = esc(text).replace("\n", "<br/>").replace(" ", "&nbsp;")
    return [Paragraph(body_html, STYLES["code"]), Spacer(1, 2)]


def toc_table(pagemap, front_only=False):
    """Contents table. pagemap maps outline label -> displayed page number."""
    rows = []
    for label, level, kind in OUTLINE:
        if front_only and kind != "front":
            continue
        if not front_only and kind != "body":
            continue
        page = pagemap.get(label, "\u2013")
        page_style = "toc_page_bold" if level == 0 else "toc_page"
        text_style = "toc_chapter" if level == 0 else "toc"
        prefix = "" if level == 0 else "&nbsp;&nbsp;&nbsp;&nbsp;"
        rows.append([
            Paragraph(prefix + esc(label), STYLES[text_style]),
            Paragraph(esc(str(page)), STYLES[page_style]),
        ])
    t = Table(rows, colWidths=[CONTENT_W - 2.4 * cm, 2.4 * cm], hAlign="CENTER")
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ]))
    return t


def list_table(registry, kind_word, pagemap):
    rows = []
    for key, caption in registry.items():
        label = f"{kind_word} {key}"
        rows.append([
            Paragraph(esc(label), STYLES["toc"]),
            Paragraph(esc(caption), STYLES["toc"]),
            Paragraph(esc(str(pagemap.get(label, "\u2013"))), STYLES["toc_page"]),
        ])
    t = Table(rows, colWidths=[2.2 * cm, CONTENT_W - 4.6 * cm, 2.4 * cm], hAlign="CENTER")
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    return t


# ---------------------------------------------------------------- document
def roman(n: int) -> str:
    vals = [(1000, "m"), (900, "cm"), (500, "d"), (400, "cd"), (100, "c"),
            (90, "xc"), (50, "l"), (40, "xl"), (10, "x"), (9, "ix"),
            (5, "v"), (4, "iv"), (1, "i")]
    out = ""
    for value, symbol in vals:
        while n >= value:
            out += symbol
            n -= value
    return out


class ReportDoc(BaseDocTemplate):
    def __init__(self, filename, **kw):
        super().__init__(filename, **kw)
        self.toc_pages = {}
        self.table_pages = {}
        self.figure_pages = {}
        self.body_start = None
        self.front_pages = None
        # Page where roman numbering starts (Acknowledgement). Set on pass two.
        self.roman_start = None

    def afterFlowable(self, flowable):
        kind = getattr(flowable, "_kind", None)
        if kind in ("h1", "h2", "front"):
            self.toc_pages[flowable._text] = self.page
            if kind == "h1" and self.body_start is None:
                self.body_start = self.page
        elif kind == "table":
            self.table_pages[flowable._key] = self.page
        elif kind == "figure":
            self.figure_pages[flowable._key] = self.page


def decorate(canvas, doc):
    """Header and footer. Called for every page."""
    if doc.page == 1:
        return
    canvas.saveState()
    canvas.setFont("Helvetica", 7.8)
    canvas.setFillColor(GREY)
    canvas.drawRightString(PAGE_W - M_RIGHT, PAGE_H - 1.4 * cm, "DocEntry-AI  \u00b7  Project Report")
    canvas.setStrokeColor(colors.HexColor("#D8DDE1"))
    canvas.setLineWidth(0.6)
    canvas.line(M_LEFT, PAGE_H - 1.6 * cm, PAGE_W - M_RIGHT, PAGE_H - 1.6 * cm)

    if doc.front_pages:
        if doc.roman_start and doc.page < doc.roman_start:
            label = None
        elif doc.page <= doc.front_pages:
            start = doc.roman_start or 2
            label = roman(doc.page - start + 1)
        else:
            label = str(doc.page - doc.front_pages)
        if label is not None:
            canvas.setFont("Helvetica", 8.4)
            canvas.setFillColor(GREY)
            canvas.drawCentredString(PAGE_W / 2, 1.15 * cm, f"Page {label}")
    canvas.restoreState()


def make_doc(path, front_pages=None, roman_start=None):
    doc = ReportDoc(
        str(path),
        pagesize=A4,
        leftMargin=M_LEFT,
        rightMargin=M_RIGHT,
        topMargin=M_TOP,
        bottomMargin=M_BOTTOM,
        title="DocEntry-AI \u2014 Project Report",
        author="Prajwal Shinde",
        subject="AI-powered document data extraction for import and export trade documents",
    )
    doc.front_pages = front_pages
    doc.roman_start = roman_start
    frame = Frame(M_LEFT, M_BOTTOM, CONTENT_W, PAGE_H - M_TOP - M_BOTTOM, id="body")
    doc.addPageTemplates([PageTemplate(id="all", frames=[frame], onPage=decorate)])
    return doc


# ---------------------------------------------------------------- diagrams
def _font(size, bold=False):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(f"/usr/share/fonts/truetype/dejavu/{name}", size)


def _box(draw, x, y, w, h, title, sub, fill, border, text_color="#FFFFFF", radius=16):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=radius, fill=fill, outline=border, width=3)
    draw.multiline_text(
        (x + w / 2, y + (h - 18) / 2 - 20), title,
        font=_font(23, True), fill=text_color, anchor="mm", align="center",
    )
    if sub:
        draw.multiline_text(
            (x + w / 2, y + h - 42), sub,
            font=_font(18), fill=text_color, anchor="mm", align="center", spacing=6,
        )


def _arrow(draw, points, color="#1B2A41", width=4):
    draw.line(points, fill=color, width=width, joint="curve")
    (x1, y1), (x2, y2) = points[-2], points[-1]
    dx, dy = x2 - x1, y2 - y1
    length = max((dx * dx + dy * dy) ** 0.5, 1)
    ux, uy = dx / length, dy / length
    px, py = -uy, ux
    draw.polygon([
        (x2, y2),
        (x2 - ux * 20 + px * 10, y2 - uy * 20 + py * 10),
        (x2 - ux * 20 - px * 10, y2 - uy * 20 - py * 10),
    ], fill=color)


def _label(draw, x, y, text, color="#3F5C7A", size=17):
    draw.text((x, y), text, font=_font(size, True), fill=color, anchor="mm")


def build_architecture() -> Path:
    path = FIG_DIR / "fig_architecture.png"
    W, H = 1400, 760
    img = PILImage.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)

    d.text((50, 22), "DocEntry-AI  \u00b7  system architecture", font=_font(26, True), fill="#1B2A41")

    bw, bh = 300, 175
    xs = [50, 383, 716, 1049]
    row1, row2 = 100, 480

    def box(col, y, title, sub, fill, border, text_color="#FFFFFF"):
        _box(d, xs[col], y, bw, bh, title, sub, fill, border, text_color)

    box(0, row1, "1 \u00b7 Input", "PDF \u00b7 image \u00b7 DOCX\nTXT \u00b7 CSV \u00b7 pasted text", "#EEF1F4", "#1B2A41", "#22272B")
    box(1, row1, "2 \u00b7 documents.py", "file  \u2192  text\nor page images", "#1B2A41", "#1B2A41")
    box(2, row1, "3 \u00b7 extractor.py", "prompt \u00b7 model call\nJSON parsing", "#1B2A41", "#1B2A41")
    box(3, row1, "4 \u00b7 Gemini API", "gemini-3.1-flash-lite\nfree tier", "#3F5C7A", "#3F5C7A")

    box(0, row2, "schemas.py", "field definitions\nper document type", "#EEF1F4", "#1B2A41", "#22272B")
    box(1, row2, "5 \u00b7 app.py", "UI \u00b7 editable\nreview grid", "#1B2A41", "#1B2A41")
    box(2, row2, "6 \u00b7 excel_writer.py", "openpyxl\ncreate / append", "#33383D", "#33383D")
    box(3, row2, "7 \u00b7 Excel .xlsx", "one row per item\n+ audit columns", "#33383D", "#33383D")

    mid1 = row1 + bh // 2
    mid2 = row2 + bh // 2
    for i in range(3):
        _arrow(d, [(xs[i] + bw, mid1), (xs[i + 1] - 5, mid1)])
        _arrow(d, [(xs[i] + bw, mid2), (xs[i + 1] - 5, mid2)])

    _arrow(d, [(xs[3] + bw // 2, row1 + bh), (xs[3] + bw // 2, 405),
               (xs[1] + bw // 2, 405), (xs[1] + bw // 2, row2 - 6)])
    _label(d, 1030, 388, "JSON reply")

    _arrow(d, [(xs[0] + bw // 2, row2 - 6), (xs[0] + bw // 2, 330),
               (xs[2] + bw // 2, 330), (xs[2] + bw // 2, row1 + bh + 6)], color="#8A9299")
    _label(d, 560, 314, "field keys used in the prompt", "#5C6369")

    img.save(path)
    return path


def build_workflow() -> Path:
    path = FIG_DIR / "fig_workflow.png"
    W, H = 1400, 860
    img = PILImage.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    d.text((50, 20), "How one document becomes a register row", font=_font(26, True), fill="#1B2A41")

    bw, bh = 420, 130
    xs = [60, 760]
    ys = [90, 290, 490, 690]
    steps = [
        ("Upload or paste", "PDF, image, DOCX, TXT, CSV\nor pasted text"),
        ("Read the file", "documents.py: text or\npage images"),
        ("Pick type and columns", "schemas.py supplies the\nfield keys"),
        ("Send the prompt", "type + columns + content\n\u2192 Gemini"),
        ("Parse the reply", "JSON records, one per\nline item"),
        ("Review the rows", "editable grid, low\nconfidence flagged"),
        ("Build the workbook", "excel_writer.py creates\nor appends"),
        ("Download", ".xlsx register with\nsource and timestamp"),
    ]
    for i, (title, sub) in enumerate(steps):
        col = i % 2
        row = i // 2
        fill = "#EEF1F4" if i not in (3, 4) else "#1B2A41"
        color = "#22272B" if i not in (3, 4) else "#FFFFFF"
        _box(d, xs[col], ys[row], bw, bh, title, sub, fill, "#1B2A41", color)

    # arrows down the first column, across, up the second
    for r in range(3):
        _arrow(d, [(xs[0] + bw // 2, ys[r] + bh), (xs[0] + bw // 2, ys[r + 1] - 5)])
    _arrow(d, [(xs[0] + bw, ys[3] + bh // 2), (xs[1] - 5, ys[3] + bh // 2)])
    for r in (3, 2, 1):
        _arrow(d, [(xs[1] + bw // 2, ys[r] - 5), (xs[1] + bw // 2, ys[r - 1] + bh + 5)])
    # final arrow to the download box (right of the last read box)
    _arrow(d, [(xs[1], ys[0] + bh // 2), (xs[1] - 5, ys[0] + bh // 2)])

    img.save(path)
    return path


def build_deployment() -> Path:
    path = FIG_DIR / "fig_deployment.png"
    W, H = 1300, 560
    img = PILImage.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    d.text((50, 22), "Deployment view", font=_font(26, True), fill="#1B2A41")

    _box(d, 50, 120, 320, 150, "User browser", "Streamlit session\nlocalhost:8501 or cloud URL", "#EEF1F4", "#1B2A41", "#22272B")
    _box(d, 470, 120, 360, 150, "Streamlit app", "app.py and four modules\nrunning on Community Cloud", "#1B2A41", "#1B2A41")
    _box(d, 930, 120, 320, 150, "Gemini API", "generativelanguage\n.googleapis.com", "#3F5C7A", "#3F5C7A")
    _box(d, 470, 370, 360, 120, "GitHub repository", "public source, no keys\nstored in the code", "#33383D", "#33383D")

    _arrow(d, [(370, 195), (465, 195)])
    _arrow(d, [(830, 195), (925, 195)])
    _label(d, 640, 168, "HTTPS")
    _arrow(d, [(650, 430), (650, 275)], color="#8A9299")
    _label(d, 700, 355, "auto deploy on push", "#5C6369")

    img.save(path)
    return path


def build_dataflow() -> Path:
    path = FIG_DIR / "fig_dataflow.png"
    W, H = 1300, 620
    img = PILImage.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    d.text((50, 22), "Data passed between modules", font=_font(26, True), fill="#1B2A41")

    _box(d, 40, 110, 270, 150, "Uploaded file", "bytes + filename", "#EEF1F4", "#1B2A41", "#22272B")
    _box(d, 380, 110, 300, 150, "Document object", "kind, text,\nimages, note", "#1B2A41", "#1B2A41")
    _box(d, 750, 110, 250, 150, "Prompt", "schema keys +\ndocument content", "#1B2A41", "#1B2A41")
    _box(d, 1070, 110, 200, 150, "JSON", "records[]", "#3F5C7A", "#3F5C7A")

    _box(d, 380, 400, 300, 150, "List of dicts", "one dict per\nline item", "#33383D", "#33383D")
    _box(d, 750, 400, 250, 150, "DataFrame", "editable review\ngrid", "#33383D", "#33383D")
    _box(d, 1070, 400, 200, 150, "Workbook", "openpyxl\n.xlsx", "#4F7196", "#4F7196")

    _arrow(d, [(310, 185), (375, 185)])
    _arrow(d, [(680, 185), (745, 185)])
    _arrow(d, [(1000, 185), (1065, 185)])
    _arrow(d, [(1170, 260), (1170, 340), (530, 340), (530, 395)])
    _arrow(d, [(680, 475), (745, 475)])
    _arrow(d, [(1000, 475), (1065, 475)])

    img.save(path)
    return path


def build_wireframe() -> Path:
    path = FIG_DIR / "fig_wireframe.png"
    W, H = 1300, 780
    img = PILImage.new("RGB", (W, H), "#23272B")
    d = ImageDraw.Draw(img)

    # sidebar
    d.rectangle([0, 0, 250, H], fill="#1D2125")
    d.rounded_rectangle([30, 40, 62, 72], radius=6, fill="#21364F")
    d.text((46, 56), "DE", font=_font(15, True), fill="#F5F7F8", anchor="mm")
    d.text((80, 50), "DocEntry-AI", font=_font(18, True), fill="#E3E6E8", anchor="lm")
    d.text((30, 96), "DOCUMENT TYPE", font=_font(12, True), fill="#98A1A8")
    d.rounded_rectangle([28, 118, 222, 156], radius=5, fill="#2B3035", outline="#3B4147")
    d.text((40, 137), "Tax Invoice", font=_font(15), fill="#E3E6E8", anchor="lm")
    d.text((30, 200), "CONNECTION", font=_font(12, True), fill="#98A1A8")
    d.ellipse([32, 226, 42, 236], fill="#2E7D32")
    d.text((50, 231), "Key loaded", font=_font(14, True), fill="#E3E6E8", anchor="lm")
    d.text((32, 252), "Model gemini-3.1-flash-lite", font=_font(13), fill="#A2ABB2")
    d.text((32, 272), "Key AQ.Ab8...3wRg", font=_font(13), fill="#A2ABB2")
    d.rounded_rectangle([28, 310, 222, 348], radius=5, fill="#2F353A", outline="#3B4147")
    d.text((125, 329), "Test connection", font=_font(13, True), fill="#E3E6E8", anchor="mm")
    d.rounded_rectangle([28, 356, 222, 394], radius=5, fill="#2F353A", outline="#3B4147")
    d.text((125, 375), "Reset extraction", font=_font(13, True), fill="#E3E6E8", anchor="mm")

    # masthead + strip
    d.rounded_rectangle([280, 30, 1270, 150], radius=5, fill="#21364F")
    d.text((300, 52), "TRADE DOCUMENTATION", font=_font(12, True), fill="#A6B4C4")
    d.text((300, 76), "Document to Excel register", font=_font(25, True), fill="#F5F7F8")
    d.text((300, 116), "Add the paperwork, choose the columns your register needs, check the",
           font=_font(13), fill="#D2D9E0")
    d.rounded_rectangle([280, 162, 1270, 206], radius=5, fill="#2B3035", outline="#3B4147")
    labels = ["1  Documents", "2  Columns", "3  Extract and review", "4  Download"]
    x = 330
    for i, text in enumerate(labels):
        d.ellipse([x, 174, x + 20, 194], fill="#454C53")
        d.text((x + 10, 184), str(i + 1), font=_font(11, True), fill="#F5F7F8", anchor="mm")
        d.text((x + 30, 184), text, font=_font(13), fill="#E4E6E8", anchor="lm")
        x += 235

    # section + uploader
    d.rounded_rectangle([304, 232, 326, 254], radius=3, fill="#2E3439")
    d.text((315, 243), "1", font=_font(11, True), fill="#B9C8D6", anchor="mm")
    d.text((334, 243), "Documents", font=_font(17, True), fill="#E3E6E8", anchor="lm")

    d.rounded_rectangle([300, 266, 900, 290], radius=4, fill="#2B3035")
    d.text((312, 278), "Upload files", font=_font(12, True), fill="#F5F7F8", anchor="lm")
    d.text((440, 278), "Paste text", font=_font(12), fill="#A2ABB2", anchor="lm")

    d.rounded_rectangle([300, 300, 1250, 400], radius=6, fill="#2B3035", outline="#3B4147", width=2)
    d.text((775, 336), "Drag and drop files here", font=_font(16, True), fill="#E3E6E8", anchor="mm")
    d.text((775, 362), "Limit 200MB per file  \u00b7  PDF, PNG, JPG, DOCX, TXT, CSV", font=_font(12), fill="#A2ABB2", anchor="mm")

    # table
    d.text((334, 436), "Extract and review", font=_font(17, True), fill="#E3E6E8", anchor="lm")
    d.rounded_rectangle([300, 460, 1250, 700], radius=5, fill="#2B3035", outline="#3B4147", width=2)
    d.rectangle([300, 460, 1250, 492], fill="#21364F")
    heads = ["Invoice No.", "Date", "PO No.", "HSN", "Qty", "Rate", "Total"]
    offsets = [315, 460, 570, 720, 820, 910, 1080]
    for text, ox in zip(heads, offsets):
        d.text((ox, 476), text, font=_font(11, True), fill="#F5F7F8", anchor="lm")
    for r in range(4):
        y = 500 + r * 44
        d.line([300, y + 34, 1250, y + 34], fill="#3B4147", width=1)
        for ox in offsets:
            d.text((ox, y + 17), "\u2014", font=_font(11), fill="#8A9299", anchor="lm")

    d.rounded_rectangle([1050, 716, 1250, 758], radius=5, fill="#4F7196")
    d.text((1150, 737), "Download Excel", font=_font(13, True), fill="#F5F7F8", anchor="mm")

    img.save(path)
    return path


def build_sequence() -> Path:
    path = FIG_DIR / "fig_sequence.png"
    W, H = 1400, 900
    img = PILImage.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    d.text((50, 22), "One extraction request, step by step", font=_font(26, True), fill="#1B2A41")

    people = [
        ("User\nbrowser", 190, "#33383D"),
        ("app.py", 540, "#1B2A41"),
        ("documents.py", 890, "#1B2A41"),
        ("extractor.py", 1180, "#3F5C7A"),
    ]
    top, bottom = 120, 810
    for name, x, colour in people:
        _box(d, x - 120, top, 240, 90, name, "", colour, colour)
        for y in range(top + 90, bottom, 18):
            d.line([x, y, x, y + 9], fill="#B9C2C9", width=2)

    messages = [
        (190, 540, "1  upload file / paste text", 260, "#1B2A41"),
        (540, 890, "2  read_document(bytes, filename)", 335, "#1B2A41"),
        (890, 540, "3  Document(text | images, note)", 410, "#5C6369"),
        (540, 1180, "4  extract_records(text, type, fields, images)", 485, "#1B2A41"),
        (1180, 1180, "5  batch 4 pages or 24,000 chars per call", 540, "#3F5C7A"),
        (1180, 540, "6  JSON records + confidence", 620, "#3F5C7A"),
        (540, 890, "7  validate_rows(rows)", 690, "#5C6369"),
        (540, 190, "8  editable grid, then download", 760, "#1B2A41"),
    ]
    for x1, x2, text, y, colour in messages:
        if x1 == x2:
            d.rounded_rectangle([x1 - 300, y - 24, x1 + 300, y + 24], radius=8,
                                fill="#EEF1F4", outline="#B9C2C9")
            d.text((x1, y), text, font=_font(16), fill=colour, anchor="mm")
        else:
            _arrow(d, [(x1, y), (x2, y)], color=colour, width=3)
            d.rectangle([min(x1, x2) + 20, y - 30, max(x1, x2) - 20, y - 6], fill="white")
            d.text(((x1 + x2) / 2, y - 18), text, font=_font(15), fill=colour, anchor="mm")

    d.text((50, 850), "Steps 5 and 6 repeat once per batch; the records are merged before validation.",
           font=_font(15), fill="#5C6369")
    img.save(path)
    return path


def build_gantt() -> Path:
    path = FIG_DIR / "fig_gantt.png"
    W, H = 1400, 700
    img = PILImage.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    d.text((48, 20), "Planned development timeline", font=_font(26, True), fill="#1B2A41")

    left, top = 330, 110
    weeks = 10
    col_w = 92
    row_h = 54
    for w in range(weeks + 1):
        x = left + w * col_w
        d.line([x, top, x, top + 7 * row_h], fill="#DDE2E6", width=1)
        if w < weeks:
            d.text((x + col_w / 2, top - 22), f"W{w + 1}", font=_font(14, True), fill="#5C6369", anchor="mm")

    tasks = [
        ("Document type auto-detection", 0, 2),
        ("Validation rules (GSTIN, totals)", 1, 3),
        ("Batch PDF splitting", 3, 2),
        ("Master register + database", 4, 3),
        ("Low-confidence cell highlighting", 5, 1),
        ("Multi-language and handwriting", 6, 3),
        ("User accounts and audit trail", 7, 3),
    ]
    for i, (name, start, span) in enumerate(tasks):
        y = top + i * row_h
        d.text((48, y + row_h / 2), name, font=_font(15), fill="#33383D", anchor="lm")
        shade = "#1B2A41" if i % 2 == 0 else "#4F7196"
        d.rounded_rectangle(
            [left + start * col_w + 6, y + 12, left + (start + span) * col_w - 6, y + row_h - 12],
            radius=6, fill=shade,
        )

    d.line([left, top + 7 * row_h, left + weeks * col_w, top + 7 * row_h], fill="#B9C2C9", width=2)
    img.save(path)
    return path


def build_all_figures():
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    return {
        "arch": build_architecture(),
        "workflow": build_workflow(),
        "deploy": build_deployment(),
        "dataflow": build_dataflow(),
        "wireframe": build_wireframe(),
        "sequence": build_sequence(),
        "gantt": build_gantt(),
    }
