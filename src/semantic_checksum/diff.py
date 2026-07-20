"""Field-level checksum diff."""

from __future__ import annotations

from typing import Any

from semantic_checksum import FIELDS
from semantic_checksum.checksum import field_checksum, normalize_fields


def field_diff(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    """Compare two field maps. Returns mismatches + normalized views."""
    left_n = normalize_fields(left)
    right_n = normalize_fields(right)
    left_c = field_checksum(left)
    right_c = field_checksum(right)
    mismatched = [k for k in FIELDS if left_c[k] != right_c[k]]
    return {
        "mismatched_fields": mismatched,
        "match": len(mismatched) == 0,
        "left": left_n,
        "right": right_n,
        "left_checksums": left_c,
        "right_checksums": right_c,
    }
