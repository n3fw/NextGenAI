# Step 3 - The routing rule (Pair C: Fabien RAMEL, Rayan IGUERCHA)

We wrote the routing policy of the sub-group (version **p2**) and adapted the kit's simulator `atelier-routage.py` to it. Each question family gets a first model, a check that depends on the use, and a fallback when the first model is unavailable.

- **Evidence:** the exact TD 1 rate of each model on each family, read from `td1/traces-td1.csv` (last attempt, 100 cells).
- **First model:** the free model with the best TD 1 rate on the family: gpt-oss-120b everywhere, gpt-oss-20b on combinations with age (5/5).
- **Check:** `none` only for an internal dashboard with a model at 100 % on the family; a quorum or a reference query for a figure shown to a customer; reference query and human review for a payout.
- **Fallback:** a model in HTTP 429 and a provider that is down are separate cases; a quorum is kept only when its voters are available, otherwise a reference query; never a model below 75 % on the family.
- **Hard questions:** C10, C16, C17, C19, where no quorum of free models reaches the right value.

The full analysis is in [`reports/td2.md`](../../reports/td2.md), section "Step 3".

## Files

| File | Content |
|---|---|
| [`step3-policy.md`](step3-policy.md) | the one-page routing rule (policy p2) |
| [`step3-routing-rule.md`](step3-routing-rule.md) | rates per family, rule, worksheet R1 to R5, simulator outputs, analysis of `choose` |
| [`step3-atelier-routage.py`](step3-atelier-routage.py) | adapted simulator: TD 1 rates read from the traces, our resources, `choose` with TD 1 cells in every reason |
| [`step3-atelier-routage-original.py`](step3-atelier-routage-original.py) | the supplied simulator, unchanged |
| [`step3-routage-avant.txt`](step3-routage-avant.txt) | output before adaptation (7 scenarios) |
| [`step3-routage-apres.txt`](step3-routage-apres.txt) | output after adaptation (15 scenarios, policy p2) |

## Reviews

| File | Content |
|---|---|
| [`review-1.md`](review-1.md) | our review of Step 1 (Pair A) |
| [`review-2.md`](review-2.md) | our review of Step 2 (Pair B) |

Our Step 3 was reviewed by Pair A ([`../A-quorum/review-2.md`](../A-quorum/review-2.md)) and Pair B ([`../B-consensus/review-2.md`](../B-consensus/review-2.md)).

## Run

From the repository root. No API key and no network; on macOS / Linux, type `python3`.

```
python td2/C-routing/step3-atelier-routage.py --traces td1/traces-td1.csv --rates-only   # TD 1 rates per family
python td2/C-routing/step3-atelier-routage.py --original                                 # supplied rule
python td2/C-routing/step3-atelier-routage.py --traces td1/traces-td1.csv                # our rule, policy p2
```
