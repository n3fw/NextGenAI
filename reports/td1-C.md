
## Work done

| Task | Evidence |
|---|---|
| References C01 to C10 written in SQL
| Batch C: `openrouter:cohere/north-mini-code:free`, 20 cells | `traces-C.csv`, [`state-C.jsonl`](../td1/state-C.jsonl) |
| Cause of every failure of batch C | [`model-question-comparison-en-C.csv`](../td1/model-question-comparison-en-C.csv) |
| Row C of the five-model summary | [`five-model-summary-en-C.csv`](../td1/five-model-summary-en-C.csv) |


## Calls

- 20 initial calls on 2026-10-21, all HTTP 200, `attempts = 1`: no retry, no access failure.
- 2 OpenRouter access checks during preparation (`check_access.py`), counted apart from the batch.
- `model_returned` = `model_requested` on every row; `cost_native = 0` measured on the 20 rows (`:free` route, `max_price` 0); `tokens_reasoning = 0` (reasoning disabled).
- Prompt: kit prompt unchanged, one fingerprint per question (C01 `d25f6373...`)

## Results: 13/20 correct

| Family | Questions | Correct |
|---|---|---|
| Period | C01 C04 C05 C06 C07 C20 | 6/6 |
| Product list | C03 C12 C13 C14 | 4/4 |
| Age on a reference date | C02 C08 C09 C11 | 1/4 |
| Age at the time of the order | C10 | 0/1 |
| Combined | C15 C16 C17 C18 C19 | 2/5 |

## Causes of the 7 failures (read from the returned SQL)

Each cause was replayed on the base: the faulty filter reproduces the value returned by the model.

| Cell | Verdict | Cause |
|---|---|---|
| C02 | incorrect (2606320 vs 590320) | `birth_year + 25 <= 2026` keeps everyone born in 2001 or earlier (age >= 25), and `CAST('2026-09' AS INTEGER)` = 2026, so the month-day test is always true |
| C08 | sql_invalid | alias `AS age` inside the `WHERE` expression: syntax error, no value |
| C10 | incorrect (119410 vs 558980) | keeps year difference 25 with birthday passed, misses year difference 26 before the birthday: exactly 439570 missing |
| C11 | incorrect (0 vs 446690) | subtraction reversed, `birth_year - 2026 = 25` is never true |
| C16 | incorrect (595500 vs 376740) | `birth_date <= '2026-09-25'` instead of `'2001-09-25'`: customers aged 20 to 25 counted |
| C17 | incorrect (371990 vs 258180) | same bound error as C16; period and product filters correct |
| C19 | incorrect (71640 vs 1990) | bounds built from each customer's own year difference: 25 never appears, only "birthday passed by 09-25" is checked |

All 7 failures concern the age convention; the period and product filters are always right. A failed access would differ from these cells: HTTP 429 or 404, no SQL, no value, not counted as a wrong answer. Batch C has none.

## Hypothesis and limits

- No public index and no paid route of the exact same model documented (absent from the 2026-09-28 portfolio; OpenRouter catalogue checked 2026-10-14 shows a free route only): N/A.
