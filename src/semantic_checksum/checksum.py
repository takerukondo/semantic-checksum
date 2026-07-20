"""Normalize and hash the frozen 5-field semantic checksum."""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any

from semantic_checksum import FIELDS

_WS = re.compile(r"\s+")


def _norm_text(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip().lower()
    text = _WS.sub(" ", text)
    return text


def normalize_fields(fields: dict[str, Any]) -> dict[str, str]:
    """Return the five fields as normalized strings. Missing keys → empty."""
    out: dict[str, str] = {}
    for key in FIELDS:
        out[key] = _norm_text(fields.get(key, ""))
    return out


def field_checksum(fields: dict[str, Any]) -> dict[str, str]:
    """Per-field SHA256 (hex, 16 chars) over normalized values."""
    norm = normalize_fields(fields)
    return {k: hashlib.sha256(v.encode("utf-8")).hexdigest()[:16] for k, v in norm.items()}


def bundle_checksum(fields: dict[str, Any]) -> str:
    """Single checksum over the ordered normalized field map."""
    norm = normalize_fields(fields)
    payload = json.dumps(norm, ensure_ascii=False, separators=(",", ":"), sort_keys=False)
    # preserve field order from FIELDS
    ordered = {k: norm[k] for k in FIELDS}
    payload = json.dumps(ordered, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:32]


def extract_marked(text: str) -> dict[str, str]:
    """
    Deterministic extractor for fixtures that mark fields as:
      [[amount:100]] [[deadline:2026-08-01]] ...
    Unknown / unmarked fields stay empty. No LLM. No embeddings.
    """
    pattern = re.compile(
        r"\[\[(amount|deadline|actor|obligation|exception)\s*:\s*(.*?)\]\]",
        re.IGNORECASE | re.DOTALL,
    )
    found: dict[str, str] = {k: "" for k in FIELDS}
    for match in pattern.finditer(text or ""):
        key = match.group(1).lower()
        found[key] = match.group(2).strip()
    return found
