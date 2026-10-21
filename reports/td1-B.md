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
