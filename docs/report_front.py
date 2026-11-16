"""
Front matter for the DocEntry-AI report: cover, contents, acknowledgement,
abstract, lists of tables and figures, abbreviations.

Page numbers come from the two-pass build in make_report.py, so the contents
and the lists always match the body.
"""

from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import PageBreak, Spacer, Table, TableStyle

import report_common as RC

# --------------------------------------------------------------------------
# Cover details - edit these before printing
# --------------------------------------------------------------------------
STUDENT = "Prajwal Shinde"
ROLL = "[Roll number]"
COLLEGE = "[Name of college]"
DEPARTMENT = "Department of Computer Science"
GUIDE = "[Name of guide]"
YEAR = "2026\u201327"
TITLE = "DocEntry-AI"
SUBTITLE = (
    "AI-Assisted Extraction of Import and Export Trade Documents "
    "into a Structured Excel Register"
)


def _cover_line(label: str, value: str) -> Table:
    row = Table(
        [[
            RC.P(f'<font color="#8A9299" size="9">{RC.esc(label.upper())}</font>', "cell"),
            RC.P(f'<b>{RC.esc(value)}</b>', "cell"),
        ]],
        colWidths=[3.4 * cm, 9.6 * cm],
    )
    row.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return row


def cover() -> list:
    story = [
        Spacer(1, 1.1 * cm),
        RC.P(
            f'<font color="#8A9299" size="9.5">{RC.esc(COLLEGE.upper())}</font>'
            f'<br/><font color="#5C6369" size="9">{RC.esc(DEPARTMENT)}</font>',
            "cell",
        ),
        Spacer(1, 2.6 * cm),
        RC.P(
            '<font color="#4F7196" size="10.5"><b>A PROJECT REPORT</b></font>',
            "cell",
        ),
        Spacer(1, 0.35 * cm),
        RC.P(
            f'<font color="#1B2A41" size="34"><b>{RC.esc(TITLE)}</b></font>',
            "cell",
        ),
        Spacer(1, 0.25 * cm),
        RC.P(
            f'<font color="#33383D" size="14.5">{RC.esc(SUBTITLE)}</font>',
            "cell",
        ),
        Spacer(1, 0.55 * cm),
    ]

    rule = Table([[""]], colWidths=[RC.CONTENT_W], rowHeights=[3])
    rule.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), RC.NAVY)]))
    story += [rule, Spacer(1, 0.5 * cm)]

    story.append(RC.P(
        "Submitted in partial fulfilment of the requirements for the award of the "
        "degree of [Programme name]",
        "note",
    ))
    story.append(Spacer(1, 1.5 * cm))

    details = [
        _cover_line("Submitted by", STUDENT),
        _cover_line("Roll number", ROLL),
        _cover_line("Guide", GUIDE),
        _cover_line("Academic year", YEAR),
    ]
    box = Table([[d] for d in details], colWidths=[13.0 * cm])
    box.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ]))
    story.append(box)
    story.append(Spacer(1, 2.2 * cm))
    story.append(RC.P(
        '<font color="#5C6369" size="9">A working application, source code and this '
        'report were prepared together. The application runs locally and on '
        'Streamlit Community Cloud.</font>',
        "cell",
    ))
    story.append(PageBreak())
    return story


def contents(pagemap: dict) -> list:
    rows = [[
        RC.P('<font color="#FFFFFF" size="9"><b>Chapter / Section</b></font>', "cell"),
        RC.P('<font color="#FFFFFF" size="9"><b>Page No.</b></font>', "cell_head"),
    ]]
    for label, level, kind in RC.OUTLINE:
        page = pagemap.get(label, "\u2013")
        if level == 0:
            style = "toc_chapter"
            text = RC.esc(label)
            page_style = "toc_page_bold"
        else:
            style = "toc"
            text = "&nbsp;&nbsp;&nbsp;&nbsp;" + RC.esc(label)
            page_style = "toc_page"
        rows.append([RC.P(text, style), RC.P(str(page), page_style)])

    table = Table(rows, colWidths=[RC.CONTENT_W - 2.6 * cm, 2.6 * cm], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), RC.NAVY),
        ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 1.6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.6),
        ("LINEBELOW", (0, 0), (-1, 0), 0.6, RC.NAVY),
    ]))
    return [*RC.front_title("Contents"), Spacer(1, 0.2 * cm), table, PageBreak()]


def acknowledgement() -> list:
    story = [*RC.front_title("Acknowledgement")]
    story.append(RC.body(
        "The work described in this report began as a small question: why does a clerk "
        "copy the same invoice number, GSTIN and total from a PDF into a spreadsheet "
        "when both files already contain the information? Answering that question "
        "properly took more time than writing the first version of the program. I am "
        "grateful to the people who made that time possible."
    ))
    story.append(RC.body(
        f"I thank my project guide, {GUIDE}, for insisting that every claim in this "
        "report be demonstrated by the application rather than described in the "
        "future tense. The comments on scope, testing and the difference between a "
        "demo and a tool changed the direction of the project more than once."
    ))
    story.append(RC.body(
        f"I thank the faculty of the {DEPARTMENT} at {COLLEGE} for the review "
        "meetings and for pointing out that a register is only useful if a human can "
        "correct it. I also thank the maintainers of PyMuPDF, python-docx, openpyxl, "
        "ReportLab and Streamlit, whose documentation answered most of the questions "
        "that came up during implementation."
    ))
    story.append(RC.body(
        "Finally, I thank my classmates who supplied sample invoices, shipping bills "
        "and delivery challans, including the badly photographed ones. The scans with "
        "a shadow across the total were the most useful test material of all."
    ))
    story.append(Spacer(1, 1.2 * cm))
    story.append(RC.P(f"<b>{RC.esc(STUDENT)}</b>", "body"))
    story.append(RC.P("Place: ____________________", "note"))
    story.append(RC.P("Date: _____________________", "note"))
    story.append(PageBreak())
    return story


def abstract() -> list:
    story = [*RC.front_title("Abstract")]
    story.append(RC.body(
        "Import and export businesses exchange a small set of documents many times: "
        "tax invoices, shipping bills, purchase orders, bills of entry and delivery "
        "challans. Each document carries the same facts in a different layout, and "
        "each consignment produces several line items. Staff read the documents and "
        "type the values into a register, usually an Excel workbook, for accounts, "
        "customs follow-up and reconciliation. The work is repetitive, it slows down "
        "when a consignment has many items, and transcription errors are difficult to "
        "find once the workbook has been shared."
    ))
    story.append(RC.body(
        "DocEntry-AI is a web application that reads these documents and produces the "
        "register directly. A user uploads one or more files, or pastes text, selects "
        "a document type and the columns the register needs, and reviews the extracted "
        "rows in an editable table before downloading an .xlsx workbook or a CSV or "
        "JSON file. The application accepts digital PDFs, scanned PDFs, photographs, "
        "Word files, plain text and CSV. Digital documents are read as text with "
        "PyMuPDF, DOCX files through python-docx, CSV through the standard library, "
        "and scans or photographs are sent as page images. Text and images are passed "
        "to a large language model through an OpenAI-compatible API, using a JSON "
        "schema derived from the selected columns. The reply is parsed into one record "
        "per line item, with a confidence value per field."
    ))
    story.append(RC.body(
        "The implementation is deliberately small and inspectable. Five modules hold "
        "the file readers, the extraction prompt and API call, the field definitions, "
        "the validation rules and the workbook writer; a sixth module stores recent "
        "runs, column presets and user-defined document types in a local SQLite file. "
        "Validation checks GSTIN checksums, HSN formats, dates, arithmetic totals and "
        "duplicate invoice numbers against an uploaded master register. Flagged cells "
        "are highlighted in the workbook and listed on a separate Checks sheet, so the "
        "export never hides a doubtful value. In testing on sample invoices, shipping "
        "bills and challans the application produced the expected line-item count and "
        "corrected values after a single edit in the review grid, reducing a "
        "twenty-minute manual entry task to under two minutes for a three-item invoice."
    ))
    story.append(RC.body(
        "The report describes the problem, the alternatives, the design, the "
        "implementation and the limits of the approach. It also records where the "
        "application is not reliable: handwriting, poor scans, unusual layouts and "
        "documents in scripts other than English still need a person. The conclusion "
        "is not that extraction can be fully automatic, but that the mechanical part "
        "can be removed while the judgement stays with the user."
    ))
    story.append(Spacer(1, 0.3 * cm))
    story.append(RC.P(
        "<b>Keywords:</b> document data extraction, large language models, import and "
        "export documentation, GST invoice, shipping bill, Streamlit, Excel automation.",
        "note",
    ))
    story.append(PageBreak())
    return story


def _list_page(title: str, registry: dict, kind_word: str, pagemap: dict) -> list:
    rows = [[
        RC.P(f'<font color="#FFFFFF" size="9"><b>{kind_word}</b></font>', "cell_head"),
        RC.P('<font color="#FFFFFF" size="9"><b>Title</b></font>', "cell_head"),
        RC.P('<font color="#FFFFFF" size="9"><b>Page</b></font>', "cell_head"),
    ]]
    for key, caption in registry.items():
        label = f"{kind_word} {key}"
        rows.append([
            RC.P(label, "toc"),
            RC.P(RC.esc(caption), "toc"),
            RC.P(str(pagemap.get(label, "\u2013")), "toc_page"),
        ])
    table = Table(
        rows,
        colWidths=[2.3 * cm, RC.CONTENT_W - 4.9 * cm, 2.0 * cm],
        repeatRows=1,
    )
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), RC.NAVY),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, RC.LIGHT]),
    ]))
    return [*RC.front_title(title), table, PageBreak()]


def list_of_tables(pagemap: dict) -> list:
    return _list_page("List of Tables", RC.TABLES, "Table", pagemap)


def list_of_figures(pagemap: dict) -> list:
    return _list_page("List of Figures", RC.FIGURES, "Figure", pagemap)


ABBREVIATIONS = [
    ("AI", "Artificial Intelligence"),
    ("API", "Application Programming Interface"),
    ("BE", "Bill of Entry"),
    ("CGST", "Central Goods and Services Tax"),
    ("CSV", "Comma-Separated Values"),
    ("DOCX", "Microsoft Word document format"),
    ("FOB", "Free On Board"),
    ("GSTIN", "Goods and Services Tax Identification Number"),
    ("HSN", "Harmonised System of Nomenclature"),
    ("IEC", "Importer-Exporter Code"),
    ("IGST", "Integrated Goods and Services Tax"),
    ("JSON", "JavaScript Object Notation"),
    ("LLM", "Large Language Model"),
    ("OCR", "Optical Character Recognition"),
    ("PDF", "Portable Document Format"),
    ("PO", "Purchase Order"),
    ("SGST", "State Goods and Services Tax"),
    ("SQLite", "Embedded relational database engine"),
    ("TOML", "Tom's Obvious Minimal Language (configuration format)"),
    ("UI", "User Interface"),
    ("URL", "Uniform Resource Locator"),
    ("XLSX", "Microsoft Excel workbook format"),
]


def abbreviations() -> list:
    rows = [[
        RC.P('<font color="#FFFFFF" size="9"><b>Abbreviation</b></font>', "cell_head"),
        RC.P('<font color="#FFFFFF" size="9"><b>Expansion</b></font>', "cell_head"),
    ]]
    for short, long in ABBREVIATIONS:
        rows.append([RC.P(f"<b>{RC.esc(short)}</b>", "toc"), RC.P(RC.esc(long), "toc")])
    table = Table(rows, colWidths=[3.6 * cm, RC.CONTENT_W - 3.6 * cm], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), RC.NAVY),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, RC.LIGHT]),
    ]))
    return [*RC.front_title("Abbreviations"), table, PageBreak()]
