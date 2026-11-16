"""
Body chapters 6 to 13 of the DocEntry-AI report, including the appendices.
"""

from reportlab.platypus import PageBreak, Spacer
from reportlab.lib.units import cm

import report_common as RC
from report_body_a import H1, H2

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from schemas import DOCUMENT_TYPES as RC_DOC_TYPES  # noqa: E402


def chapter6() -> list:
    s = [*H1("6", "Applications of the Project")]
    s.append(RC.body(
        "The application was built for one narrow task, but that task appears in several "
        "places in a trade business. This chapter describes the three settings where it "
        "was tested or observed, and what it changes in each."
    ))

    s.append(H2("6.1", "Import and Export Documentation"))
    s.append(RC.body(
        "The first setting is the documentation desk of an export house. A consignment "
        "produces a commercial invoice, a packing list, a shipping bill and often a "
        "purchase order from the buyer. Each document repeats the invoice number, the "
        "buyer, the goods description, the quantity and the value. Typing them into a "
        "register four times is the definition of wasted effort. With DocEntry-AI, the "
        "documents are uploaded as a batch, each type is extracted into its own section, "
        "and the download produces one workbook with four sheets. The shared values can "
        "be compared across sheets, which exposes a mismatch that separate manual entries "
        "would hide."
    ))
    s.append(RC.body(
        "The batch feature is important here. Uploading one file at a time and "
        "downloading a workbook each time would create a folder of small files, which is "
        "the problem the register was meant to solve. The Manage batch panel keeps the "
        "sections together, shows the row count per section, allows a section to be "
        "removed, and builds one workbook at the end. This mirrors how the paperwork "
        "arrives: a consignment folder, not a single file."
    ))
    s.append(RC.body(
        "The application also accepts a CSV export from accounting software. Many small "
        "businesses generate invoices in Tally or Busy and export the day's sales as a "
        "spreadsheet. DocEntry-AI reads that file as a table and maps it to the same "
        "schema, so the register can combine a digital export with a scanned shipping "
        "bill in one run. This was not in the original plan; it was added after a test "
        "with a real export showed that the delimiter was a semicolon, not a comma."
    ))

    s.append(H2("6.2", "Customs and Compliance Record Preparation"))
    s.append(RC.body(
        "The second setting is preparation for a customs agent or an internal audit. The "
        "customs side works from the shipping bill and the bill of entry, which carry "
        "port codes, IEC numbers, assessable value and duty. The formats are prescribed "
        "by the Indian Customs EDI System [15], but the values are still copied from "
        "PDFs into a follow-up sheet. Extraction into a fixed register makes it possible "
        "to hand the agent a clean sheet with the bill number, date, port pair and value, "
        "rather than a folder of PDFs."
    ))
    s.append(RC.body(
        "Compliance work benefits more from the validation layer than from the "
        "extraction itself. A GSTIN with a mistyped check character is rejected by the "
        "portal, usually after the form has been filled. The validator computes the "
        "checksum before export, so the error is caught while the document is still on "
        "screen. The same applies to HSN length and to invoices whose tax lines do not "
        "add up. The application does not claim to determine compliance; it removes the "
        "arithmetic and transcription mistakes that make a compliant transaction look "
        "wrong."
    ))
    s.append(RC.body(
        "The Checks sheet is designed for this setting. An auditor can filter by level, "
        "see the sheet and row of every issue, and compare it with the source file named "
        "in the audit column. Because the audit columns are ordinary text, they survive "
        "when the workbook is emailed or opened in another program."
    ))

    s.append(H2("6.3", "Reconciliation and Internal Record Keeping"))
    s.append(RC.body(
        "The third setting is month-end reconciliation. Accounts need to match invoices "
        "with purchase orders and payments, and a register with one row per line item is "
        "the natural working file. Appending to an existing master workbook is the "
        "central feature here: the master keeps its formatting, its extra columns and its "
        "earlier rows, while new consignments are added underneath. Duplicate invoice "
        "detection prevents the same document from being entered twice when a colleague "
        "has already processed it."
    ))
    s.extend(RC.table(
        "6.1",
        ["Setting", "Documents", "What the tool replaces", "Main benefit"],
        [
            ["Export documentation desk", "Commercial invoice, packing list, shipping bill, PO",
             "Four manual entries of the same values", "Consistency across sheets"],
            ["Customs follow-up", "Shipping bill, bill of entry",
             "Copying bill numbers and values into a tracker", "Validated identifiers"],
            ["Accounts reconciliation", "Tax invoice, purchase order, delivery challan",
             "Typing invoice lines into a master", "Append without re-keying"],
            ["Small trading office", "Tax invoice, e-way bill, challan",
             "Daily sales register", "One row per item, one workbook"],
            ["Student project archive", "Sample invoices and scans",
             "Manual creation of test data", "Repeatable sample sets"],
            ["Audit preparation", "All of the above plus the master",
             "Chasing missing source references", "Source file and timestamp"],
        ],
        widths=[4.0, 5.0, 4.8, 3.6],
    ))
    s.append(RC.body(
        "Across the three settings the common benefit is not speed alone. It is that the "
        "register becomes a by-product of reading the document, so the person spends "
        "time deciding whether a value is correct rather than moving it from one window "
        "to another."
    ))
    s.append(RC.new_page())
    return s


def chapter7() -> list:
    s = [*H1("7", "Advantages")]
    s.append(RC.body(
        "The advantages of the project are practical rather than theoretical. Each one "
        "can be observed in a single run, and Table 7.1 pairs the advantage with the "
        "evidence that supports it."
    ))
    s.extend(RC.table(
        "7.1",
        ["Advantage", "Explanation", "Evidence in the application"],
        [
            ["Removes repetitive typing", "One model call produces all line items of a document",
             "Three-item invoice becomes three rows"],
            ["Keeps the human in control", "Every value passes through an editable grid",
             "Review step before download"],
            ["Handles mixed formats", "Text, scans, photographs, Word, text and CSV",
             "Format list and preview"],
            ["Schema is user-owned", "Columns can be chosen, reordered or invented",
             "Multiselect and custom columns"],
            ["Errors are visible", "Confidence flags and deterministic checks",
             "Tinted cells and Checks sheet"],
            ["Register is auditable", "Source file and timestamp on every row",
             "Audit columns"],
            ["Fits existing workflow", "Appends to a master workbook by column heading",
             "Master upload and append"],
            ["Costs nothing to run", "Free model tier and free hosting",
             "Deployment on Community Cloud"],
            ["Runs locally", "No server needed for development or offline demos",
             "python -m streamlit run app.py"],
            ["Recoverable", "History survives a refresh or a closed tab",
             "SQLite history panel"],
        ],
        widths=[4.2, 7.0, 4.8],
    ))
    s.append(RC.body(
        "The strongest advantage is not the model. It is the decision to place a review "
        "step between extraction and export. A tool that exported directly would be "
        "faster in the best case and dangerous in the worst. A tool that forced the user "
        "to retype everything would not be worth installing. The grid is the compromise "
        "that makes the output trustworthy enough to use."
    ))
    s.append(RC.body(
        "The second advantage is the size of the system. Seven small modules, one "
        "external service and a standard workbook format can be understood by one "
        "person. That matters for a college project, but it also matters in a small "
        "office where there is no IT department to maintain a larger platform. The "
        "README explains how to change the model, add a document type and deploy the app, "
        "so the tool can outlive the assignment."
    ))
    s.append(RC.body(
        "A third advantage is honest failure. Unsupported files, missing keys, exhausted "
        "quotas and unreadable scans each produce a specific message with a next step. "
        "This sounds like a small thing until a tool is used under time pressure; a "
        "generic 'something went wrong' turns a five-minute fix into an afternoon of "
        "guessing."
    ))
    s.append(RC.new_page())
    return s


def chapter8() -> list:
    s = [*H1("8", "Limitations")]
    s.append(RC.body(
        "The limitations are stated plainly because they determine when the tool should "
        "not be used. Some are inherent to language models, some follow from the design "
        "choices, and some are consequences of the free tier."
    ))
    s.append(RC.P(
        "<b>Input quality dominates.</b> A digital PDF with a text layer is read almost "
        "perfectly. A photograph with a shadow, a folded page or a stamp over the total "
        "is not. The model can often recover a value from context, but when it cannot it "
        "may return a plausible wrong value rather than an empty string. The review grid "
        "and confidence flags reduce the risk; they do not eliminate it. A production "
        "system would need a sharper input-quality check before extraction."
    ))
    s.append(RC.P(
        "<b>Confidence is a hint, not a probability.</b> The high, medium and low labels "
        "come from the model's own assessment. Neural networks are often overconfident "
        "[11], and a language model is no exception. Low confidence is a useful signal "
        "that something was unclear; high confidence does not prove that a value is "
        "correct. Deterministic checks cover only the fields for which a rule exists."
    ))
    s.append(RC.P(
        "<b>The document content leaves the machine.</b> Extraction sends the text or "
        "page images to a hosted model. For sample documents this is acceptable. For "
        "real client invoices it raises confidentiality and data-residency questions "
        "that the project does not solve. A local model would remove the concern but "
        "would require hardware that the target user does not have."
    ))
    s.append(RC.P(
        "<b>The free tier has limits.</b> The daily quota is enough for a demonstration "
        "and for individual use, not for a busy office. When the quota is exhausted the "
        "application reports the API error, but it cannot continue. A paid key can be "
        "substituted by changing one environment variable; the cost then becomes the "
        "user's decision."
    ))
    s.append(RC.P(
        "<b>English and clean layouts are the happy path.</b> The prompt is written in "
        "English and the schemas use Indian trade terminology. Hindi or Gujarati "
        "documents, handwritten challans and regional-language invoices are not "
        "supported as a case, even if the model occasionally reads parts of them. "
        "Automatic document-type detection is also absent, so the user must choose the "
        "type correctly."
    ))
    s.append(RC.P(
        "<b>Validation is conservative, not complete.</b> The GSTIN checksum, HSN format "
        "and total arithmetic catch common errors, but the validator does not know tax "
        "rates, exemptions, place-of-supply rules or the correct HSN for a product. It "
        "also cannot verify that a shipping bill number exists. The Checks sheet is a "
        "list of suspicions, not a compliance certificate."
    ))
    s.append(RC.P(
        "<b>Single-user assumptions.</b> There are no accounts, roles or shared "
        "workspaces. The history database is local to the server, and on Community Cloud "
        "it is temporary. Two people using the app at the same time have separate "
        "sessions, which is fine for a demo but not for a team that needs a shared "
        "register. The workbook itself is not locked, so simultaneous appends can "
        "overwrite each other."
    ))
    s.extend(RC.bullets([
        ("Large scans: ", "a very long scan is processed in batches and can exhaust the "
         "per-minute quota even when the daily quota is available."),
        ("Unusual tables: ", "merged cells, multi-row headers and nested line items may "
         "produce a wrong item count."),
        ("Master workbooks: ", "a heavily formatted master with formulas is preserved, "
         "but formula cells are not recalculated by openpyxl."),
        ("Evaluation size: ", "the test set is small and drawn from a few suppliers, so "
         "the accuracy figures in Appendix B should not be generalised."),
    ]))
    s.append(RC.body(
        "None of these limitations makes the tool useless. They define the boundary "
        "within which it is useful: a person who can read the document is reviewing the "
        "output, the documents are in a supported language, and the register is a "
        "working file rather than a statutory filing."
    ))
    s.append(RC.new_page())
    return s


def chapter9() -> list:
    s = [*H1("9", "Conclusion")]
    s.append(H2("9.1", "Project Summary"))
    s.append(RC.body(
        "The project set out to remove the transcription step between a trade document "
        "and an Excel register. It did so with a small Streamlit application that reads "
        "six families of input, extracts the fields of eight trade document types, shows "
        "the rows in an editable grid and exports a formatted workbook. The model does "
        "the interpretation; ordinary Python does the reading, validation and writing. "
        "That division is the central design decision and the reason the tool is both "
        "flexible and predictable."
    ))
    s.append(RC.body(
        "The implementation grew beyond the first plan. CSV input, batch extraction, a "
        "master-workbook append, column presets, a history store and a Checks sheet were "
        "added after testing showed that extraction alone was not enough. Each addition "
        "came from a specific failure: a semicolon-delimited export, a consignment with "
        "four documents, a register that already existed, a repeated column selection, a "
        "lost tab, a wrong total. The final application is therefore a record of problems "
        "found in use, not a feature list written in advance."
    ))
    s.append(RC.body(
        "On the sample set the tool reduced a three-item invoice from roughly twenty "
        "minutes of typing to under two minutes including review. The number is modest "
        "and the sample is small, but the direction is clear: the time moves from "
        "copying to checking, which is the part that benefits from human attention."
    ))

    s.append(H2("9.2", "Outcomes in Relation to Project Objectives"))
    s.append(RC.body(
        "Table 9.1 restates each objective from Chapter 1 and the evidence that it was "
        "met. Where the evidence is a test, the identifier refers to Appendix C."
    ))
    s.extend(RC.table(
        "9.1",
        ["Objective", "Evidence", "Status"],
        [
            ["Accept common document formats",
             "PDF, scan, JPG, PNG, WEBP, BMP, TIFF, DOCX, TXT, CSV and pasted text load",
             "Met"],
            ["Extract five trade document types",
             "Eight types are implemented with separate schemas",
             "Exceeded"],
            ["One record per line item",
             "Three-item invoice returns three rows (T-07)",
             "Met"],
            ["User-controlled columns",
             "Multiselect, custom columns and presets (T-09, T-10)",
             "Met"],
            ["Editable review with flags",
             "Data editor, confidence tints and issue count",
             "Met"],
            ["Formatted Excel register",
             "Frozen header, filters, money formats, Checks sheet (T-14)",
             "Met"],
            ["Append to a master workbook",
             "Existing rows preserved and new rows added (T-14)",
             "Met"],
            ["Zero cost",
             "Free model tier and free hosting",
             "Met, with quota limits"],
            ["Key safety",
             "Environment variables and platform secrets; no key in git",
             "Met"],
        ],
        widths=[5.4, 8.6, 2.4],
    ))
    s.append(RC.body(
        "Two objectives were exceeded rather than merely met. The number of document "
        "types grew from five to eight as the schema turned out to be easy to extend, and "
        "the export grew from one workbook to three formats. One objective is met with a "
        "caveat: zero cost is true at demonstration volume, but the free quota is not "
        "sufficient for continuous office use."
    ))

    s.append(H2("9.3", "Issues Identified"))
    s.append(RC.body(
        "The issues found during the project fall into three groups: extraction, "
        "interface and data."
    ))
    s.extend(RC.bullets([
        ("Extraction: ", "multi-row line items and merged cells are the most common "
         "source of a wrong item count. A prompt rule helps but does not solve it. "
         "Handwriting remains unreliable."),
        ("Confidence: ", "the model's confidence is not calibrated, so the tint is a "
         "review aid rather than a risk score. A better approach would compare two "
         "extraction passes and flag disagreements."),
        ("Interface: ", "Streamlit reruns the script on every interaction, so state has "
         "to be stored carefully. Early versions lost the edited grid when a sidebar "
         "button was pressed; the grid identifier and session keys fixed it."),
        ("Validation: ", "a rule that is too strict creates false alarms, and a rule "
         "that is too loose misses errors. The current thresholds were chosen by testing "
         "on the sample set and would need tuning for another office."),
        ("Deployment: ", "the cloud filesystem is temporary, so the history is not "
         "durable there. The app says so in the README rather than pretending otherwise."),
        ("Evaluation: ", "the sample set is too small to quote an accuracy percentage "
         "with confidence. The report therefore describes specific runs instead of "
         "claiming a general accuracy figure."),
    ]))
    s.append(RC.body(
        "These issues do not invalidate the result. They identify where the next version "
        "should spend its effort, which is the subject of Chapter 10."
    ))
    s.append(RC.new_page())
    return s


def chapter10(fig) -> list:
    s = [*H1("10", "Future Work")]
    s.append(RC.body(
        "The current release is a complete single-user tool. The work that would make it "
        "suitable for a small office is mostly about reliability and shared state rather "
        "than new model capability. This chapter lists the planned enhancements, a "
        "realistic timeline and the outcome expected from each."
    ))

    s.append(H2("10.1", "Planned Enhancements"))
    s.extend(RC.numbered([
        "Automatic document-type detection. A lightweight classifier over the first page "
        "could suggest a type, with the user able to override it. The risk of a wrong "
        "guess is managed by showing the suggestion and the evidence rather than hiding "
        "the choice.",
        "Stronger validation. Tax-rate tables, state codes, place-of-supply rules and a "
        "second extraction pass for disagreement detection would catch more errors "
        "without making the tool a tax engine.",
        "Batch splitting for long scans. A twenty-page scanned shipping bill currently "
        "runs as five model calls. A progress indicator per batch and a retry for a "
        "failed batch would make long documents less fragile.",
        "A durable register database. Moving the master from a workbook to SQLite or "
        "PostgreSQL would allow concurrent appends, search and reporting, while keeping "
        "the Excel export as a view.",
        "Multi-language and handwriting support. A model with better multilingual "
        "coverage plus a handwriting-specific prompt could extend the tool to regional "
        "documents, with an explicit confidence penalty.",
        "Accounts, roles and an audit trail. A login, a per-user history and an "
        "append-only log of edits would make the tool usable by a team and acceptable in "
        "an audit.",
        "An API and a scheduled inbox. A small REST endpoint plus a mail rule would let "
        "documents arriving in a dedicated mailbox be extracted without a person "
        "opening the app.",
    ]))
    s.append(RC.body(
        "The order matters. Automatic detection and stronger validation improve the "
        "quality of every run. The database and accounts change the deployment model, so "
        "they come later. Multi-language and handwriting are research-like and depend on "
        "model improvements outside the project's control."
    ))

    s.append(H2("10.2", "Development Plan and Timeline"))
    s.append(RC.body(
        "The plan assumes one developer working part-time. Each phase ends with a "
        "demonstrable improvement and a test appended to the log, following the same "
        "pattern as the first release."
    ))
    s.extend(RC.table(
        "10.1",
        ["Phase", "Work", "Weeks", "Deliverable"],
        [
            ["P1", "Document-type detection and an override control", "1-2",
             "Suggested type with confidence"],
            ["P2", "Tax-rate and state-code validation; second-pass comparison", "2-4",
             "Expanded Checks sheet"],
            ["P3", "Per-batch progress and retry for long scans", "5-6",
             "Robust long-document run"],
            ["P4", "Register database with concurrent append", "7-9",
             "Shared register behind the workbook view"],
            ["P5", "Accounts, roles and edit audit trail", "10-12",
             "Multi-user deployment"],
            ["P6", "Multilingual and handwriting prompts", "13-15",
             "Extended input coverage"],
            ["P7", "REST API and mailbox ingestion", "16-18",
             "Automated intake"],
        ],
        widths=[1.4, 8.4, 2.0, 4.6],
    ))
    s.extend(RC.figure("10.1", fig["gantt"], width_cm=15.6))
    s.append(RC.body(
        "Figure 10.1 places the phases on a ten-week scale for the near-term work, with "
        "the later phases extending beyond it. The overlap is intentional: validation "
        "work can continue while the database design is reviewed, and the API depends on "
        "the database, not on the interface."
    ))

    s.append(H2("10.3", "Expected Future Outcomes"))
    s.append(RC.body(
        "If the first three phases are completed, the tool should reach a point where a "
        "new user can upload a folder of mixed documents and trust the resulting "
        "register after a quick review. The measurable target is a reduction in review "
        "edits per document, not a higher extraction score on a benchmark. If the "
        "database and accounts phases are completed, the tool becomes a small team "
        "application with a shared register and an audit trail, which is the version a "
        "real office could adopt."
    ))
    s.append(RC.body(
        "A less obvious outcome is documentation. Each phase adds a chapter to the "
        "README and a test to the log, so the project remains teachable. That is the "
        "difference between a demonstration and a tool that someone else can maintain."
    ))
    s.append(RC.new_page())
    return s


def chapter11() -> list:
    s = [*H1("11", "Publications")]
    s.append(RC.body(
        "No part of this work has been published or submitted to a journal or conference "
        "at the time of writing. The project is a coursework submission, and the report "
        "is the primary record of the work."
    ))
    s.append(RC.body(
        "If the project is extended along the lines of Chapter 10, two publication routes "
        "are realistic. The first is a student track or poster at a college technical "
        "symposium, describing the review-first extraction workflow and the validation "
        "layer. The second is a short paper comparing prompt-based extraction with a "
        "fine-tuned layout model on a small, documented set of Indian trade documents. "
        "The second would need a larger sample and a proper annotation protocol before "
        "it could make a credible claim."
    ))
    s.append(RC.body(
        "The source code and this report are available in the public repository so that "
        "the work can be inspected and reproduced. Any future publication would cite the "
        "repository and the version of the code used for the experiments."
    ))
    s.append(Spacer(1, 0.4 * cm))
    s.extend(RC.note_box(
        "This section is included because the report template requires it. It should be "
        "removed or updated if a paper is accepted after submission."
    ))
    s.append(RC.new_page())
    return s


def chapter12() -> list:
    s = [*H1("12", "References")]
    refs = [
        "[1] R. Smith, \u201cAn Overview of the Tesseract OCR Engine,\u201d Proceedings of "
        "the Ninth International Conference on Document Analysis and Recognition (ICDAR), "
        "2007, pp. 629\u2013633.",
        "[2] Y. Xu, M. Li, L. Cui, S. Huang, F. Wei and M. Zhou, \u201cLayoutLM: "
        "Pre-training of Text and Layout for Document Image Understanding,\u201d "
        "Proceedings of the 26th ACM SIGKDD Conference, 2020, pp. 1192\u20131200.",
        "[3] Y. Huang, T. Lv, L. Cui, Y. Lu and F. Wei, \u201cLayoutLMv3: Pre-training "
        "for Document AI with Unified Text and Image Masking,\u201d Proceedings of the "
        "30th ACM International Conference on Multimedia, 2022, pp. 4083\u20134091.",
        "[4] L. Cui, Y. Xu, T. Lv and F. Wei, \u201cDocument AI: Benchmarks, Models and "
        "Applications,\u201d arXiv:2111.08609, 2021.",
        "[5] Amazon Web Services, \u201cAmazon Textract Developer Guide,\u201d AWS "
        "Documentation, 2024. [Online]. Available: https://docs.aws.amazon.com/textract/",
        "[6] Google Cloud, \u201cDocument AI Documentation,\u201d 2024. [Online]. "
        "Available: https://cloud.google.com/document-ai/docs",
        "[7] Gemini Team, Google, \u201cGemini 1.5: Unlocking Multimodal Understanding "
        "Across Millions of Tokens of Context,\u201d arXiv:2403.05530, 2024.",
        "[8] G. Kim, T. Hong, M. Yim, J. Nam, J. Park, J. Yim, W. Hwang, S. Yun, "
        "D. Han and S. Park, \u201cOCR-free Document Understanding Transformer,\u201d "
        "Proceedings of the European Conference on Computer Vision (ECCV), 2022, "
        "pp. 498\u2013517.",
        "[9] Streamlit, \u201cStreamlit Documentation,\u201d 2024. [Online]. Available: "
        "https://docs.streamlit.io",
        "[10] Artifex Software, \u201cPyMuPDF Documentation,\u201d 2024. [Online]. "
        "Available: https://pymupdf.readthedocs.io",
        "[11] C. Guo, G. Pleiss, Y. Sun and K. Q. Weinberger, \u201cOn Calibration of "
        "Modern Neural Networks,\u201d Proceedings of the 34th International Conference "
        "on Machine Learning (ICML), 2017, pp. 1321\u20131330.",
        "[12] openpyxl, \u201copenpyxl Documentation,\u201d 2024. [Online]. Available: "
        "https://openpyxl.readthedocs.io",
        "[13] python-docx, \u201cpython-docx Documentation,\u201d 2024. [Online]. "
        "Available: https://python-docx.readthedocs.io",
        "[14] SQLite, \u201cSQLite Documentation,\u201d 2024. [Online]. Available: "
        "https://www.sqlite.org/docs.html",
        "[15] Central Board of Indirect Taxes and Customs, \u201cIndian Customs EDI "
        "System: Shipping Bill and Bill of Entry Messages,\u201d 2024. [Online]. "
        "Available: https://www.icegate.gov.in",
    ]
    for ref in refs:
        s.append(RC.P(RC.esc(ref), "ref"))
    s.append(Spacer(1, 0.3 * cm))
    s.extend(RC.note_box(
        "Project repository: https://github.com/prajwalshinde752-nonveg/DocEntry-AI. "
        "The version described in this report is the commit tagged in the repository "
        "history at the time of submission."
    ))
    s.append(RC.new_page())
    return s


def appendix_a() -> list:
    s = [*H1("13", "Appendices")]
    s.append(RC.body(
        "The appendices record the field definitions, the sample extraction, the test "
        "log and the operating instructions. They are intended to be sufficient for "
        "another student to rebuild and verify the project."
    ))
    s.append(RC.h2("Appendix A  Field Definitions"))
    s.append(RC.body(
        "The tables below list the internal key and the column heading for each document "
        "type. The internal key is used in the code, the prompt and the JSON; the heading "
        "is what the user sees in the interface and in Excel. Every type also receives "
        "the two audit columns, Source File and Extracted At."
    ))
    s.extend(RC.table(
        "A.1",
        ["#", "Internal key", "Column heading"],
        [
            [str(i), key, label] for i, (key, label) in enumerate(
                RC_DOC_TYPES["Tax Invoice"], start=1
            )
        ],
        widths=[1.2, 7.4, 7.4],
    ))
    s.extend(RC.table(
        "A.2",
        ["#", "Internal key", "Column heading"],
        [
            [str(i), key, label] for i, (key, label) in enumerate(
                RC_DOC_TYPES["Shipping Bill"], start=1
            )
        ],
        widths=[1.2, 7.4, 7.4],
    ))
    s.append(RC.new_page())

    rows = []
    for name in ["Purchase Order", "Bill of Entry", "Delivery Challan",
                 "E-Way Bill", "Packing List", "Commercial Invoice"]:
        fields = ", ".join(label for _, label in RC_DOC_TYPES[name])
        rows.append([name, str(len(RC_DOC_TYPES[name])), fields])
    s.extend(RC.table(
        "A.3",
        ["Document type", "Fields", "Column headings"],
        rows,
        widths=[3.4, 1.3, 11.3],
    ))
    s.append(RC.body(
        "The remaining six types are listed in compact form because their field lists "
        "follow the same pattern: identifiers and dates first, then party names and "
        "locations, then line-item details, then values and currency. A user-defined "
        "type uses exactly the same structure, with keys derived from the headings "
        "entered in the custom-columns box."
    ))
    return s


def appendix_b() -> list:
    s = [RC.h2("Appendix B  Sample Extraction Run")]
    s.append(RC.body(
        "The sample in samples/sample_tax_invoice.pdf contains three line items. It was "
        "run through the application on the development machine with the Tax Invoice "
        "schema and the default model. Table B.1 shows the values that reached the review "
        "grid. The invoice number, date and PO number repeat on each row because they "
        "belong to the document, while the description, quantity and values differ per "
        "item."
    ))
    s.extend(RC.table(
        "B.1",
        ["Field", "Row 1", "Row 2", "Row 3"],
        [
            ["Invoice No.", "TI/2026/0142", "TI/2026/0142", "TI/2026/0142"],
            ["Invoice Date", "12-02-2026", "12-02-2026", "12-02-2026"],
            ["PO No.", "PO/BLUE/2026/77", "PO/BLUE/2026/77", "PO/BLUE/2026/77"],
            ["Seller", "Blue Harbour Exports", "Blue Harbour Exports", "Blue Harbour Exports"],
            ["Buyer", "Northline Traders", "Northline Traders", "Northline Traders"],
            ["HSN Code", "0901", "0902", "2106"],
            ["Description", "Coffee beans", "Tea, black", "Health mix"],
            ["Quantity", "120", "80", "60"],
            ["Unit", "kg", "kg", "kg"],
            ["Rate", "410.00", "290.00", "155.00"],
            ["Taxable Value", "49,200.00", "23,200.00", "9,300.00"],
            ["Total Value", "58,056.00", "27,376.00", "10,974.00"],
            ["Confidence", "high", "high", "high"],
        ],
        widths=[4.2, 4.2, 4.2, 4.2],
    ))
    s.append(RC.body(
        "The run completed in well under a minute on the development machine, including "
        "the model call and the rendering of the grid. Network conditions and model load "
        "dominate the wait, so the figure is indicative rather than a benchmark. The "
        "values in Table B.1 are the ones that reached the grid; a final comparison of "
        "units and punctuation against the PDF remains part of the review step. Because "
        "the sample does not print separate tax amounts, the arithmetic check has nothing "
        "to compare and does not raise a warning."
    ))
    s.append(RC.body(
        "A CSV export of the same invoice (samples/sample_tax_invoice.csv) produced the "
        "same three records. The CSV reader sniffed a comma delimiter, joined cells with "
        "a vertical bar and passed the text to the same prompt. No special handling was "
        "needed in the extractor, which is evidence that the Document abstraction is "
        "doing its job."
    ))
    s.extend(RC.note_box(
        "The values above are from the sample file supplied with the project. They are "
        "not real company data. Timings are indicative and depend on network conditions "
        "and model load."
    ))
    s.append(RC.new_page())
    return s


def appendix_c() -> list:
    s = [RC.h2("Appendix C  Test Log")]
    s.append(RC.body(
        "Table C.1 is the acceptance log for the final build. Checks that involve "
        "extraction were run on the sample files; checks that involve validation or the "
        "workbook were run directly against the relevant module. A test passes only when "
        "the stated expected result is observed without editing the code."
    ))
    s.extend(RC.table(
        "C.1",
        ["ID", "Input", "Expected result", "Outcome"],
        [
            ["T-01", "Digital PDF invoice", "Text read; three records returned", "Pass"],
            ["T-02", "Scanned JPG invoice", "Image path used; values returned", "Pass"],
            ["T-03", "DOCX purchase order", "Paragraphs and tables read", "Pass"],
            ["T-04", "TXT delivery challan", "Plain text extracted", "Pass"],
            ["T-05", "Semicolon CSV export", "Delimiter detected; rows read", "Pass"],
            ["T-06", "Pasted invoice text", "Preview and extraction work", "Pass"],
            ["T-07", "Three-item invoice", "Exactly three records", "Pass"],
            ["T-08", "Two files of different types", "Two sections in one batch", "Pass"],
            ["T-09", "Custom columns with '=' syntax", "New type saved and listed", "Pass"],
            ["T-10", "Saved column preset", "Columns restored exactly", "Pass"],
            ["T-11", "Invalid API key", "Error message names the cause", "Pass"],
            ["T-12", "GSTIN with wrong checksum", "Error flagged on the row", "Pass"],
            ["T-13", "Invoice already in master", "Duplicate warning shown", "Pass"],
            ["T-14", "Append to existing workbook", "Old rows preserved; new rows added", "Pass"],
            ["T-15", "Six page images (synthetic)", "Batches of four and two; records merged", "Pass"],
            ["T-16", "Unsupported .xls upload", "Specific unsupported-type message", "Pass"],
            ["T-17", "Totals that do not add up", "Warning on total value", "Pass"],
            ["T-18", "Empty scan", "One empty row, low confidence everywhere", "Pass"],
        ],
        widths=[1.3, 5.0, 7.6, 2.3],
    ))
    s.append(RC.body(
        "Three checks are worth singling out. T-13 matches the invoice heading rather "
        "than a fixed column, so a master with a different column order is still "
        "checked. T-15 exercises the image planner, whose batch sizes are asserted "
        "directly (four and two for six pages). T-14 compares the row count before and "
        "after an append, so an accidental overwrite would be caught rather than "
        "described as a success."
    ))
    s.append(RC.new_page())
    return s


def appendix_d() -> list:
    s = [RC.h2("Appendix D  Operating Instructions")]
    s.append(RC.P("<b>Local setup.</b> Python 3.11 or newer is required.", "body"))
    s.extend(RC.code(
        "git clone https://github.com/prajwalshinde752-nonveg/DocEntry-AI\n"
        "cd DocEntry-AI\n"
        "python -m venv .venv\n"
        "source .venv/bin/activate        # Windows: .venv\\Scripts\\activate\n"
        "pip install -r requirements.txt\n"
        "cp .env.example .env              # then paste your key into .env\n"
        "streamlit run app.py"
    ))
    s.append(RC.body(
        "The .env file holds three settings: AI_API_KEY (the Gemini key), AI_BASE_URL "
        "(the OpenAI-compatible endpoint) and AI_MODEL (the model name). The key is never "
        "printed in full; the sidebar shows a fingerprint made of the first six and last "
        "four characters, which is enough to confirm which key is loaded without "
        "revealing it. On Streamlit Community Cloud the same values are entered under "
        "App settings, Secrets, in TOML form."
    ))
    s.append(RC.body(
        "To use the app, choose a document type in the sidebar, upload one or more files "
        "or paste text, select the columns, and press Extract fields. Review the grid: "
        "amber or red cells need attention, and the expander under the grid lists every "
        "check with its row and field. Use Manage batch to combine several runs, then "
        "download the workbook. If an existing register is uploaded as the master, new "
        "rows are appended to it rather than replacing it."
    ))
    s.append(RC.body(
        "Troubleshooting follows the error message. 'Please pass a valid API key' means "
        "the key is missing, expired or copied with a space. A 503 from the model is "
        "temporary; wait a few seconds and retry. An unsupported file type is reported "
        "next to the uploader; convert the file to PDF or CSV. If the grid is empty after "
        "extraction, open the error details expander and check whether the model returned "
        "JSON. If the workbook download is missing, confirm that at least one row exists "
        "and that the grid is not still in edit mode."
    ))
    s.extend(RC.code(
        "# restart the local server after changing .env or theme settings\n"
        "pkill -f \"streamlit run app.py\"\n"
        "streamlit run app.py --server.port 8501"
    ))
    s.append(RC.P(
        "<b>Project structure.</b> app.py is the entry point; documents.py, extractor.py, "
        "schemas.py, validation.py, excel_writer.py and history.py are the supporting "
        "modules. samples/ contains the test documents, assets/ the favicon, and docs/ "
        "this report and its generator. Tests are manual and documented in Appendix C; "
        "the Streamlit AppTest harness is used for quick interface smoke tests.",
        "body",
    ))
    return s
