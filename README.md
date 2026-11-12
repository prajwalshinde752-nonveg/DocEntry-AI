# DocEntry-AI

Turn import/export trade documents into clean Excel register rows.

**Accepted input:** upload a PDF (digital *or* scanned), a JPG/PNG/WEBP/BMP/TIFF
photo, a Word `.docx`, a `.txt` or a `.csv` export — or just paste the text
straight into the app.

**Flow:** Add a document (upload or paste) → choose columns → AI extracts the fields → you review and
edit → download Excel (fresh, or appended to your existing master register).

**Every line item becomes its own row.** An invoice with three products produces
three rows, each repeating the invoice number, date and party details.

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
| `extractor.py` | Sends the text/images to the AI, parses the fields |
| `schemas.py` | The fields we extract for each document type |
| `excel_writer.py` | Builds / appends the Excel register |
| `samples/` | Test documents |

## Adding a document type

Open `schemas.py`, add an entry to `DOCUMENT_TYPES` with `(key, label)` pairs.
It appears in the app immediately — no other code changes.

## Current limits

- Documents with more than 50 line items are capped at 50 rows.
- Scanned PDFs: only the first 5 pages are read.
- CSV files: the first 200 rows are read.
- Photos are downscaled to 1600 px wide before sending.
- No storage — data lives in the browser session until you download it.

These are deliberate, so the first version stays finishable.

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
