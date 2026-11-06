"""
DocEntry-AI — turn trade documents into Excel rows.

Run with:   streamlit run app.py
"""

import os
from datetime import datetime

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

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

st.set_page_config(page_title="DocEntry-AI", page_icon="📄", layout="wide")

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
    st.title("📄 DocEntry-AI")
    st.caption("Documents in. Clean Excel rows out.")

    doc_type = st.selectbox("Document type", list(DOCUMENT_TYPES))

    st.divider()
    if extractor.has_api_key():
        st.success("AI key loaded")
    else:
        st.error("No AI key found")
        st.caption("Copy `.env.example` to `.env` and add your key.")
    st.caption(f"Model: `{extractor.model_name()}`")

    if st.button("Test connection", use_container_width=True):
        ok, message = extractor.test_connection()
        if ok:
            st.success(f"Works. Model replied: {message}")
        else:
            st.error("Connection failed")
            st.code(message[:800])

    st.divider()
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
st.title("Trade Document → Excel")
st.caption(
    "Upload a document, pick the columns you need, check the extracted values, "
    "then download the register."
)


# --------------------------------------------------------------------------
# Step 1 — upload
# --------------------------------------------------------------------------
st.subheader("1 · Upload documents")
files = st.file_uploader(
    "PDF files (one or many)",
    type=["pdf"],
    accept_multiple_files=True,
)

if files:
    with st.expander("Preview extracted text from the first file"):
        try:
            preview = extractor.extract_text(files[0].getvalue())
            if extractor.looks_scanned(preview):
                st.warning(
                    "This PDF has almost no text in it — it is probably a scan. "
                    "Text extraction needs a digital (text-based) PDF for now."
                )
            else:
                st.text(preview[:2000] + ("…" if len(preview) > 2000 else ""))
        except Exception as exc:  # noqa: BLE001
            st.error(f"Could not read the PDF: {exc}")


# --------------------------------------------------------------------------
# Step 2 — choose columns
# --------------------------------------------------------------------------
st.subheader("2 · Choose columns")

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
st.subheader("3 · Extract and review")

if st.button("Extract fields", type="primary", disabled=not (files and chosen_fields)):
    if not extractor.has_api_key():
        st.error("Add your AI key to `.env` first.")
    else:
        rows, low = [], []
        bar = st.progress(0.0, text="Starting…")

        for i, file in enumerate(files):
            bar.progress(i / len(files), text=f"Reading {file.name}…")
            try:
                text = extractor.extract_text(file.getvalue())
            except Exception as exc:  # noqa: BLE001
                st.error(f"{file.name}: could not read PDF — {exc}")
                continue

            if extractor.looks_scanned(text):
                st.warning(f"{file.name}: looks like a scanned PDF, skipped.")
                continue

            try:
                values, confidence = extractor.extract_fields(text, doc_type, chosen_fields)
            except Exception as exc:  # noqa: BLE001
                st.error(f"{file.name}: extraction failed — {exc}")
                continue

            row = dict(values)
            row["source_file"] = file.name
            row["extracted_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            rows.append(row)

            labels = dict(chosen_fields)
            for key, level in confidence.items():
                if level != "high":
                    low.append(f"{file.name} → {labels.get(key, key)} ({level})")

        bar.empty()
        st.session_state["rows"] = rows
        st.session_state["low"] = low
        if rows:
            st.success(f"Extracted {len(rows)} document(s). Check the values before exporting.")

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
        key="review_grid",
    )

    if st.session_state["low"]:
        st.warning(
            "Check these fields carefully:\n\n"
            + "\n".join(f"- {item}" for item in st.session_state["low"])
        )

    # ----------------------------------------------------------------------
    # Step 4 — export
    # ----------------------------------------------------------------------
    st.subheader("4 · Download the register")

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
    st.info("Nothing extracted yet. Upload a PDF and press **Extract fields**.")
