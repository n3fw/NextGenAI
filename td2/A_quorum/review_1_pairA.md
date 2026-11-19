### Step 2 (Pair B) reviewed by Pair A (Eléa SCHOM, Clorie HU)

**What we checked.** We read the Step 2 section and re-ran every cell of [`td2/step2.ipynb`](../td2/step2.ipynb), then compared each figure with [`td1/traces-td1.csv`](../td1/traces-td1.csv), [`td1/reference-td1.csv`](../td1/reference-td1.csv) and `td1/data/boutique.sqlite`.

| Claim of Pair B | How we checked | Result |
|---|---|---|
| No shared wrong value in our batch (last attempts) | re-ran the `shared_wrong_value` query | confirmed: 0 rows |
| 18 wrong answers on 9 questions | counted `verdict = incorrect` on the last attempt of each cell | confirmed: 18 cells on C02, C08, C10, C11, C15 to C19 |
| C11 answers of our 5 models | read the 5 C11 rows of the traces | confirmed: 120B, Qwen, Dots 446690; 20B 322160; Cohere 0 |
| 2-of-3 and 3-of-5 votes on C11 | compared with the output of `vote_k_sur_n` ([`td2/step1-2of3-vs-3of5.jsonl`](../td2/step1-2of3-vs-3of5.jsonl)) | identical: 446690 with 2 votes (2-of-3) and 3 votes (3-of-5) |
| Simulated vote with the pilot answer of 20B (0) | recounted by hand | confirmed: 3-of-5 gives 446690 (3 votes) against 0 (2 votes); 20B is not in the fixed 2-of-3 panel |
| M1 and M2 return 0 on the shop database | ran both queries on `td1/data/boutique.sqlite` | confirmed: 0 and 0 |
| Root causes of M1 and M2 | read the `WHERE` clauses | confirmed: M1 keeps a single birth date (2001-12-01); M2 requires a birth date both on or before 2026-12-01 and on or after 2027-12-01 |
| Delta query: 6 customers, 446690 cents | ran the delta query | confirmed: C001, C002, C003, C006, C008, C009, total 446690 = reference, the whole gap with 0 |
| Independent check in Python, without SQL | ran the Python cell | confirmed: same 6 customers, total 446690 |
| DEMO-VOTE on the one-row toy table | ran the cell | confirmed: `>` gives 0, `>=` gives 100; `[0, 0, 100]` with k = 2 keeps 0, as Pair A's test T6 |

**Issues found and fixed by Pair B:**

1. The notebook did not run from a fresh clone: its paths pointed to a local copy of the course kit and to the wrong folder. Fixed: `../td1/traces-td1.csv`, `../td1/data/` and `../td1/data/boutique.sqlite`.
2. The report linked to `td2/TD2.ipynb`, which does not exist. Fixed: [`td2/step2.ipynb`](../td2/step2.ipynb).
3. The report named `data/boutique.sqlite`. Fixed: `td1/data/boutique.sqlite`.

**Status:** every figure reproduced and correct; the notebook runs from a fresh clone. The complete SQL queries M1, M2 and the delta query are in [`td2/step2.ipynb`](../td2/step2.ipynb), Part 2.
