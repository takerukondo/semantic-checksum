"""Score a golden set of adversarial bilingual pairs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from semantic_checksum import FIELDS
from semantic_checksum.checksum import extract_marked
from semantic_checksum.diff import field_diff


def load_golden(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("golden file must be a JSON list")
    return data


def score_pair(pair: dict[str, Any]) -> dict[str, Any]:
    """
    Each pair provides en/ja texts (with [[field:value]] marks) and
    expected_mismatched_fields (list of field names that should differ).
    """
    en_fields = extract_marked(pair["en"])
    ja_fields = extract_marked(pair["ja"])
    # allow explicit field overrides for cases without marks
    if "en_fields" in pair:
        en_fields = {**en_fields, **pair["en_fields"]}
    if "ja_fields" in pair:
        ja_fields = {**ja_fields, **pair["ja_fields"]}

    diff = field_diff(en_fields, ja_fields)
    expected = sorted(pair.get("expected_mismatched_fields", []))
    got = sorted(diff["mismatched_fields"])
    ok = expected == got
    return {
        "id": pair.get("id", "?"),
        "ok": ok,
        "expected": expected,
        "got": got,
        "attack": pair.get("attack", ""),
        "diff": diff,
    }


def score_golden(path: Path) -> dict[str, Any]:
    pairs = load_golden(path)
    results = [score_pair(p) for p in pairs]
    passed = sum(1 for r in results if r["ok"])
    failed = [r["id"] for r in results if not r["ok"]]
    return {
        "total": len(results),
        "passed": passed,
        "failed": failed,
        "accuracy": (passed / len(results)) if results else 0.0,
        "fields": list(FIELDS),
        "results": results,
    }
