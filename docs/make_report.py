"""
Build the full DocEntry-AI project report.

    python docs/make_report.py

The report is laid out twice. The first pass records where every heading, table
and figure actually landed; the second pass writes those page numbers into the
contents and the lists of tables and figures. Nothing is estimated by hand.

Writes:
    docs/Project-Report.pdf
    docs/figures/*.png
"""

from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

import pymupdf  # noqa: E402

import report_common as RC  # noqa: E402
import report_front as FRONT  # noqa: E402
import report_body_a as A  # noqa: E402
import report_body_b as B  # noqa: E402

OUT = HERE / "Project-Report.pdf"
TMP = HERE / "_pass.pdf"


def story(pagemap: dict, fig: dict) -> list:
    s = []
    s += FRONT.cover()
    s += FRONT.contents(pagemap)
    s += FRONT.acknowledgement()
    s += FRONT.abstract()
    s += FRONT.list_of_tables(pagemap)
    s += FRONT.list_of_figures(pagemap)
    s += FRONT.abbreviations()

    s += A.chapter1(fig)
    s += A.chapter2()
    s += A.chapter3(fig)
    s += A.chapter4()
    s += A.chapter5(fig)
    s += B.chapter6()
    s += B.chapter7()
    s += B.chapter8()
    s += B.chapter9()
    s += B.chapter10(fig)
    s += B.chapter11()
    s += B.chapter12()
    s += B.appendix_a()
    s.append(RC.new_page())
    s += B.appendix_b()
    s.append(RC.new_page())
    s += B.appendix_c()
    s.append(RC.new_page())
    s += B.appendix_d()
    return s


def build(path: Path, pagemap: dict, fig: dict,
          front_pages=None, roman_start=None) -> RC.ReportDoc:
    doc = RC.make_doc(path, front_pages=front_pages, roman_start=roman_start)
    doc.build(story(pagemap, fig))
    return doc


def collect(doc: RC.ReportDoc, roman_start: int, front_pages: int) -> dict:
    def label(page: int) -> str:
        if roman_start and page < roman_start:
            return "\u2013"
        if page <= front_pages:
            start = roman_start or 2
            return RC.roman(page - start + 1)
        return str(page - front_pages)

    pages = {}
    for name, page in doc.toc_pages.items():
        pages[name] = label(page)
    for key, page in doc.table_pages.items():
        pages[f"Table {key}"] = label(page)
    for key, page in doc.figure_pages.items():
        pages[f"Figure {key}"] = label(page)
    return pages


def main() -> None:
    fig = RC.build_all_figures()

    pagemap: dict = {}
    front_pages = None
    roman_start = None
    doc = None

    for attempt in range(1, 5):
        doc = build(TMP, pagemap, fig, front_pages, roman_start)
        body_start = doc.toc_pages["1  Introduction"]
        ack_start = doc.toc_pages["Acknowledgement"]
        front_pages = body_start - 1
        roman_start = ack_start
        newmap = collect(doc, roman_start, front_pages)
        same = (newmap == pagemap
                and doc.front_pages == front_pages
                and doc.roman_start == roman_start)
        print(f"pass {attempt}: {doc.page} pages, body starts at {body_start}, "
              f"front {front_pages}, stable={same}")
        if same:
            break
        pagemap = newmap

    TMP.replace(OUT)

    missing_tables = [k for k in RC.TABLES if f"Table {k}" not in pagemap]
    missing_figures = [k for k in RC.FIGURES if f"Figure {k}" not in pagemap]
    if missing_tables:
        print("MISSING TABLES:", missing_tables)
    if missing_figures:
        print("MISSING FIGURES:", missing_figures)

    with pymupdf.open(OUT) as pdf:
        pages = pdf.page_count
    print(f"written: {OUT} ({pages} pages)")
    if not 40 <= pages <= 50:
        print(f"NOTE: {pages} pages is outside the requested 40-50 range.")

    print("\nContents page numbers:")
    for label, level, kind in RC.OUTLINE:
        print(f"  {pagemap.get(label, '?'):>4}  {label}")


if __name__ == "__main__":
    main()
