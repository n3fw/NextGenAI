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

