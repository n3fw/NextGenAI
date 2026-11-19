# Review 1 - Step 1 (Pair A) reviewed by Pair B (Lydia CHAIB, Quentin PERRIGAULT)

**What we checked.** We read `vote_k_sur_n` in [`td1/skeleton-multi-llm-en.py`](../../td1/skeleton-multi-llm-en.py) against the TD 2 contract. 

| Claim of Pair A | How we checked | Result |
|---|---|---|
| `vote_k_sur_n` follows the 5 points of the contract | read the code line by line | confirmed: k checked as a strict majority, duplicate `(provider, model)` refused, only `executed` proposals with a value vote, a failed member stays in `n`, no invented value on abstention |
| 10 / 10 contract tests pass | ran `python test-vote.py` | confirmed: identical to [`step1-tests.txt`](../step1-tests.txt) and [`voting-tests-td2.csv`](../../td1/voting-tests-td2.csv) |
| The four synthetic examples of the kit | ran `python atelier-vote.py` | confirmed: identical to [`step1-synthetic.jsonl`](../step1-synthetic.jsonl) (agreement 100; disagreement and unavailable abstain; wrong consensus keeps 0) |
| `atelier-vote.py` is the kit's file, unchanged | compared with the course kit | identical |
| Fixed 2-of-3 panel on C01 to C20 | ran `python atelier-vote.py --traces traces-td1.csv --case C01` to `C20` | confirmed: identical to [`step1-2of3-atelier.jsonl`](../step1-2of3-atelier.jsonl) |
| Twenty-question table, 2-of-3 vs 3-of-5 | ran `python compare-quorums.py --traces traces-td1.csv` (and `--json`) | confirmed: identical to [`step1-table.md`](../step1-table.md) and [`step1-2of3-vs-3of5.jsonl`](../step1-2of3-vs-3of5.jsonl); 16 right, 0 wrong, 4 abstentions for both |
| Input data: 103 rows, 100 cells, 20 prompt fingerprints, one real experiment, no conflicting reference | counted in `td1/traces-td1.csv` | confirmed: one experiment dated 2026-10-21, `nature = real`, one reference per question |
| Every voting row carries its SQL | checked the last attempt of each `correct` / `incorrect` cell | confirmed: 0 voting row without `sql` |
| C08: North `sql_invalid` (alias `AS age` inside the `WHERE`) | read the C08 row of North | confirmed: `syntax error near "AS"` |
| Margins (C02, C08, C11, C15 exactly at the threshold) and the four abstentions (C10, C16, C17, C19) | recounted from the table | confirmed |


**Status:** every figure reproduced and correct.
