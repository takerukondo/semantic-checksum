from __future__ import annotations

import json
from pathlib import Path

import pytest

from semantic_checksum.checksum import bundle_checksum, extract_marked, field_checksum
from semantic_checksum.diff import field_diff
from semantic_checksum.score import score_golden

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = ROOT / "data" / "golden.json"


def test_extract_marked_fields():
    text = "Pay [[amount:100]] by [[deadline:2026-08-01]] [[actor:buyer]]"
    fields = extract_marked(text)
    assert fields["amount"] == "100"
    assert fields["deadline"] == "2026-08-01"
    assert fields["actor"] == "buyer"
    assert fields["obligation"] == ""
    assert fields["exception"] == ""


def test_japanese_marks():
    text = "料金は[[amount:1000]]円。主体は[[actor:発注者]]。"
    fields = extract_marked(text)
    assert fields["amount"] == "1000"
    assert fields["actor"] == "発注者"


def test_field_diff_detects_amount():
    left = extract_marked("[[amount:100]] [[deadline:d]] [[actor:a]] [[obligation:must]] [[exception:none]]")
    right = extract_marked("[[amount:200]] [[deadline:d]] [[actor:a]] [[obligation:must]] [[exception:none]]")
    diff = field_diff(left, right)
    assert diff["mismatched_fields"] == ["amount"]
    assert diff["match"] is False


def test_checksum_deterministic():
    fields = {"amount": "100", "deadline": "D", "actor": "A", "obligation": "must", "exception": "none"}
    assert field_checksum(fields) == field_checksum(fields)
    assert bundle_checksum(fields) == bundle_checksum(fields)


def test_golden_score_perfect():
    report = score_golden(GOLDEN)
    assert report["total"] >= 20
    assert report["failed"] == []
    assert report["accuracy"] == 1.0


def test_path_missing_exits(tmp_path, capsys):
    from semantic_checksum.cli import main

    missing = tmp_path / "nope.txt"
    with pytest.raises(SystemExit) as exc:
        main(["extract", str(missing)])
    assert exc.value.code == 2
