"""
Asks the AI model to turn a document into clean field values.

The document arrives either as text (digital PDF, Word, txt, csv) or as images
(photo, scan, scanned PDF). Both are sent to the same model. Long documents are
split into batches and the records are merged, so there is no fixed page or row
limit.
"""

import base64
import json
import os
import re

from openai import OpenAI

# How much one API call carries. Scans go in small batches so the model can
# still read every page at full resolution.
IMAGE_PAGES_PER_CALL = 4
TEXT_CHARS_PER_CALL = 24_000
MAX_RECORDS = 1_000  # a sanity guard, not a feature limit


# --------------------------------------------------------------------------
# Settings (read from the .env file)
# --------------------------------------------------------------------------

def _api_key() -> str | None:
    return os.getenv("AI_API_KEY") or os.getenv("OPENAI_API_KEY")


def has_api_key() -> bool:
    return bool(_api_key())


def key_fingerprint() -> str:
    """A safe way to see *which* key the app is using."""
    key = _api_key() or ""
    if not key:
        return "not set"
    return f"{key[:6]}…{key[-4:]} ({len(key)} chars)"


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
# Prompt
# --------------------------------------------------------------------------

def _prompt(
    doc_type: str,
    fields: list[tuple[str, str]],
    has_images: bool,
    part: int = 1,
    parts: int = 1,
) -> str:
    field_lines = "\n".join(f"- {key}: {label}" for key, label in fields)
    source = (
        "The document is attached as one or more images (photos or scans). "
        "Read the text in the images carefully."
        if has_images
        else "The document text is given below."
    )
    part_note = ""
    if parts > 1:
        part_note = (
            f"\nThis is part {part} of {parts} of a longer document. Extract every "
            "line item you can see in THIS part. Do not invent or repeat items from "
            "other parts.\n"
        )
    return f"""You are a careful data-entry assistant for Indian import/export trade documents.

Document type: {doc_type}
{source}
{part_note}
Extract these fields:
{field_lines}

Rules:
- Reply with ONLY valid JSON, in exactly this shape:
  {{"records": [{{"fields": {{"<key>": "<value>"}}, "confidence": {{"<key>": "high"|"medium"|"low"}}}}]}}
- Return ONE record for EVERY line item (every row of goods/services) in the document.
  A document with thirty item rows must produce thirty records. Never stop early
  and never merge rows together.
- Document-level values (invoice number, date, seller, buyer, currency, total) must be
  repeated in every record, so each row stands on its own.
- If the document contains several separate invoices, return one record per line item
  and keep each invoice's own header values.
- Use the exact field keys listed above.
- Copy values exactly as printed. Do NOT invent, guess or calculate anything.
- Keep numbers as text so leading zeros are not lost (e.g. "000123").
- Keep dates in the format they appear in the document.
- If a field is missing or unreadable, use "" and confidence "low".
"""


def _content(text: str, images: list[bytes] | None) -> str | list[dict]:
    """Plain text when there are no images, otherwise text + image parts."""
    if not images:
        return text

    parts: list[dict] = [{"type": "text", "text": text}]
    for image in images:
        b64 = base64.b64encode(image).decode("ascii")
        parts.append(
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
            }
        )
    return parts


# --------------------------------------------------------------------------
# Parsing
# --------------------------------------------------------------------------

def _parse_json(raw: str) -> dict:
    """The model should return JSON, but sometimes wraps it in ``` fences."""
    raw = raw.strip()
    raw = re.sub(r"^```(?:json)?|```$", "", raw, flags=re.MULTILINE).strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        start, end = raw.find("{"), raw.rfind("}")
        if start != -1 and end != -1:
            return json.loads(raw[start : end + 1])
        raise


def _normalise(record: dict, fields: list[tuple[str, str]]) -> tuple[dict, dict]:
    values = record.get("fields", {}) or {}
    confidence = record.get("confidence", {}) or {}
    return (
        {key: str(values.get(key, "") or "") for key, _ in fields},
        {key: str(confidence.get(key, "low")) for key, _ in fields},
    )


def _records_from(data, fields: list[tuple[str, str]]) -> list[tuple[dict, dict]]:
    """Accept the new {"records": [...]} shape and the old {"fields": ...} one."""
    if isinstance(data, list):
        return [_normalise(r, fields) for r in data if isinstance(r, dict)]

    records = data.get("records")
    if isinstance(records, list):
        return [_normalise(r, fields) for r in records if isinstance(r, dict)]

    if "fields" in data:
        return [_normalise(data, fields)]

    return []


# --------------------------------------------------------------------------
# Chunking
# --------------------------------------------------------------------------

def _text_chunks(text: str, size: int = TEXT_CHARS_PER_CALL) -> list[str]:
    """Split on line boundaries so a table row is never cut in half."""
    if len(text) <= size:
        return [text]

    chunks: list[str] = []
    current = ""
    for line in text.splitlines(keepends=True):
        while len(line) > size:  # a single enormous line
            if current:
                chunks.append(current)
                current = ""
            chunks.append(line[:size])
            line = line[size:]
        if len(current) + len(line) > size and current:
            chunks.append(current)
            current = line
        else:
            current += line
    if current:
        chunks.append(current)
    return chunks


def _image_batches(images: list[bytes], size: int = IMAGE_PAGES_PER_CALL) -> list[list[bytes]]:
    return [images[i : i + size] for i in range(0, len(images), size)] or [[]]


def _plan(text: str, images: list[bytes]) -> list[tuple[str, list[bytes]]]:
    """Return the (text, images) pairs that make up one document."""
    if images:
        # Scanned documents: send pages in batches, carrying any embedded text
        # along with the first batch only.
        batches = _image_batches(images)
        return [(text if index == 0 else "", batch) for index, batch in enumerate(batches)]
    return [(chunk, []) for chunk in _text_chunks(text)]


# --------------------------------------------------------------------------
# Main calls
# --------------------------------------------------------------------------

def _extract_once(
    text: str,
    doc_type: str,
    fields: list[tuple[str, str]],
    images: list[bytes],
    part: int,
    parts: int,
) -> list[tuple[dict, dict]]:
    client = _client()
    prompt = _prompt(doc_type, fields, bool(images), part=part, parts=parts)

    if images:
        user_content = _content(prompt, images)
    else:
        user_content = prompt + "\n\nDOCUMENT TEXT:\n---\n" + text + "\n---\n"

    request = dict(
        model=model_name(),
        temperature=0,
        messages=[{"role": "user", "content": user_content}],
    )

    try:
        response = client.chat.completions.create(
            **request,
            response_format={"type": "json_object"},
        )
    except Exception as exc:  # noqa: BLE001
        # Some providers/models reject JSON mode (or certain prompts while it
        # is on). The prompt already asks for JSON, so retry once without it.
        message = str(exc).lower()
        if "response_format" not in message and "400" not in message:
            raise
        if "api key" in message or "permission" in message:
            raise
        response = client.chat.completions.create(**request)

    data = _parse_json(response.choices[0].message.content or "{}")
    return _records_from(data, fields)


def extract_records(
    text: str,
    doc_type: str,
    fields: list[tuple[str, str]],
    images: list[bytes] | None = None,
) -> list[tuple[dict, dict]]:
    """Return one (values, confidence) pair per line item in the document."""
    images = images or []
    plan = _plan(text, images)
    records: list[tuple[dict, dict]] = []

    for index, (chunk_text, chunk_images) in enumerate(plan, start=1):
        records.extend(
            _extract_once(
                chunk_text,
                doc_type,
                fields,
                chunk_images,
                part=index,
                parts=len(plan),
            )
        )
        if len(records) >= MAX_RECORDS:
            records = records[:MAX_RECORDS]
            break

    if not records:
        empty = {key: "" for key, _ in fields}
        records = [(empty, {key: "low" for key, _ in fields})]

    return records


def extract_fields(
    text: str,
    doc_type: str,
    fields: list[tuple[str, str]],
    images: list[bytes] | None = None,
) -> tuple[dict, dict]:
    """Return the first record's (values, confidence)."""
    return extract_records(text, doc_type, fields, images=images)[0]


def error_detail(exc: Exception) -> str:
    """Full error text, including the API's own explanation when available."""
    parts = [str(exc)]
    response = getattr(exc, "response", None)
    if response is not None:
        try:
            body = response.text or ""
        except Exception:  # noqa: BLE001
            body = ""
        if body and body not in parts[0]:
            parts.append(body[:2000])
    return "\n\n".join(parts)[:3000]


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
