# Review 2 - Step 3 (Pair C) reviewed by Pair A (Eléa SCHOM, Clorie HU)

**What we checked.** We re-ran the three commands of Step 3 (`python td2/C-routing/step3-atelier-routage.py ...`) from the repository root and compared the per-family rates with [`td1/traces-td1.csv`](../../td1/traces-td1.csv).

| Claim of Pair C | How we checked | Result |
|---|---|---|
| TD 1 rates per family (25 cells of the table) | recounted the last attempt of each model on the cells of each family | confirmed, 25 / 25 |
| `--original` gives the supplied rule | compared with `python td1/atelier-routage.py` | identical: 7 scenarios |
| [`td2/C-routing/step3-routage-apres.txt`](../C-routing/step3-routage-apres.txt) is the output of the adapted rule | re-ran `--traces td1/traces-td1.csv` | identical: 15 scenarios, policy p2 |
| Cost of a paid request | recomputed from the TD 1 median of gpt-oss-120b (638 input and 186 output tokens) | confirmed: about 0.00021 USD (gpt-oss-120b, OpenRouter) and 0.00008 USD (deepseek-v4.1-flash) |
| Priority order in the supplied `choose` | read the four branches of the code | confirmed: an available subscription is taken in the first branch, before `defer` is tested |

**Issues found and fixed by Pair C (policy p1 to p2):**

1. R2 "preferred provider unavailable" fell back to qwen, also on Groq. Fixed: a model in 429 and Groq down are now separate cases; Groq down falls back to dots or north-mini on OpenRouter (scenarios `groq down, F1` and `groq down, F2`).
2. The scenario `free routes down` asked for a 2-of-3 quorum with no voter left. Fixed: a quorum is kept only when its voters are available, otherwise a reference query.
3. The paid OpenRouter route of gpt-oss-120b got no check although that route was never measured. Fixed: stated as an assumption, with a reference query.
4. R3 justified a 60-minute refill by a per-minute limit. Fixed: stated as an assumption of the kit scenario.
5. "No free model can answer C10, C16, C17, C19 alone" was wrong (gpt-oss-20b answers all four). Fixed: "no quorum of free models reaches the right value".
6. Step 3 was only in `td2/`. Fixed: now also in `reports/td2.md`.
7. The commands used `python3`. Fixed: `python` (`python3` on macOS and Linux).

**Status:** every figure reproduced and correct. Open point at review time, outside Step 3: the qwen row of [`td1/five-model-summary-en.csv`](../../td1/five-model-summary-en.csv) read "5 out of 6" on period questions and "paid" access, against 6/6 and a free route in the traces and the portfolio. Fixed afterwards.
