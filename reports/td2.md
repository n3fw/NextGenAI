## Step 1 - The k-of-n vote (Pair A)

Code: `td1/skeleton-multi-llm-en.py` (method `Orchestrateur.vote_k_sur_n`), driver `td1/compare-quorums.py`, tests `td1/test-vote.py`.

Nature of all results below: **real** TD 1 traces ([`td1/traces-td1.csv`](../td1/traces-td1.csv), 103 rows, one experiment of 2026-10-21, 20 distinct `prompt_sha256`, no conflicting reference), replayed offline. No new network call. The four examples at the top are **synthetic** (kit values, not shop data).

### Method

`Orchestrateur.vote_k_sur_n(self, traces_question, k)` in `skeleton-multi-llm-en.py`:

1. `n = len(traces_question)`: the panel is fixed before the answers; a member in `error` stays in `n`.
2. `k` must satisfy `n // 2 < k <= n` (an integer, not a bool), otherwise `ValueError`.
3. Two proposals with the same `(provider, model_requested)` → `ValueError` (one model, one vote).
4. Only proposals with `verdict == "executed"` and `value is not None` vote; values are compared exactly as integers in cents.
5. If a value reaches `k`: `{"consensus": True, "value", "votes", "models"}`; otherwise `{"consensus": False, "value": None, "votes": <largest count>, "models": []}`. The method never receives the reference.

Proposals are built by the kit (`proposals_for` in `atelier-vote.py`): the **last attempt** of each panel member, and a value votes only if its TD 1 verdict is `correct` or `incorrect` (so `sql_invalid` and `not_executed` become `error`).

### Contract tests (`cd td1 && python test-vote.py`)

Panel and threshold are declared in each test before the vote. Results: [`td1/voting-tests-td2.csv`](../td1/voting-tests-td2.csv) (course template `voting-tests-en.csv`), console output [`td2/step1-tests.txt`](../td2/step1-tests.txt). 10 / 10 pass:

| Test | n, k | Inputs | Expected | Result |
|---|---|---|---|---|
| T1 agreement | 3, 2 | 100, 100, 120 | 100 | 100 (2 votes) |
| T2 disagreement | 3, 2 | 100, 110, 120 | abstain | abstain, best 1 |
| T3 one unavailable | 3, 2 | 42, 42, None | 42 | 42 (2 votes), n stays 3 |
| T4 two unavailable | 3, 2 | 42, None, None | abstain | abstain, best 1 |
| T5 slide 21 | 5, 3 | 42, 42, None, None, 41 | abstain | abstain, best 2 |
| T6 wrong consensus | 3, 2 | 0, 0, 100 | 0 | 0 (2 votes): agreement is not truth |
| T7 duplicate route | 3, 2 | 120B twice | ValueError | ValueError |
| T8 k not a majority | 3, 1 | 42, 42, 41 | ValueError | ValueError |
| T9 k above n | 3, 4 | 42, 42, 42 | ValueError | ValueError |
| T10 zero is a value | 3, 2 | 0, 0, None | 0 | 0 (None is not 0) |

### Synthetic examples of the kit (`cd td1 && python atelier-vote.py`)

| Example | Values | Decision (2-of-3) | vs reference 100 |
|---|---|---|---|
| agreement | 100, 100, 120 | 100, 2 votes | right |
| disagreement | 100, 110, 120 | abstain, best 1 | — |
| unavailable | 100, None, None | abstain, best 1 (n stays 3) | — |
| wrong consensus | 0, 0, 100 | **0**, 2 votes | **wrong**: agreement is not truth |

Evidence: [`td2/step1-synthetic.jsonl`](../td2/step1-synthetic.jsonl).

### Twenty questions: fixed 2-of-3 panel vs 3-of-5 quorum

- 2-of-3: openai/gpt-oss-120b (Groq), cohere/north-mini-code:free (OpenRouter), qwen/qwen3.8-27b (Groq), k = 2.
- 3-of-5: the same three + openai/gpt-oss-20b (Groq) + dots-studio/dots-3-note-preview:free (OpenRouter), k = 3.
- ∅ = member in `n` without a vote (invalid SQL or HTTP 429 on its last attempt).

Command: `cd td1 && python compare-quorums.py --traces traces-td1.csv` (add `--json` for one line per case). Evidence: [`td2/step1-2of3-vs-3of5.jsonl`](../td2/step1-2of3-vs-3of5.jsonl), [`td2/step1-2of3-atelier.jsonl`](../td2/step1-2of3-atelier.jsonl) (the 2-of-3 decisions of `atelier-vote.py --case C01..C20`: identical to those of the driver).

| Case | Reference | Last-attempt values (120B, North, Qwen, 20B, Dots) | 2-of-3 decision | vs ref | 3-of-5 decision | vs ref | 2-of-3 → 3-of-5 |
|---|---|---|---|---|---|---|---|
| C01 | 792800 | 120B 792800, North 792800, Qwen 792800, 20B 792800, Dots 792800 | **792800** (3/3, k=2) | right | **792800** (5/5, k=3) | right | same |
| C02 | 590320 | 120B 590320, North 2606320, Qwen 590320, 20B 0, Dots 590320 | **590320** (2/3, k=2) | right | **590320** (3/5, k=3) | right | same |
| C03 | 936350 | 120B 936350, North 936350, Qwen 936350, 20B 936350, Dots 936350 | **936350** (3/3, k=2) | right | **936350** (5/5, k=3) | right | same |
| C04 | 2826250 | 120B 2826250, North 2826250, Qwen 2826250, 20B 2826250, Dots 2826250 | **2826250** (3/3, k=2) | right | **2826250** (5/5, k=3) | right | same |
| C05 | 38480 | 120B 38480, North 38480, Qwen 38480, 20B 38480, Dots 38480 | **38480** (3/3, k=2) | right | **38480** (5/5, k=3) | right | same |
| C06 | 0 | 120B 0, North 0, Qwen 0, 20B 0, Dots 0 | **0** (3/3, k=2) | right | **0** (5/5, k=3) | right | same |
| C07 | 13970 | 120B 13970, North 13970, Qwen 13970, 20B 13970, Dots 13970 | **13970** (3/3, k=2) | right | **13970** (5/5, k=3) | right | same |
| C08 | 605580 | 120B 605580, North ∅, Qwen 605580, 20B 605580, Dots 160920 | **605580** (2/3, k=2) | right | **605580** (3/5, k=3) | right | same |
| C09 | 487980 | 120B 487980, North 487980, Qwen 487980, 20B 487980, Dots 487980 | **487980** (3/3, k=2) | right | **487980** (5/5, k=3) | right | same |
| C10 | 558980 | 120B 558980, North 119410, Qwen ∅, 20B 558980, Dots 0 | abstain (best 1/3, k=2) | abstain | abstain (best 2/5, k=3) | abstain | same |
| C11 | 446690 | 120B 446690, North 0, Qwen 446690, 20B 322160, Dots 446690 | **446690** (2/3, k=2) | right | **446690** (3/5, k=3) | right | same |
| C12 | 1666490 | 120B 1666490, North 1666490, Qwen 1666490, 20B 1666490, Dots 1666490 | **1666490** (3/3, k=2) | right | **1666490** (5/5, k=3) | right | same |
| C13 | 107740 | 120B 107740, North 107740, Qwen 107740, 20B 107740, Dots 107740 | **107740** (3/3, k=2) | right | **107740** (5/5, k=3) | right | same |
| C14 | 0 | 120B 0, North 0, Qwen 0, 20B 0, Dots 0 | **0** (3/3, k=2) | right | **0** (5/5, k=3) | right | same |
| C15 | 168680 | 120B 168680, North 168680, Qwen 0, 20B 168680, Dots 138920 | **168680** (2/3, k=2) | right | **168680** (3/5, k=3) | right | same |
| C16 | 376740 | 120B 376740, North 595500, Qwen ∅, 20B 376740, Dots 211260 | abstain (best 1/3, k=2) | abstain | abstain (best 2/5, k=3) | abstain | same |
| C17 | 258180 | 120B 80190, North 371990, Qwen 248490, 20B 258180, Dots 258180 | abstain (best 1/3, k=2) | abstain | abstain (best 2/5, k=3) | abstain | same |
| C18 | 62480 | 120B 62480, North 62480, Qwen 62480, 20B 62480, Dots 39580 | **62480** (3/3, k=2) | right | **62480** (4/5, k=3) | right | same |
| C19 | 1990 | 120B 1990, North 71640, Qwen 83580, 20B 1990, Dots 0 | abstain (best 1/3, k=2) | abstain | abstain (best 2/5, k=3) | abstain | same |
| C20 | 1106090 | 120B 1106090, North 1106090, Qwen 1106090, 20B 1106090, Dots 1106090 | **1106090** (3/3, k=2) | right | **1106090** (5/5, k=3) | right | same |

| Quorum | Right | Wrong | Abstentions | Right / answers given | Right / questions asked |
|---|---|---|---|---|---|
| 2-of-3 | 16 | 0 | 4 | 16 / 16 | 16 / 20 |
| 3-of-5 | 16 | 0 | 4 | 16 / 16 | 16 / 20 |

### Commentary: where moving from 2-of-3 to 3-of-5 changes something

**No decision changes on these twenty questions**: the same 16 consensus values (all equal to the reference) and the same 4 abstentions (C10, C16, C17, C19). What changes is the vote margin.

Margin now exactly at the threshold (one more failure → abstention):

- **C02**: 2-of-3 accepts 590320 with 120B + Qwen; North votes 2606320 (incorrect). 3-of-5 adds Dots 590320 (correct) but also 20B 0 (incorrect): 3 votes for k = 3. The 3-of-5 margin is zero.
- **C08**: North is in `n` without a vote (`sql_invalid`, alias `AS age` inside WHERE, no value). 2-of-3: 120B + Qwen = 2/3. 3-of-5: + 20B 605580, while Dots votes 160920 (incorrect): 3/5, zero margin. The invalid SQL weighs more against a 3-of-5 quorum: it is one vote missing out of three required.
- **C11**: 120B + Qwen 446690; North 0 (incorrect). 3-of-5: + Dots 446690, 20B 322160 (incorrect): 3/5, zero margin.
- **C15**: 120B + North 168680; Qwen 0 (incorrect). 3-of-5: + 20B 168680, Dots 138920 (incorrect): 3/5, zero margin.

Margin improved:

- **C18**: Qwen got HTTP 429 on attempt 1, then 62480 on attempt 2 (the last attempt is the one that votes). 3/3 → 4/5, Dots 39580 the only dissent: one spare vote above k = 3.
- C01, C03–C07, C09, C12–C14, C20: unanimous in both (3/3 and 5/5).

Abstentions that 3-of-5 does not rescue (best count goes from 1 to 2, still below k = 3):

- **C10**: Qwen `sql_invalid` (no value), North 119410, Dots 0: only 120B and 20B give 558980. 2/5 < 3.
- **C16**: Qwen's last attempt (attempt 2) is HTTP 429: no vote, but it stays in `n`. North 595500, Dots 211260. Only 120B + 20B give 376740: 2/5. With "2 of the 4 answers received" the threshold would have been lowered after seeing the answers — forbidden (slide 21).
- **C17**: 120B 80190, North 371990, Qwen 248490 are three different wrong values; 20B and Dots both give the reference 258180: 2/5. The two right models are exactly the two outside the fixed panel.
- **C19**: Qwen's attempt 1 is HTTP 429, attempt 2 gives 83580 (incorrect); North 71640, Dots 0. Only 120B + 20B give 1990: 2/5.

### What we conclude (on this batch only)

- Neither quorum delivered a wrong value here; both say "I do not know" on 4 / 20. Twenty questions do not give a general error rate.
- 3-of-5 costs two more calls per question for no extra right answer on this batch, and it is thinner: four questions (C02, C08, C11, C15) pass with zero margin.
- The four abstentions are all age-convention questions (C10, C16, C17, C19). On C10, C16, C19 the two right answers come from 120B and 20B, two models of the **same family** (openai gpt-oss): counting them as independent evidence would overstate the agreement.
- No two models share the same wrong value on the same question in this batch (the only repeated wrong value, 0, appears on different questions): Pair B uses DEMO-SQL-C11.

### Limits

- The `incorrect` / `correct` verdicts of TD 1 are not used by the vote; they only decide whether a value is valid. A value is accepted as cast even if its SQL is wrong.
- The vote does not check that the SQL is stored (slide 7). All voting rows of this batch do carry a `sql` field.
- `models` lists `provider:model_requested` in panel order, as the skeleton docstring requires.

## Step 2 - The wrong consensus (Pair B)

Notebook: [`td2/TD2.ipynb`](../td2/TD2.ipynb).

### Why we use DEMO-SQL-C11

We searched our 100 TD 1 cells for a question where at least two models return the same wrong value (`verdict = incorrect`, identical `value`, last attempt of each model). The search returns **0 rows**, and it also returns nothing when retries are included. Our models give 18 wrong answers on 9 questions, but they never share a wrong value on the same question.

The assignment tells us to use the historical case DEMO-SQL-C11 in this situation.

### The case

| Item | Value |
|---|---|
| Question | C11: revenue excluding VAT, in euro cents, from customers exactly 25 years old on 2026-12-01 (all their orders) |
| Source / nature | Instructor's historical pilot batch, September 2026. **Not from our traces** |
| Models agreeing | `openai/gpt-oss-20b` (Groq) and `cohere/north-mini-code:free` (OpenRouter) |
| Shared wrong value | 0 |
| Reference | 446690 ([`reference-td1.csv`](../td1/reference-td1.csv)) |
| Gap | 446690 cents |

### Does the shared wrong value win?

**Real votes, from our TD 1 traces.** In our batch, Cohere also answered 0, but 20B answered 322160, so the two models do not agree here.

| Panel | Threshold | Votes | Decision | Against the reference |
|---|---|---|---|---|
| 120B, Cohere, Qwen | 2 of 3 | 446690: 2 (120B, Qwen); 0: 1 (Cohere) | 446690 | right |
| 120B, Cohere, Qwen, 20B, Dots | 3 of 5 | 446690: 3 (120B, Qwen, Dots); 322160: 1 (20B); 0: 1 (Cohere) | 446690 | right |

We counted these votes in the notebook. They match Pair A's `vote_k_sur_n` output for C11 in [`td2/step1-2of3-vs-3of5.jsonl`](../td2/step1-2of3-vs-3of5.jsonl).

**Simulation, not an observed result.** The pilot only gives the answers of 20B and Cohere. To test the shared 0, we give 20B the pilot answer and keep our TD 1 answers for the other models.

| Panel | Threshold | Votes | Decision |
|---|---|---|---|
| 120B, Cohere, Qwen | 2 of 3 | 446690: 2; 0: 1 | 446690: 20B is not in this panel, so 0 only gets Cohere's vote |
| 120B, Cohere, Qwen, 20B, Dots | 3 of 5 | 446690: 3; 0: 2 | 446690: the shared wrong value is outvoted |

### Why the two SQL queries are wrong

To be exactly 25 on 2026-12-01, a customer must be born **after 2000-12-01 and on or before 2001-12-01**.

**M1, `openai/gpt-oss-20b`, returns 0:**

The `WHERE` keeps only one birth date instead of a full year of birth dates. No customer was born on 2001-12-01, so no order is kept.

**M2, `cohere/north-mini-code:free`, returns 0:**


The `WHERE` asks for customers born on or before 2026-12-01 and also on or after 2027-12-01. Nobody can satisfy both conditions, so no row is kept.

The two models reach the same 0 for two different reasons. In both cases, `COALESCE` turns the empty sum into 0, so the query runs normally and the mistake is easy to miss.

### Delta query on `data/boutique.sqlite`

M1 and M2 keep no customer, so every customer counted by the reference is missing from them.

The corrected version gives these results : 

| `customer_id` | `birth_date` | Revenue excl. VAT (cents) |
|---|---|---|
| C001 | 2001-09-25 | 135000 |
| C002 | 2001-09-24 | 25920 |
| C003 | 2001-09-26 | 47900 |
| C006 | 2001-11-30 | 77450 |
| C008 | 2001-05-15 | 99090 |
| C009 | 2001-03-10 | 61330 |
| **Total** | | **446690** |

These 6 customers account for the exact gap: 446690 - 0 = 446690 cents.

### Independent check

We recomputed the result in plain Python, without SQL, from `customers.csv`, `orders.csv` and `product.csv`. For each customer, we take 2026 minus the birth year, and subtract 1 if the birthday falls after December 1. We then add `quantity_product * price` for the orders of customers aged 25.

Python finds the same 6 customers and the same total, 446690, which equals our reference.

### DEMO-VOTE (invented example)

This example comes from the assignment. It is **synthetic**: it is not a model answer and it does not use the shop database. One sale of 100 cents is dated 2026-01-01, and the period includes that day.

| Condition | Result |
|---|---|
| `sale_date > '2026-01-01' AND sale_date < '2026-01-02'` | 0: the sale is missed |
| `sale_date >= '2026-01-01' AND sale_date < '2026-01-02'` | 100: the sale is counted |

With the proposals `[0, 0, 100]` and 2 votes needed, 0 wins even though the reference is 100. Pair A's test T6 gives the same decision.

Two models agreeing does not prove that they are right. M1 and M2 run without error and agree on 0, while the correct answer is 446690. A vote can reduce isolated mistakes, but an answer that matters still needs a check that does not depend on the models, such as a reference query or a separate calculation on the data.

### Limits

- DEMO-SQL-C11 is a historical case. We do not have the pilot answers of 120B, Qwen and Dots, so the votes that include the shared 0 are simulations.

## Step 3 - The routing rule (Pair C)

Code: [`td2/step3-atelier-routage.py`](../td2/step3-atelier-routage.py) (adapted simulator, `POLICY_VERSION = "p2"`), supplied version kept as [`td2/step3-atelier-routage-original.py`](../td2/step3-atelier-routage-original.py). One-page rule: [`td2/step3-policy.md`](../td2/step3-policy.md).

Nature of the results below: the rates come from the **real** TD 1 traces ([`td1/traces-td1.csv`](../td1/traces-td1.csv), last attempt of each model on each question, 100 cells) compared with [`td1/reference-td1.csv`](../td1/reference-td1.csv). The simulator decisions are a **simulation**: no network call, and the availability of each resource is given by the scenario. Prices come from `portefeuille-modeles-2026-09-28.csv`.

Counting: a rate is the number of `correct` cells over the number of questions in the family. An `incorrect`, `sql_invalid` or `not_executed` (HTTP 429) cell counts as not correct and stays in the denominator.

Commands (from the repository root; `python3` on macOS and Linux):

```
python td2/step3-atelier-routage.py --traces td1/traces-td1.csv --rates-only   # TD 1 rates per family
python td2/step3-atelier-routage.py --original                                 # supplied rule
python td2/step3-atelier-routage.py --traces td1/traces-td1.csv                # our rule, policy p2
```

Evidence: [`td2/step3-routage-avant.txt`](../td2/step3-routage-avant.txt) (before adaptation), [`td2/step3-routage-apres.txt`](../td2/step3-routage-apres.txt) (after adaptation).

### TD 1 rates per family

| Family (cells) | gpt-oss-120b | gpt-oss-20b | qwen3.8-27b | north-mini-code:free | dots-3-note-preview:free |
|---|---|---|---|---|---|
| F1 period (C01, C04, C05, C06, C07, C20) | 6/6 | 6/6 | 6/6 | 6/6 | 6/6 |
| F2 age on a date (C02, C08, C09, C11) | 4/4 | 2/4 (C02, C11 incorrect) | 4/4 | 1/4 (C02, C11 incorrect; C08 sql_invalid) | 3/4 (C08 incorrect) |
| F2b age at the order (C10) | 1/1 | 1/1 | 0/1 (sql_invalid) | 0/1 (incorrect) | 0/1 (incorrect) |
| F3 product list (C12; C03, C13, C14 with a period) | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 |
| Combinations with age (C15 to C19) | 4/5 (C17 incorrect) | 5/5 | 1/5 (C15, C17, C19 incorrect; C16 HTTP 429) | 2/5 (C16, C17, C19 incorrect) | 1/5 (C15, C16, C18, C19 incorrect) |
| **Total** | **19/20** | **18/20** | **15/20** | **13/20** | **14/20** |

**Questions where no quorum of free models reaches the right value:** C10, C16, C17 and C19. At most 2 of the 5 models are correct on each of them, so neither the 2-of-3 panel nor the 3-of-5 quorum reaches the reference (Step 1 above: both quorums abstain on these four questions).

Single models do answer them: gpt-oss-20b is right on all four, and gpt-oss-120b on three (it misses C17). The danger is that nothing tells us in advance which model will be right. The checking cost studied in TD 3 comes from these questions.

### The rule

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

### Routing rule worksheet (course template `routing-rule-en.md`)

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

### Simulator

**Before adaptation** (supplied rule, `td2/step3-routage-avant.txt`):

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

**After adaptation** (`td2/step3-routage-apres.txt`, policy p2). The seven supplied scenarios keep their names and are mapped to our families: difficulty 1 becomes F1, difficulty 3 becomes F2, high impact becomes a payout, and difficulty 4 becomes a family absent from TD 1. Eight more scenarios test the rest of our rule.

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

### Priority in the supplied `choose`

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

### Limits and open points

- `five-model-summary-en.csv` gives qwen "5 out of 6" on period questions and "paid" access. The merged traces (last attempt) give 6/6, and the portfolio lists the Groq route for qwen3.8-27b as free. This needs to be harmonised with the member who filled in that file.
- `cohere/north-mini-code:free` and `dots-studio/dots-3-note-preview:free` are not in `portefeuille-modeles-2026-09-28.csv`. They are treated as free because of their `:free` suffix on OpenRouter and the `cost_native = 0` in the TD 1 traces.

### Contributions of Pair C

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
  - Step 3 is now in this report;
  - the commands use `python`.

### Next steps

In TD 3, compute the cost of the "reference + human review" check on C10, C16, C17 and C19. Then decide whether a paid model, measured on the same 20 questions, could replace it.
