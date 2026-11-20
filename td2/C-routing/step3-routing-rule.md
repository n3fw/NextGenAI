## Step 3 - The routing rule (Pair C)

**Policy version: p2** (after the sub-group cross-review). The one-page rule is in `td2/C-routing/step3-policy.md`; this file holds the evidence, the simulator outputs and the analysis.

**Pair C:** Fabien, Rayan. This version merges the two drafts of the pair. The originals are kept outside the repository.

**Sources:** `traces-td1.csv`, which holds 100 cells, all `real`. For each (model, question) pair, only the last attempt counts, sorted by `date_utc`. Answers are compared with `reference-td1.csv`, and prices come from `portefeuille-modeles-2026-09-28.csv`. There was no re-run and no network call.

**Counting:** a rate is the number of `correct` cells over the number of questions in the family. An `incorrect`, `sql_invalid` or `not_executed` (HTTP 429) cell counts as not correct and stays in the denominator.

**Replay** (from the repository root; `python` on Windows, `python3` on macOS and Linux):
```
python td2/C-routing/step3-atelier-routage.py --traces td1/traces-td1.csv --rates-only   # TD 1 rates per family
python td2/C-routing/step3-atelier-routage.py --original                                 # supplied rule  -> td2/C-routing/step3-routage-avant.txt
python td2/C-routing/step3-atelier-routage.py --traces td1/traces-td1.csv                # our rule (p2)  -> td2/C-routing/step3-routage-apres.txt
```

### 1. TD 1 rates per family

| Family (cells) | gpt-oss-120b | gpt-oss-20b | qwen3.8-27b | north-mini-code:free | dots-3-note-preview:free |
|---|---|---|---|---|---|
| F1 period (C01, C04, C05, C06, C07, C20) | 6/6 | 6/6 | 6/6 | 6/6 | 6/6 |
| F2 age on a date (C02, C08, C09, C11) | 4/4 | 2/4 (C02, C11 incorrect) | 4/4 | 1/4 (C02, C11 incorrect; C08 sql_invalid) | 3/4 (C08 incorrect) |
| F2b age at the order (C10) | 1/1 | 1/1 | 0/1 (sql_invalid) | 0/1 (incorrect) | 0/1 (incorrect) |
| F3 product list (C12; C03, C13, C14 with a period) | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 |
| Combinations with age (C15 to C19) | 4/5 (C17 incorrect) | 5/5 | 1/5 (C15, C17, C19 incorrect; C16 HTTP 429) | 2/5 (C16, C17, C19 incorrect) | 1/5 (C15, C16, C18, C19 incorrect) |
| **Total** | **19/20** | **18/20** | **15/20** | **13/20** | **14/20** |

**Questions where no quorum of free models reaches the right value:** C10, C16, C17 and C19. At most 2 of the 5 models are correct on each of them, so neither the 2-of-3 panel nor the 3-of-5 quorum reaches the reference (Pair A's table: abstention on these four questions).

Single models do answer them: gpt-oss-20b is right on all four, and gpt-oss-120b on three (it misses C17). The danger is that nothing tells us in advance which model will be right. The checking cost studied in TD 3 comes from these questions.

### 2. The rule

All five TD 1 models are reached through a free route, with a price of 0. "The cheapest correct model" therefore becomes: the free model with the best TD 1 rate on the family. Ties are broken by the total out of 20.

**Error cost by use:**
- internal dashboard: low;
- figure shown to a customer: medium;
- amount paid out: high.

| Family | First model (justifying cells) | Internal dashboard | Customer figure | Payout | If the first model is unavailable |
|---|---|---|---|---|---|
| F1 period | gpt-oss-120b, Groq (6/6: C01, C04 to C07, C20; 19/20 overall) | none (100 %) | 3-of-5 (all 5 models at 6/6) | 3-of-5 + reference query | Model in 429: gpt-oss-20b, then qwen (6/6, Groq). Groq down: dots, then north-mini (6/6, OpenRouter). Then the subscription with a reference query. Then wait if the request can wait. Otherwise abstain. |
| F3 product list | gpt-oss-120b (4/4: C03, C12 to C14) | none | 3-of-5 (5 models at 4/4) | 3-of-5 + reference query | Same as F1 (dots and north-mini are at 4/4 on OpenRouter). |
| F2 age on a date | gpt-oss-120b (4/4: C02, C08, C09, C11) | none (100 %) | Reference query + human review. Only 2 models are at 4/4, so a 3-of-5 would abstain or keep a wrong value. | Reference query + human review | Model in 429: qwen3.8-27b (4/4, Groq). Groq down: dots (3/4, OpenRouter, missed C08), always with a check: 2-of-3 if three eligible voters are available, otherwise the reference query. Then the subscription with a reference query. Then wait. Then abstain. Never north-mini (1/4). |
| F2b age at the order | gpt-oss-120b (1/1: C10) | none (100 %, but a single cell, so weak evidence) | Reference query + human review. Only 120b and 20b are right, so both 2-of-3 and 3-of-5 abstain. | Reference query + human review | Model in 429: gpt-oss-20b (1/1 on C10, Groq). Groq down: no free OpenRouter model is eligible (0/1), so the subscription with a reference query. Then wait. Then abstain. |
| Combinations with age | gpt-oss-20b (5/5: C15 to C19) | none (only model at 100 %) | Reference query + human review (C16, C17, C19: only 2 models right) | Reference query + human review | Model in 429: gpt-oss-120b (4/5, missed C17) with a reference query (only 2 eligible voters, so no quorum is possible). Groq down: the subscription with a reference query. Then wait. Then abstain. |

**No silent fallback.** A model below 75 % on the family is never used, even at price zero. Changing the model without changing the provider does not help when the provider is down, so the fallback list separates "the model is in 429" from "Groq is down".

**A quorum must have voters.** A 2-of-3 needs three distinct eligible models available, a 3-of-5 needs five. When they are not available, the quorum is replaced by the reference query (an exact SQL query written without a model). Paid routes do not vote, because their cost would have to be added to the request.

**Consistency constraint.** `none` appears only for the internal dashboard, and only when the first model scored 100 % on the family. A figure shown to a customer or a payout always gets a quorum or a deterministic check.

**Why a reference check instead of 3-of-5 on F2, F2b and combinations.** A quorum counts votes but does not see why an answer is wrong. When fewer than three models were right on every cell of a family, a 3-of-5 vote can either abstain or keep a wrong value that several models happen to share.

In our batch, the errors on C02 and C11 are not shared: gpt-oss-20b and north-mini each return a different wrong value (0 and 2,606,320 on C02; 322,160 and 0 on C11). There is therefore no wrong consensus on these questions. Their weak rates still make a quorum unreliable.

**Limits.**
- Twenty questions, one database and one pass per model give an observation specific to this batch.
- They do not establish a general error rate, a lasting model ranking, or a guarantee for any quorum.
- F2b rests on a single cell (C10).

### 3. Routing rule worksheet (`templates/routing-rule-en.md`)

- **Use case and cost of an error:** internal dashboard (low), figure shown to a customer (medium), amount paid out (high).
- **Families and supporting observations:** F1, F2, F2b, F3 and combinations with age. Rates are in section 1.
- **Eligible models and access routes:**
  - The five TD 1 models through their free routes, eligible at 75 % or more on the family. Below 100 %, a quorum is required.
  - The claude-opus-5-5 subscription (G1, "retenu"). It was not measured in TD 1, so it is never used without a check.
  - gpt-oss-120b through OpenRouter (G4, paid). Assumption: same model as the Groq route measured in TD 1. The OpenRouter route itself was not measured, so it always gets a reference query.
  - deepseek-v4.1-flash (G3, paid). It was not measured in TD 1.
- **First route and reason:** the free model with the best TD 1 rate on the family. That is gpt-oss-120b everywhere, except gpt-oss-20b on combinations.
- **Additional check or escalation:** given by `required_check(use, accuracy, n_perfect)`, following the table in section 2.
- **Maximum delay and cost basis:**
  - The delay is `deadline_minutes` for each request.
  - Paid routes are costed with the TD 1 median for gpt-oss-120b: 638 input tokens and 186 output tokens per request.
  - gpt-oss-120b on OpenRouter: 0.15 and 0.60 USD per million tokens, about 0.00021 USD per request.
  - deepseek-v4.1-flash: 0.035 and 0.29 USD per million tokens, about 0.00008 USD per request.
  - A route measured in TD 1 goes before a cheaper route that was never measured.
- **Stop, defer or human review:**
  - Defer if the request can wait and a free eligible model refills before the deadline. The availability must be checked again at wake-up.
  - Abstain if no route fits the deadline and budget, or if the family is not covered by TD 1.
  - Human review for every payout and for customer figures on F2, F2b and combinations.

| ID | Situation | Selected action | Reason tied to the rule | Evidence or explicit assumption |
|---|---|---|---|---|
| R1 | Ordinary question, preferred route available | run gpt-oss-120b (scenario `simple`) | best TD 1 rate on F1, 100 % | F1: 6/6 |
| R2 | Preferred provider unavailable | Groq down: run dots on OpenRouter + reference query (scenario `groq down, F2`). Model only in 429: run qwen (scenario `preferred model in 429`). | best free model at another provider; below 100 %, so a check; only 1 eligible voter, so no quorum | F2: dots 3/4 (missed C08), qwen 4/4 |
| R3 | Deferrable request, free quota exhausted | defer 60 min on gpt-oss-120b (scenario `deferrable`) | can wait; the announced refill comes before the deadline; availability is measured again at wake-up | assumption from the kit scenario: the quota refills in 60 minutes (for example an hourly or daily quota). This is not the per-minute limit seen in TD 1, which cleared within seconds (qwen succeeded on its second attempt). |
| R4 | Urgent request, no adequate route within the budget | abstain (scenario `budget exhausted`) | no free route in time and a budget of 0 | no figure is better than an unchecked one |
| R5 | High cost of error, models agree | run gpt-oss-120b + reference query + human review (scenario `high impact`) | agreement does not prove the value; a payout needs a deterministic check | only 2 models at 4/4 on F2 |

### 4. Simulator `td2/C-routing/step3-atelier-routage.py`

**Before adaptation** (supplied rule, `td2/C-routing/step3-routage-avant.txt`):

| Scenario | Action | Resource | Cash | Reason |
|---|---|---|---|---|
| simple | run | small-free | 0 | eligible included capacity |
| complex | run | senior-subscription | 0 | eligible included capacity |
| deferrable | defer (60 min) | senior-subscription | 0 | recheck availability at wake-up |
| urgent | run | senior-api | 0.30 | available route within the authorised budget |
| budget exhausted | abstain | – | 0 | no eligible resource within deadline and budget |
| high impact | run + source verification and human review | senior-subscription | 0 | eligible included capacity |
| unknown capability | abstain | – | 0 | no eligible resource within deadline and budget |

**Adaptation:**
- **Resources.** `RESOURCES` now holds:
  - the five TD 1 models through their free routes (G5, level 1);
  - the claude-opus-5-5 subscription (G1, level 3);
  - gpt-oss-120b through OpenRouter (G4, level 1, paid);
  - deepseek-v4.1-flash (G3, level 2, paid).
- **Eligibility.** The abstract `level` is replaced by each model's exact TD 1 rate on the family, read from `traces-td1.csv`. The portfolio level (level 1 = G5 and G4, level 2 = G3 and G2, level 3 = G1) is kept for information only: it describes a model, it is not a result on our questions. A single level could not express our results: gpt-oss-20b is 5/5 on combinations but only 2/4 on F2.
- **Requests.** A request carries a `family` and a `use`. The check depends on the use, the TD 1 rate of the chosen model, and the number of distinct TD 1 models at 100 % on the family.
- **Feasible checks.** A quorum is kept only if enough eligible voters are available now. Otherwise it becomes a reference query. A route whose rate is assumed, not measured, never gets `none`.
- **Reasons.** Every `reason` cites the TD 1 cells behind the decision, and every output line carries the policy version.
- **Priority order.** The supplied order is kept: included capacity, then defer, then paid route, then abstain. Inside the included capacity, measured free models go first and the unmeasured subscription comes next. On paid routes, a route measured in TD 1 goes before a cheaper unmeasured one.

**After adaptation** (`td2/C-routing/step3-routage-apres.txt`, policy p2). The seven supplied scenarios keep their names and are mapped to our families: difficulty 1 becomes F1, difficulty 3 becomes F2, high impact becomes a payout, and difficulty 4 becomes a family absent from TD 1. Eight more scenarios test the rest of our rule.

| Scenario | Request | Action | Resource | Cash (USD) | Check |
|---|---|---|---|---|---|
| simple | F1, dashboard | run | gpt-oss-120b | 0 | none |
| complex | F2, dashboard | run | gpt-oss-120b | 0 | none |
| deferrable | F2, dashboard, free routes and subscription exhausted | defer 60 min | gpt-oss-120b | 0 | none |
| urgent | F2, dashboard, deadline 5 min | run | gpt-oss-120b (OpenRouter, paid) | 0.00021 | reference query (route not measured) |
| budget exhausted | F2, dashboard, budget 0 | abstain | – | 0 | – |
| high impact | F2, payout | run | gpt-oss-120b | 0 | reference + human review |
| unknown capability | family absent from TD 1 | abstain | – | 0 | – |
| preferred model in 429 | F2, dashboard, 120b in 429 | run | qwen3.8-27b | 0 | none |
| groq down, F1 | F1, dashboard, Groq down | run | dots-3-note-preview (OpenRouter) | 0 | none (6/6) |
| groq down, F2 | F2, dashboard, Groq down | run | dots-3-note-preview (OpenRouter) | 0 | reference query (3/4, 1 voter) |
| customer figure | F3, customer | run | gpt-oss-120b | 0 | 3-of-5 quorum |
| customer figure, weak family | F2b, customer | run | gpt-oss-120b | 0 | reference + human review |
| combined, payout | combinations, payout | run | gpt-oss-20b | 0 | reference + human review |
| free routes down | F1, dashboard, all free routes exhausted | run | claude-opus-5-5 (subscription) | 0 | reference query (no voter left) |
| deferrable, customer figure | F2, customer, everything included exhausted | defer 60 min | gpt-oss-120b | 0 | reference + human review |

### 5. Priority in the supplied `choose`

`choose` tests its branches in a fixed order:
1. included capacity that is available (`cash == 0`), whether free or an already paid subscription;
2. `defer` to an exhausted free resource that refills before `deadline_minutes`;
3. a paid route within the budget;
4. `abstain`.

The deferral branch is reached only when the first list is empty. So an available subscription (`cash == 0`, `allocation > 0`) is always chosen before waiting for an exhausted free resource (`cash == 0`, `allocation == 0`). `allocation` only breaks ties inside the first branch: an available free resource would win over the subscription.

Four reasons support this order:
- the subscription is already paid, so using it costs nothing more;
- it answers at once, while `defer` adds delay;
- reaching the reset time does not prove that capacity will be there at wake-up (the docstring says so);
- unused allocation is lost at the end of the period.

The order should be reversed in three cases:
- **The subscription allocation is scarce or shared** and must be kept for urgent or high-impact requests before its next reset. A request that can wait should not consume it.
- **The free model was measured as better on the family in TD 1** (for example gpt-oss-120b at 4/4 on F2), while the subscription model was never measured on these cells.
- **A confidentiality constraint excludes the subscription provider.**

Our adapted `choose` applies the second case. It first tries the free models measured at 75 % or more on the family, and takes the subscription only when they are all unavailable (scenario `free routes down`).

### 6. Notes to reconcile with the sub-group

- `five-model-summary-en.csv` gives qwen "5 out of 6" on period questions and "paid" access. The merged traces (last attempt) give 6/6, and the portfolio lists the Groq route for qwen3.8-27b as free. This needs to be harmonised with the member who filled in that file.
- `cohere/north-mini-code:free` and `dots-studio/dots-3-note-preview:free` are not in `portefeuille-modeles-2026-09-28.csv`. They are treated as free because of their `:free` suffix on OpenRouter and the `cost_native = 0` in the TD 1 traces.

### 7. Contributions (Pair C)

- **Fabien:**
  - per-family rates and their justifying cells;
  - the routing rule worksheet R1 to R5;
  - the paid gpt-oss-120b route costed from the TD 1 tokens;
  - the `unknown capability` and `preferred model in 429` scenarios;
  - the analysis of the `choose` branches.
- **Rayan:**
  - simulator that reads its rates directly from the traces;
  - subscription and deepseek routes from the portfolio;
  - checks driven by the number of models at 100 %;
  - analysis of the reversal conditions;
  - the remark on `five-model-summary-en.csv`.
- **Merge:** we kept the better choice from each draft and fixed the inconsistencies:
  - the count of models at 100 % is now passed to every branch;
  - the paid gpt-oss-120b route is no longer counted as a sixth model;
  - the deepseek cost is now computed from the portfolio price;
  - the wording on C02 and C11 is corrected (no shared wrong value).

- **Cross-review (p1 to p2):** seven remarks from the sub-group were applied:
  - the fallback now separates a model in 429 from a provider that is down;
  - a quorum is kept only when its voters are available;
  - the unmeasured OpenRouter route of gpt-oss-120b gets a reference query;
  - the 60-minute refill is stated as a kit assumption;
  - the sentence on C10, C16, C17 and C19 is corrected;
  - this section is copied into `reports/td2.md`;
  - the commands use `python`.

### 8. Next steps

In TD 3, compute the cost of the "reference + human review" check on C10, C16, C17 and C19. Then decide whether a paid model, measured on the same 20 questions, could replace it.
