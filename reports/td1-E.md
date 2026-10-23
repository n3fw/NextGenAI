# Model E (`openrouter:dots-studio/dots-3-note-preview:free`)

## Work done

| Task | Evidence |
|---|---|
| Batch E: `openrouter:dots-studio/dots-3-note-preview:free`, 20 cells | [`traces-E.csv`](../td1/traces-E.csv), [`state-E.jsonl`](../td1/state-E.jsonl) |
| Independent check of the twenty references (Python on the CSV files, no SQL) | [`check-references.py`](../td1/check-references.py), [`reference-td1.csv`](../td1/reference-td1.csv) |
| Merge of the five batches A to E | [`traces-td1.csv`](../td1/traces-td1.csv), [`traces-td1.jsonl`](../td1/traces-td1.jsonl) |
| Cause of every failure of batch E (and of batches A to D) | [`model-question-comparison-en.csv`](../td1/model-question-comparison-en.csv) |
| Five-model summary (documented columns and results by family) | [`five-model-summary-en.csv`](../td1/five-model-summary-en.csv) |

## Calls

- 20 initial calls on 2026-10-21 (13:16 to 13:18 UTC), all HTTP 200, `attempts = 1`: no retry, no access failure.
- 2 OpenRouter access checks during preparation (`check_access.py`, 2026-10-16, 5/5 models OK), counted apart from the batch.
- OpenRouter account counter read on 2026-10-21 at 15:30: **22 requests** (2 checks + 20 cells), **0.00 USD spent**, about 16K tokens.
- `model_returned` = `model_requested` on every row; `cost_native = 0` measured on the 20 rows (`:free` route, `max_price` 0); `tokens_reasoning = 0` (reasoning disabled).
- Tokens: 11,858 prompt and 3,872 completion in total; the longest output was 460 tokens, far below the 1,024 cap, so no output was truncated.
- Latency: mean ≈ 3.8 s, median ≈ 3.3 s, max ≈ 9.0 s (C01). Dots is the slowest model of the five.
- Prompt: kit prompt unchanged, one fingerprint per question, identical to batches A to D (C01 `d25f6373...`).

## Results: 14/20 correct

| Family | Questions | Correct |
|---|---|---|
| Period | C01 C04 C05 C06 C07 C20 | 6/6 |
| Product list | C03 C12 C13 C14 | 4/4 |
| Age on a reference date | C02 C08 C09 C11 | 3/4 |
| Age at the time of the order | C10 | 0/1 |
| Combined | C15 C16 C17 C18 C19 | 1/5 |

## Causes of the 6 failures (read from the returned SQL)

Each faulty SQL was replayed on the base: it reproduces the value returned by the model, and the missing amount was recomputed separately.

| Cell | Verdict | Cause |
|---|---|---|
| C08 | incorrect (160920 vs 605580) | hard-coded birth dates instead of an interval: only customers born on 2001-09-23, 09-24 or 09-25 are kept. It counts the customer born 2001-09-25, who is still 24 on 2026-09-24 (135000), and misses all the others aged 25 |
| C10 | incorrect (0 vs 558980) | in SQLite `\|\|` binds tighter than `+`: `substr(birth_date,1,4) + 25 \|\| substr(...)` returns the integer 2026, not a date text. An integer is always lower than a text, so the 26th-anniversary test is never true: 0 rows |
| C15 | incorrect (138920 vs 168680) | `year difference = 25 AND birthday month-day <= '09-25'` keeps only customers born in 2001; customers born from 2000-09-26 to 2000-12-31 (also 25 on 2026-09-25) are missed: exactly 29760 missing |
| C16 | incorrect (211260 vs 376740) | same age filter as C15, product filter correct: exactly 165480 missing (customers born late 2000) |
| C18 | incorrect (39580 vs 62480) | age at the order date from `year difference = 25` with birthday passed; misses lines where the year difference is 26 and the birthday had not come yet: exactly 22900 missing |
| C19 | incorrect (0 vs 1990) | `birth_date > '2001-09-25'` excludes exactly the customers who are 25 on 2026-09-25 (born 2000-09-26 to 2001-09-25), so no line matches |

All 6 failures concern the age convention (5 broken conventions, 1 SQL logic error on operator precedence); the period and product filters are always right. None is an access failure: HTTP 200, SQL returned and executed, value present. A failed access would show HTTP 429 or 404, no SQL and no value, and would not count as a wrong answer. Batch E has none; batch D gives one (C16, HTTP 429 twice, `not_executed`).

## Hypothesis and limits

- Routing hypothesis for this batch: Dots can serve the period and product families (10/10), not the age families (4/10).
- 20 questions, one attempt each: no variance estimate, no general error rate, no ranking.
- No public index and no paid route of the exact same model documented (absent from the 2026-09-28 portfolio; OpenRouter catalogue checked 2026-10-14 shows a free route only): N/A.
- AI assistance (Claude) was used for the reference check script, the merge of the traces and the explanations of the failures. Every value was rechecked on the base. The prompts used are kept in [`prompts-en.md`](../prompts-en.md).
