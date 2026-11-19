# Review 3 - Step 3 (Pair C) reviewed by Pair B (Lydia CHAIB, Quentin PERRIGAULT)

**What we checked.** We re-ran the three commands of Step 3 from the repository root on a fresh clone. We recounted the per-family rates with our own script, without using Pair C's code. We then read `choose`, `required_check` and `feasible_check` in [`td2/step3-atelier-routage.py`](../step3-atelier-routage.py) against [`td2/step3-policy.md`](../step3-policy.md).

| Claim of Pair C | How we checked | Result |
|---|---|---|
| TD 1 rates per family (25 cells of the table) | recounted the last attempt of each model on each family from [`td1/traces-td1.csv`](../../td1/traces-td1.csv), with our own script | confirmed, 25 / 25; totals 19, 18, 15, 13, 14 out of 20 |
| `--original` gives the supplied rule | compared with `python td1/atelier-routage.py` and [`step3-routage-avant.txt`](../step3-routage-avant.txt) | identical: 7 scenarios |
| [`step3-routage-apres.txt`](../step3-routage-apres.txt) is the output of the adapted rule | re-ran `--traces td1/traces-td1.csv` | identical: 15 scenarios, policy p2 |
| Cost of a paid request | median tokens of gpt-oss-120b in the traces (638 input, 185.5 output) x prices of `portefeuille-modeles-2026-09-28.csv` | confirmed: about 0.00021 USD (gpt-oss-120b, OpenRouter) and 0.00008 USD (deepseek-v4.1-flash) |
| C10, C16, C17, C19: at most 2 of the 5 models are right | recounted per question | confirmed |
| The policy table, the code and the outputs agree | read the three functions and followed each scenario by hand | consistent, including the fallbacks (model in 429, Groq down) and the replacement of an impossible quorum by the reference query |


**Status:** every figure reproduced and correct
