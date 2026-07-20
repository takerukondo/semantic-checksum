# semantic-checksum

`semantic-checksum` catches five expensive kinds of requirement drift after a human has marked the important fields: amount, deadline, actor, obligation, and exception.

It is intentionally not a translation model. I built it for the less glamorous part of bilingual delivery work: once both sides agree which fragments carry contractual meaning, CI should notice if one of those fragments changes.

```text
EN: [[actor:buyer]] [[obligation:must pay]] [[amount:1000000]]
JA: [[actor:buyer]] [[obligation:must pay]] [[amount:100000]]
                                                        ^ one zero vanished
```

## Try it

Requires Python 3.11 or newer.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"

semantic-checksum score data/golden.json
pytest -q
```

To compare two files, annotate each field once:

```text
Pay [[amount:1000000]] by [[deadline:2026-08-01]].
[[actor:buyer]] [[obligation:must pay]] [[exception:none]].
```

```bash
semantic-checksum extract spec-en.txt
semantic-checksum diff spec-en.txt spec-ja.txt
```

`diff` exits `0` for a complete match, `1` for drift, and `2` for incomplete input. Two unannotated documents are incomplete; they are never treated as a successful match.

## Why explicit marks?

An earlier version of this idea sounded more magical than it was. A checksum cannot discover meaning in raw prose. Automatic extraction would add another fallible model and blur whether the failure came from translation or extraction. This small tool keeps that boundary visible: a person chooses the five values, then a deterministic check guards them.

The included golden set contains 24 synthetic EN/JA pairs with amount swaps, deadline shifts, actor swaps, polarity changes, exception changes, and aligned controls. It exercises the checker; it is not a translation-quality benchmark.

## Scope

- Offline, deterministic, and dependency-free at runtime.
- Exact normalized-value comparison; it does not know that `1M` and `1,000,000` may be equivalent.
- Five fields only. Nested clauses and multiple obligations need a richer schema.
- The annotations are part of the input contract, not model output.

MIT © 2026 Takeru Kondo
