# Review 1 - Step 1 (Pair A) reviewed by Pair C (Fabien RAMEL, Rayan IGUERCHA)

**What we checked.** We read `vote_k_sur_n` in [`td1/skeleton-multi-llm-en.py`](../../td1/skeleton-multi-llm-en.py) against its docstring, then re-ran the commands of Step 1: `atelier-vote.py` from `td1/`, `test-vote.py` and `compare-quorums.py` from `td2/A-quorum/`.

| Claim of Pair A | How we checked | Result |
|---|---|---|
| The method follows the docstring contract (failed member stays in `n`, strict majority, duplicate refused, no invented value) | read the code, ran [`test-vote.py`](../A-quorum/test-vote.py) | confirmed: 10 / 10 tests pass |
| The four synthetic examples of the kit | ran `python atelier-vote.py` from `td1/` | confirmed: identical to [`step1-synthetic.jsonl`](../A-quorum/step1-synthetic.jsonl) (agreement 100; disagreement and unavailable abstain; wrong consensus keeps 0) |
| Twenty-question table, 2-of-3 vs 3-of-5 | ran `python compare-quorums.py --traces ../../td1/traces-td1.csv` | identical to [`step1-table.md`](../A-quorum/step1-table.md): 16 right, 0 wrong, 4 abstentions for both |
| The 2-of-3 column matches the kit's own script | ran `python atelier-vote.py --traces traces-td1.csv --case C01` to `C20` from `td1/` | identical to [`step1-2of3-atelier.jsonl`](../A-quorum/step1-2of3-atelier.jsonl) |
| Values in the table are the last attempts | compared with the raw rows of [`td1/traces-td1.csv`](../../td1/traces-td1.csv) | confirmed, including Qwen attempt 2 on C16, C18, C19 |

**Issue found and fixed by Pair A:**

1. The rule "a failed member does not shrink the panel" was cited as Lecture 2, slide 21; it is slide 16. Fixed in `reports/td2.md` and in the test name (`T5-slide16-3of5` in [`test-vote.py`](../A-quorum/test-vote.py), [`voting-tests-td2.csv`](../A-quorum/voting-tests-td2.csv) and [`step1-tests.txt`](../A-quorum/step1-tests.txt)).

**Status:** every figure reproduced and correct.
