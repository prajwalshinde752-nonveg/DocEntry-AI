"""
Reading documents and pulling out field values.

Two steps:
  1. extract_text()   -> gets the raw text out of a PDF
  2. extract_fields() -> asks an AI model to turn that text into clean values
"""

import json
import os
import re
from io import BytesIO

import pdfplumber
from openai import OpenAI


# --------------------------------------------------------------------------
# Settings (read from the .env file)
# --------------------------------------------------------------------------

def _api_key() -> str | None:
    return os.getenv("AI_API_KEY") or os.getenv("OPENAI_API_KEY")


def has_api_key() -> bool:
    return bool(_api_key())


def model_name() -> str:
    return os.getenv("AI_MODEL", "gemini-3.1-flash-lite")


def _client() -> OpenAI:
    key = _api_key()
    if not key:
        raise RuntimeError(
            "No API key found. Copy .env.example to .env and put your key in it."
        )
    base_url = os.getenv("AI_BASE_URL") or None
    return OpenAI(api_key=key, base_url=base_url)


# --------------------------------------------------------------------------
# Step 1: PDF -> text
# --------------------------------------------------------------------------

def extract_text(pdf_bytes: bytes) -> str:
    """Read all pages of a digital PDF and return the text.

    Scanned PDFs contain images, not text, so this returns almost nothing for
    them. The app detects that and asks the user to use a text-based PDF.
    """
    parts: list[str] = []
    with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            parts.append(page.extract_text() or "")
    return "\n".join(parts).strip()


def looks_scanned(text: str) -> bool:
    return len(text.strip()) < 40


# --------------------------------------------------------------------------
# Step 2: text -> field values (the AI part)
# --------------------------------------------------------------------------

def _prompt(doc_type: str, fields: list[tuple[str, str]], text: str) -> str:
    field_lines = "\n".join(f"- {key}: {label}" for key, label in fields)
    return f"""You are a careful data-entry assistant for Indian import/export trade documents.

Document type: {doc_type}

Extract these fields from the document text:
{field_lines}

Rules:
- Reply with ONLY valid JSON, in exactly this shape:
  {{"fields": {{"<key>": "<value>"}}, "confidence": {{"<key>": "high" | "medium" | "low"}}}}
- Use the exact field keys listed above.
- Copy values exactly as printed. Do NOT invent, guess or calculate anything.
- Keep numbers as text so leading zeros are not lost (e.g. "000123").
- Keep dates in the format they appear in the document.
- If a field is missing or unreadable, use "" and confidence "low".
- If there are multiple items, put the first item's values in the fields.

DOCUMENT TEXT:
---
{text}
---
"""


def _parse_json(raw: str) -> dict:
    """The model should return JSON, but sometimes wraps it in ``` fences."""
    raw = raw.strip()
    raw = re.sub(r"^```(?:json)?|```$", "", raw, flags=re.MULTILINE).strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Last resort: grab the outermost { ... }
        start, end = raw.find("{"), raw.rfind("}")
        if start != -1 and end != -1:
            return json.loads(raw[start : end + 1])
        raise


def extract_fields(
    text: str,
    doc_type: str,
    fields: list[tuple[str, str]],
) -> tuple[dict, dict]:
    """Return (values, confidence) for the requested fields."""
    client = _client()
    prompt = _prompt(doc_type, fields, text)

    request = dict(
        model=model_name(),
        temperature=0,
        messages=[{"role": "user", "content": prompt}],
    )

    try:
        response = client.chat.completions.create(
            **request,
            response_format={"type": "json_object"},
        )
    except Exception as exc:  # noqa: BLE001
        # Some providers/models do not support JSON mode. The prompt already
        # asks for JSON, so retry without it instead of failing.
        if "response_format" not in str(exc).lower():
            raise
        response = client.chat.completions.create(**request)

    data = _parse_json(response.choices[0].message.content or "{}")

    values = data.get("fields", {}) or {}
    confidence = data.get("confidence", {}) or {}

    # Keep only the fields we asked for, and make sure every key exists.
    values = {key: str(values.get(key, "") or "") for key, _ in fields}
    confidence = {key: str(confidence.get(key, "low")) for key, _ in fields}
    return values, confidence


def test_connection() -> tuple[bool, str]:
    """Send one tiny request so the user can check their key and model."""
    try:
        client = _client()
        response = client.chat.completions.create(
            model=model_name(),
            messages=[{"role": "user", "content": "Reply with the single word: ok"}],
        )
        reply = (response.choices[0].message.content or "").strip()
        return True, reply or "(empty reply, but the connection worked)"
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)

