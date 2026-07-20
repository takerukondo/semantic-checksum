from __future__ import annotations

from pathlib import Path

import pytest

from semantic_checksum.cli import main

ROOT = Path(__file__).resolve().parents[1]


def test_diff_exit_codes(tmp_path):
    a = tmp_path / "a.txt"
    b = tmp_path / "b.txt"
    a.write_text("[[amount:1]] [[deadline:d]] [[actor:a]] [[obligation:m]] [[exception:e]]", encoding="utf-8")
    b.write_text("[[amount:2]] [[deadline:d]] [[actor:a]] [[obligation:m]] [[exception:e]]", encoding="utf-8")
    assert main(["diff", str(a), str(a)]) == 0
    assert main(["diff", str(a), str(b)]) == 1


def test_score_cli_on_golden():
    assert main(["score", str(ROOT / "data" / "golden.json")]) == 0


def test_japanese_path(tmp_path):
    d = tmp_path / "要件"
    d.mkdir()
    f = d / "仕様.txt"
    f.write_text("[[amount:9]] [[deadline:今日]] [[actor:現場]] [[obligation:確認必須]] [[exception:なし]]", encoding="utf-8")
    assert main(["extract", str(f)]) == 0


def test_path_traversal_read_outside_still_errors_cleanly(tmp_path):
    """CLI should not crash on nonsense paths; missing file → exit 2."""
    bogus = tmp_path / ".." / ".." / "no-such-semantic-checksum-file-xyz"
    with pytest.raises(SystemExit) as exc:
        main(["extract", str(bogus)])
    assert exc.value.code == 2
