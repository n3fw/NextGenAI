# Step 1 - Majority voting on TD 1 traces (Pair A: Eléa Schom and Clorie Hu)

We implement strict majority voting ($k$-of-$n$ with $k > n/2$) to aggregate the last-attempt SQL answers from TD 1 across 20 cases (C01–C20), comparing a 3-model panel (`2-of-3`) against a 5-model panel (`3-of-5`).

- **Unit tests:** 10/10 tests passed (`T1` to `T10`), covering agreement, disagreement, unavailable models (`None`), duplicate routes, invalid majority thresholds, and `0` as a valid consensus value[cite: 2].
- **2-of-3 panel** (`120B`, `North`, `Qwen`): **16 right, 0 wrong, 4 abstentions** (`C10`, `C16`, `C17`, `C19`) out of 20 questions[cite: 3].
- **3-of-5 panel** (`120B`, `North`, `Qwen`, `20B`, `Dots`): **16 right, 0 wrong, 4 abstentions** (`C10`, `C16`, `C17`, `C19`) out of 20 questions[cite: 3].
- **Lesson:** Strict majority voting eliminates all wrong answers from individual models by abstaining when models disagree, though expanding from 3 to 5 models yields identical decisions across all 20 cases on this batch[cite: 3].

The full explanation is in [`reports/td2.md`](../../reports/td2.md), section "Step 1".

## Files

| File | Content |
|---|---|
| [`step1-tests.txt`](step1-tests.txt) | execution log of the 10 unit tests (`T1`–`T10`) confirming all assertions pass[cite: 2] |
| [`step1-synthetic.jsonl`](step1-synthetic.jsonl) | 4 simulated voting scenarios (`agreement`, `disagreement`, `unavailable`, `wrong consensus`)[cite: 4] |
| [`step1-2of3-atelier.jsonl`](step1-2of3-atelier.jsonl) | `2-of-3` majority voting results on the 20 TD 1 cases[cite: 1] |
| [`step1-2of3-vs-3of5.jsonl`](step1-2of3-vs-3of5.jsonl) | side-by-side comparison of `2-of-3` vs `3-of-5` voting decisions per case[cite: 5] |
| [`step1-table.md`](step1-table.md) | summary Markdown table comparing model values, `2-of-3`, and `3-of-5` decisions against reference[cite: 3] |
| [`review_1_pairA.md`](review_1_pairA.md) | peer review file 1: Step 2 |
| [`review_2_pairA.md`](review_2_pairA.md) | peer review file 2: Step 3 |

## Run

All outputs in this folder (`td2/step1/`) are generated from the TD 1 traces (`../../td1/traces-td1.csv`). No API key and no network are needed.
