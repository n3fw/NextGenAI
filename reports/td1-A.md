
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

# Model B (`groq:openai/gpt-oss-20b`)

## 1. Results and traces

| Item | Link |
|---|---|
| Raw trace (CSV) | [`traces/trace-B.csv`](../traces/trace-B.csv) |
| Comparison CSV | [`results/model-question-comparison-en.csv`](../results/model-question-comparison-en.csv) |
| Five-model summary | [`results/five-model-summary-en.csv`](../results/five-model-summary-en.csv) |

**Overall: 18/20 correct, 2 incorrect, 0 access failures, 0 `not_executed`, 0 retries** (`attempts` = 1 for all cells, HTTP 200 everywhere, `model_returned` = `model_requested`).

| Family | Correct / evaluated | Cells |
|---|---|---|
| Period only | 6/6 | C01, C04, C05, C06, C07, C20 |
| Age only | 3/5 | C08, C09, C10 correct; **C02, C11 incorrect** |
| Product only | 1/1 | C12 |
| Combined (product+period, period+age, product+age, all three) | 8/8 | C03, C13, C14, C15, C16, C17, C18, C19 |

Combined questions are counted only in the "Combined" row here; if the results are viewed by dimension they would also appear in the period, age and product views (overlap).

Latency: mean ≈ 829 ms, median ≈ 790 ms, max ≈ 1.9 s per call. `cost_native` is empty (no cost measurement).

## 2. Failures and observed causes

Both failures are **wrong answers on executed SQL**, not access failures (HTTP 200, no error field).

- **C02** (exactly 25 years old on 2026-09-25): the SQL filters `birth_date > '2025-09-25' AND birth_date <= '2026-09-25'`, i.e. people born in the year before the reference date (age 0). No customer matches, so the result is 0 instead of 590320.
- **C11** (exactly 25 on 2026-12-01): the SQL filters `birth_date <= '2006-12-01' AND birth_date > '2001-12-01'`, i.e. ages 20 to 25 (a five-year window) instead of exactly 25. Result 322160 instead of 446690.

**Observed cause (both):** wrong conversion of "exactly N years old on a reference date" into a birth-date window. The same type of question was answered correctly for the reference dates 2026-09-24 (C08), 2026-09-26 (C09) and for the order-time variant (C10, C18), and for 2026-09-25 combined with other filters (C15–C17, C19).

## 3. Hypotheses

1. The model is reliable on period and product filters in this batch, but the age-at-reference-date arithmetic is a weak spot; the error is inconsistent across near-identical questions, suggesting sensitivity to the date values rather than a systematic misunderstanding.
2. Routing hypothesis: age-at-reference-date questions may need a stronger model, a checked template, or a validation step on the generated date window. To be tested on more runs.

## 4. Limitations

- 20 questions, **one attempt each**; no repeated runs, so no estimate of variance and no general error rate.
- References were taken from the trace; [independent recheck: to be done / done by X].
- No cost measurement (`cost_native` empty); prices come from public pages, not from the bill.
- Index and price information: Groq's official page lists 0.10 / 0.50 USD per million tokens (input / output); aggregators list 0.075 / 0.30; discrepancy unresolved. No numeric public index retrieved (N/A in the summary).
- No failed access occurred in this batch, so no retry or missing-measurement case is available from this trace. For R3, an **instructor-supplied historical or simulated example** will be used: [identify it here, label it `replay` or `simulation`].

## 5. Contributions

| Member | Contribution |
|---|---|
| [Name A] | Ran model B (`groq:openai/gpt-oss-20b`), produced `trace-B.csv`, filled the comparison rows and the model B summary row, wrote this section |
| [Name B] | [model / task] |
| [Name C] | [model / task] |

## 6. What to do with it

- Rerun C02 and C11 (and the other age questions) several times to check whether the error is stable.
- Recheck the references independently.
- Test a prompt that spells out the birth-date window rule for "exactly N years old on date D".
- Complete the other four models' rows and build the models × questions pivot from the long CSV for the plenary.
- Prepare to explain one instructor-selected trace: its `prompt_sha256` fingerprint, and any missing measurement or retry.


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

# Text-to-SQL Benchmark Evaluation Report: Qwen 3.8 27B Model (Groq)

## 1. Context and Objectives

The goal of this study is to evaluate the performance of the **`qwen/qwen3.8-27b`** language model, hosted on the **Groq** platform, as part of TD1. The model is run against a suite of **20 test queries** (numbered **C01 to C20**) that ask it to generate SQLite queries aggregating revenue (excl. tax) on the `boutique.sqlite` database.

The analysis cross-references two datasets:
* `traces-D.csv`: The actual API execution traces (containing the requests sent, HTTP codes, response times, tokens, SQL queries, and the value computed by the model).
* `model-question-comparison-en-D.csv`: The summary file comparing results against the reference values (`reference_cents`).

---

## 2. Overall Performance Summary

### Key Statistics (Actual Traces)

* **Number of test cases:** 20 (C01 to C20)
* **Total number of API call attempts:** 23
* **VALID and CORRECT SQL queries (`correct`):** **15 / 20 (75%)**
* **Invalid SQL queries (`sql_invalid`):** **1 / 20 (5%)** (SQLite syntax error)
* **Queries executed but with an INCORRECT result (`incorrect`):** **3 / 20 (15%)** (logic error)
* **Queries Not Executed (`not_executed`):** **1 / 20 (5%)** (blocked by HTTP 429 rate limit)

---

## 3. Analysis by Criteria Category

The queries were classified by the filtering dimensions they involve: **Period (dates)**, **Customer age**, and **Product types**.

| Category | Queries | Successes (`correct`) | Failures | Success rate |
| :--- | :--- | :--- | :--- | :--- |
| **Period only** | C01, C04, C05, C06, C07, C20 | **6 / 6** | 0 | **100%** |
| **Age only** | C02, C08, C09, C10, C11 | **4 / 5** | C10 (`sql_invalid`) | **80%** |
| **Product only** | C12 | **1 / 1** | 0 | **100%** |
| **Period + Products** | C03, C13, C14 | **3 / 3** | 0 | **100%** |
| **Period + Age** | C15, C18 | **1 / 2** | C15 (`incorrect`) | **50%** |
| **Products + Age** | C16 | **0 / 1** | C16 (`not_executed`, HTTP 429) | **0%** |
| **Period + Products + Age** | C17, C19 | **0 / 2** | C17 (`incorrect`), C19 (`incorrect`) | **0%** |

---

## 4. In-Depth Analysis of Errors and Weaknesses

### 4.1. SQL Syntax Errors (`sql_invalid`)
* **Case C10** (*Customer age at the time of the order*):
  * **Problem:** The model made a typo in the SQLite function name, generating `COALESE(...)` instead of `COALESCE(...)`.
  * **Consequence:** SQLite execution failed with `runtime_error: no such function: COALESE`.

### 4.2. Business Logic Errors (`incorrect`)
* **Cases C15, C17, C19** (*Complex combinations of age and period*):
  * **Problem:** As soon as a query combines an age check (e.g., 25 years old at a reference date) with date-range and/or product constraints, the model fails to build the complex boolean `WHERE` clauses (handling of leap-year birth dates or overlapping date ranges with `strftime`).
  * **Case C15:** Computed result of `0` instead of `168,680` euro cents.
  * **Case C17:** Computed result of `248,490` instead of `258,180` euro cents.
  * **Case C19:** Computed result of `83,580` instead of `1,990` euro cents.

### 4.3. Infrastructure Constraints and Rate Limits (`HTTP 429`)
* **Problem:** Groq's free tier sets a strict cap of **1,000 output tokens per minute (OTPM)**.
* **Impact on the benchmark:**
  * **C16:** Consistent failure after 2 attempts (`HTTP 429: Rate limit reached`).
  * **C18 & C19:** The first attempt failed with `HTTP 429`. A second automatic attempt allowed the query to run.

---

## 5. Audit of Data Anomalies / Discrepancies (`traces-D.csv` vs `model-question-comparison-en-D.csv`)

The cross-analysis of the two files revealed several inconsistencies in the summary file `model-question-comparison-en-D.csv`:

1. **C10 / C11 swap:** In the comparison file, C10 is marked `correct` and C11 is marked `sql_invalid` (`COALESE`), whereas the actual traces show the exact opposite (C10 failed on `COALESE` and C11 succeeded).
2. **Raw value for C02:** In `model-question-comparison-en-D.csv`, the `value_cents` column shows `0` even though the status is `correct` and the actual trace shows `590320`.
3. **False positive on C16:** C16 is marked `correct` in the comparison file, even though the trace confirms the model never managed to execute the query because of the `HTTP 429` rate limit.
4. **Validation of C20:** C20 is marked `incorrect` in the comparison file, but the execution trace confirms a `correct` status with the exact value `1,106,090`.

---

## 6. Recommendations and Outlook

1. **System Prompt & Anti-Typo:** Add an explicit rule to the model's prompt for SQLite function syntax (`COALESCE`).
2. **Temperature Management / Retry:** Implement a wait delay (exponential backoff) to work around Groq's 1,000 OTPM cap.
3. **Reasoning on temporal logic:** For complex age calculations, enrich the prompt with examples of proven SQLite formulas (`date(c.birth_date, '+25 years')`).

