"""
Front matter for the Word report: cover, certificate, declaration,
acknowledgement, abstract, lists of tables and figures, abbreviations and
contents.

Details that change between students live in the block below. Everything else
is derived from the same content that produces the PDF.
"""

from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt

import docx_common as DC
import report_common as RC

# --------------------------------------------------------------------------
# Cover details - edit these before printing
# --------------------------------------------------------------------------

TITLE = "DocEntry-AI"
SUBTITLE = (
    "AI-Assisted Extraction of Import and Export Trade Documents "
    "into a Structured Excel Register"
)

STUDENT = "Prajwal Shinde"
ROLL = "[Roll number]"
STUDENTS = [(STUDENT, ROLL)]

YEAR_OF_STUDY = "Third Year"
DEGREE = "BACHELOR OF TECHNOLOGY"
DEGREE_LONG = "Bachelor of Technology (Artificial Intelligence and Data Science)"
UNIVERSITY = "Dr. Babasaheb Ambedkar Technological University, Lonere."
COLLEGE_TRUST = "Yashoda Shikshan Prasarak Mandal's"
COLLEGE = "YASHODA TECHNICAL CAMPUS, SATARA"
COLLEGE_SUB = "An Autonomous Institute"
FACULTY = "FACULTY OF ENGINEERING"
FACULTY_LINE = "Faculty of Engineering"
BRANCH = "Artificial Intelligence and Data Science"
DEPARTMENT = "Department of Artificial Intelligence and Data Science Engineering"
ADDRESS = "Wadhe, Satara - 415011"
YEAR = "2026 - 27"

GUIDE = "[Name of guide]"
HOD = "[Name of Head of Department]"
DIRECTOR = "[Name of Director]"


def _centre(doc, text, size=12, bold=False, italic=False, after=6, before=0):
    return DC.para(doc, text, size=size, bold=bold, italic=italic,
                   align=WD_ALIGN_PARAGRAPH.CENTER, after=after, before=before)


def _signature_block(doc, names, roles) -> None:
    table = doc.add_table(rows=2, cols=len(names))
    table.autofit = True
    for i, (name, role) in enumerate(zip(names, roles)):
        DC.cell_text(table.rows[0].cells[i], name, size=11, bold=True,
                     align=WD_ALIGN_PARAGRAPH.CENTER)
        DC.cell_text(table.rows[1].cells[i], role, size=11,
                     align=WD_ALIGN_PARAGRAPH.CENTER)


# --------------------------------------------------------------------------
# Cover
# --------------------------------------------------------------------------

def cover(doc) -> None:
    DC.blank_lines(doc, 1, 18)
    _centre(doc, f"\u201c{TITLE}\u201d", size=18, bold=True, after=14)
    _centre(doc, "A PROJECT PHASE I REPORT", size=14, after=12)
    _centre(doc, "Submitted in partial fulfillment for the award of the degree of",
            size=12, bold=True, italic=True, after=6)
    _centre(doc, DEGREE, size=16, bold=True, after=14)
    _centre(doc, "Submitted to", size=13, bold=True, italic=True, after=8)
    _centre(doc, UNIVERSITY, size=16, bold=True, italic=True, after=14)
    _centre(doc, "Submitted By", size=13, bold=True, italic=True, after=10)

    for index, (name, roll) in enumerate(STUDENTS, start=1):
        _centre(doc, f"{index})  {name}  ({roll})", size=13, after=6)

    _centre(doc, "of", size=13, after=4)
    _centre(doc, YEAR_OF_STUDY, size=13, after=14)
    _centre(doc, "Under the Guidance of", size=13, after=6)
    _centre(doc, GUIDE, size=13, bold=True, after=18)
    _centre(doc, DEPARTMENT, size=12.5, bold=True, after=4)
    _centre(doc, COLLEGE_TRUST, size=12, after=4)
    _centre(doc, COLLEGE, size=14, bold=True, after=2)
    _centre(doc, COLLEGE_SUB, size=12, after=2)
    _centre(doc, FACULTY_LINE, size=12, after=2)
    _centre(doc, ADDRESS, size=12, after=10)
    _centre(doc, YEAR, size=13, bold=True)


# --------------------------------------------------------------------------
# Certificate and declaration
# --------------------------------------------------------------------------

def _college_head(doc) -> None:
    _centre(doc, COLLEGE_TRUST, size=12, after=2)
    _centre(doc, COLLEGE, size=16, bold=True, after=2)
    _centre(doc, COLLEGE_SUB, size=13, bold=True, after=2)
    _centre(doc, FACULTY, size=13, bold=True, after=2)
    _centre(doc, DEPARTMENT, size=13, bold=True, after=10)


def certificate(doc, first: bool = False) -> None:
    p = DC.para(doc, page_break=not first)
    _college_head(doc)
    _centre(doc, "CERTIFICATE", size=16, bold=True, before=12, after=14)

    names = " and ".join(name for name, _ in STUDENTS)
    who = "the candidate" if len(STUDENTS) == 1 else "them"
    body = (
        f"This is to certify that the Project Report entitled \u201c{TITLE}\u201d "
        f"submitted by {names} of {YEAR_OF_STUDY} is a record of the bonafide work "
        f"carried out by {who} under my guidance, and it is approved for the partial "
        f"fulfillment of the requirement of DBATU, Lonere, for the award of the degree "
        f"{DEGREE_LONG} for Academic Year {YEAR}."
    )
    DC.para(doc, body, size=12, after=10, spacing=1.5)
    DC.para(doc, "", after=6)
    DC.para(doc, "The work has been examined and is found satisfactory in scope and "
                 "quality for the award of the degree.", size=12, after=24)
    DC.blank_lines(doc, 3)

    _signature_block(doc, [GUIDE, HOD, DIRECTOR],
                     ["Guide", "Head of Department", "Director"])
    DC.para(doc, "", after=18)
    _centre(doc, "(External Examiner)", size=11, after=24)
    DC.para(doc, "Place: Satara", size=11, after=2)
    DC.para(doc, "Date:", size=11)


def declaration(doc) -> None:
    DC.para(doc, page_break=True)
    _centre(doc, "DECLARATION BY STUDENT(S)", size=14, bold=True, after=14)
    names = ", ".join(name for name, _ in STUDENTS)
    DC.para(doc, (
        "This is to declare that this report has been written by us. No part of the "
        "report is plagiarized from other sources. All information included from other "
        "sources has been duly acknowledged. We aver that if any part of the report is "
        "found to be plagiarized, we shall take full responsibility for it."
    ), size=12, after=16)
    DC.para(doc, "Signature of Students", size=12, bold=True, after=10)
    for index, (name, _) in enumerate(STUDENTS, start=1):
        DC.para(doc, f"{index}.  {name}   ______________________________", size=12, after=8)
    DC.blank_lines(doc, 2)
    DC.para(doc, "Place: Satara", size=12, after=2)
    DC.para(doc, "Date:", size=12)


# --------------------------------------------------------------------------
# Acknowledgement and abstract
# --------------------------------------------------------------------------

def acknowledgement(doc, first: bool = False) -> None:
    DC.para(doc, page_break=not first)
    _centre(doc, "ACKNOWLEDGEMENT", size=14, bold=True, after=14)

    DC.para(doc, (
        f"We would like to express our sincere gratitude to everyone who supported and "
        f"guided us throughout the development of our project, \u201c{TITLE}\u201d."
    ), size=12, after=8)
    DC.para(doc, (
        f"First and foremost, we thank our project guide, {GUIDE}, for the guidance, "
        "continuous encouragement and constructive suggestions at every stage. The "
        "comments on scope, testing and the difference between a demonstration and a "
        "tool changed the direction of the work more than once."
    ), size=12, after=8)
    DC.para(doc, (
        f"We are grateful to {HOD}, Head of the {DEPARTMENT}, for providing the "
        "laboratory facilities, academic support and the freedom to choose a problem "
        "outside the usual syllabus."
    ), size=12, after=8)
    DC.para(doc, (
        f"We also thank {DIRECTOR}, Director of {COLLEGE.title()}, for the institutional "
        "support that made the project possible."
    ), size=12, after=8)
    DC.para(doc, (
        "We extend our gratitude to all the faculty members of the department for their "
        "suggestions and technical assistance, and to our classmates who supplied sample "
        "invoices, shipping bills and delivery challans, including the badly photographed "
        "ones. The scans with a shadow across the total were the most useful test material "
        "of all."
    ), size=12, after=8)
    DC.para(doc, (
        "We thank the maintainers of PyMuPDF, python-docx, openpyxl, ReportLab and "
        "Streamlit, whose documentation answered most of the questions that came up "
        "during implementation, and our friends and families for their patience while "
        "the work was being finished."
    ), size=12, after=20)

    _centre(doc, ", ".join(name for name, _ in STUDENTS), size=12, bold=True, after=10)
    DC.para(doc, "Place: Satara", size=11, after=2)
    DC.para(doc, "Date:", size=11)


def abstract(doc) -> None:
    DC.para(doc, page_break=True)
    _centre(doc, "ABSTRACT", size=14, bold=True, after=12)
    for flowable in _walk(_abstract_flowables()):
        if type(flowable).__name__ != "Paragraph":
            continue
        if getattr(flowable, "_kind", "") == "front":
            continue  # the heading is printed above
        DC.para(doc, flowable.getPlainText(), size=12, after=5, spacing=1.3)


def _abstract_flowables():
    import report_front

    return report_front.abstract()


def _walk(items):
    for item in items:
        if isinstance(item, list):
            yield from _walk(item)
        elif type(item).__name__ == "KeepTogether":
            yield from _walk(item._content)
        else:
            yield item


# --------------------------------------------------------------------------
# Lists and contents
# --------------------------------------------------------------------------

def _front_list(doc, title: str, headers: list[str], rows: list[tuple]) -> None:
    DC.para(doc, page_break=True)
    _centre(doc, title, size=14, bold=True, after=14)

    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = 1
    DC.table_borders(table)
    DC.repeat_header(table.rows[0])
    for i, head in enumerate(headers):
        DC.cell_text(table.rows[0].cells[i], head, size=10.5, bold=True,
                     align=WD_ALIGN_PARAGRAPH.CENTER)
        DC.cell_shade(table.rows[0].cells[i], "EEF1F4")

    for values in rows:
        cells = table.add_row().cells
        for i, value in enumerate(values):
            align = WD_ALIGN_PARAGRAPH.CENTER if i != 1 else WD_ALIGN_PARAGRAPH.LEFT
            DC.cell_text(cells[i], str(value), size=10.5, align=align)

    widths = [1.1, 4.75, 1.0]
    DC.table_widths(table, widths)


def list_of_tables(doc, pagemap: dict) -> None:
    rows = [
        (f"Table {key}", caption, pagemap.get(f"Table {key}", "\u2013"))
        for key, caption in RC.TABLES.items()
    ]
    _front_list(doc, "LIST OF TABLES", ["Table No.", "Title", "Page No."], rows)


def list_of_figures(doc, pagemap: dict) -> None:
    rows = [
        (f"Figure {key}", caption, pagemap.get(f"Figure {key}", "\u2013"))
        for key, caption in RC.FIGURES.items()
    ]
    _front_list(doc, "LIST OF FIGURES", ["Figure No.", "Title", "Page No."], rows)


def abbreviations(doc) -> None:
    import report_front

    DC.para(doc, page_break=True)
    _centre(doc, "ABBREVIATIONS", size=14, bold=True, after=14)

    table = doc.add_table(rows=0, cols=2)
    table.autofit = False
    for short, long in report_front.ABBREVIATIONS:
        cells = table.add_row().cells
        DC.cell_text(cells[0], short, size=11, bold=True)
        DC.cell_text(cells[1], long, size=11)
    DC.table_widths(table, [1.3, 5.55])


def contents(doc, pagemap: dict) -> None:
    DC.para(doc, page_break=True)
    _centre(doc, "CONTENTS", size=14, bold=True, after=14)

    table = doc.add_table(rows=1, cols=3)
    DC.table_borders(table)
    DC.repeat_header(table.rows[0])
    headers = ["Chapter", "Contents", "Page No."]
    for i, head in enumerate(headers):
        DC.cell_text(table.rows[0].cells[i], head, size=10.5, bold=True,
                     align=WD_ALIGN_PARAGRAPH.CENTER)
        DC.cell_shade(table.rows[0].cells[i], "EEF1F4")

    for label, level, kind in RC.OUTLINE:
        if kind == "front":
            number, title = "", label
        else:
            parts = label.split("  ", 1)
            number, title = parts[0], parts[1] if len(parts) > 1 else ""

        cells = table.add_row().cells
        DC.cell_text(cells[0], number, size=10.5, bold=(level == 0),
                     align=WD_ALIGN_PARAGRAPH.CENTER)
        cell_text = title if level == 0 else "      " + title
        DC.cell_text(cells[1], cell_text, size=10.5, bold=(level == 0))
        DC.cell_text(cells[2], str(pagemap.get(label, "\u2013")), size=10.5,
                     align=WD_ALIGN_PARAGRAPH.CENTER)

    DC.table_widths(table, [0.9, 5.15, 0.8])
