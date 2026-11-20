# Step 1 - The k-of-n vote (Pair A: Eléa SCHOM, Clorie HU)

We completed `Orchestrateur.vote_k_sur_n` (strict majority, k of n with `n // 2 < k <= n`) and ran it on the last attempt of each model for the 20 TD 1 questions (C01 to C20), comparing the fixed 2-of-3 panel of `atelier-vote.py` with a 3-of-5 quorum over the five TD 1 models.

- **Contract tests:** 10 / 10 pass (agreement, disagreement, unavailable members, duplicate route, invalid threshold, 0 as a value).
- **2-of-3 panel** (120B, North, Qwen): 16 right, 0 wrong, 4 abstentions (C10, C16, C17, C19).
- **3-of-5 quorum** (the same three + 20B, Dots): 16 right, 0 wrong, 4 abstentions, the same decisions on all 20 questions; four questions (C02, C08, C11, C15) pass with no spare vote.
- **Lesson:** on this batch neither quorum delivered a wrong value, but agreement is not proof: the synthetic test T6 (`0, 0, 100`, reference 100) shows a wrong value accepted by 2 votes.

The full analysis is in [`reports/td2.md`](../../reports/td2.md), section "Step 1".

## Files

| File | Content |
|---|---|
| [`../../td1/skeleton-multi-llm-en.py`](../../td1/skeleton-multi-llm-en.py) | the completed `vote_k_sur_n` (it stays in `td1/`, next to the kit files it needs) |
| [`test-vote.py`](test-vote.py) | the 10 contract tests; writes `voting-tests-td2.csv` |
| [`voting-tests-td2.csv`](voting-tests-td2.csv) | test results, in the format of the course template `voting-tests-en.csv` |
| [`step1-tests.txt`](step1-tests.txt) | console output of `test-vote.py` |
| [`step1-synthetic.jsonl`](step1-synthetic.jsonl) | the 4 synthetic examples of `atelier-vote.py` (simulation) |
| [`step1-2of3-atelier.jsonl`](step1-2of3-atelier.jsonl) | `atelier-vote.py --case C01` to `C20`: the fixed 2-of-3 panel on the real traces |
| [`compare-quorums.py`](compare-quorums.py) | driver comparing 2-of-3 and 3-of-5 with the kit's own rules |
| [`step1-2of3-vs-3of5.jsonl`](step1-2of3-vs-3of5.jsonl) | one JSON line per question, both decisions |
| [`step1-table.md`](step1-table.md) | the 20-question comparison table |

## Reviews

| File | Content |
|---|---|
| [`review-1.md`](review-1.md) | our review of Step 2 (Pair B) |
| [`review-2.md`](review-2.md) | our review of Step 3 (Pair C) |

Our Step 1 was reviewed by Pair B ([`../B-consensus/review-1.md`](../B-consensus/review-1.md)) and Pair C ([`../C-routing/review-1.md`](../C-routing/review-1.md)).

## Run

No API key and no network. On macOS / Linux, type `python3`.

```
cd td2/A-quorum
python test-vote.py                                          # 10/10 passed
python compare-quorums.py --traces ../../td1/traces-td1.csv  # add --json for one line per question
cd ../../td1
python atelier-vote.py                                       # the 4 synthetic examples
python atelier-vote.py --traces traces-td1.csv --case C02    # the fixed 2-of-3 panel on one question
```
