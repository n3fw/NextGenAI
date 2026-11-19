# Step 2 - The wrong consensus (Pair B: Lydia Chaib and Quentin Perrigault)

Our TD 1 batch has no question where two models share the same wrong value, so we use the historical case **DEMO-SQL-C11** given by the assignment.

- **Case:** C11, revenue from customers exactly 25 years old on 2026-12-01. In the instructor's pilot (September 2026), `openai/gpt-oss-20b` and `cohere/north-mini-code:free` both answer **0**. The reference is **446690**.
- **Cause:** two different `WHERE` mistakes that keep no customer, so `COALESCE` turns the empty sum into 0.
- **Gap:** 6 customers missed by both queries, 446690 cents in total, confirmed by an independent Python check.
- **Lesson:** two models agreeing does not prove that they are right; an important answer needs a check that does not depend on the models.

The full explanation is in [`reports/td2.md`](../../reports/td2.md), section "Step 2".

## Files

| File | Content |
|---|---|
| [`step2.ipynb`](step2.ipynb) | search for a shared wrong value, votes on C11, M1 and M2 queries, delta query, Python check, DEMO-VOTE |
| [`review-1.md`](review-1.md) | our review of Step 1 (Pair A) |
| [`review-3.md`](review-3.md) | our review of Step 3 (Pair C) |

## Run

Open `step2.ipynb` from this folder (`td2/B-consensus/`). It reads `../../td1/traces-td1.csv`, `../../td1/data/` and `../../td1/data/boutique.sqlite`. No API key and no network are needed.
