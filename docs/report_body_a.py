"""
Body chapters 1 to 5 of the DocEntry-AI report.
"""

from reportlab.platypus import PageBreak, Spacer

import report_common as RC


def H1(number: str, title: str):
    return RC.h1(f"{number}  {title}")


def H2(number: str, title: str):
    return RC.h2(f"{number}  {title}")


def chapter1(fig) -> list:
    s = [*H1("1", "Introduction")]
    s.append(RC.body(
        "This chapter explains why the project exists. It describes the paperwork "
        "that an import or export business handles, the way that paperwork is "
        "currently converted into a register, and the specific failures that the "
        "application is designed to remove. It then states the objectives, the "
        "boundary of the work and the outcomes that were used to judge whether the "
        "project succeeded."
    ))

    s.append(H2("1.1", "Background and Motivation"))
    s.append(RC.body(
        "A single export consignment can generate a tax invoice, a packing list, a "
        "shipping bill, a purchase order, a delivery challan and, on the import side, "
        "a bill of entry. Each document is issued by a different party and follows a "
        "layout chosen by that party. The invoice number appears in the top right on "
        "one form and under the seller's address on another. The GSTIN may be printed "
        "as 'GSTIN', 'GST No.' or 'GSTIN/UIN'. The line items may be a bordered table, "
        "a set of repeated blocks, or a single paragraph of text. None of this matters "
        "to the people who read the documents, because a trained clerk can find the "
        "values in a few seconds. It matters a great deal to software, which is why "
        "most offices still type the values by hand."
    ))
    s.append(RC.body(
        "The typed values usually end up in an Excel register with one row per line "
        "item. The register is the working memory of the business: accounts use it to "
        "match invoices with payments, the customs agent uses it to follow up on a "
        "shipping bill, and management uses it to see what was exported and at what "
        "value. A register that is incomplete or wrong causes problems that surface "
        "weeks later: a payment that cannot be reconciled, a credit that is claimed "
        "against the wrong invoice, a quantity that does not match the bill of entry."
    ))
    s.append(RC.body(
        "The motivation for this project came from watching that transcription happen. "
        "The information already exists in a machine-readable form in most cases: "
        "modern invoices are generated from accounting software and exported as PDFs "
        "with selectable text. The barrier is not reading the characters but mapping "
        "an unpredictable layout onto a fixed set of columns. Recent language models "
        "are good at exactly that mapping when they are given the document and a clear "
        "description of the columns. The project asks whether that capability can be "
        "packaged into a tool that a non-programmer can use, with a review step that "
        "keeps the person in control of the result."
    ))

    s.append(H2("1.2", "Problem Statement"))
    s.append(RC.body(
        "The present process is manual, sequential and repeated for every document. "
        "Table 1.1 lists the steps a clerk follows and the weakness of each. The "
        "weaknesses compound: a misread invoice number in step three is copied into "
        "the register, checked against nothing in step four, and approved in step "
        "five. The error is only discovered when a different document is compared "
        "with the register much later."
    ))
    s.extend(RC.table(
        "1.1",
        ["Step", "What the clerk does", "Weakness of the step"],
        [
            ["1", "Receives the documents by email, WhatsApp or courier",
             "Files arrive as photos, scans and PDFs in no fixed order"],
            ["2", "Identifies the document type and the party",
             "Similar forms are easy to confuse, especially part shipments"],
            ["3", "Reads each field and types it into the register",
             "Slow; values are keyed from memory of the layout"],
            ["4", "Adds line items and calculates totals",
             "Arithmetic is reliable but copying between rows is not"],
            ["5", "Checks the register against the document",
             "The same person checks the same reading, so errors survive"],
            ["6", "Saves, prints or shares the workbook",
             "No record of which document produced which row"],
        ],
        widths=[1.1, 6.4, 8.4],
    ))
    s.append(RC.body(
        "The problem statement for the project is therefore: given a trade document in "
        "a common electronic format, produce the rows of an Excel register "
        "automatically, show the values to the user for correction, and preserve "
        "enough information to trace every row back to its source. The solution must "
        "work on a normal laptop, must not require a paid subscription, and must fail "
        "visibly rather than silently when a value cannot be read."
    ))

    s.append(H2("1.3", "Objectives of the Project"))
    s.append(RC.body(
        "The objectives were written so that each one could be demonstrated in the "
        "finished application rather than only described in the report."
    ))
    s.extend(RC.numbered([
        "Accept the document formats that a small trade office actually receives: "
        "digital PDF, scanned PDF, photographs, DOCX, TXT and CSV, plus pasted text.",
        "Extract the fields of the five core trade document types into a common record "
        "structure, with one record per line item rather than one record per file, and "
        "allow further types to be added without changing the extractor.",
        "Let the user choose which columns the register needs, including columns that "
        "are not part of the built-in schema, and accept values the model leaves blank.",
        "Present every extracted row in an editable table, mark low-confidence fields "
        "and validation problems, and never export a value without showing it first.",
        "Generate a formatted Excel workbook with one sheet per document type, a checks "
        "sheet, frozen headers and filters, and support appending to an existing master "
        "register.",
        "Keep the cost at zero for a college project by using the free tier of a "
        "hosted model, and keep the API key out of the source code and the repository.",
    ]))
    s.append(RC.body(
        "A sixth objective is implicit in the others: the system must be understandable "
        "by its author six months later. That is why the code is split into small "
        "modules with one responsibility each, and why the report describes the actual "
        "functions rather than an imagined architecture."
    ))

    s.append(H2("1.4", "Scope and Limitations"))
    s.append(RC.body(
        "The project covers the path from a document to a reviewable register. It does "
        "not attempt to replace accounting software, file documents with a government "
        "portal, or decide whether a transaction is compliant. Table 1.2 states the "
        "boundary explicitly so that the absence of a feature is understood as a "
        "decision rather than an omission."
    ))
    s.extend(RC.table(
        "1.2",
        ["Inside the scope", "Outside the scope"],
        [
            ["Upload or paste one or many documents at once",
             "Automatic download of documents from email or a portal"],
            ["Eight built-in trade document types plus user-defined types",
             "A complete customs tariff or duty calculator"],
            ["Text PDFs, scanned PDFs, photos, DOCX, TXT, CSV",
             "Handwriting and non-Latin scripts as a supported case"],
            ["Field selection, custom columns and saved presets",
             "User accounts, roles and shared team workspaces"],
            ["Editable review grid with confidence and validation flags",
             "A full accounting ledger or double-entry bookkeeping"],
            ["Excel, CSV and JSON export; append to a master workbook",
             "Direct GST portal or ICEGATE filing"],
            ["Local history of runs and presets in SQLite",
             "Long-term cloud storage of sensitive documents"],
        ],
        widths=[8.1, 8.1],
    ))
    s.append(RC.body(
        "Two limitations deserve emphasis. First, extraction quality depends on the "
        "quality of the input: a clean digital PDF is close to perfect, a photograph "
        "taken at an angle in poor light is not. Second, the application sends document "
        "content to a third-party model over the internet. That is acceptable for "
        "sample and training documents but would need a data-processing agreement for "
        "real client work. The report returns to both points in Chapter 8."
    ))

    s.append(H2("1.5", "Expected Outcomes"))
    s.append(RC.body(
        "The outcomes were defined as observable changes in the manual process, not as "
        "a list of screens. Table 1.3 pairs each expected outcome with the evidence "
        "that was used to check it."
    ))
    s.extend(RC.table(
        "1.3",
        ["Task", "Before the project", "After the project", "Evidence"],
        [
            ["Read a three-item invoice",
             "About twenty minutes of typing",
             "One upload, one model call, under two minutes",
             "Timed run in Appendix B"],
            ["Register layout",
             "Recreated by hand for each workbook",
             "Generated with formatting, filters and checks",
             "Downloaded .xlsx file"],
            ["Correct a wrong value",
             "Find the cell, compare with the PDF",
             "Edit the marked cell in the review grid",
             "Editable grid, confidence flags"],
            ["Add the same columns next week",
             "Remember the previous workbook",
             "Save and reuse a column preset",
             "SQLite preset record"],
            ["Prove where a row came from",
             "Memory or filename in a folder",
             "Source File and Extracted At audit columns",
             "Audit columns in every sheet"],
        ],
        widths=[4.2, 4.1, 4.8, 3.5],
    ))
    s.append(RC.new_page())
    return s


def chapter2() -> list:
    s = [*H1("2", "Literature Review and Theoretical Background")]
    s.append(RC.body(
        "Document data extraction is an old problem with a new set of tools. This "
        "chapter reviews the main approaches, explains the concepts that the "
        "implementation depends on, compares existing systems, and identifies the gap "
        "that a small, free, trade-specific tool can fill."
    ))

    s.append(H2("2.1", "Review of Previous Work Related to Document Data Extraction"))
    s.append(RC.body(
        "The earliest practical approach was template matching. A document type was "
        "described by fixed coordinates or anchor words, and values were read from the "
        "expected position. It works well for a single supplier who never changes the "
        "form and fails as soon as the layout moves. Optical character recognition "
        "(OCR) made the characters available but did not solve the mapping problem; "
        "Tesseract [1] remains a strong free OCR engine, yet its output is a stream of "
        "words whose relationship to a field is not explicit."
    ))
    s.append(RC.body(
        "Layout-aware deep learning changed the picture. LayoutLM [2] combined word "
        "tokens with bounding boxes and the two-dimensional position of each word, so "
        "the model could learn that a value to the right of the word 'Invoice No.' is "
        "probably the invoice number (see the survey in [4]). LayoutLMv3 [3] extended "
        "this to images and text without a separate OCR pipeline. Donut [8] went further "
        "and read the page "
        "image directly, producing structured output without OCR. These models are "
        "accurate on the benchmarks they were trained for, but fine-tuning one on a "
        "new document set requires labelled data, a GPU and more time than a college "
        "project allows."
    ))
    s.append(RC.body(
        "Commercial intelligent document processing services package the same ideas. "
        "Amazon Textract [5], Google Document AI [6] and Azure Document Intelligence "
        "provide OCR, table extraction and pre-trained invoice models through an API. "
        "They are excellent for production volumes, but they are priced per page, "
        "require cloud configuration, and return their own schema rather than the "
        "columns a small register needs. Off-the-shelf tools such as Docsumo and "
        "Nanonets add a user interface and template management, again on a subscription."
    ))
    s.append(RC.body(
        "The most recent line of work uses general-purpose language models. A model "
        "such as Gemini or GPT-4o can be given the document and a description of the "
        "desired JSON, and will return the values without any task-specific training. "
        "The approach trades determinism for flexibility: the same prompt handles a "
        "new supplier, a new layout or a new field, but the model can still misread a "
        "digit or invent a value. Research on structured output and function calling "
        "has reduced the formatting problem, and confidence handling remains the "
        "responsibility of the application. Table 2.1 summarises the families of "
        "methods."
    ))
    s.extend(RC.table(
        "2.1",
        ["Approach", "Representative work", "Strength", "Weakness"],
        [
            ["Template and coordinate rules", "Early OCR form readers",
             "Fast and predictable for one layout",
             "Breaks on any layout change"],
            ["OCR plus keyword rules", "Tesseract with custom scripts [1]",
             "Free and local",
             "Rules multiply; poor on scans"],
            ["Layout-aware neural models", "LayoutLM, LayoutLMv3 [2][3]",
             "High accuracy on known forms",
             "Needs labels, GPU and training"],
            ["OCR-free document models", "Donut [8]",
             "Skips the OCR stage",
             "Large model; limited to trained tasks"],
            ["Cloud IDP services", "Textract, Document AI, Azure [5][6]",
             "Managed, scalable, table support",
             "Per-page cost; cloud setup; vendor schema"],
            ["Table extraction libraries", "Camelot, pdfplumber",
             "Precise on ruled tables",
             "Fails on scans and merged cells"],
            ["General LLM prompting", "Gemini, GPT-4 class models [7]",
             "No training; adapts to new fields",
             "Non-deterministic; needs validation"],
            ["Hybrid with human review", "This project",
             "Combines model speed with human judgement",
             "Review effort grows with document count"],
        ],
        widths=[3.8, 4.6, 4.4, 4.2],
    ))

    s.append(H2("2.2", "Key Concepts: Document Processing, OCR, and Data Extraction"))
    s.append(RC.P(
        "<b>Digital text versus raster images.</b> A PDF can contain a text layer or "
        "only pixels. The difference decides the whole pipeline. A digital PDF can be "
        "read by a library such as PyMuPDF [10] in milliseconds, and the text is exact. "
        "A scan or photograph has no text layer; the page must either be sent to a "
        "vision-capable model or passed through OCR first. DocEntry-AI checks the "
        "amount of text on the page and chooses the path automatically. This is more "
        "reliable than trusting the file extension, because a 'digital' PDF exported "
        "from a scanner is often an image with an empty text layer."
    ))
    s.append(RC.P(
        "<b>Optical character recognition.</b> OCR converts pixels into characters. A "
        "classical pipeline detects text regions, segments lines and words, classifies "
        "characters and assembles the result. Accuracy depends on resolution, contrast, "
        "skew and font. Trade documents add stamps, signatures, carbon-copy shading and "
        "tables with thin rules, all of which confuse classical OCR. Modern multimodal "
        "models perform recognition and interpretation in one step, which is why the "
        "project sends page images directly rather than running a separate OCR engine. "
        "The trade-off is that errors are less predictable and cannot be corrected by "
        "improving an OCR configuration."
    ))
    s.append(RC.P(
        "<b>Layout and reading order.</b> A table is not a sequence of words; it is a "
        "two-dimensional arrangement in which the column header applies to the cells "
        "below it. Language models see an image or a linear text stream, so the prompt "
        "must describe the expected structure. In this project the line-item fields are "
        "listed explicitly and the model is told to return one object per item. For "
        "digital PDFs, PyMuPDF returns text in reading order, which preserves row "
        "boundaries well enough for invoices but can interleave columns in a complex "
        "shipping bill. The review grid exists partly to catch that failure."
    ))
    s.append(RC.P(
        "<b>Information extraction and schema.</b> Extraction is the mapping from "
        "unstructured content to a schema: a set of named fields with expected types. "
        "A schema can be expressed as a Python list of key-label pairs, as JSON Schema, "
        "or as a table definition. The important property is that the schema is "
        "explicit and stable, because the Excel columns, the prompt and the validation "
        "rules all derive from it. In DocEntry-AI the schema lives in schemas.py and is "
        "the single source of truth for the user interface and the export."
    ))
    s.append(RC.P(
        "<b>Confidence and grounding.</b> A language model's output is a prediction, "
        "not a measurement. Asking the model for a confidence label per field is a "
        "useful heuristic but not a calibrated probability; neural confidence is known "
        "to be poorly calibrated [11], and a language model is no exception. The "
        "application therefore treats confidence as a sorting aid: low-confidence cells "
        "are highlighted for review, and every value is checked by deterministic rules "
        "(GSTIN checksum, HSN format, date parsing, totals) where such rules exist. The "
        "rule decides; confidence only orders the review."
    ))
    s.append(RC.P(
        "<b>Batching and token limits.</b> A model call has a context limit measured in "
        "tokens. A long scanned shipping bill with twenty pages will not fit in one "
        "call at full resolution. The extractor splits images into batches of four "
        "pages and text into chunks of 24,000 characters, numbers each batch, and tells "
        "the model which part it is reading. The returned records are concatenated. "
        "This keeps memory bounded and avoids silently truncating the last pages, which "
        "is a common failure in simple wrappers."
    ))

    s.append(H2("2.3", "Review of Existing Systems and Methods"))
    s.append(RC.body(
        "Table 2.2 compares the options that were considered for this project. The "
        "comparison is not a benchmark; it records the properties that mattered for a "
        "single-user, zero-cost deployment."
    ))
    s.extend(RC.table(
        "2.2",
        ["System or method", "Input", "Output", "Cost", "Fit for this project"],
        [
            ["Tesseract OCR", "Images, scanned PDFs", "Plain text with boxes",
             "Free", "Useful engine, but no field mapping"],
            ["LayoutLM family", "Images plus OCR words", "Labelled tokens",
             "Free model, costly training", "Too heavy without labelled data"],
            ["Amazon Textract", "Images, PDFs", "Key-value pairs, tables",
             "Per page", "Accurate, but needs AWS account and budget"],
            ["Google Document AI", "Images, PDFs", "Entities, tables",
             "Per page", "Good invoice parser, vendor-specific schema"],
            ["Azure Document Intelligence", "Images, PDFs", "Entities, tables",
             "Per page", "Similar trade-offs to Textract"],
            ["Nanonets / Docsumo", "Images, PDFs", "Structured records",
             "Subscription", "Polished UI, but closed and paid"],
            ["Manual Excel entry", "Human reading", "Rows in a workbook",
             "Staff time", "The baseline the project tries to improve"],
            ["LLM with review (this project)", "Text, images, CSV",
             "Rows and confidence", "Free tier", "Matches scope and budget"],
        ],
        widths=[4.0, 3.3, 3.6, 2.7, 4.0],
    ))
    s.append(RC.body(
        "The commercial services are the strongest on difficult scans, because they "
        "combine OCR, layout analysis and a specialised invoice model. They are also "
        "the least suitable here: a student cannot justify a per-page charge for a "
        "demonstration, and the register needs its own columns rather than a generic "
        "invoice schema. The local deep-learning models are free but require training "
        "data that the project does not have. The language-model route is the only one "
        "that offers schema flexibility, zero cost at the expected volume, and a "
        "reasonable implementation size."
    ))
    s.append(RC.body(
        "Streamlit [9] was chosen for the interface after comparing it with Flask and "
        "Django. Streamlit turns a Python script into a reactive web page without "
        "writing HTML, JavaScript or route handlers, and it includes file upload, "
        "tables and download buttons as built-in widgets. For a single-page internal "
        "tool this is a good fit; for a public multi-user product it would not be. "
        "openpyxl [12] handles the workbook, python-docx [13] the Word files, and "
        "SQLite [14] the local history. All are free and available on the deployment "
        "platform."
    ))

    s.append(H2("2.4", "Gap Analysis"))
    s.append(RC.body(
        "The review reveals a gap that is narrow but real. Existing systems are either "
        "powerful and expensive, or free and rigid. None of them is organised around "
        "the register that a small trade office actually maintains."
    ))
    s.extend(RC.bullets([
        ("Cost: ", "per-page pricing is difficult to justify for low-volume, "
         "occasional use, which is exactly the pattern in a small export house."),
        ("Schema ownership: ", "cloud invoice models return their own fields. A "
         "register often needs a PO number, a scheme code or a column that exists only "
         "in that office."),
        ("Correction loop: ", "most tools stop at extraction. The user needs a table "
         "where a wrong value can be fixed before it reaches the workbook."),
        ("Register-level checks: ", "duplicate invoice numbers, GSTIN checksums and "
         "arithmetic totals are not part of generic extraction, but they are what make "
         "a register trustworthy."),
        ("Traceability: ", "a row without a source filename and timestamp cannot be "
         "audited later, yet many simple scripts drop that information."),
        ("Local control: ", "a small office may be willing to use a hosted model but "
         "not to upload its whole archive to a document-management service."),
    ]))
    s.append(RC.body(
        "DocEntry-AI addresses these points with a deliberately modest design: a "
        "free-tier model for interpretation, deterministic code for validation, and a "
        "review grid that makes the human correction step explicit. The next chapter "
        "describes that design."
    ))
    s.append(RC.new_page())
    return s


def chapter3(fig) -> list:
    s = [*H1("3", "System Overview and Design")]
    s.append(RC.body(
        "This chapter describes the proposed system as a whole: its design goals, the "
        "block diagram, the responsibilities of each component, the processing "
        "workflow and the criteria used to select the tools."
    ))

    s.append(H2("3.1", "Proposed DocEntry-AI System"))
    s.append(RC.body(
        "DocEntry-AI is a single-page web application with a four-step flow: documents, "
        "columns, extraction and review, download. The user can upload several files "
        "or paste text, choose a document type and columns, press one button, correct "
        "the result, and export. The application does not store documents permanently; "
        "it keeps the extracted rows in the session and records a compact history entry "
        "in a local SQLite file so that work survives a page refresh."
    ))
    s.append(RC.body(
        "Four design goals shaped the implementation. First, the path from upload to "
        "download should be visible; a user should never wonder what the program is "
        "doing. Second, no value should reach the workbook without passing through the "
        "review grid. Third, failures should be specific: a missing key, an unsupported "
        "file and an unreadable scan produce different messages. Fourth, the whole "
        "system should run on a free tier, with no paid service other than the model's "
        "free quota."
    ))
    s.append(RC.body(
        "The application is intentionally stateless with respect to documents. Each "
        "browser session holds its own rows, and the only shared state is the history "
        "database on the server. This simplifies deployment and avoids the privacy "
        "problem of retaining client documents. The history stores extracted values, "
        "not the original files, and can be cleared from the sidebar."
    ))

    s.append(H2("3.2", "Block Diagram of the Proposed System"))
    s.append(RC.body(
        "Figure 3.1 shows the main blocks and the direction of data flow. The top row "
        "is the extraction path; the bottom row is the preparation and export path. "
        "Two loops are important. The model's JSON reply returns to extractor.py, not "
        "directly to the interface, so that parsing and normalisation happen in one "
        "place. The schema block feeds both the prompt and the Excel writer, which is "
        "why the columns selected by the user appear identically in both."
    ))
    s.extend(RC.figure("3.1", fig["arch"], width_cm=16.0))
    s.append(RC.body(
        "The input block accepts six families of files. documents.py converts each one "
        "into a Document object that carries either text or a list of JPEG page "
        "images, plus a short note describing what was read. extractor.py builds the "
        "prompt, splits long input into batches, calls the model through an "
        "OpenAI-compatible endpoint and parses the reply. app.py owns the session, the "
        "review grid and the download. validation.py checks the rows, and "
        "excel_writer.py builds the workbook. schemas.py is the shared contract, and "
        "history.py is the side store for runs and presets."
    ))

    s.append(H2("3.3", "Description of System Components"))
    s.append(RC.body(
        "Table 3.1 lists the modules with their responsibilities and approximate size. "
        "The split follows the direction of data rather than the screen layout, so each "
        "module can be tested on its own."
    ))
    s.extend(RC.table(
        "3.1",
        ["Module", "Responsibility", "Key functions", "Lines"],
        [
            ["app.py", "Interface, session state, review grid, downloads",
             "section, load_source, render grid", "~1000"],
            ["documents.py", "Read any supported file into text or page images",
             "read_document, _read_pdf, _read_csv", "~150"],
            ["extractor.py", "Prompt, batching, API call, JSON parsing",
             "extract_records, _parse_json, test_connection", "~330"],
            ["schemas.py", "Built-in fields, audit columns, custom column parser",
             "DOCUMENT_TYPES, parse_custom_columns", "~230"],
            ["validation.py", "GSTIN, HSN, dates, totals, duplicates",
             "validate_rows, is_valid_gstin", "~330"],
            ["excel_writer.py", "Workbook, checks sheet, CSV and JSON export",
             "build_workbook, build_csv, build_json", "~370"],
            ["history.py", "SQLite store for runs, presets and custom types",
             "save_run, list_runs, save_preset", "~240"],
        ],
        widths=[3.3, 6.3, 5.4, 1.6],
    ))
    s.append(RC.body(
        "app.py is the largest file because Streamlit mixes layout and state in one "
        "script. It is divided into numbered sections that mirror the four steps, with "
        "a sidebar for document type, connection status, history, custom columns and "
        "presets. Session keys hold the rows, the low-confidence map, the validation "
        "issues, the batch of extracted sections and the current grid identifier. When "
        "the grid is edited, the new rows replace the session rows before export."
    ))
    s.append(RC.body(
        "documents.py has one public function, read_document, and a small dataclass. "
        "The PDF reader is the only one with a decision: if the extracted text is at "
        "least forty characters, the PDF is treated as digital; otherwise every page is "
        "rendered at 150 dpi and converted to JPEG. Images are downscaled to 1600 "
        "pixels wide, which is enough for a model to read a table while keeping the "
        "request small. CSV files are sniffed for a delimiter, because exports from "
        "Excel on some machines use semicolons or tabs."
    ))
    s.append(RC.body(
        "extractor.py contains the prompt and the only network call in the project. It "
        "reads the key from the environment, constructs an OpenAI client with the "
        "Gemini-compatible base URL, sends a chat completion at temperature zero, and "
        "parses the reply. The prompt names the document type, lists every field with "
        "its label, describes the one-object-per-line-item rule, and forbids commentary "
        "outside the JSON. Parsing is defensive: it strips code fences, finds the "
        "outermost braces and accepts either a list or an object with a records key."
    ))
    s.append(RC.body(
        "schemas.py is small but central. Each document type is a list of key-label "
        "pairs, and AUDIT_COLUMNS adds the source file and timestamp. Users can define "
        "their own columns as lines of text, either 'key=Label' or just 'Label'; the "
        "parser turns the label into a safe key and resolves duplicates. Those custom "
        "types are saved in SQLite and merged with the built-in list at startup."
    ))
    s.append(RC.body(
        "validation.py is deliberately conservative. It validates GSTIN structure with "
        "the official checksum, checks HSN lengths, parses dates in several formats, "
        "compares taxable value plus tax with the invoice total, and looks for invoice "
        "numbers that already exist in an uploaded master workbook. It does not decide "
        "tax liability and does not correct values; it only reports issues with a row, "
        "a field, a message and a level."
    ))
    s.append(RC.body(
        "excel_writer.py creates the register. It writes a header row with the navy "
        "fill used throughout the project, freezes it, adds an autofilter, formats "
        "money and quantity columns, highlights issue cells and adds a Checks sheet. "
        "When a master workbook is supplied, it matches columns by heading and appends "
        "rows to the matching sheet, creating a sheet if the document type is new. The "
        "same rows can be exported as CSV or JSON for further processing."
    ))
    s.extend(RC.figure("3.3", fig["dataflow"], width_cm=15.6))
    s.append(RC.body(
        "Figure 3.3 shows the objects that cross module boundaries. Keeping the "
        "Document, the list of records and the workbook as plain Python values makes "
        "the modules easy to test with a script, without starting the web server."
    ))

    s.append(H2("3.4", "Document Processing Workflow"))
    s.append(RC.body(
        "The workflow has eight stages, shown in Figure 3.2. The numbered stages are "
        "not all visible to the user: stages two and five happen inside one button "
        "press, and stage seven runs automatically before the download section appears."
    ))
    s.extend(RC.figure("3.2", fig["workflow"], width_cm=15.4))
    s.extend(RC.numbered([
        "The user uploads files or pastes text. Each file is read immediately so that "
        "format problems are reported before extraction starts.",
        "documents.py decides between text and images. The decision and the number of "
        "pages are shown in a preview expander.",
        "The user selects a document type and the columns for the register. The "
        "selection can come from a preset or from custom column text.",
        "extractor.py builds a prompt containing the type, the fields and the document "
        "content, then splits long content into batches.",
        "Each batch is sent to the model at temperature zero. The reply is parsed into "
        "records and merged with the records from earlier batches.",
        "The records are normalised: missing fields become empty strings, unexpected "
        "keys are dropped, and confidence values are mapped to high, medium or low.",
        "validation.py checks the rows, and app.py renders the editable grid with "
        "low-confidence cells and issue counts.",
        "The user corrects values, then downloads the workbook. A compact history entry "
        "is written so the run can be reopened.",
    ]))
    s.append(RC.body(
        "Two details in the workflow prevent common failures. Files are read before the "
        "extract button is enabled, so an unsupported extension or a corrupt PDF is "
        "caught early with a specific message. And if the model returns no usable "
        "record, the extractor returns one empty record with every field marked low "
        "rather than an empty list. The interface can then explain that nothing was "
        "read, instead of showing a blank table with no diagnosis."
    ))

    s.append(H2("3.5", "Selection Criteria for Components and Tools"))
    s.append(RC.body(
        "The tool selection followed five criteria: zero cost for the expected volume, "
        "Python support, a permissive licence, availability on Streamlit Community "
        "Cloud, and a small enough surface to understand completely. Table 3.2 records "
        "the alternatives that were considered."
    ))
    s.extend(RC.table(
        "3.2",
        ["Decision", "Options considered", "Chosen", "Reason"],
        [
            ["Interface", "Flask, Django, Streamlit", "Streamlit",
             "Built-in upload, table and download widgets"],
            ["Model access", "Gemini SDK, OpenAI SDK, raw HTTP", "OpenAI SDK",
             "One client works with Gemini's compatible endpoint"],
            ["Model", "Gemini Flash, GPT-4o mini, local Llama", "Gemini Flash Lite",
             "Free tier; vision support; low latency"],
            ["PDF reading", "pdfplumber, PyMuPDF, pypdf", "PyMuPDF",
             "Text and page rendering in one library"],
            ["Excel writing", "pandas, xlsxwriter, openpyxl", "openpyxl",
             "Formatting, appending and highlighting"],
            ["History store", "JSON file, TinyDB, SQLite", "SQLite",
             "Standard library, reliable concurrent reads"],
            ["Hosting", "Render, Railway, Streamlit Cloud", "Streamlit Cloud",
             "Free for public apps; secrets manager"],
        ],
        widths=[3.2, 5.5, 3.6, 5.0],
    ))
    s.append(RC.body(
        "The model choice deserves a note. Gemini's free tier is the only option in the "
        "comparison that combines vision input, a usable daily quota and an "
        "OpenAI-compatible endpoint. The compatible endpoint matters because it lets "
        "the project use a well-documented SDK and switch provider by changing two "
        "environment variables. The model name is not hard-coded in the logic; it is "
        "read from AI_MODEL, so a newer model can be tested without editing the source."
    ))
    s.extend(RC.figure("3.4", fig["deploy"], width_cm=15.0))
    s.append(RC.body(
        "Figure 3.4 shows the deployment. During development the app runs on localhost "
        "with a .env file. In production it runs on Streamlit Community Cloud, reads the "
        "key from the platform's secrets manager, and pulls the code from the public "
        "GitHub repository. No key is stored in the repository; the .env and "
        "secrets.toml files are ignored by git. This separation is part of the design, "
        "not an afterthought, because a leaked key would end the free quota and expose "
        "the account."
    ))
    s.append(RC.new_page())
    return s


def chapter4() -> list:
    s = [*H1("4", "System Specifications")]
    s.append(RC.body(
        "This chapter states what the system needs in order to run, and what it must do. "
        "The requirements are written so that each can be checked against the finished "
        "application; the test log in Appendix C refers back to them."
    ))

    s.append(H2("4.1", "Hardware Requirements"))
    s.append(RC.body(
        "The application runs on an ordinary laptop. The heavy work is done by the "
        "model service, so the local machine only reads files, holds a table and builds "
        "a workbook. Memory matters mainly when a large scanned PDF is rendered to "
        "images, because each page becomes a JPEG in memory before batching."
    ))
    s.extend(RC.table(
        "4.1",
        ["Component", "Minimum", "Recommended", "Why"],
        [
            ["Processor", "Dual-core 2.0 GHz", "Quad-core 2.4 GHz",
             "PDF rendering and Excel writing"],
            ["Memory", "4 GB", "8 GB",
             "Page images and the review table"],
            ["Storage", "500 MB free", "2 GB free",
             "Python environment, samples, history"],
            ["Display", "1366 x 768", "1920 x 1080",
             "The review grid has many columns"],
            ["Network", "1 Mbps", "5 Mbps",
             "Model calls carry page images"],
            ["Camera (optional)", "5 MP phone camera", "12 MP camera",
             "Photographing paper documents"],
        ],
        widths=[3.4, 3.6, 3.6, 6.4],
    ))
    s.append(RC.body(
        "On the development machine (a Linux laptop with 8 GB of RAM) a three-page "
        "digital invoice was read in under a second and the model call took a few "
        "seconds. A twenty-page scanned shipping bill used noticeably more memory "
        "during rendering but completed because the images are batched and released "
        "between calls. No GPU is required."
    ))

    s.append(H2("4.2", "Software Requirements"))
    s.append(RC.body(
        "The software stack is entirely free and cross-platform. Versions are pinned "
        "loosely in requirements.txt so that the deployment platform can install "
        "current compatible releases; runtime.txt fixes the Python version."
    ))
    s.extend(RC.table(
        "4.2",
        ["Software", "Version used", "Purpose"],
        [
            ["Python", "3.11 or newer", "Language runtime"],
            ["Streamlit", "1.40 or newer", "Web interface, upload, table, download"],
            ["PyMuPDF", "1.24 or newer", "PDF text extraction and page rendering"],
            ["python-docx", "1.1 or newer", "Read Word paragraphs and tables"],
            ["Pillow", "10.0 or newer", "Image decode, orientation, downscale, JPEG"],
            ["openpyxl", "3.1 or newer", "Create and append Excel workbooks"],
            ["openai", "1.30 or newer", "Client for the OpenAI-compatible endpoint"],
            ["python-dotenv", "1.0 or newer", "Read the local .env file"],
            ["SQLite", "Bundled with Python", "History, presets, custom types"],
            ["Git and GitHub", "Any current version", "Version control and deployment"],
            ["Streamlit Community Cloud", "Hosted service", "Public deployment"],
        ],
        widths=[3.9, 3.4, 9.7],
    ))
    s.append(RC.body(
        "A browser with a current JavaScript engine is required for the upload and "
        "download widgets. Chrome, Firefox and Edge were used during testing. The "
        "editable grid uses the same component in all three, with minor differences in "
        "scroll behaviour on narrow screens."
    ))

    s.append(H2("4.3", "Functional Requirements"))
    s.append(RC.body(
        "Functional requirements describe behaviour. Each has an identifier used in the "
        "test log so that the evidence can be traced back to the specification."
    ))
    s.extend(RC.table(
        "4.3",
        ["ID", "Requirement", "Acceptance check"],
        [
            ["FR-01", "Accept PDF, PNG, JPG, WEBP, BMP, TIFF, DOCX, TXT and CSV",
             "Each format loads without an error"],
            ["FR-02", "Accept several files in one run", "Rows from all files appear"],
            ["FR-03", "Accept pasted text as a document", "Preview shows the text"],
            ["FR-04", "Detect digital versus scanned PDFs",
             "Text PDF read as text; scan read as images"],
            ["FR-05", "Offer eight built-in document types",
             "Type list contains all eight"],
            ["FR-06", "Allow a user-defined type and columns",
             "New type survives a reload"],
            ["FR-07", "Extract one record per line item",
             "Three-item invoice returns three rows"],
            ["FR-08", "Return a confidence value per field",
             "Low-confidence cells are marked"],
            ["FR-09", "Let the user edit every extracted cell", "Edits reach the export"],
            ["FR-10", "Validate GSTIN, HSN, dates and totals",
             "Issues listed with row and field"],
            ["FR-11", "Detect duplicate invoice numbers in a master sheet",
             "Duplicate is flagged"],
            ["FR-12", "Export XLSX with one sheet per type", "Sheets match types"],
            ["FR-13", "Append to an existing master workbook",
             "Existing rows are preserved"],
            ["FR-14", "Export CSV and JSON", "Files open in a text editor"],
            ["FR-15", "Keep a local history of runs", "History survives a refresh"],
            ["FR-16", "Allow column presets", "Preset restores the columns"],
            ["FR-17", "Show connection status and test the key",
             "Test button reports success or failure"],
        ],
        widths=[1.6, 8.6, 6.8],
    ))
    s.append(RC.body(
        "The requirement that extraction return one record per line item is the most "
        "consequential. A simpler design would return one record per document, but that "
        "would force the user to split a three-item invoice by hand, which defeats the "
        "purpose. The prompt and the review grid are therefore built around a list of "
        "records, and the Excel writer receives a list of sections, each with its own "
        "document type and rows."
    ))

    s.append(H2("4.4", "Non-Functional Requirements"))
    s.append(RC.body(
        "Non-functional requirements describe quality. They are stated with a measure so "
        "that 'fast' or 'usable' does not remain an opinion."
    ))
    s.extend(RC.table(
        "4.4",
        ["ID", "Requirement", "Measure"],
        [
            ["NFR-01", "Usable without training", "A new user completes a run in under five minutes"],
            ["NFR-02", "First result within a reasonable wait",
             "Typical one-page invoice under 15 seconds"],
            ["NFR-03", "No silent failure", "Every error has a message and a next step"],
            ["NFR-04", "Secrets never in source", "No key in git history or logs"],
            ["NFR-05", "Works on a standard laptop", "No GPU; under 8 GB RAM"],
            ["NFR-06", "Recoverable from a refresh", "Rows restored from history"],
            ["NFR-07", "Accessible contrast", "Text meets WCAG AA on the dark theme"],
            ["NFR-08", "Deterministic export", "Same rows produce the same workbook"],
            ["NFR-09", "Portable", "Runs on Linux, Windows and macOS"],
            ["NFR-10", "Free to operate", "Fits the model free tier for a demo"],
        ],
        widths=[2.0, 7.4, 7.6],
    ))
    s.append(RC.body(
        "NFR-02 is deliberately modest. The model call dominates the response time and "
        "depends on the network; promising instant results would be dishonest. The "
        "interface shows a spinner and a short description of the current batch so that "
        "a long scan does not look like a frozen page."
    ))
    s.append(RC.new_page())
    return s


def chapter5(fig) -> list:
    s = [*H1("5", "Implementation")]
    s.append(RC.body(
        "This chapter follows the path of a document through the code. For each step it "
        "shows the relevant function, explains why it is written that way, and notes the "
        "failure modes that the implementation handles. Table 5.1 is a map of the source "
        "tree."
    ))
    s.extend(RC.table(
        "5.1",
        ["File", "Approximate size", "Responsibility"],
        [
            ["app.py", "1,000 lines", "Page layout, state, review grid, downloads"],
            ["documents.py", "150 lines", "One reader per input format"],
            ["extractor.py", "330 lines", "Prompt, batching, API call, JSON parsing"],
            ["schemas.py", "230 lines", "Field definitions and custom columns"],
            ["validation.py", "330 lines", "Business-rule checks"],
            ["excel_writer.py", "370 lines", "Workbook, checks sheet, CSV, JSON"],
            ["history.py", "240 lines", "SQLite runs, presets and custom types"],
            ["README.md", "—", "Setup, formats, limits and deployment"],
        ],
        widths=[3.6, 3.0, 10.4],
    ))

    s.append(H2("5.1", "Document Upload"))
    s.append(RC.body(
        "Upload is handled by two Streamlit tabs, one for files and one for pasted text. "
        "The file uploader accepts multiple files and a wide list of extensions. Each "
        "uploaded file is read as soon as it appears, not when the extract button is "
        "pressed, so that a corrupt or unsupported file is reported next to the "
        "uploader. A preview expander shows the detected kind, the number of characters "
        "or pages, and the first part of the text. This is the user's first chance to "
        "notice that a scan was read as an empty page."
    ))
    s.extend(RC.code(
        'SUPPORTED_TYPES = ["pdf", "png", "jpg", "jpeg", "webp", "bmp",\n'
        '                   "tif", "tiff", "docx", "txt", "csv"]\n'
        "\n"
        "def read_document(data: bytes, filename: str) -> Document:\n"
        "    ext = _extension(filename)\n"
        "    if ext not in SUPPORTED_TYPES:\n"
        "        raise ValueError(f\"Unsupported file type '.{ext}'.\")\n"
        "    if ext == \"pdf\":\n"
        "        return _read_pdf(data)\n"
        "    if ext in IMAGE_TYPES:\n"
        "        return _read_image(data)\n"
        "    if ext == \"docx\":\n"
        "        return _read_docx(data)\n"
        "    if ext == \"csv\":\n"
        "        return _read_csv(data)\n"
        "    return Document(kind=\"text\", text=data.decode(\"utf-8\", \"replace\"))"
    ))
    s.append(RC.body(
        "The PDF reader is worth reading in full because it contains the only branch "
        "that changes the type of processing. If the concatenated text of all pages is "
        "at least forty characters, the file is treated as digital and the text is "
        "returned. Otherwise the pages are rendered at 150 dpi, converted to RGB and "
        "compressed as JPEG. The 150 dpi choice is a compromise: 300 dpi produces "
        "larger payloads without a measurable improvement on printed invoices, while 96 "
        "dpi loses the thin strokes of a decimal point. The image reader also applies "
        "EXIF orientation, because phone photographs are often stored sideways."
    ))
    s.append(RC.body(
        "DOCX files are read paragraph by paragraph and then table by table, with cells "
        "joined by a vertical bar. That crude serialisation keeps a table row on one "
        "line, which the model reads as a row. CSV files are sniffed for a delimiter and "
        "serialised the same way, so an invoice exported as a spreadsheet looks like a "
        "table to the model. Text files are decoded as UTF-8 with replacement, so a "
        "stray byte produces a visible replacement character rather than a crash."
    ))
    s.extend(RC.figure("5.1", fig["wireframe"], width_cm=15.6))
    s.append(RC.body(
        "Figure 5.1 is a wireframe of the review screen, not a screenshot. It shows the "
        "sidebar with the document type and connection status, the navy masthead, the "
        "charcoal step strip, the upload area and the editable grid with its download "
        "button. The actual colours follow the dark theme described in the README."
    ))

    s.append(H2("5.2", "Document Type Identification and Data Extraction"))
    s.append(RC.body(
        "The document type is chosen by the user rather than detected automatically. "
        "Automatic detection was considered and rejected for the first release: an "
        "invoice and a purchase order can contain almost the same words, and a wrong "
        "guess would send a confusing prompt and produce plausible but wrong columns. "
        "The type is a deliberate input, and the type name appears in the prompt, the "
        "workbook sheet name and the history entry."
    ))
    s.append(RC.body(
        "The prompt is assembled from the field list so that adding a column in "
        "schemas.py changes the extraction without touching extractor.py. It has four "
        "parts: the role and task, the document type, the field list, and the rules. "
        "The rules are short and concrete: return one object per line item; use an empty "
        "string when a value is absent; do not invent values; return JSON only; and "
        "mark confidence as high, medium or low."
    ))
    s.extend(RC.code(
        "def _prompt(doc_type, fields, has_images, part=1, parts=1):\n"
        "    field_lines = \"\\n\".join(f\"- {k}: {label}\" for k, label in fields)\n"
        "    source = \"The document is attached as one or more images\" \\\n"
        "        if has_images else \"The document text is given below.\"\n"
        "    return f\"\"\"You are a careful data-entry assistant for Indian\n"
        "import/export trade documents.\n"
        "\n"
        "Document type: {doc_type}\n"
        "{source}\n"
        "\n"
        "Extract these fields:\n{field_lines}\n"
        "\n"
        "Rules:\n"
        "- Reply with ONLY valid JSON, in exactly this shape:\n"
        "  {{\"records\": [{{\"fields\": {{\"<key>\": \"<value>\"}},\n"
        "   \"confidence\": {{\"<key>\": \"high\"|\"medium\"|\"low\"}}}}]}}\n"
        "- Return ONE record for EVERY line item; never merge rows.\n"
        "- Repeat document-level values in every record.\n"
        "- Copy values exactly. Do NOT invent, guess or calculate.\n"
        "- Keep numbers as text so leading zeros are not lost.\n"
        "- If a field is missing or unreadable, use \"\" and confidence \"low\".\n"
        "\"\"\""
    ))
    s.append(RC.body(
        "The model is called at temperature zero to reduce variation. The reply is "
        "rarely pure JSON: a model may wrap it in a fenced block, add a sentence of "
        "explanation, or return a bare list. The parser therefore strips code fences, "
        "tries a direct JSON parse, and falls back to the outermost braces. If parsing "
        "still fails, the raw reply is kept for the error expander so that the user can "
        "see what the model actually said."
    ))
    s.extend(RC.code(
        "def _parse_json(raw: str) -> dict:\n"
        "    raw = raw.strip()\n"
        "    raw = re.sub(r\"^```(?:json)?|```$\", \"\", raw, flags=re.MULTILINE).strip()\n"
        "    try:\n"
        "        return json.loads(raw)\n"
        "    except json.JSONDecodeError:\n"
        "        start, end = raw.find(\"{\"), raw.rfind(\"}\")\n"
        "        if start != -1 and end != -1:\n"
        "            return json.loads(raw[start:end + 1])\n"
        "        raise"
    ))
    s.append(RC.body(
        "Long documents are split before the call. The planner keeps text and images "
        "separate: text is chunked at 24,000 characters on line boundaries, images are "
        "grouped four pages at a time. Each call is told which part it is reading, so "
        "the model does not try to summarise a whole twenty-page bill from four pages. "
        "The returned records are concatenated in order, and the sanity cap of 1,000 "
        "records prevents a runaway loop from filling memory. The cap is not a feature "
        "limit; a document with more than a thousand line items is outside the intended "
        "use case."
    ))
    s.extend(RC.figure("5.2", fig["sequence"], width_cm=15.6))
    s.append(RC.body(
        "Figure 5.2 shows the call sequence. The browser never talks to the model "
        "directly; the key stays on the server. The test connection button sends a "
        "one-word request and reports the reply or the exact API error, which is the "
        "quickest way to distinguish a wrong key from a model name that is not available "
        "on the free tier."
    ))

    s.append(H2("5.3", "Column Selection and Field Mapping"))
    s.append(RC.body(
        "The column selector is a multiselect populated from the chosen document type, "
        "with the audit columns at the end. The order of the selected columns becomes "
        "the order of the Excel columns, which lets a user put the invoice number and "
        "date first without editing the schema. A select-all and clear-all pair sits "
        "above the list, and a custom-columns expander accepts one column per line."
    ))
    s.extend(RC.code(
        "def parse_custom_columns(text: str) -> list[tuple[str, str]]:\n"
        "    columns, seen = [], set()\n"
        "    for raw in (text or \"\").splitlines():\n"
        "        line = raw.strip()\n"
        "        if not line or line.startswith(\"#\"):\n"
        "            continue\n"
        "        if \"=\" in line:\n"
        "            key_part, label = line.split(\"=\", 1)\n"
        "            key = _slug(key_part) if key_part.strip() else _slug(label)\n"
        "            label = label.strip() or key\n"
        "        else:\n"
        "            label = line\n"
        "            key = _slug(label)\n"
        "        base, n = key, 2\n"
        "        while key in seen:\n"
        "            key = f\"{base}_{n}\"\n"
        "            n += 1\n"
        "        seen.add(key)\n"
        "        columns.append((key.strip(), label.strip()))\n"
        "    return columns"
    ))
    s.append(RC.body(
        "The parser accepts 'HSN Code' and 'hsn=HSN Code'. The first form derives the "
        "key from the label, which is convenient; the second lets a user keep a short "
        "key while showing a long heading. Duplicate keys receive a numeric suffix so "
        "that two columns called 'Amount' do not overwrite each other in the record "
        "dictionary. Custom types are saved with their columns in SQLite and appear in "
        "the type list on the next load."
    ))
    s.append(RC.body(
        "Presets solve a smaller but frequent problem: the same office exports the same "
        "register every week. A preset stores only the column list, not the values, and "
        "can be applied to any document type. This is intentionally simple; a preset "
        "that also stored a document type and a filename pattern would be a workflow "
        "engine, which is beyond the project's scope."
    ))
    s.extend(RC.table(
        "5.2",
        ["Document type", "Fields", "Audit", "Characteristic columns"],
        [
            ["Tax Invoice", "20", "2",
             "GSTIN pair, HSN, taxable value, IGST/CGST/SGST, PO number"],
            ["Shipping Bill", "17", "2",
             "Port of loading/discharge, vessel, FOB value, scheme"],
            ["Purchase Order", "12", "2",
             "PO number and date, supplier, delivery terms"],
            ["Bill of Entry", "14", "2",
             "BE number, importer IEC, ports, assessable value, duty"],
            ["Delivery Challan", "10", "2",
             "Challan number, consignor/consignee, vehicle"],
            ["E-Way Bill", "18", "2",
             "Validity, both GSTINs, distance, transporter, vehicle"],
            ["Packing List", "14", "2",
             "Packages, net and gross weight, marks, ports"],
            ["Commercial Invoice", "18", "2",
             "Origin/destination, incoterms, amount, total value"],
        ],
        widths=[3.6, 2.0, 1.8, 9.6],
    ))
    s.append(RC.body(
        "Table 5.2 shows why a single generic schema would not work. The eight types share "
        "a vocabulary but not a shape: the invoice has three tax columns, the shipping "
        "bill has ports and a scheme, the bill of entry has duty and origin, and the "
        "challan has transport details. A generic 'amount' field would collapse "
        "information that the register needs to keep separate."
    ))

    s.append(H2("5.4", "Data Review and Editing"))
    s.append(RC.body(
        "The review grid is a Streamlit data editor bound to a list of dictionaries. "
        "Every visible column is editable except the audit columns, which are filled in "
        "by the application. Low-confidence cells are tinted, and a caption above the "
        "grid reports how many fields are marked low. Editing a value does not rerun "
        "the model; it updates the session rows and marks the row as reviewed."
    ))
    s.append(RC.body(
        "Validation runs on the rows before the grid is drawn and again before export. "
        "The checks are intentionally limited to rules that can be stated exactly. A "
        "GSTIN is fifteen characters: two state digits, five letters, four digits, a "
        "letter, an alphanumeric, the letter Z and a checksum character. The checksum is "
        "computed with alternating weights and a base-36 alphabet, which catches most "
        "typing errors that a length check would miss. HSN codes are checked for four, "
        "six or eight digits, with an optional decimal form. Dates are parsed with "
        "several common formats; an unparseable date is a warning, not an error, because "
        "the source may use a format the parser does not know."
    ))
    s.append(RC.body(
        "The arithmetic check is the most useful in practice. When taxable value, tax "
        "amounts and total value are all present, the validator compares taxable value "
        "plus tax with the total, allowing a small rounding tolerance. A mismatch of "
        "more than one rupee is reported. It does not decide which number is wrong; it "
        "only says that the three cannot all be true, which is exactly the kind of "
        "signal a clerk needs before signing the register."
    ))
    s.append(RC.body(
        "Duplicate detection uses the master workbook. If the user uploads the register "
        "that already exists, the writer reads its invoice column (matching either "
        "'Invoice No.' or 'Invoice Number') and passes the set to the validator. A new "
        "row whose invoice number is already present is flagged as a possible duplicate. "
        "This is deliberately a warning rather than a block: a credit note can legally "
        "reuse a number with a suffix, and the decision belongs to the user."
    ))

    s.append(H2("5.5", "Excel Register Generation and Download"))
    s.append(RC.body(
        "The exporter receives a batch, which is a list of sections. Each section has a "
        "document type, a column list and rows. A single-type run produces one sheet; a "
        "mixed batch produces one sheet per type. Sheet names are cleaned of characters "
        "that Excel forbids, truncated to thirty-one characters, and made unique. The "
        "header row is frozen, an autofilter is added, money columns receive a two-decimal "
        "format and quantity columns a general numeric format. Column widths are "
        "estimated from the longest value with a cap, so a long description does not "
        "produce a column wider than the screen."
    ))
    s.extend(RC.code(
        "def build_workbook(sections, master_bytes=None):\n"
        "    check_entries = []\n"
        "    if not sections:\n"
        "        raise ValueError(\"Nothing to export.\")\n"
        "    if master_bytes and len(sections) == 1:\n"
        "        wb = load_workbook(BytesIO(master_bytes))\n"
        "        ws = wb.active\n"
        "        start = ws.max_row + 1\n"
        "        _append_rows(ws, sections[0][\"rows\"], sections[0][\"columns\"],\n"
        "                     start, sections[0].get(\"issues\"))\n"
        "    else:\n"
        "        wb = Workbook()\n"
        "        wb.remove(wb.active)\n"
        "        used = set()\n"
        "        for section in sections:\n"
        "            ws = wb.create_sheet(_clean_sheet_name(section[\"name\"], used))\n"
        "            _append_rows(ws, section[\"rows\"], section[\"columns\"], 2,\n"
        "                         section.get(\"issues\"))\n"
        "        _validation_sheet(wb, check_entries)\n"
        "    out = BytesIO()\n"
        "    wb.save(out)\n"
        "    return out.getvalue()"
    ))
    s.append(RC.body(
        "Appending to a master workbook is the feature that turns the tool from a "
        "converter into a register builder. The master can be used when the batch has a "
        "single document type, because a multi-sheet batch has no single sheet to extend. "
        "Values are written under the master's existing headings: the writer reads the "
        "header row, matches each heading to a selected column, and leaves a cell blank "
        "when the master has a column that the current run did not extract. A column "
        "selected in the app but absent from the master is not added automatically, "
        "because silently reshaping someone's register is worse than leaving a column "
        "out; the user can add the heading to the master and run the append again."
    ))
    s.append(RC.body(
        "The Checks sheet lists every validation issue with the sheet name, row number, "
        "column heading, message and level. The same issues are used to highlight cells: "
        "errors in red, warnings in amber, information in blue. Highlighting is done by "
        "cell reference after the rows are written, so the colour always matches the "
        "row that produced the issue even when rows are appended to an existing sheet."
    ))
    s.append(RC.body(
        "CSV and JSON exports use the same sections. CSV is convenient for import into "
        "another program but cannot carry multiple sheets, so a mixed batch writes the "
        "sections one after another with a type column. JSON preserves the nested "
        "structure and is intended for a future API or for debugging. Both are generated "
        "in memory and offered as downloads; nothing is written to the server's disk "
        "except the optional history database."
    ))
    s.append(RC.new_page())
    return s
