"""
Asks the AI model to turn a document into clean field values.

The document arrives either as text (digital PDF, Word, txt) or as images
(photo, scan, scanned PDF). Both are sent to the same model.
"""

import base64
import json
import os
import re

from openai import OpenAI


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

def _prompt(doc_type: str, fields: list[tuple[str, str]], has_images: bool) -> str:
    field_lines = "\n".join(f"- {key}: {label}" for key, label in fields)
    source = (
        "The document is attached as one or more images (photos or scans). "
        "Read the text in the images carefully."
        if has_images
        else "The document text is given below."
    )
    return f"""You are a careful data-entry assistant for Indian import/export trade documents.

Document type: {doc_type}
{source}

Extract these fields:
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


# --------------------------------------------------------------------------
# Main call
# --------------------------------------------------------------------------

def extract_fields(
    text: str,
    doc_type: str,
    fields: list[tuple[str, str]],
    images: list[bytes] | None = None,
) -> tuple[dict, dict]:
    """Return (values, confidence) for the requested fields."""
    client = _client()
    prompt = _prompt(doc_type, fields, bool(images))

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

    values = data.get("fields", {}) or {}
    confidence = data.get("confidence", {}) or {}

    # Keep only the fields we asked for, and make sure every key exists.
    values = {key: str(values.get(key, "") or "") for key, _ in fields}
    confidence = {key: str(confidence.get(key, "low")) for key, _ in fields}
    return values, confidence


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
