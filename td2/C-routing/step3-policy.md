# Routing policy of the sub-group (TD 2, Step 3, Pair C)

**Version: p2** (18 November 2026). p1 was the first push; p2 applies the sub-group cross-review.
The code that applies this policy is `td2/C-routing/step3-atelier-routage.py` (`POLICY_VERSION = "p2"`). Evidence and analysis are in `td2/C-routing/step3-routing-rule.md`.

**Evidence:** `td1/traces-td1.csv`, 100 cells, last attempt per model and question. A rate is `correct / cases`; an error or an HTTP 429 counts as not correct.

## The rule, one line per family

| Family (TD 1 cells) | TD 1 rates: 120b / 20b / qwen / north / dots | First model called | Dashboard | Customer figure | Payout | If the first model is unavailable |
|---|---|---|---|---|---|---|
| F1 period (C01, C04, C05, C06, C07, C20) | 6/6, 6/6, 6/6, 6/6, 6/6 | gpt-oss-120b (Groq, free) | none | 3-of-5 | 3-of-5 + reference query | 429: gpt-oss-20b, qwen. Groq down: dots, north-mini (OpenRouter, 6/6). |
| F3 product list (C03, C12, C13, C14) | 4/4, 4/4, 4/4, 4/4, 4/4 | gpt-oss-120b | none | 3-of-5 | 3-of-5 + reference query | Same as F1. |
| F2 age on a date (C02, C08, C09, C11) | 4/4, 2/4, 4/4, 1/4, 3/4 | gpt-oss-120b | none | reference query + human review | reference query + human review | 429: qwen (4/4). Groq down: dots (3/4) with a check. Never north-mini or gpt-oss-20b. |
| F2b age at the order (C10) | 1/1, 1/1, 0/1, 0/1, 0/1 | gpt-oss-120b | none (single cell) | reference query + human review | reference query + human review | 429: gpt-oss-20b. Groq down: subscription + reference query. |
| Combinations with age (C15 to C19) | 4/5, 5/5, 1/5, 2/5, 1/5 | gpt-oss-20b (Groq, free) | none | reference query + human review | reference query + human review | 429: gpt-oss-120b (4/5) + reference query. Groq down: subscription + reference query. |

All five TD 1 models are free, so "the cheapest correct model" is the free model with the best TD 1 rate on the family, then the best total out of 20.

## Rules the code applies, in order

1. **Filter.** A model is eligible on a family only at 75 % or more in TD 1. A weaker model stays out, even at price zero. A family absent from TD 1 gives an abstention.
2. **Included capacity first.** Run the best eligible free model that is available. If none is, run the subscription (claude-opus-5-5, never measured in TD 1), always with a check.
3. **Defer.** If the request can wait and an eligible free model refills before the deadline, wait. A refill time is a promise: availability is measured again at wake-up.
4. **Paid route.** Otherwise run a paid route within the budget. A route measured in TD 1 goes before a cheaper unmeasured one. gpt-oss-120b on OpenRouter costs about 0.00021 USD per request; its rates are assumed from the Groq route, so it always gets a reference query.
5. **Abstain.** Otherwise abstain and say why. No figure is better than an unchecked figure.

## Checks

- **`none`** is allowed only for an internal dashboard, with a model measured at 100 % on the family, on the route that was measured.
- **A model with at least one TD 1 error on the family, or never measured,** gets a 2-of-3 quorum, even for a dashboard.
- **A customer figure or a payout** always gets a quorum or a reference query. On F2, F2b and combinations, fewer than three models are at 100 %, so the check is the reference query with a human review.
- **A quorum needs voters.** 2-of-3 needs three distinct eligible models available, 3-of-5 needs five. If they are not available, the quorum becomes a reference query.
- **A failed or missing check means no delivery.** The check belongs to the request, not to the route: a fallback route keeps the same check or a stricter one.

## Retries (stated here, not simulated)

On an HTTP 429, retry the same resource after 1 minute, at most 10 attempts (Lecture 2, slide 32). Then move to the next eligible resource. In TD 1, qwen succeeded on its second attempt.

## Limits

Twenty questions and one pass per model give an observation for this batch. They do not give a general error rate, a lasting ranking, or a guarantee for any quorum. F2b rests on one cell.

## Changes from p1 to p2

- The fallback separates a model in 429 from a provider that is down.
- A quorum is kept only when its voters are available.
- The OpenRouter route of gpt-oss-120b is marked as assumed and gets a reference query.
- The 60-minute refill is a kit assumption, not the per-minute limit seen in TD 1.
- C10, C16, C17 and C19 are described as questions where no quorum reaches the right value.
