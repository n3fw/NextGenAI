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
| [`td1/`](td1/README.md) | course kit code (`skeleton-multi-llm-en.py` with our `vote_k_sur_n`, `sandbox_sqlite.py`, `check_access.py`, `verify-data.py`, `atelier-vote.py`, `atelier-routage.py`), `schema.sql`, `questions-td1.json`, `modeles-autorises.json`, `data/`, and the TD 1 results (references, traces, summary tables) |
| [`td2/`](td2/README.md) | TD 2, one folder per pair: [`A-quorum/`](td2/A-quorum/README.md) (k-of-n vote), [`B-consensus/`](td2/B-consensus/README.md) (wrong consensus), [`C-routing/`](td2/C-routing/README.md) (routing rule); each folder holds the README of the step and the two reviews written by that pair |
| [`td3/`](td3/README.md) | TD 3 |
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
python atelier-vote.py                                  # TD 2: the 4 synthetic examples of the kit
python atelier-vote.py --traces traces-td1.csv --case C02   # TD 2: the fixed 2-of-3 panel on one question
python atelier-routage.py                               # TD 2: the 7 routing scenarios of the kit

cd ../td2/A-quorum
python test-vote.py                                     # TD 2 step 1: 10 contract tests of vote_k_sur_n
python compare-quorums.py --traces ../../td1/traces-td1.csv   # TD 2 step 1: 2-of-3 vs 3-of-5 on C01 to C20

cd ../..
python td2/C-routing/step3-atelier-routage.py --traces td1/traces-td1.csv   # TD 2 step 3: our routing rule (p2)
```

TD 2 step 2 is a notebook: open `td2/B-consensus/step2.ipynb` from its folder and run all cells.

Expected results:

| Command | Expected output |
|---|---|
| `--rates` | 120B 19/20, 20B 18/20, Qwen 15/20, Dots 14/20, North 13/20 |
| `test-vote.py` | `10/10 passed` |
| `compare-quorums.py` | 2-of-3 and 3-of-5: 16 right, 0 wrong, 4 abstentions (C10, C16, C17, C19) |
| `step3-atelier-routage.py` | identical to `td2/C-routing/step3-routage-apres.txt` (15 scenarios, policy p2) |

## Open items

- [ ] TD 3: `td3/` and `reports/td3.md`.
