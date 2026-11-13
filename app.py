"""
DocEntry-AI — turn trade documents into Excel rows.

Run with:   streamlit run app.py
"""

import os
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

import documents
import extractor
from excel_writer import build_excel, default_filename
from schemas import AUDIT_COLUMNS, DOCUMENT_TYPES

load_dotenv(override=True)

# Locally the key comes from .env. On Streamlit Community Cloud there is no .env
# file — the key is set in the app dashboard, and arrives through st.secrets.
def _load_cloud_secrets() -> None:
    try:
        secrets = dict(st.secrets)
    except Exception:  # no secrets configured — normal when running locally
        return
    for key in ("AI_API_KEY", "AI_BASE_URL", "AI_MODEL"):
        if not os.getenv(key) and key in secrets:
            os.environ[key] = str(secrets[key])


_load_cloud_secrets()

ICON = Path(__file__).resolve().parent / "assets" / "icon.png"

st.set_page_config(
    page_title="DocEntry-AI",
    page_icon=str(ICON) if ICON.exists() else None,
    layout="wide",
)

# --------------------------------------------------------------------------
# Look and feel
# --------------------------------------------------------------------------
st.markdown(
    """
    <style>
      #MainMenu, footer { visibility: hidden; }
      .block-container {
          padding-top: 2.2rem; padding-bottom: 3rem; max-width: 1180px;
      }

      /* masthead */
      .de-head {
          background: #1B2A41;
          border-radius: 4px;
          padding: 24px 28px 22px;
          margin-bottom: 10px;
      }
      .de-head .de-kicker {
          font-size: 10.5px; letter-spacing: .16em; text-transform: uppercase;
          color: #A6B4C4; font-weight: 600; margin-bottom: 8px;
      }
      .de-head h1 {
          font-size: 29px; line-height: 1.15; color: #FFFFFF;
          font-weight: 600; letter-spacing: -.01em; margin: 0 0 9px; padding: 0;
      }
      .de-head p {
          color: #D2D9E0; font-size: 14px; line-height: 1.55;
          margin: 0; max-width: 68ch;
      }

      /* section headings */
      .de-section {
          display: flex; align-items: baseline; gap: 11px;
          margin: 32px 0 2px;
      }
      .de-section .de-num {
          font-size: 11px; font-weight: 600; color: #1B2A41;
          background: #EDEFF2; border-radius: 3px; padding: 3px 9px;
          letter-spacing: .08em;
      }
      .de-section .de-title {
          font-size: 19px; font-weight: 600; color: #33383D;
          letter-spacing: -.01em;
      }
      .de-hint {
          font-size: 13px; color: #4A5057; margin: 0 0 12px;
      }

      /* sidebar */
      .de-brand { display: flex; align-items: center; gap: 10px; }
      .de-brand .de-mark {
          width: 30px; height: 30px; border-radius: 6px;
          background: #1B2A41; color: #FFFFFF;
          font-size: 12.5px; font-weight: 700;
          display: flex; align-items: center; justify-content: center;
      }
      .de-brand .de-name {
          font-size: 16.5px; font-weight: 600; color: #33383D;
          letter-spacing: -.01em;
      }
      .de-brand-sub {
          font-size: 12px; color: #6E767D;
          margin: 3px 0 22px 40px;
      }
      .de-label {
          font-size: 10.5px; letter-spacing: .12em; text-transform: uppercase;
          color: #6E767D; font-weight: 600; margin: 0 0 5px;
      }
      .de-status {
          border-left: 2px solid #1B2A41;
          padding: 2px 0 2px 11px;
          font-size: 12.5px; line-height: 1.75; color: #4A5057;
      }
      .de-status b { color: #33383D; font-weight: 600; }
      .de-dot {
          display: inline-block; width: 7px; height: 7px; border-radius: 50%;
          margin-right: 6px; vertical-align: middle;
      }

      /* tighten default Streamlit spacing a little */
      .stTabs [data-baseweb="tab-list"] { gap: 4px; }
    </style>
    """,
    unsafe_allow_html=True,
)


def section(number: str, title: str, hint: str = "") -> None:
    """A numbered step heading, e.g. 1  Documents."""
    st.markdown(
        f'<div class="de-section"><span class="de-num">{number}</span>'
        f'<span class="de-title">{title}</span></div>',
        unsafe_allow_html=True,
    )
    if hint:
        st.markdown(f'<p class="de-hint">{hint}</p>', unsafe_allow_html=True)


# --------------------------------------------------------------------------
# Remember things between button clicks
# --------------------------------------------------------------------------
st.session_state.setdefault("rows", [])
st.session_state.setdefault("low", [])
st.session_state.setdefault("doc_type", None)


# --------------------------------------------------------------------------
# Sidebar
# --------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        '<div class="de-brand"><span class="de-mark">DE</span>'
        '<span class="de-name">DocEntry-AI</span></div>'
        '<div class="de-brand-sub">Import &amp; export documents</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="de-label">Document type</div>', unsafe_allow_html=True)
    doc_type = st.selectbox(
        "Document type", list(DOCUMENT_TYPES), label_visibility="collapsed"
    )

    st.divider()
    st.markdown('<div class="de-label">Connection</div>', unsafe_allow_html=True)

    if extractor.has_api_key():
        dot, state = '<span class="de-dot" style="background:#2E7D32"></span>', "Key loaded"
    else:
        dot, state = '<span class="de-dot" style="background:#B3261E"></span>', "No key found"

    _fingerprint = getattr(extractor, "key_fingerprint", None)
    if _fingerprint:
        key_line = _fingerprint()
    else:
        # A freshly deployed app can briefly run an older cached copy of
        # extractor.py. Do not crash the whole page because of it.
        key_line = "loaded (restart to refresh)"

    st.markdown(
        f'<div class="de-status">{dot}<b>{state}</b><br>'
        f"Model {extractor.model_name()}<br>Key {key_line}</div>",
        unsafe_allow_html=True,
    )
    if not extractor.has_api_key():
        st.caption("Copy `.env.example` to `.env` and add your key.")

    st.write("")
    if st.button("Test connection", use_container_width=True):
        ok, message = extractor.test_connection()
        if ok:
            st.success(f"Works. Model replied: {message}")
        else:
            st.error("Connection failed")
            st.code(message[:800])
            if "valid api key" in message.lower():
                st.info(
                    "Google rejected the key. If you are on the deployed app, "
                    "fix it in Streamlit Cloud → Settings → Secrets. If this is "
                    "localhost, check `.env`."
                )

    if st.button("Reset extraction", use_container_width=True):
        st.session_state["rows"] = []
        st.session_state["low"] = []
        st.rerun()

# A different document type means the old rows no longer make sense.
if st.session_state["doc_type"] != doc_type:
    st.session_state["doc_type"] = doc_type
    st.session_state["rows"] = []
    st.session_state["low"] = []


# --------------------------------------------------------------------------
# Header
# --------------------------------------------------------------------------
st.markdown(
    """
    <div class="de-head">
      <div class="de-kicker">Trade documentation</div>
      <h1>Document to Excel register</h1>
      <p>Add the paperwork, choose the columns your register needs, check the
      extracted values, then download the workbook.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------------------------------
# Step 1 — add documents (upload OR paste)
# --------------------------------------------------------------------------
section("1", "Documents", "Upload one or many files, or paste the text of a document.")

tab_upload, tab_paste = st.tabs(["Upload files", "Paste text"])


with tab_upload:
    files = st.file_uploader(
        "PDF, image, Word, TXT or CSV files (one or many)",
        type=documents.SUPPORTED_TYPES,
        accept_multiple_files=True,
    )

with tab_paste:
    pasted = st.text_area(
        "Paste the document text",
        height=220,
        placeholder="Copy the text from an email, portal or PDF and paste it here…",
    )
    pasted_name = st.text_input("Name for this row", value="pasted-text")

# Both input methods feed one list.
sources: list[dict] = []
for file in files or []:
    sources.append({"name": file.name, "data": file.getvalue()})
if pasted and pasted.strip():
    sources.append({"name": pasted_name.strip() or "pasted-text", "text": pasted})


def load_source(source: dict) -> documents.Document:
    if "text" in source:
        return documents.Document(kind="pasted", text=source["text"])
    return documents.read_document(source["data"], source["name"])


if sources:
    st.caption(
        f"**{len(sources)} document(s) queued:** "
        + ", ".join(f"`{s['name']}`" for s in sources[:8])
        + (" …" if len(sources) > 8 else "")
    )
    with st.expander(f"Preview document 1 of {len(sources)}"):
        try:
            preview = load_source(sources[0])
            if preview.has_images:
                st.caption(
                    f"{preview.kind} · read as image(s) — the AI will look at "
                    f"{len(preview.images)} page(s)."
                )
                for image in preview.images[:2]:
                    st.image(image, width=420)
            elif preview.text.strip():
                st.caption(f"{preview.kind} · read as text")
                st.text(preview.text[:2000] + ("…" if len(preview.text) > 2000 else ""))
            else:
                st.warning("This document appears to be empty.")
            if preview.note:
                st.info(preview.note)
        except Exception as exc:  # noqa: BLE001
            st.error(f"Could not read the document: {exc}")


# --------------------------------------------------------------------------
# Step 2 — choose columns
# --------------------------------------------------------------------------
section(
    "2",
    "Columns",
    "These become the columns of the Excel register. Remove any you do not need.",
)

schema = DOCUMENT_TYPES[doc_type] + AUDIT_COLUMNS
all_labels = [label for _, label in schema]
chosen_labels = st.multiselect(
    "Columns for the Excel register",
    options=all_labels,
    default=all_labels,
)

chosen_fields = [(k, label) for k, label in schema if label in chosen_labels]


# --------------------------------------------------------------------------
# Step 3 — extract
# --------------------------------------------------------------------------
section(
    "3",
    "Extract and review",
    "One row is created for each line item in the document.",
)

if st.button("Extract fields", type="primary", disabled=not (sources and chosen_fields)):
    if not extractor.has_api_key():
        st.error("Add your AI key to `.env` first.")
    else:
        rows, low = [], []
        bar = st.progress(0.0, text="Starting…")

        for i, source in enumerate(sources):
            name = source["name"]
            bar.progress(i / len(sources), text=f"Reading {name}…")
            try:
                doc = load_source(source)
            except Exception as exc:  # noqa: BLE001
                st.error(f"{name}: could not read — {exc}")
                continue

            if doc.is_empty:
                st.warning(f"{name}: no readable content, skipped.")
                continue

            try:
                try:
                    records = extractor.extract_records(
                        doc.text, doc_type, chosen_fields, images=doc.images
                    )
                except TypeError:
                    # Very old cached extractor.py that predates image support.
                    values, confidence = extractor.extract_fields(
                        doc.text, doc_type, chosen_fields
                    )
                    records = [(values, confidence)]
            except Exception as exc:  # noqa: BLE001
                st.error(f"{name}: extraction failed")
                with st.expander("Error details (copy this if you ask for help)"):
                    _detail = getattr(extractor, "error_detail", None)
                    st.code(_detail(exc) if _detail else repr(exc))
                    st.caption(
                        f"Model: {extractor.model_name()} · "
                        f"text: {len(doc.text):,} chars · "
                        f"images: {len(doc.images)} · "
                        f"fields: {len(chosen_fields)}"
                    )
                continue

            labels = dict(chosen_fields)
            many = len(records) > 1
            for item_no, (values, confidence) in enumerate(records, start=1):
                row = dict(values)
                row["source_file"] = (
                    f"{name} [item {item_no}]" if many else name
                )
                row["extracted_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                rows.append(row)

                where = f"{name} item {item_no}" if many else name
                for key, level in confidence.items():
                    if level != "high":
                        low.append(f"{where} → {labels.get(key, key)} ({level})")

        bar.empty()
        st.session_state["rows"] = rows
        st.session_state["low"] = low
        # New key -> a fresh review grid, so rows from an older run cannot
        # linger and hide the newly extracted ones.
        st.session_state["grid_id"] = st.session_state.get("grid_id", 0) + 1
        if rows:
            st.success(
                f"Extracted {len(rows)} row(s) from {len(sources)} document(s). "
                "Check the values before exporting."
            )

# --- editable review grid ------------------------------------------------
if st.session_state["rows"]:
    keys = [k for k, _ in chosen_fields]
    labels = {k: label for k, label in chosen_fields}

    df = pd.DataFrame(st.session_state["rows"])
    for key in keys:
        if key not in df:
            df[key] = ""
    df = df[keys]

    st.caption("Click any cell to correct it. You can also add or delete rows.")
    edited = st.data_editor(
        df,
        hide_index=True,
        num_rows="dynamic",
        column_config={k: st.column_config.TextColumn(labels[k]) for k in keys},
        key=f"review_grid_{st.session_state.get('grid_id', 0)}",
    )

    if st.session_state["low"]:
        st.warning(
            "Check these fields carefully:\n\n"
            + "\n".join(f"- {item}" for item in st.session_state["low"])
        )

    # ----------------------------------------------------------------------
    # Step 4 — export
    # ----------------------------------------------------------------------
    section(
        "4",
        "Download",
        "Create a new register, or add these rows to an existing one.",
    )

    master = st.file_uploader(
        "Optional: append to an existing master register (.xlsx)",
        type=["xlsx"],
        key="master",
    )
    master_bytes = master.getvalue() if master else None
    if master_bytes:
        st.info("New rows will be added below the existing data in that file.")

    records = edited.fillna("").astype(str).to_dict("records")
    excel_bytes = build_excel(records, chosen_fields, master_bytes=master_bytes)

    st.download_button(
        "Download Excel",
        data=excel_bytes,
        file_name=default_filename(),
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary",
    )
else:
    st.info("No rows yet. Add a document above and press **Extract fields**.")
