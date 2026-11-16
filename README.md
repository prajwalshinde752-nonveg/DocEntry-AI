# DocEntry-AI

Turn import/export trade documents into clean Excel register rows.

**Accepted input:** upload a PDF (digital *or* scanned), a JPG/PNG/WEBP/BMP/TIFF
photo, a Word `.docx`, a `.txt` or a `.csv` export — or just paste the text
straight into the app.

**Flow:** Add a document (upload or paste) → choose columns → AI extracts the fields → you review and
edit → download Excel (fresh, or appended to your existing master register).

**Every line item becomes its own row.** An invoice with three products produces
three rows, each repeating the invoice number, date and party details.

Long documents are read in batches, so pages and line items are no longer cut
off at an arbitrary limit.

## What the app checks for you

Before export, every row is checked automatically:

- **GSTIN** — format and checksum (covers seller, buyer, supplier and recipient).
- **HSN** — must be 4, 6 or 8 digits (`8471`, `847130`, `8471.30` are accepted).
- **Totals** — taxable value + IGST + CGST + SGST must match the total (within ₹1).
- **Dates** — unrecognised formats are flagged but left exactly as extracted.
- **Duplicates** — invoice numbers already in the uploaded master register, or
  repeated across source documents.
- **Empty document numbers** — invoice / PO / challan / bill numbers.

Flagged cells are colour-highlighted in the Excel file and listed on a
`Checks` sheet. Low-confidence AI fields are listed separately.

## Batch, history and custom columns

- **Batch export** — extract several documents (even different document types)
  and download one workbook. Each document type gets its own sheet.
- **History** — every extraction is saved in `.docentry/history.db`. Reopen a
  run from the sidebar to review, add it to a batch, or delete it.
- **Custom columns** — in step 2, add `key=Heading` lines (or just headings) to
  extend any document type; save the selection as a reusable preset.
- **Custom document types** — choose *Custom document type* in the sidebar, name
  it, add its fields, and save it. It appears in the dropdown next time.
- **CSV / JSON** download is offered next to Excel.

## Setup (once)

**1. Get a free AI key**

1. Open https://aistudio.google.com/apikey
2. Click **Create API key** (free, no credit card)
3. Copy the key

**2. Put it in `.env`**

```bash
cd DocEntry-AI
nano .env      # paste the key after AI_API_KEY=
```

`.env` should look like:

```
AI_API_KEY=AIza...your-key...
AI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
AI_MODEL=gemini-3.1-flash-lite
```

Then open the app and press **Test connection** in the sidebar. If you see
"Works", you are done.

> Using OpenAI instead? Set `AI_BASE_URL=` (leave it empty) and
> `AI_MODEL=gpt-4o-mini`.

## Run

```bash
./run.sh
```

or:

```bash
.venv/bin/streamlit run app.py
```

A browser tab opens at http://localhost:8501

## Files

| File | What it does |
|---|---|
| `app.py` | The screens, and the order they appear in |
| `documents.py` | Turns any supported file into text or images (PDF, image, DOCX, TXT, CSV) |
| `extractor.py` | Sends the text/images to the AI, batches long documents, parses the fields |
| `schemas.py` | The fields we extract for each document type, plus custom-column parsing |
| `validation.py` | GSTIN/HSN/total/date/duplicate checks |
| `excel_writer.py` | Builds / appends the styled Excel register, plus CSV and JSON |
| `history.py` | Local SQLite store for runs, column presets and custom document types |
| `samples/` | Test documents |

## Adding a document type

Open `schemas.py`, add an entry to `DOCUMENT_TYPES` with `(key, label)` pairs.
It appears in the app immediately — no other code changes. You can also create
one from the app without touching the code.

## Current limits

- One API call handles 4 scanned pages or ~24,000 characters of text; longer
  documents are split automatically and the records are merged.
- 1,000 extracted rows is a safety ceiling per document.
- Photos are downscaled to 1600 px wide before sending.
- Data lives in the browser session plus the local history database until you
  download it. On Streamlit Community Cloud that database is temporary.

These are deliberate, so the app stays predictable.

## Deploy a public link (free)

GitHub stores the code. To get a link anyone can open, use **Streamlit
Community Cloud** on top of it.

1. Push this project to a **public** GitHub repo.
2. Go to <https://share.streamlit.io> → **New app**.
3. Choose your repo, branch `main`, main file `app.py`.
4. Open **Advanced settings → Secrets** and paste:

```toml
AI_API_KEY = "AIza...your-real-key..."
AI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
AI_MODEL = "gemini-3.1-flash-lite"
```

5. Click **Deploy**.

The API key never goes in the repo — `.env` is in `.gitignore`, and on Cloud the
key comes from the Secrets box instead.

> Free apps go to sleep after a while of no use. The first visit after that
> takes ~30 seconds to wake up.
