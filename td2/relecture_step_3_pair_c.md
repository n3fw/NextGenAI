### Step 3 (Pair C) reviewed by Pair A (Eléa SCHOM, Clorie HU)

**What we checked.** We read [`td2/step3-routing-rule.md`](../td2/step3-routing-rule.md) and [`td2/step3-policy.md`](../td2/step3-policy.md), inspected [`td2/step3-atelier-routage.py`](../td2/step3-atelier-routage.py), and re-ran all three replay commands (`--rates-only`, `--original`, and the default p2 simulation) against [`td1/traces-td1.csv`](../td1/traces-td1.csv) to compare the outputs with [`td2/step3-routage-avant.txt`](../td2/step3-routage-avant.txt) and [`td2/step3-routage-apres.txt`](../td2/step3-routage-apres.txt).

| Claim of Pair C | How we checked | Result |
|---|---|---|
| TD 1 rates per family across the 100 cells | ran `--rates-only` on `td1/traces-td1.csv` | confirmed: 120b 19/20, 20b 18/20, qwen 15/20, north-mini 13/20, dots 14/20 |
| No quorum of free models reaches the right value on C10, C16, C17, C19 | checked cell counts (at most 2/5 models correct per question) and Pair A's Step 1 table | confirmed: both 2-of-3 and 3-of-5 abstain on these 4 questions |
| No shared wrong value on C02 and C11 | checked wrong answers in the traces | confirmed: 20b gives 0 and 322,160; north-mini gives 2,606,320 and 0 |
| Replay `--original` matches `step3-routage-avant.txt` | ran `python3 td2/step3-atelier-routage.py --original` and diffed outputs | identical: all 7 baseline scenarios match line for line |
| Replay of policy `p2` matches `step3-routage-apres.txt` | ran `python3 td2/step3-atelier-routage.py --traces td1/traces-td1.csv` | identical: all 5 rate lines and 15 simulation decisions match line for line |
| Cost calculation for paid routes (`0.00021` and `0.00008` USD) | checked `build_resources` against TD 1 median tokens (638 in, 186 out) and portfolio prices | confirmed: $(638 \times 0.15 + 186 \times 0.60) \times 10^{-6} \approx 0.000207$ USD and $(638 \times 0.035 + 186 \times 0.29) \times 10^{-6} \approx 0.000076$ USD |
| Fallback separates model-level 429 from provider-level outage | inspected `scenarios` and `choose` on `preferred model in 429` vs `groq down, F1/F2` | confirmed: 429 falls back to `qwen` (Groq, 4/4, `none`), while Groq outage falls back to `dots` (OpenRouter, 3/4, `reference query`) |
| Quorum degrades to reference query when voters are unavailable | checked `feasible_check` on `groq down, F2` and `free routes down` | confirmed: 1 voter and 0 voters trigger deterministic fallback to `reference query` |
| Unmeasured routes never run without a check | checked `assumed=True` on OpenRouter 120b and `accuracy=None` on subscription / DeepSeek | confirmed: `urgent` (`assumed=True`) upgrades `none` to `reference query`; subscription gets `reference query` |
| Policy `p1` to `p2` cross-review updates applied consistently | compared `step3-policy.md`, `step3-routing-rule.md` and `step3-atelier-routage.py` | confirmed: all 7 cross-review items are implemented and consistent across code and docs |

**Minor observations (no blocking issue):**

1. **Inconsistent handling of human review on `groq down, F2`:** In `feasible_check` (`step3-atelier-routage.py`, line 179), when a `2-of-3 quorum` (required for a dashboard with a model $< 100\%$, such as `dots` at 3/4) lacks voters, it degrades to `reference query` (without human review), whereas a `3-of-5 quorum + reference` degrades to `reference query + human review`. This matches the intended logic, though the string manipulation (`if extra else ""`) is slightly implicit.
2. **CLI default path:** Running `step3-atelier-routage.py` without `--traces` defaults to `Path("traces-td1.csv")` in the current working directory rather than `td1/traces-td1.csv`, though the documented replay commands explicitly pass `--traces td1/traces-td1.csv`.

**Status:** every rate, cost calculation, and simulation output reproduced and verified; the script runs cleanly from the repository root with zero network calls. Policy `p2` in [`td2/step3-policy.md`](../td2/step3-policy.md) and [`td2/step3-atelier-routage.py`](../td2/step3-atelier-routage.py) is validated.