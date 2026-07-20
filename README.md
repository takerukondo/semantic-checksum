# semantic-checksum

> **Status: experimental / alpha** — field schema, golden set, and CLI may change without notice.

Detect **meaning drift** between bilingual requirements on a **frozen 5-field checksum**:

| field | meaning |
|---|---|
| `amount` | 数値・金額・上限 |
| `deadline` | 期限 |
| `actor` | 主体 |
| `obligation` | 義務・極性 |
| `exception` | 例外 |

CLI only. **No embeddings. No MQM. No Web UI. No LLM judge as primary metric.**

## vs prior art (one screen)

| tool | what it measures | this repo |
|---|---|---|
| AlignScore / MQM | document / translation quality | **field checksum mismatch on adversarial pairs** |
| ContractNLI | NLI over contracts | frozen 5-field schema + synthetic golden scorecard |
| SemShift | semantic shift datasets | CLI contract test, not a research leaderboard claim |

## Install

Requires **Python ≥ 3.11**. Offline. No telemetry.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## Marked text format

Fixtures mark fields inline (deterministic extractor, zero LLM):

```text
Pay [[amount:1000000]] by [[deadline:2026-08-01]].
[[actor:buyer]] [[obligation:must pay]] [[exception:none]].
```

## CLI

```bash
# extract → checksum JSON
semantic-checksum extract path/to/spec.txt

# field diff (exit 1 on mismatch)
semantic-checksum diff en.txt ja.txt

# score synthetic golden (≥20 adversarial pairs)
semantic-checksum score data/golden.json
```

## Golden set

`data/golden.json` — 24 adversarial pairs covering amount swap, deadline shift, actor swap, obligation polarity, exception toggle, and multi-field attacks (plus aligned controls). Primary metric = exact match of `expected_mismatched_fields`.

## Tests

```bash
pytest -q
```

## License

MIT © 2026 Takeru Kondo
