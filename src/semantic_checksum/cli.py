"""CLI: extract → checksum → field diff → golden score."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from semantic_checksum import FIELDS, __version__
from semantic_checksum.checksum import bundle_checksum, extract_marked, field_checksum
from semantic_checksum.diff import field_diff
from semantic_checksum.score import score_golden


def _read_text(path: Path) -> str:
    # Reject path traversal / absolute escape relative to CWD when under data/
    resolved = path.resolve()
    try:
        text = resolved.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        print(f"error: invalid UTF-8 in {path}: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    except OSError as exc:
        print(f"error: cannot read {path}: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    return text


def cmd_extract(args: argparse.Namespace) -> int:
    text = _read_text(Path(args.path))
    fields = extract_marked(text)
    out = {
        "fields": fields,
        "field_checksums": field_checksum(fields),
        "bundle_checksum": bundle_checksum(fields),
        "schema": list(FIELDS),
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


def cmd_diff(args: argparse.Namespace) -> int:
    left = extract_marked(_read_text(Path(args.left)))
    right = extract_marked(_read_text(Path(args.right)))
    result = field_diff(left, right)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["match"] else 1


def cmd_score(args: argparse.Namespace) -> int:
    report = score_golden(Path(args.golden))
    summary = {
        "total": report["total"],
        "passed": report["passed"],
        "failed": report["failed"],
        "accuracy": report["accuracy"],
        "fields": report["fields"],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if args.verbose:
        print(json.dumps(report["results"], ensure_ascii=False, indent=2))
    return 0 if not report["failed"] else 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="semantic-checksum",
        description=(
            "Detect meaning drift across bilingual requirements on a frozen "
            "5-field checksum (amount/deadline/actor/obligation/exception). "
            "No embeddings. No MQM. CLI only."
        ),
    )
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    e = sub.add_parser("extract", help="Extract marked fields and print checksums")
    e.add_argument("path", help="Path to marked text file")
    e.set_defaults(func=cmd_extract)

    d = sub.add_parser("diff", help="Field-diff two marked texts (exit 1 on mismatch)")
    d.add_argument("left")
    d.add_argument("right")
    d.set_defaults(func=cmd_diff)

    s = sub.add_parser("score", help="Score synthetic golden adversarial pairs")
    s.add_argument("golden", help="Path to golden JSON list")
    s.add_argument("-v", "--verbose", action="store_true")
    s.set_defaults(func=cmd_score)
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
