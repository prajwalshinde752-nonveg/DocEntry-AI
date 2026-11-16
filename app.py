"""
DocEntry-AI — turn trade documents into Excel rows.

Run with:   streamlit run app.py
"""

import os
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

import documents
import extractor
import history
import validation
from excel_writer import build_csv, build_json, build_workbook, default_filename
from schemas import (
    AUDIT_COLUMNS,
    DOCUMENT_TYPES,
    merge_columns,
    parse_custom_columns,
)

load_dotenv(override=True)

CUSTOM_OPTION = "Custom document type"


def _load_cloud_secrets() -> None:
    """Locally the key comes from .env; on Cloud it comes from st.secrets."""
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

      /* dark charcoal surfaces */
      .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
          background-color: #23272B;
      }
      [data-testid="stSidebar"] { background-color: #1D2125; }
      [data-testid="stHeader"] { background-color: #23272B; }
      [data-testid="stFileUploaderDropzone"] {
          background-color: #2B3035; border-color: #3B4147;
      }
      [data-testid="stFileUploaderDropzone"]:hover { border-color: #4F7196; }
      .stTextInput input, .stTextArea textarea,
      [data-baseweb="input"], [data-baseweb="textarea"],
      [data-baseweb="select"] > div {
          background-color: #2B3035 !important;
          border-color: #3B4147 !important;
          color: #E3E6E8 !important;
      }
      .stButton > button {
          background-color: #2F353A; border: 1px solid #3B4147; color: #E3E6E8;
      }
      .stButton > button:hover {
          background-color: #383F45; border-color: #4F7196; color: #F5F7F8;
      }
      .stButton > button[kind="primary"] {
          background-color: #4F7196; border-color: #4F7196; color: #F5F7F8;
      }
      [data-testid="stExpander"] details {
          background-color: #2B3035; border-color: #3B4147;
      }
      [data-testid="stDataFrame"], [data-testid="stDataEditor"] {
          background-color: #2B3035;
      }
      .stTabs [data-baseweb="tab-list"] { background-color: transparent; }
      .stTabs [data-baseweb="tab"] { color: #A2ABB2; }
      .stTabs [aria-selected="true"] { color: #F5F7F8; }
      [data-baseweb="popover"] ul, [role="listbox"] { background-color: #2B3035; }
      .stCode, pre { background-color: #1D2125 !important; }
      [data-testid="stMarkdownContainer"] p { color: #E3E6E8; }
      label, .stSelectbox label { color: #A2ABB2 !important; }
      [data-testid="stWidgetLabel"] p { color: #A2ABB2; }

      /* masthead */
      .de-head {
          background: #21364F;
          border-radius: 4px;
          padding: 24px 28px 22px;
          margin-bottom: 10px;
      }
      .de-head .de-kicker {
          font-size: 10.5px; letter-spacing: .16em; text-transform: uppercase;
          color: #A6B4C4; font-weight: 600; margin-bottom: 8px;
      }
      .de-head h1 {
          font-size: 29px; line-height: 1.15; color: #F5F7F8;
          font-weight: 600; letter-spacing: -.01em; margin: 0 0 9px; padding: 0;
      }
      .de-head p {
          color: #D2D9E0; font-size: 14px; line-height: 1.55;
          margin: 0; max-width: 68ch;
      }

      /* step strip */
      .de-steps {
          display: flex; flex-wrap: wrap; align-items: center; gap: 10px;
          background: #2B3035; border: 1px solid #3B4147; border-radius: 4px;
          padding: 12px 18px; margin: 0 0 26px;
      }
      .de-step {
          display: flex; align-items: center; gap: 8px;
          font-size: 12.5px; color: #E4E6E8;
      }
      .de-step b {
          display: inline-flex; align-items: center; justify-content: center;
          width: 19px; height: 19px; border-radius: 50%;
          background: #454C53; color: #F5F7F8;
          font-size: 11px; font-weight: 600;
      }
      .de-sep { width: 1px; height: 16px; background: #454C53; }

      /* section headings */
      .de-section {
          display: flex; align-items: baseline; gap: 11px;
          margin: 32px 0 2px;
      }
      .de-section .de-num {
          font-size: 11px; font-weight: 600; color: #B9C8D6;
          background: #2E3439; border-radius: 3px; padding: 3px 9px;
          letter-spacing: .08em;
      }
      .de-section .de-title {
          font-size: 19px; font-weight: 600; color: #E3E6E8;
          letter-spacing: -.01em;
      }
      .de-hint {
          font-size: 13px; color: #A2ABB2; margin: 0 0 12px;
      }

      /* sidebar */
      .de-brand { display: flex; align-items: center; gap: 10px; }
      .de-brand .de-mark {
          width: 30px; height: 30px; border-radius: 6px;
          background: #21364F; color: #F5F7F8;
          font-size: 12.5px; font-weight: 700;
          display: flex; align-items: center; justify-content: center;
      }
      .de-brand .de-name {
          font-size: 16.5px; font-weight: 600; color: #E3E6E8;
          letter-spacing: -.01em;
      }
      .de-brand-sub {
          font-size: 12px; color: #98A1A8;
          margin: 3px 0 22px 40px;
      }
      .de-label {
          font-size: 10.5px; letter-spacing: .12em; text-transform: uppercase;
          color: #98A1A8; font-weight: 600; margin: 0 0 5px;
      }
      .de-status {
          border-left: 2px solid #4F7196;
          padding: 2px 0 2px 11px;
          font-size: 12.5px; line-height: 1.75; color: #A2ABB2;
      }
      .de-status b { color: #E3E6E8; font-weight: 600; }
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
st.session_state.setdefault("issues", [])
st.session_state.setdefault("batch", [])
st.session_state.setdefault("current_uid", None)
st.session_state.setdefault("grid_id", 0)
st.session_state.setdefault("custom_doc_types", {})
st.session_state.setdefault("custom_text", "")
st.session_state.setdefault("preset_extra", [])

if not st.session_state.get("_types_loaded"):
    try:
        st.session_state["custom_doc_types"] = history.list_doc_types()
    except Exception:  # noqa: BLE001 - history is optional
        st.session_state["custom_doc_types"] = {}
    st.session_state["_types_loaded"] = True


def _safe_runs(limit: int = 30) -> list[dict]:
    try:
        return history.list_runs(limit)
    except Exception:  # noqa: BLE001
        return []


def _safe_presets() -> list[dict]:
    try:
        return history.list_presets()
    except Exception:  # noqa: BLE001
        return []


def _add_to_batch(run: dict) -> None:
    """Append a run and make it the one shown in the review grid."""
    batch = st.session_state["batch"]

    # Re-opening a saved run should refresh it, not add a second copy.
    if run.get("db_id"):
        for item in batch:
            if item.get("db_id") == run["db_id"]:
                run["uid"] = item["uid"]
                break

    st.session_state["batch"] = [
        item for item in batch if item["uid"] != run["uid"]
    ] + [run]
    st.session_state["current_uid"] = run["uid"]
    st.session_state["rows"] = run["rows"]
    st.session_state["issues"] = run.get("issues", [])
    st.session_state["low"] = run.get("low", [])
    st.session_state["grid_id"] = st.session_state.get("grid_id", 0) + 1


def _find_run(uid: str | None) -> dict | None:
    if not uid:
        return None
    for run in st.session_state["batch"]:
        if run["uid"] == uid:
            return run
    return None


def _run_from_history(run: dict) -> dict:
    return {
        "uid": uuid4().hex,
        "db_id": run.get("id"),
        "doc_type": run["doc_type"],
        "label": run.get("label") or run["doc_type"],
        "rows": run["rows"],
        "columns": run["columns"],
        "issues": run.get("issues", []),
        "low": [],
        "created_at": run.get("created_at") or datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


def _base_columns(doc_type: str) -> list[tuple[str, str]]:
    return DOCUMENT_TYPES.get(doc_type) or st.session_state["custom_doc_types"].get(doc_type, [])


def _apply_run_settings(run: dict) -> None:
    """Point the sidebar and column picker at a saved run (before widgets render)."""
    doc_type = run["doc_type"]
    options = (
        list(DOCUMENT_TYPES)
        + list(st.session_state["custom_doc_types"])
        + [CUSTOM_OPTION]
    )
    options = list(dict.fromkeys(options))
    if doc_type in options:
        st.session_state["doc_type_select"] = doc_type
        st.session_state["custom_name"] = ""
    else:
        st.session_state["doc_type_select"] = CUSTOM_OPTION
        st.session_state["custom_name"] = doc_type
    st.session_state["custom_name_input"] = st.session_state["custom_name"]

    st.session_state["type_sig"] = st.session_state["doc_type_select"]

    base = _base_columns(doc_type) + AUDIT_COLUMNS
    base_keys = {key for key, _ in base}
    base_labels = {label for _, label in base}
    st.session_state["preset_extra"] = [
        (key, label)
        for key, label in run["columns"]
        if key not in base_keys and label not in base_labels
    ]
    st.session_state["columns_override"] = [label for _, label in run["columns"]]


# Process a deferred "Review" click before the sidebar widgets are created.
_pending_load = st.session_state.pop("_pending_load_id", None)
if _pending_load:
    try:
        _db_run = history.get_run(_pending_load)
    except Exception:  # noqa: BLE001
        _db_run = None
    if _db_run:
        _saved_run = _run_from_history(_db_run)
        _apply_run_settings(_saved_run)
        _add_to_batch(_saved_run)


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
    type_options = (
        list(DOCUMENT_TYPES)
        + list(st.session_state["custom_doc_types"])
        + [CUSTOM_OPTION]
    )
    type_options = list(dict.fromkeys(type_options))
    if st.session_state.get("doc_type_select") not in type_options:
        st.session_state["doc_type_select"] = type_options[0]

    doc_type_selection = st.selectbox(
        "Document type", type_options, key="doc_type_select", label_visibility="collapsed"
    )

    if doc_type_selection == CUSTOM_OPTION:
        if "custom_name_input" not in st.session_state:
            st.session_state["custom_name_input"] = st.session_state.get("custom_name", "")
        custom_name = st.text_input(
            "Name this document type",
            key="custom_name_input",
            placeholder="e.g. Freight Invoice",
        )
        st.session_state["custom_name"] = custom_name
        effective_doc_type = custom_name.strip() or "Custom document"
        type_schema = []
    else:
        effective_doc_type = doc_type_selection
        type_schema = _base_columns(effective_doc_type)

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

    if st.button("Reset review", use_container_width=True):
        st.session_state["rows"] = []
        st.session_state["low"] = []
        st.session_state["issues"] = []
        st.session_state["current_uid"] = None
        st.session_state["grid_id"] = st.session_state.get("grid_id", 0) + 1
        st.rerun()

    # ---- history ----------------------------------------------------------
    recent = _safe_runs(15)
    with st.expander(f"History · {len(recent)} run(s)"):
        if not recent:
            st.caption("Runs are saved here after each extraction.")
        for item in recent:
            st.markdown(
                f"**{item['doc_type']}** · {item['row_count']} row(s)  \n"
                f"<span style='font-size:11px;color:#98A1A8'>{item['created_at']}</span>",
                unsafe_allow_html=True,
            )
            cols = st.columns(3)
            if cols[0].button("Review", key=f"hist_review_{item['id']}", use_container_width=True):
                st.session_state["_pending_load_id"] = item["id"]
                st.rerun()
            if cols[1].button("Add", key=f"hist_add_{item['id']}", use_container_width=True):
                try:
                    db_run = history.get_run(item["id"])
                except Exception as exc:  # noqa: BLE001
                    st.warning(f"Could not load the run: {exc}")
                else:
                    if db_run:
                        _add_to_batch(_run_from_history(db_run))
                st.rerun()
            if cols[2].button("Delete", key=f"hist_del_{item['id']}", use_container_width=True):
                try:
                    history.delete_run(item["id"])
                except Exception as exc:  # noqa: BLE001
                    st.warning(f"Could not delete the run: {exc}")
                st.rerun()
            st.divider()

        if recent and st.button("Clear all history", use_container_width=True):
            try:
                history.clear_runs()
            except Exception as exc:  # noqa: BLE001
                st.warning(f"Could not clear history: {exc}")
            st.rerun()


# A different document type means the old rows no longer make sense.
if st.session_state.get("type_sig") != doc_type_selection:
    st.session_state["type_sig"] = doc_type_selection
    st.session_state["rows"] = []
    st.session_state["low"] = []
    st.session_state["issues"] = []
    st.session_state["current_uid"] = None
    st.session_state["columns_override"] = None
    st.session_state["columns_ms"] = None
    st.session_state["preset_extra"] = []


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
    <div class="de-steps">
      <span class="de-step"><b>1</b> Documents</span>
      <span class="de-sep"></span>
      <span class="de-step"><b>2</b> Columns</span>
      <span class="de-sep"></span>
      <span class="de-step"><b>3</b> Extract and review</span>
      <span class="de-sep"></span>
      <span class="de-step"><b>4</b> Download</span>
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
                    f"{len(preview.images)} page(s), in batches."
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
    "These become the columns of the Excel register. Add your own, or apply a saved preset.",
)

with st.expander("Custom columns"):
    st.caption(
        "One column per line — `key=Heading` or just `Heading`. "
        "Example: `freight=Freight Charges`."
    )
    st.text_area(
        "Custom columns",
        key="custom_text",
        height=110,
        placeholder="Freight Charges\ndiscount=Discount %",
        label_visibility="collapsed",
    )

custom_fields = parse_custom_columns(st.session_state.get("custom_text", ""))
extra_columns = merge_columns(custom_fields, st.session_state.get("preset_extra", []))
schema = merge_columns(type_schema, extra_columns, AUDIT_COLUMNS)
all_labels = [label for _, label in schema]

override = st.session_state.pop("columns_override", None)
selected_state = st.session_state.get("columns_ms")
if override:
    selected = override
elif selected_state is None:
    selected = all_labels
else:
    selected = [label for label in selected_state if label in all_labels]
    if selected_state and not selected:
        selected = all_labels

st.session_state["columns_ms"] = selected

# A newly added custom column should appear selected, while fields the user
# deliberately removed stay removed.
known_labels = st.session_state.get("known_labels") or []
new_labels = [label for label in all_labels if label not in known_labels]
if new_labels and not override:
    keep = set(selected) | set(new_labels)
    selected = [label for label in all_labels if label in keep]
    st.session_state["columns_ms"] = selected
st.session_state["known_labels"] = list(all_labels)

chosen_labels = st.multiselect(
    "Columns for the Excel register",
    options=all_labels,
    key="columns_ms",
)

chosen_fields = [(key, label) for key, label in schema if label in chosen_labels]

if doc_type_selection == CUSTOM_OPTION:
    saved_name = (st.session_state.get("custom_name") or "").strip()
    label_col, button_col = st.columns([3, 1])
    label_col.caption(
        f"Fields define the **{saved_name or 'custom'}** document type. "
        "Save it to reuse the same fields later."
    )
    if button_col.button(
        "Save document type",
        disabled=not (saved_name and extra_columns) or saved_name in DOCUMENT_TYPES,
    ):
        stored = merge_columns(type_schema, extra_columns)
        st.session_state["custom_doc_types"][saved_name] = stored
        try:
            history.save_doc_type(saved_name, stored)
        except Exception as exc:  # noqa: BLE001
            st.warning(f"Could not save the document type: {exc}")
        else:
            st.success(f"Saved document type “{saved_name}”.")
            st.rerun()

# ---- presets --------------------------------------------------------------
with st.expander("Column presets"):
    presets = _safe_presets()
    names = [preset["name"] for preset in presets]

    if names:
        if st.session_state.get("preset_choice") not in names:
            st.session_state["preset_choice"] = names[0]
        chosen_preset = st.selectbox("Saved presets", names, key="preset_choice")
        apply_col, delete_col = st.columns(2)
        if apply_col.button("Apply preset", use_container_width=True):
            preset = next(p for p in presets if p["name"] == chosen_preset)
            keep_keys = {key for key, _ in type_schema + AUDIT_COLUMNS}
            keep_labels = {label for _, label in type_schema + AUDIT_COLUMNS}
            st.session_state["preset_extra"] = [
                (key, label)
                for key, label in preset["columns"]
                if key not in keep_keys and label not in keep_labels
            ]
            st.session_state["columns_override"] = [label for _, label in preset["columns"]]
            st.rerun()
        if delete_col.button("Delete preset", use_container_width=True):
            try:
                history.delete_preset(chosen_preset)
            except Exception as exc:  # noqa: BLE001
                st.warning(f"Could not delete the preset: {exc}")
            st.rerun()
    else:
        st.caption("No presets saved yet.")

    preset_name = st.text_input("Save current columns as", placeholder="e.g. GST register")
    if st.button("Save preset", disabled=not (preset_name.strip() and chosen_fields)):
        try:
            history.save_preset(preset_name.strip(), chosen_fields)
        except Exception as exc:  # noqa: BLE001
            st.error(f"Could not save the preset: {exc}")
        else:
            st.success(f"Preset “{preset_name.strip()}” saved.")
            st.rerun()

if not chosen_fields:
    st.warning("Choose at least one column before extracting.")


# --------------------------------------------------------------------------
# Step 3 — extract
# --------------------------------------------------------------------------
section(
    "3",
    "Extract and review",
    "One row is created for each line item in the document. Long documents are read in batches.",
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
                        doc.text, effective_doc_type, chosen_fields, images=doc.images
                    )
                except TypeError:
                    # Very old cached extractor.py that predates image support.
                    values, confidence = extractor.extract_fields(
                        doc.text, effective_doc_type, chosen_fields
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

        if rows:
            issues = validation.validate_rows(rows)
            uid = uuid4().hex
            try:
                db_id = history.save_run(
                    effective_doc_type, rows, chosen_fields, issues
                )
            except Exception:  # noqa: BLE001
                db_id = None

            run = {
                "uid": uid,
                "db_id": db_id,
                "doc_type": effective_doc_type,
                "label": f"{effective_doc_type} · {len(rows)} row(s)",
                "rows": rows,
                "columns": chosen_fields,
                "issues": issues,
                "low": low,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            }
            _add_to_batch(run)
            st.success(
                f"Extracted {len(rows)} row(s) from {len(sources)} document(s). "
                "Check the values before exporting."
            )
            if db_id:
                st.caption("Saved to history.")
        else:
            st.warning("No rows were extracted. Check the error messages above.")


# --- editable review grid ------------------------------------------------
current_run = _find_run(st.session_state.get("current_uid"))
if st.session_state["rows"] and current_run:
    keys = [key for key, _ in current_run["columns"]]
    labels = {key: label for key, label in current_run["columns"]}

    df = pd.DataFrame(st.session_state["rows"])
    for key in keys:
        if key not in df:
            df[key] = ""
    df = df[keys]

    # Checks are recomputed from what is on screen, so the Checks column is
    # current. They are stored again below after any edits.
    pre_issues = validation.validate_rows(df.fillna("").astype(str).to_dict("records"))
    st.session_state["issues"] = pre_issues
    issues_by_row = validation.issues_per_row(pre_issues)

    def _issue_text(index: int) -> str:
        row_issues = issues_by_row.get(index, [])
        return " · ".join(
            f"{labels.get(issue['key'], issue['key'])}: {issue['message']}"
            for issue in row_issues
        )

    df["_checks"] = [_issue_text(index) for index in range(len(df))]

    st.caption("Click any cell to correct it. You can also add or delete rows.")
    edited = st.data_editor(
        df,
        hide_index=True,
        num_rows="dynamic",
        disabled=["_checks"],
        column_config={
            **{key: st.column_config.TextColumn(labels[key]) for key in keys},
            "_checks": st.column_config.TextColumn("Checks", width="large"),
        },
        key=f"review_grid_{st.session_state.get('grid_id', 0)}",
    )

    records = edited.drop(columns=["_checks"], errors="ignore").fillna("").astype(str).to_dict("records")
    post_issues = validation.validate_rows(records)
    current_run["rows"] = records
    current_run["issues"] = post_issues
    st.session_state["rows"] = records
    st.session_state["issues"] = post_issues

    if post_issues:
        st.warning(
            f"Checks: {validation.summarise(post_issues)}. "
            "Highlighted cells are also colour-coded in the Excel file."
        )
        with st.expander("See every check"):
            st.dataframe(
                pd.DataFrame(
                    [
                        {
                            "Row": issue["row"] + 1,
                            "Column": labels.get(issue["key"], issue["key"]),
                            "Level": issue["level"],
                            "Message": issue["message"],
                        }
                        for issue in post_issues
                    ]
                ),
                hide_index=True,
                use_container_width=True,
            )
    else:
        st.success("Checks passed: no GSTIN, HSN, total or duplicate issues found.")

    if st.session_state["low"]:
        st.warning(
            "Low-confidence fields — check these carefully:\n\n"
            + "\n".join(f"- {item}" for item in st.session_state["low"])
        )

else:
    if not st.session_state["batch"]:
        st.info("No rows yet. Add a document above and press **Extract fields**.")
    else:
        st.caption("Choose a run under History → Review, or extract a new document to edit it.")


# --------------------------------------------------------------------------
# Step 4 — export (this batch can contain several runs and document types)
# --------------------------------------------------------------------------
batch = st.session_state["batch"]
if batch:
    section(
        "4",
        "Download",
        "Export the whole batch, or add it to an existing register.",
    )

    total_rows = sum(len(item["rows"]) for item in batch)
    st.caption(f"**Batch:** {len(batch)} run(s), {total_rows} row(s).")

    with st.expander("Manage batch"):
        for item in list(batch):
            row_col, remove_col = st.columns([5, 1])
            row_col.markdown(
                f"**{item['doc_type']}** · {len(item['rows'])} row(s)  \n"
                f"<span style='font-size:11px;color:#98A1A8'>{item.get('created_at', '')}</span>",
                unsafe_allow_html=True,
            )
            if remove_col.button("Remove", key=f"batch_remove_{item['uid']}"):
                st.session_state["batch"] = [
                    candidate for candidate in batch if candidate["uid"] != item["uid"]
                ]
                if st.session_state.get("current_uid") == item["uid"]:
                    st.session_state["rows"] = []
                    st.session_state["issues"] = []
                    st.session_state["current_uid"] = None
                st.rerun()

        if st.button("Clear batch"):
            st.session_state["batch"] = []
            st.session_state["rows"] = []
            st.session_state["issues"] = []
            st.session_state["current_uid"] = None
            st.rerun()

    # Group runs by document type -> one sheet each.
    groups: dict[str, list[dict]] = {}
    for item in batch:
        groups.setdefault(item["doc_type"], []).append(item)

    sections: list[dict] = []
    for doc_type, runs in groups.items():
        columns = merge_columns(*[run["columns"] for run in runs])
        rows: list[dict] = []
        for run in runs:
            rows.extend(run["rows"])
        sections.append(
            {
                "name": doc_type,
                "columns": columns,
                "rows": rows,
                "issues": [],
            }
        )

    master = None
    if len(sections) == 1:
        master = st.file_uploader(
            "Optional: append to an existing master register (.xlsx)",
            type=["xlsx"],
            key="master",
        )
    elif len(sections) > 1:
        st.caption(
            "A master register can only be appended when the batch has one "
            "document type. This batch will download as a new multi-sheet workbook."
        )

    master_bytes = master.getvalue() if master else None
    if master_bytes:
        st.info("New rows will be added below the existing data in that file.")

    # Re-run checks with the master register so duplicates are caught too.
    for section_data in sections:
        section_data["issues"] = validation.validate_rows(
            section_data["rows"], master_bytes
        )

    all_issues = [issue for section_data in sections for issue in section_data["issues"]]
    if all_issues:
        st.warning(f"Final checks: {validation.summarise(all_issues)}.")
        with st.expander("See every final check"):
            st.dataframe(
                pd.DataFrame(
                    [
                        {
                            "Sheet": section_data["name"],
                            "Row": issue["row"] + 1,
                            "Column": dict(section_data["columns"]).get(
                                issue["key"], issue["key"]
                            ),
                            "Level": issue["level"],
                            "Message": issue["message"],
                        }
                        for section_data in sections
                        for issue in section_data["issues"]
                    ]
                ),
                hide_index=True,
                use_container_width=True,
            )
    elif sections:
        st.success("Final checks: no issues found.")

    try:
        excel_bytes = build_workbook(sections, master_bytes=master_bytes)
        csv_bytes = build_csv(sections)
        json_bytes = build_json(sections)
    except Exception as exc:  # noqa: BLE001
        st.error(f"Could not build the workbook: {exc}")
    else:
        prefix = "DocEntry_Batch" if len(sections) > 1 else "DocEntry_Register"
        filename = default_filename(prefix)
        download_col, csv_col, json_col = st.columns([2, 1, 1])
        download_col.download_button(
            "Download Excel",
            data=excel_bytes,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
            use_container_width=True,
        )
        csv_col.download_button(
            "CSV",
            data=csv_bytes,
            file_name=filename.replace(".xlsx", ".csv"),
            mime="text/csv",
            use_container_width=True,
        )
        json_col.download_button(
            "JSON",
            data=json_bytes,
            file_name=filename.replace(".xlsx", ".json"),
            mime="application/json",
            use_container_width=True,
        )

