### Step 3 (Pair C) reviewed by Pair A (Eléa SCHOM, Clorie HU)

**What we checked.** We re-ran the three commands of Step 3 from the repository root and compared the per-family rates with [`td1/traces-td1.csv`](../td1/traces-td1.csv).

| Claim of Pair C | How we checked | Result |
|---|---|---|
| TD 1 rates per family (25 cells of the table) | recounted the last attempt of each model on the cells of each family | confirmed, 25 / 25 |
| `--original` gives the supplied rule | compared with `python td1/atelier-routage.py` | identical: 7 scenarios |
| [`td2/step3-routage-apres.txt`](../td2/step3-routage-apres.txt) is the output of the adapted rule | re-ran `--traces td1/traces-td1.csv` | identical: 15 scenarios, policy p2 |
| Cost of a paid request | recomputed from the TD 1 median of gpt-oss-120b (638 input and 186 output tokens) | confirmed: about 0.00021 USD (gpt-oss-120b, OpenRouter) and 0.00008 USD (deepseek-v4.1-flash) |
| Priority order in the supplied `choose` | read the four branches of the code | confirmed: an available subscription is taken in the first branch, before `defer` is tested |

**Issues found and fixed by Pair C (policy p1 to p2):**

1. R2 "preferred provider unavailable" fell back to qwen, also on Groq. Fixed: a model in 429 and Groq down are now separate cases; Groq down falls back to dots or north-mini on OpenRouter (scenarios `groq down, F1` and `groq down, F2`).
2. The scenario `free routes down` asked for a 2-of-3 quorum with no voter left. Fixed: a quorum is kept only when its voters are available, otherwise a reference query.
3. The paid OpenRouter route of gpt-oss-120b got no check although that route was never measured. Fixed: stated as an assumption, with a reference query.
4. R3 justified a 60-minute refill by a per-minute limit. Fixed: stated as an assumption of the kit scenario.
5. "No free model can answer C10, C16, C17, C19 alone" was wrong (gpt-oss-20b answers all four). Fixed: "no quorum of free models reaches the right value".
6. Step 3 was only in `td2/`. Fixed: now in this report.
7. The commands used `python3`. Fixed: `python` (`python3` on macOS and Linux).

**Status:** every figure reproduced and correct. Open point, outside Step 3: the qwen row of [`td1/five-model-summary-en.csv`](../td1/five-model-summary-en.csv) still reads "5 out of 6" on period questions and "paid" access, against 6/6 and a free route in the traces and the portfolio.

### Step 1 (Pair A) reviewed by Pair C (Fabien RAMEL, Rayan IGUERCHA)

**What we checked.** We read `vote_k_sur_n` in [`td1/skeleton-multi-llm-en.py`](../td1/skeleton-multi-llm-en.py) against its docstring, then re-ran the four commands of Step 1 from `td1/`.

| Claim of Pair A | How we checked | Result |
|---|---|---|
| The method follows the docstring contract (failed member stays in `n`, strict majority, duplicate refused, no invented value) | read the code, ran [`td1/test-vote.py`](../td1/test-vote.py) | confirmed: 10 / 10 tests pass |
| The four synthetic examples of the kit | ran `python atelier-vote.py` | confirmed: agreement 100; disagreement and unavailable abstain; wrong consensus keeps 0 |
| Twenty-question table, 2-of-3 vs 3-of-5 | ran `python compare-quorums.py --traces traces-td1.csv` | identical to the report: 16 right, 0 wrong, 4 abstentions for both |
| The 2-of-3 column matches the kit's own script | ran `python atelier-vote.py --traces traces-td1.csv --case C01` to `C20` | identical to [`td2/step1-2of3-atelier.jsonl`](../td2/step1-2of3-atelier.jsonl) |
| Values in the table are the last attempts | compared with the raw rows of the traces | confirmed, including Qwen attempt 2 on C16, C18, C19 |

**Issue found and fixed by Pair A:**

1. The rule "a failed member does not shrink the panel" was cited as Lecture 2, slide 21; it is slide 16. Fixed in this report and in the test name (`T5-slide16-3of5` in [`td1/test-vote.py`](../td1/test-vote.py), [`td1/voting-tests-td2.csv`](../td1/voting-tests-td2.csv) and [`td2/step1-tests.txt`](../td2/step1-tests.txt)).

**Status:** every figure reproduced and correct.
