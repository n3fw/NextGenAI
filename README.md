___
# Next Generation AI
_DIA3, Subgroup 4_

Lydia CHAIB \
Eléa SCHOM \
Clorie HU \
Quentin PERRIGAULT \
Fabien RAMEL \
Rayan IGUERCHA

## Pack and data

| Item | Value |
|---|---|
| Course kit | pack `2026-10-14-students-1` (kit of 14 October 2026) |
| TD 2 assignment | pack `2026-11-18-students-5` |
| Database | `td1/data/boutique.sqlite`, never modified |
| Database SHA-256 | `0077e235adc2ca647b484e3083c98a6d7cae3ef3655ce366a299caf13398fec2` (matches `td1/data/manifest.json`, checked by `verify-data.py`) |
| Prompt | kit prompt unchanged, see [`prompts-en.md`](prompts-en.md) |

## Environment

- Python 3.10 or later, standard library only: no package to install.
- Used on Windows (PowerShell). On Windows, type `python`; on macOS / Linux, type `python3`.
- No API key is needed to replay the results below: every command works offline on the stored traces.
- Keys (`GROQ_API_KEY`, `OPENROUTER_API_KEY`) stay in each member's environment variables, never in the repository (see [`.gitignore`](.gitignore)).

## Repository layout

| Path | Content |
|---|---|
| `td1/` | kit code (`skeleton-multi-llm-en.py`, `sandbox_sqlite.py`, `check_access.py`, `verify-data.py`, `atelier-vote.py`, `atelier-routage.py`), `schema.sql`, `questions-td1.json`, `modeles-autorises.json`, `data/` |
| `td1/reference-td1.csv` | our 20 reference queries and values (C01 to C20) |
| `td1/traces-td1.csv`, `td1/traces-td1.jsonl` | merged TD 1 traces; `traces-A.csv` to `traces-E.csv`: one file per member batch |
| `td1/model-question-comparison-en.csv` | one latest result per model and question (100 rows) |
| `td1/five-model-summary-en.csv` | the five models: index, prices, access, results by family |
| `td1/compare-quorums.py`, `td1/test-vote.py`, `td1/voting-tests-td2.csv` | TD 2 step 1: vote driver and tests |
| `td2/` | TD 2 evidence (outputs of the vote) |
| `reports/td1.md`, `reports/td2.md`, `reports/td3.md` | session reports |

## TD 1 models

| Member batch | Provider:model | Trace file |
|---|---|---|
| A | `groq:openai/gpt-oss-120b` | `td1/traces-A.csv` |
| B | `groq:openai/gpt-oss-20b` | `td1/traces-B.csv` |
| C | `openrouter:cohere/north-mini-code:free` | `td1/traces-C.csv` |
| D | `groq:qwen/qwen3.8-27b` | `td1/traces-D.csv` |
| E | `openrouter:dots-studio/dots-3-note-preview:free` | `td1/traces-E.csv` |

## Replay the work from a fresh clone

```bash
git clone https://github.com/n3fw/NextGenAI.git
cd NextGenAI/td1

python verify-data.py                                   # database hash and integrity: "ok": true
python skeleton-multi-llm-en.py --rates                 # TD 1 rates per model from traces-td1.jsonl
python skeleton-multi-llm-en.py --replay traces-td1.csv --state replay.jsonl --out replay.csv
                                                        # re-run every stored SQL offline (nature = replay)
python test-vote.py                                     # TD 2: 10 contract tests of vote_k_sur_n
python atelier-vote.py                                  # TD 2: the 4 synthetic examples of the kit
python atelier-vote.py --traces traces-td1.csv --case C02   # TD 2: the fixed 2-of-3 panel on one question
python compare-quorums.py --traces traces-td1.csv       # TD 2: 2-of-3 vs 3-of-5 on C01 to C20
python atelier-routage.py                               # TD 2: the 7 routing scenarios of the kit
```

Expected results:

| Command | Expected output |
|---|---|
| `--rates` | 120B 19/20, 20B 18/20, Qwen 15/20, Dots 14/20, North 13/20 |
| `test-vote.py` | `10/10 passed` |
| `compare-quorums.py` | 2-of-3 and 3-of-5: 16 right, 0 wrong, 4 abstentions (C10, C16, C17, C19) |

## Open items

- [ ] TD 2 step 2 (Pair B): wrong consensus on DEMO-SQL-C11 and delta query on `td1/data/boutique.sqlite`.
- [ ] TD 2 step 3 (Pair C): one-page routing rule and adapted `atelier-routage.py`, outputs before and after.
- [ ] `reports/td2.md`: sections of Pairs B and C, contribution of each member, limits, next steps.
- [ ] `td1/reference-td1.csv`: record which member checked which reference query.
- [ ] `td1/traces-td1.jsonl`: add the three missing Qwen attempts (HTTP 429, attempt 1 on C16, C18, C19) present in `traces-D.csv`.
- [ ] `reports/td1.md`: fix the 11 links to files that are not in the repository (`state-*.jsonl`, per-member CSVs, `check-references.py`, `results/`, `traces/`).
- [ ] TD 3: `reports/td3.md`.
