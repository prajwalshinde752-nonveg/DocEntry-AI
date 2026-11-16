"""
Shared helpers for the Word version of the report.

The Word file follows the college template in ``Report v3.pdf``: Times New
Roman, Letter paper, a roman-numbered front matter section, and an arabic
body section with the report title in the header and the department and page
number in the footer.
"""

from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

FONT = "Times New Roman"
MONO = "Courier New"

PAGE_W = Inches(8.5)
PAGE_H = Inches(11)
M_LEFT = Inches(0.75)
M_RIGHT = Inches(0.9)
M_TOP = Inches(1.0)
M_BOTTOM = Inches(0.9)
CONTENT_W = 6.85  # inches, used for tab stops and table widths

BLACK = RGBColor(0, 0, 0)
GREY = RGBColor(0x59, 0x59, 0x59)

ROMAN = ("i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x",
         "xi", "xii", "xiii", "xiv", "xv")


# --------------------------------------------------------------------------
# Document and section setup
# --------------------------------------------------------------------------

def configure_document(doc) -> None:
    """Set the base style and the page size/margins of the first section."""
    normal = doc.styles["Normal"]
    normal.font.name = FONT
    normal.font.size = Pt(12)
    normal.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
    normal.paragraph_format.line_spacing = 1.5
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    section = doc.sections[0]
    _page_setup(section)


def _page_setup(section) -> None:
    section.page_width = PAGE_W
    section.page_height = PAGE_H
    section.left_margin = M_LEFT
    section.right_margin = M_RIGHT
    section.top_margin = M_TOP
    section.bottom_margin = M_BOTTOM
    section.header_distance = Inches(0.5)
    section.footer_distance = Inches(0.35)


def new_section(doc):
    section = doc.add_section(WD_SECTION.NEW_PAGE)
    _page_setup(section)
    return section


def set_page_numbering(section, fmt: str | None = None, start: int | None = None) -> None:
    """Set the numbering format and/or the starting number of a section."""
    sect_pr = section._sectPr
    pg = sect_pr.find(qn("w:pgNumType"))
    if pg is None:
        pg = OxmlElement("w:pgNumType")
        sect_pr.append(pg)
    if fmt:
        pg.set(qn("w:fmt"), fmt)
    if start is not None:
        pg.set(qn("w:start"), str(start))


# --------------------------------------------------------------------------
# Runs, paragraphs and fields
# --------------------------------------------------------------------------

def run(paragraph, text: str, size: float = 12, bold: bool = False,
        italic: bool = False, font: str = FONT, color=None):
    r = paragraph.add_run(text)
    r.font.name = font
    r._element.rPr.rFonts.set(qn("w:eastAsia"), font)
    r.font.size = Pt(size)
    r.bold = bold
    r.italic = italic
    if color is not None:
        r.font.color.rgb = color
    return r


def para(doc, text: str = "", size: float = 12, bold: bool = False,
         italic: bool = False, align=None, before: float = 0,
         after: float = 6, spacing: float = 1.5, indent: float = 0,
         hanging: float = 0, keep_next: bool = False,
         page_break: bool = False, font: str = FONT, color=None):
    p = doc.add_paragraph()
    fmt = p.paragraph_format
    fmt.space_before = Pt(before)
    fmt.space_after = Pt(after)
    fmt.line_spacing = spacing
    fmt.alignment = align
    if indent:
        fmt.left_indent = Inches(indent)
    if hanging:
        fmt.first_line_indent = Inches(-hanging)
    if keep_next:
        fmt.keep_with_next = True
    if page_break:
        fmt.page_break_before = True
    if text:
        run(p, text, size=size, bold=bold, italic=italic, font=font, color=color)
    return p


def add_field(paragraph, instruction: str, placeholder: str = "1",
              size: float = 12, font: str = FONT) -> None:
    """Insert a Word field such as PAGE into a paragraph."""
    def _fld(kind):
        el = OxmlElement("w:fldChar")
        el.set(qn("w:fldCharType"), kind)
        return el

    r1 = paragraph.add_run()
    r1._r.append(_fld("begin"))

    r2 = paragraph.add_run()
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = f" {instruction} "
    r2._r.append(instr)

    r3 = paragraph.add_run()
    r3._r.append(_fld("separate"))

    r4 = run(paragraph, placeholder, size=size, font=font)

    r5 = paragraph.add_run()
    r5._r.append(_fld("end"))
    return r4


def tab_right(paragraph) -> None:
    paragraph.paragraph_format.tab_stops.add_tab_stop(
        Inches(CONTENT_W), WD_TAB_ALIGNMENT.RIGHT
    )


# --------------------------------------------------------------------------
# Tables
# --------------------------------------------------------------------------

def _edge(tag: str, size: int = 4, color: str = "000000"):
    el = OxmlElement(f"w:{tag}")
    el.set(qn("w:val"), "single")
    el.set(qn("w:sz"), str(size))
    el.set(qn("w:space"), "0")
    el.set(qn("w:color"), color)
    return el


def table_borders(table, size: int = 4, color: str = "000000") -> None:
    tbl_pr = table._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for tag in ("top", "left", "bottom", "right", "insideH", "insideV"):
        borders.append(_edge(tag, size, color))
    tbl_pr.append(borders)


def cell_shade(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)


def cell_text(cell, text: str, size: float = 9.5, bold: bool = False,
              italic: bool = False, align=WD_ALIGN_PARAGRAPH.LEFT) -> None:
    cell.text = ""
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(1)
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.alignment = align
    run(p, text, size=size, bold=bold, italic=italic)


def repeat_header(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    el = OxmlElement("w:tblHeader")
    el.set(qn("w:val"), "true")
    tr_pr.append(el)


def no_split(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    el = OxmlElement("w:cantSplit")
    el.set(qn("w:val"), "true")
    tr_pr.append(el)


def table_widths(table, widths_in: list[float]) -> None:
    table.autofit = False
    for row in table.rows:
        for cell, width in zip(row.cells, widths_in):
            cell.width = Inches(width)


def blank_lines(doc, count: int, size: float = 12) -> None:
    for _ in range(count):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.0
        p.add_run().font.size = Pt(size)
