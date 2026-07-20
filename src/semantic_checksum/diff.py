"""Field-level checksum diff."""

from __future__ import annotations

from typing import Any

from semantic_checksum import FIELDS
from semantic_checksum.checksum import field_checksum, normalize_fields


def field_diff(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    """Compare two field maps. Returns mismatches + normalized views."""
    left_n = normalize_fields(left)
    right_n = normalize_fields(right)
    missing_left = [key for key in FIELDS if not left_n[key]]
    missing_right = [key for key in FIELDS if not right_n[key]]
    left_c = field_checksum(left)
    right_c = field_checksum(right)
    mismatched = [k for k in FIELDS if left_c[k] != right_c[k]]
    return {
        "mismatched_fields": mismatched,
        # Two unannotated documents must not be reported as a successful match.
        "match": len(mismatched) == 0 and not missing_left and not missing_right,
        "complete": not missing_left and not missing_right,
        "missing_left": missing_left,
        "missing_right": missing_right,
        "left": left_n,
        "right": right_n,
        "left_checksums": left_c,
        "right_checksums": right_c,
    }
