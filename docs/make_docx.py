"""
Build the Word version of the report.

    python docs/make_docx.py

The Word file follows the college format of ``~/Downloads/Report v3.pdf``:
a cover, certificate and declaration, roman-numbered front matter, chapter
divider pages, and a header/footer carrying the title, department and page
number. Body content comes from the same modules that build the PDF, so the
two files cannot drift apart.

The contents and the two lists need real page numbers, which only exist after
layout. The document is therefore written once with dashes, converted to PDF
with LibreOffice to read the page numbers, and written again. Body numbering
restarts at 1, so filling the numbers cannot move the body pages.

LibreOffice must include the Writer module. Set ``DOCX_SOFFICE`` to the
``soffice`` executable if it is not on PATH.

Writes:
    docs/Project-Report.docx and ~/Downloads/Report v3.docx
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

import docx  # noqa: E402
import pymupdf  # noqa: E402
from docx.enum.text import WD_ALIGN_PARAGRAPH  # noqa: E402
from docx.shared import Inches, Pt  # noqa: E402

import docx_common as DC  # noqa: E402
import docx_front as FRONT  # noqa: E402
import report_body_a as A  # noqa: E402
import report_body_b as B  # noqa: E402
import report_common as RC  # noqa: E402

OUT = HERE / "Project-Report.docx"
COPY = Path.home() / "Downloads" / "Report v3.docx"


def _soffice() -> str:
    """Locate a LibreOffice build that can read and write Writer documents.

    ``DOCX_SOFFICE`` wins, then the normal PATH entry. Only LibreOffice with
    the Writer module can open DOCX, so a bare core/Impress install is not
    enough.
    """
    candidates = [os.environ.get("DOCX_SOFFICE"), shutil.which("soffice")]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return candidate
    raise RuntimeError(
        "LibreOffice with Writer was not found. Install libreoffice-writer or "
        "set DOCX_SOFFICE to a soffice executable."
    )



# --------------------------------------------------------------------------
# Reading the shared content
# --------------------------------------------------------------------------

def _walk(items):
    for item in items:
        if isinstance(item, list):
            yield from _walk(item)
        elif type(item).__name__ == "KeepTogether":
            yield from _walk(item._content)
        else:
            yield item


def body_flowables(fig):
    return (
        A.chapter1(fig) + A.chapter2() + A.chapter3(fig) + A.chapter4()
        + A.chapter5(fig) + B.chapter6() + B.chapter7() + B.chapter8()
        + B.chapter9() + B.chapter10(fig) + B.chapter11() + B.chapter12()
        + B.appendix_a() + B.appendix_b() + B.appendix_c() + B.appendix_d()
    )


# --------------------------------------------------------------------------
# Renderers for the flowables the report already produces
# --------------------------------------------------------------------------

def _shade_paragraph(p, fill="F2F3F4") -> None:
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn

    p_pr = p._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    p_pr.append(shd)


def _chapter_divider(doc, label: str, page_break: bool = True) -> str:
    parts = label.split("  ", 1)
    number = parts[0]
    title = parts[1] if len(parts) > 1 else ""

    DC.para(doc, page_break=page_break, after=0, spacing=1.0)
    DC.blank_lines(doc, 15, 12)
    DC.para(doc, f"CHAPTER {number}", size=24, align=WD_ALIGN_PARAGRAPH.CENTER,
            after=16, spacing=1.0)
    DC.para(doc, title.upper(), size=22, align=WD_ALIGN_PARAGRAPH.CENTER,
            after=0, spacing=1.0)
    return title


def _chapter_opening(doc, state) -> None:
    """Start the first page after a divider with the chapter title."""
    title = state.get("opening")
    if not title:
        return
    DC.para(doc, title, size=16, bold=True, align=WD_ALIGN_PARAGRAPH.LEFT,
            page_break=True, after=14, keep_next=True, spacing=1.2)
    state["opening"] = None


def _render_paragraph(doc, p, state) -> None:
    style = p.style.name
    text = p.getPlainText()

    if style == "h1":
        label = getattr(p, "_text", text)
        title = _chapter_divider(doc, label, page_break=not state["first"])
        state["first"] = False
        state["opening"] = title
        return

    if style == "h2":
        _chapter_opening(doc, state)
        DC.para(doc, text, size=14, bold=True, align=WD_ALIGN_PARAGRAPH.LEFT,
                before=14, after=8, keep_next=True, spacing=1.2)
        return

    # Any other content starts the chapter's first page, so the title must be
    # written before it.
    _chapter_opening(doc, state)

    if style == "body":
        DC.para(doc, text, size=12, after=8)
        return

    if style == "bullet":
        bullet = getattr(p, "bulletText", None) or "\u2022"
        DC.para(doc, f"{bullet}  {text}", size=12, after=4, indent=0.3,
                hanging=0.3, align=WD_ALIGN_PARAGRAPH.LEFT)
        return

    if style == "caption":
        kind = getattr(p, "_kind", "")
        if kind == "table":
            DC.para(doc, text, size=10.5, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER,
                    after=4, keep_next=True, spacing=1.0)
        else:
            DC.para(doc, text, size=10.5, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER,
                    before=4, after=10, spacing=1.0)
        return

    if style == "code":
        p_doc = doc.add_paragraph()
        fmt = p_doc.paragraph_format
        fmt.space_before = Pt(2)
        fmt.space_after = Pt(8)
        fmt.line_spacing = 1.0
        fmt.left_indent = Inches(0.12)
        fmt.alignment = WD_ALIGN_PARAGRAPH.LEFT
        _shade_paragraph(p_doc)
        DC.run(p_doc, text, size=8, font=DC.MONO)
        return

    if style == "ref":
        DC.para(doc, text, size=11, after=5, indent=0.35, hanging=0.35,
                align=WD_ALIGN_PARAGRAPH.LEFT, spacing=1.15)
        return

    if style == "note":
        DC.para(doc, text, size=10.5, italic=True, after=8,
                align=WD_ALIGN_PARAGRAPH.LEFT, spacing=1.15)
        return

    if style == "front":
        DC.para(doc, text, size=14, bold=True, after=10, page_break=True)
        return

    DC.para(doc, text, size=12, after=6)


def _render_table(doc, table) -> None:
    data = table._cellvalues
    rows = len(data)
    cols = len(data[0])

    # note_box() produces a one-cell table; render it as a shaded callout.
    first = data[0][0]
    if rows == 1 and cols == 1 and hasattr(first, "style") and first.style.name == "note":
        box = doc.add_table(rows=1, cols=1)
        DC.table_borders(box)
        cell = box.rows[0].cells[0]
        DC.cell_shade(cell, "F1F3F5")
        DC.cell_text(cell, first.getPlainText(), size=10.5, italic=True)
        DC.para(doc, "", after=4, spacing=1.0)
        return

    width_pt = sum(getattr(table, "_colWidths", []) or [])
    if not width_pt:
        width_pt = 490.0
    scale = min(1.0, (DC.CONTENT_W * 72) / width_pt)
    widths = [(w * scale) / 72 for w in table._colWidths]

    docx_table = doc.add_table(rows=0, cols=cols)
    docx_table.alignment = 1
    DC.table_borders(docx_table)

    for r, row in enumerate(data):
        cells = docx_table.add_row().cells
        DC.no_split(docx_table.rows[-1])
        for c, cell in enumerate(row):
            style = cell.style.name if hasattr(cell, "style") else "cell"
            text = cell.getPlainText()
            DC.cell_text(
                cells[c],
                text,
                size=9.5,
                bold=style in ("cell_head", "cell_bold"),
                align=WD_ALIGN_PARAGRAPH.LEFT,
            )
            if style == "cell_head":
                DC.cell_shade(cells[c], "E9EDF1")
    DC.repeat_header(docx_table.rows[0])
    DC.table_widths(docx_table, widths)
    DC.para(doc, "", after=4, spacing=1.0)


def _render_image(doc, image) -> None:
    width_pt = image.drawWidth
    width_in = min(6.4, width_pt / 72)
    p = doc.add_paragraph()
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(str(image.filename), width=Inches(width_in))


def render_body(doc, flowables) -> None:
    state = {"first": True, "opening": None}
    for item in _walk(flowables):
        name = type(item).__name__
        if name == "Paragraph":
            _render_paragraph(doc, item, state)
        elif name == "Table":
            _chapter_opening(doc, state)
            _render_table(doc, item)
        elif name == "Image":
            _chapter_opening(doc, state)
            _render_image(doc, item)


# --------------------------------------------------------------------------
# Sections, headers and footers
# --------------------------------------------------------------------------

def _front_header(section) -> None:
    section.header.is_linked_to_previous = False
    p = section.header.paragraphs[0]
    p.style = "Normal"
    p.text = ""
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_after = Pt(0)
    DC.add_field(p, "PAGE", size=10)
    DC.run(p, ".", size=10)


def _body_header_footer(section) -> None:
    section.header.is_linked_to_previous = False
    p = section.header.paragraphs[0]
    p.style = "Normal"
    p.text = ""
    p.paragraph_format.space_after = Pt(0)
    DC.run(p, FRONT.TITLE, size=12, italic=True)

    section.footer.is_linked_to_previous = False
    f = section.footer.paragraphs[0]
    f.style = "Normal"
    f.text = ""
    f.paragraph_format.space_after = Pt(0)
    DC.tab_right(f)
    DC.run(f, FRONT.BRANCH, size=11, italic=True)
    DC.run(f, "\tPage ", size=12)
    DC.add_field(f, "PAGE", size=12)


# --------------------------------------------------------------------------
# Build
# --------------------------------------------------------------------------

def build(path: Path, pagemap: dict, fig) -> None:
    document = docx.Document()
    DC.configure_document(document)

    FRONT.cover(document)

    prelim = DC.new_section(document)
    prelim.header.is_linked_to_previous = False
    prelim.footer.is_linked_to_previous = False
    FRONT.certificate(document, first=True)
    FRONT.declaration(document)

    front = DC.new_section(document)
    DC.set_page_numbering(front, fmt="lowerRoman", start=1)
    _front_header(front)
    FRONT.acknowledgement(document, first=True)
    FRONT.abstract(document)
    FRONT.list_of_tables(document, pagemap)
    FRONT.list_of_figures(document, pagemap)
    FRONT.abbreviations(document)
    FRONT.contents(document, pagemap)

    body = DC.new_section(document)
    DC.set_page_numbering(body, fmt="decimal", start=1)
    _body_header_footer(body)
    render_body(document, body_flowables(fig))

    document.core_properties.title = f"{FRONT.TITLE} - Project Report"
    document.core_properties.author = FRONT.STUDENT
    document.core_properties.subject = FRONT.SUBTITLE
    document.save(str(path))


# --------------------------------------------------------------------------
# Page numbers from the rendered file
# --------------------------------------------------------------------------

def to_pdf(docx_path: Path, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    profile = out_dir / "lo-profile"
    subprocess.run(
        [
            _soffice(), "--headless", "--norestore",
            f"-env:UserInstallation=file://{profile}",
            "--convert-to", "pdf",
            "--outdir", str(out_dir),
            str(docx_path),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=600,
    )
    return out_dir / (docx_path.stem + ".pdf")


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def read_pages(pdf_path: Path) -> list[list[str]]:
    pages = []
    with pymupdf.open(pdf_path) as pdf:
        for page in pdf:
            lines = [_norm(line) for line in page.get_text().splitlines()]
            pages.append([line for line in lines if line])
    return pages


def compute_pagemap(pages: list[list[str]]) -> tuple[dict, int, int]:
    body_start = None
    for i, lines in enumerate(pages):
        if any(line.upper().startswith("CHAPTER 1") for line in lines):
            body_start = i
            break
    if body_start is None:
        raise RuntimeError("Could not find the first chapter page.")

    front_start = None
    for i in range(body_start):
        if any("ACKNOWLEDGEMENT" in line for line in pages[i]):
            front_start = i
            break
    if front_start is None:
        raise RuntimeError("Could not find the acknowledgement page.")

    pagemap: dict = {}

    # Front matter runs in roman numerals from the acknowledgement page.
    front_titles = {
        "Acknowledgement": "ACKNOWLEDGEMENT",
        "Abstract": "ABSTRACT",
        "List of Tables": "LIST OF TABLES",
        "List of Figures": "LIST OF FIGURES",
        "Abbreviations": "ABBREVIATIONS",
    }
    for label, needle in front_titles.items():
        for i in range(front_start, body_start):
            if any(line == needle for line in pages[i]):
                pagemap[label] = DC.ROMAN[i - front_start]
                break

    body_pages = pages[body_start:]

    # Chapters begin on their own divider page.
    for label, level, kind in RC.OUTLINE:
        if kind != "body" or level != 0:
            continue
        number = _norm(label).split(" ", 1)[0]
        needle = f"CHAPTER {number}"
        for index, lines in enumerate(body_pages, start=1):
            if any(line.upper().startswith(needle) for line in lines):
                pagemap[label] = str(index)
                break

    # A section heading sits alone on its line.
    for label, level, kind in RC.OUTLINE:
        if kind != "body" or level == 0:
            continue
        target = _norm(label)
        for index, lines in enumerate(body_pages, start=1):
            if any(line == target for line in lines):
                pagemap[label] = str(index)
                break

    for registry, prefix in ((RC.TABLES, "Table"), (RC.FIGURES, "Figure")):
        for key, caption in registry.items():
            needle = _norm(f"{prefix} {key} ").lower()
            head = _norm(caption)[:24].lower()
            for index, lines in enumerate(body_pages, start=1):
                if any(line.lower().startswith(needle) and head in line.lower()
                       for line in lines):
                    pagemap[f"{prefix} {key}"] = str(index)
                    break

    return pagemap, body_start, front_start


def main() -> None:
    fig = RC.build_all_figures()
    tmp = Path(tempfile.mkdtemp(prefix="docentry-docx-"))
    try:
        first = tmp / "pass1.docx"
        build(first, {}, fig)
        pages = read_pages(to_pdf(first, tmp / "p1"))
        print(f"pass 1: {len(pages)} pages")

        pagemap, body_start, front_start = compute_pagemap(pages)
        missing = [l for l, _, _ in RC.OUTLINE if l not in pagemap]
        missing += [f"Table {k}" for k in RC.TABLES if f"Table {k}" not in pagemap]
        missing += [f"Figure {k}" for k in RC.FIGURES if f"Figure {k}" not in pagemap]
        if missing:
            raise RuntimeError("No page number found for: " + ", ".join(missing))

        build(OUT, pagemap, fig)
        pages2 = read_pages(to_pdf(OUT, tmp / "p2"))
        pagemap2, _, _ = compute_pagemap(pages2)
        if pagemap2 != pagemap:
            changed = [k for k in pagemap if pagemap.get(k) != pagemap2.get(k)]
            print("page numbers moved:", ", ".join(changed))
            build(OUT, pagemap2, fig)
            pages2 = read_pages(to_pdf(OUT, tmp / "p3"))
            pagemap3, _, _ = compute_pagemap(pages2)
            if pagemap3 != pagemap2:
                raise RuntimeError("Page numbers did not settle after three passes.")
            pagemap = pagemap2

        body_pages = len(pages2) - body_start
        print(f"front matter: {body_start} pages before chapter 1, "
              f"body: {body_pages} numbered pages, total: {len(pages2)}")

        COPY.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(OUT, COPY)
        print(f"written: {OUT}")
        print(f"copied:  {COPY}")

        print("\nContents page numbers:")
        for label, level, kind in RC.OUTLINE:
            print(f"  {pagemap.get(label, '?'):>4}  {label}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
