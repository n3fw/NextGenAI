# TD 1 - Five free models on twenty SQL questions

Five models, one per member batch (A to E), each answered the same twenty questions (C01 to C20) on the shop database with the same prompt ([`prompts-en.md`](../prompts-en.md)). Each SQL answer was run in the read-only sandbox and compared with our reference value, computed without any model.

This folder also holds the course kit, because `skeleton-multi-llm-en.py` looks for its resources next to itself. The TD 2 vote (`vote_k_sur_n`) is completed in that same skeleton.

## Results

| File | Content |
|---|---|
| [`reference-td1.csv`](reference-td1.csv) | our 20 reference queries and values |
| [`reference-check-td1.ipynb`](reference-check-td1.ipynb) | independent check of the 20 references |
| [`traces-td1.csv`](traces-td1.csv), [`traces-td1.jsonl`](traces-td1.jsonl) | merged traces: 103 rows (every attempt), 100 cells |
| `traces-A.csv` to `traces-E.csv`, `state-A.jsonl` to `state-E.jsonl` | the traces and state file of each member batch |
| [`model-question-comparison-en.csv`](model-question-comparison-en.csv) | one latest result per model and question (100 rows) |
| [`five-model-summary-en.csv`](five-model-summary-en.csv) | the five models: index, prices, access, results by family |

| Model (batch) | Correct out of 20 |
|---|---|
| groq:openai/gpt-oss-120b (A) | 19 |
| groq:openai/gpt-oss-20b (B) | 18 |
| groq:qwen/qwen3.8-27b (D) | 15 |
| openrouter:dots-studio/dots-3-note-preview:free (E) | 14 |
| openrouter:cohere/north-mini-code:free (C) | 13 |

## Course kit (pack `2026-10-14-students-1`)

`skeleton-multi-llm-en.py`, `sandbox_sqlite.py`, `check_access.py`, `verify-data.py`, `atelier-vote.py`, `atelier-routage.py`, `schema.sql`, `questions-td1.json`, `modeles-autorises.json` and `data/` (the shop database and its CSV files, never modified).

## Run

From this folder; no API key and no network. On macOS / Linux, type `python3`.

```
python verify-data.py                       # database hash and integrity
python skeleton-multi-llm-en.py --rates     # rates per model from traces-td1.jsonl
python skeleton-multi-llm-en.py --replay traces-td1.csv --state replay.jsonl --out replay.csv
```

The full report is [`reports/td1.md`](../reports/td1.md).
