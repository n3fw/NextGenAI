# Review 2 - Step 2 (Pair B) reviewed by Pair C (Fabien RAMEL, Rayan IGUERCHA)

**What we checked.** We opened [`step2.ipynb`](../B-consensus/step2.ipynb) from its own folder (`td2/B-consensus/`) on a fresh clone and ran every cell. We then rechecked the claims that matter for our routing rule directly on [`td1/traces-td1.csv`](../../td1/traces-td1.csv) and `td1/data/boutique.sqlite`, without the notebook.

| Claim of Pair B | How we checked | Result |
|---|---|---|
| The notebook runs from a fresh clone | ran all cells from `td2/B-consensus/` | confirmed: no error; it reads `../../td1/traces-td1.csv`, `../../td1/data/` and `../../td1/data/boutique.sqlite` |
| No two models share a wrong value on the same question, last attempts and retries included | grouped the `incorrect` rows by question and value, first on the last attempt of each cell, then on all 103 rows | confirmed: 0 group in both cases, so the historical case DEMO-SQL-C11 is the right choice |
| M1 and M2 return 0 on the shop database | ran both queries on `td1/data/boutique.sqlite` | confirmed: 0 and 0 |
| M1 keeps a single birth date | counted the customers born on 2001-12-01 | confirmed: 0 customer, hence 0 |
| M2 asks for an impossible window | read the `WHERE`: on or before 2026-12-01 and on or after 2027-12-01 | confirmed: no birth date satisfies both |
| Delta query: 6 customers, 446690 cents | ran the last SQL cell of the notebook | confirmed: C001, C002, C003, C006, C008, C009, total 446690 = reference in [`td1/reference-td1.csv`](../../td1/reference-td1.csv) |
| The votes that include the shared 0 are labelled as a simulation | read the Step 2 section of `reports/td2.md` | confirmed: the real votes (from our traces) and the simulated ones (pilot answer of 20B) are in separate tables |

**Consequence for Step 3.** Both the real votes and the simulation keep 446690 on C11, but only because three other models answer it correctly. This is why our policy asks for a reference query, not only a quorum, on F2 questions shown to a customer or paid out.

**Issues found:** none beyond those already reported by Pair A in [`review-1.md`](../A-quorum/review-1.md) (notebook paths, missing notebook link, database path), all fixed.

**Status:** every figure reproduced and correct.
