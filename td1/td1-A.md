
## Work done

| Task | Evidence |
|---|---|
| References C16 to C20 written in SQL, cross-checked by an independent query of the other duo member | [`reference-td1.csv`](../td1/reference-td1.csv) |
| Batch A: `groq:openai/gpt-oss-120b`, 20 cells | [`traces-A.csv`](../td1/traces-A.csv), [`state-A.jsonl`](../td1/state-A.jsonl) |
| Cause of every failure of batch A | [`model-question-comparison-en-A.csv`](../td1/model-question-comparison-en-A.csv) |
| Row A of the five-model summary | [`five-model-summary-en-A.csv`](../td1/five-model-summary-en-A.csv) |


## Calls

- 20 initial calls on 2026-10-21 (13:37 to 13:39 UTC), all HTTP 200, `attempts = 1`: no retry, no access failure.
- 3 Groq and 2 OpenRouter access checks during preparation (one `check_access.py` run, 5/5 OK), counted apart from the batch.
- `model_returned` = `model_requested` on every row; `cost_native` empty on the 20 rows (Groq returns no native cost, so the field stays empty, never 0); `tokens_reasoning` from 17 to 420 (`reasoning_effort` low).
- Tokens: 12814 input and 5047 output over the 20 calls; latency 569 ms to 4734 ms, median 1557 ms.
- Prompt: kit prompt unchanged, one fingerprint per question (C01 `d25f6373...`), identical to the other batches.
- Groq Free allowance: about 43% left after the batch (account read on 2026-10-21).

## Results: 19/20 correct

| Family | Questions | Correct |
|---|---|---|
| Period | C01 C04 C05 C06 C07 C20 | 6/6 |
| Product list | C03 C12 C13 C14 | 4/4 |
| Age on a reference date | C02 C08 C09 C11 | 4/4 |
| Age at the time of the order | C10 | 1/1 |
| Combined | C15 C16 C17 C18 C19 | 4/5 |

## Cause of the failure (read from the returned SQL)

The cause was replayed on the base: the model's SQL, run again, reproduces the value returned by the model.

| Cell | Verdict | Cause |
|---|---|---|
| C17 | incorrect (80190 vs 258180) | `c.birth_date = date('2026-09-25', '-25 years')`: an equality instead of the completed-age interval, so only customers born exactly on 2001-09-25 are kept instead of everyone born from 2000-09-26 to 2001-09-25: exactly 177990 missing. Period and product filters correct; SQL valid; output not truncated (428 completion tokens, cap 1024) |

The only failure concerns the age convention, on a question that combines period, product list and age. The same model applies the correct age rule on C02, C08, C09, C11, C15, C16, C18 and C19, so the error appears in one combined case, not in the age family as a whole. A failed access would differ from this cell: HTTP 429 or 404, no SQL, no value, not counted as a wrong answer. Batch A has none.

## Hypothesis and limits

- Public index 11.6 (Artificial Analysis Intelligence Index via OpenRouter rankings, read 2026-09-28: lecture CM1 and kit portfolio). Paid route of the exact same model: Groq Developer, 0.15 USD/M input and 0.60 USD/M output, checked 2026-10-05 (kit `methode-cout-en.md`).
- Real spend 0 USD (Groq Free plan, no payment method). API-equivalent cost of the 20 calls at Groq Developer prices: (12814 x 0.15 + 5047 x 0.60) / 1,000,000 = 0.00495 USD, assuming reasoning tokens are included in `tokens_completion` (completion >= reasoning on all 20 rows).
- Routing hypothesis for this batch: GPT-OSS 120B is enough for single-filter questions (15/15); combined questions with an age filter should be checked or sent to a second model.
- Limits: one run per question at temperature 0, 20 questions on one database; the observation supports a routing hypothesis, not a general error rate or ranking.
