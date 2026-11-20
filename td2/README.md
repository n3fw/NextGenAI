# TD 2 - The quorum, then the routing rule

Session of 18 November 2026, pack `2026-11-18-students-5`. Every result is replayed offline from the stored TD 1 traces ([`td1/traces-td1.csv`](../td1/traces-td1.csv)): no new model call was made in TD 2.

| Step | Pair | Members | Folder | Result |
|---|---|---|---|---|
| 1 - The k-of-n vote | A | Eléa SCHOM, Clorie HU | [`A-quorum/`](A-quorum/README.md) | 2-of-3 and 3-of-5: 16 right, 0 wrong, 4 abstentions on C01 to C20 |
| 2 - The wrong consensus | B | Lydia CHAIB, Quentin PERRIGAULT | [`B-consensus/`](B-consensus/README.md) | DEMO-SQL-C11: two models agree on 0, reference 446690, 6 customers missed |
| 3 - The routing rule | C | Fabien RAMEL, Rayan IGUERCHA | [`C-routing/`](C-routing/README.md) | policy p2, adapted simulator, 15 scenarios |

## Cross-review

Each pair reviewed the two other steps. A review is stored in the folder of the pair that wrote it.

| Step reviewed | Reviewed by Pair A | Reviewed by Pair B | Reviewed by Pair C |
|---|---|---|---|
| Step 1 (Pair A) | – | [`B-consensus/review-1.md`](B-consensus/review-1.md) | [`C-routing/review-1.md`](C-routing/review-1.md) |
| Step 2 (Pair B) | [`A-quorum/review-1.md`](A-quorum/review-1.md) | – | [`C-routing/review-2.md`](C-routing/review-2.md) |
| Step 3 (Pair C) | [`A-quorum/review-2.md`](A-quorum/review-2.md) | [`B-consensus/review-2.md`](B-consensus/review-2.md) | – |

The full report is [`reports/td2.md`](../reports/td2.md).
