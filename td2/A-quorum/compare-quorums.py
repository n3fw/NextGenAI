#!/usr/bin/env python3
"""TD 2, Step 1 (Pair A): fixed 2-of-3 panel against a 3-of-5 quorum, C01 to C20.

Stored TD 1 traces only: no network, no key. Lives in td2/A-quorum/ and loads
atelier-vote.py and skeleton-multi-llm-en.py from td1/. From this folder:

    python compare-quorums.py --traces ../../td1/traces-td1.csv            # Markdown table
    python compare-quorums.py --traces ../../td1/traces-td1.csv --json     # one JSON line per case

It reuses the kit's own functions (load_vote, proposals_for, evaluate) so that
both quorums follow exactly the same rules as atelier-vote.py: last attempt per
member, a value votes only if its verdict is correct/incorrect and not empty,
a failed member stays in n. The reference is compared AFTER the decision.
"""
import argparse
import csv
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
KIT = HERE.parent.parent / "td1"  # atelier-vote.py and the skeleton live with the course kit
spec = importlib.util.spec_from_file_location("atelier_vote", KIT / "atelier-vote.py")
kit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kit)

PANEL_2_OF_3 = list(kit.PANEL)  # the fixed panel of atelier-vote.py, unchanged
PANEL_3_OF_5 = PANEL_2_OF_3 + [  # the two other TD 1 models
    ("groq", "openai/gpt-oss-20b"),
    ("openrouter", "dots-studio/dots-3-note-preview:free"),
]
SHORT = {"openai/gpt-oss-120b": "120B", "cohere/north-mini-code:free": "North",
         "qwen/qwen3.8-27b": "Qwen", "openai/gpt-oss-20b": "20B",
         "dots-studio/dots-3-note-preview:free": "Dots"}


def decide(vote, rows, case, panel, k):
    kit.PANEL = panel  # proposals_for reads the module-level panel
    try:
        proposals = kit.proposals_for(rows, case, "real")
    finally:
        kit.PANEL = PANEL_2_OF_3
    result = vote(proposals, k)
    return proposals, result


def label(result, reference):
    if not result["consensus"]:
        return "abstain"
    return "right" if result["value"] == reference else "WRONG"


def cell(result, n, k):
    if result["consensus"]:
        return f"**{result['value']}** ({result['votes']}/{n}, k={k})"
    return f"abstain (best {result['votes']}/{n}, k={k})"


def ballot(proposals):
    return ", ".join(f"{SHORT[p.model_requested]} {p.value if p.value is not None else '∅'}" for p in proposals)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--traces", type=Path, required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    with args.traces.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    loaded = kit.load_vote()

    totals = {"2of3": {"right": 0, "WRONG": 0, "abstain": 0}, "3of5": {"right": 0, "WRONG": 0, "abstain": 0}}
    lines = []
    for i in range(1, 21):
        case = f"C{i:02d}"
        refs = {int(r["reference"]) for r in rows if r["case_id"] == case and r["nature"] == "real" and r["reference"]}
        if len(refs) != 1:
            raise SystemExit(f"{case}: expected one reference, found {refs}")
        reference = refs.pop()
        p3, r3 = decide(loaded, rows, case, PANEL_2_OF_3, 2)
        p5, r5 = decide(loaded, rows, case, PANEL_3_OF_5, 3)
        l3, l5 = label(r3, reference), label(r5, reference)
        totals["2of3"][l3] += 1
        totals["3of5"][l5] += 1
        if args.json:
            print(json.dumps({"case": case, "nature": "real", "reference": reference,
                              "2of3": r3, "3of5": r5, "2of3_vs_ref": l3, "3of5_vs_ref": l5}))
        lines.append(f"| {case} | {reference} | {ballot(p5)} | {cell(r3, 3, 2)} | {l3} | "
                     f"{cell(r5, 5, 3)} | {l5} | {'**changes**' if (l3, r3['value']) != (l5, r5['value']) else 'same'} |")
    if not args.json:
        print("| Case | Reference | Last-attempt values (120B, North, Qwen, 20B, Dots) | 2-of-3 decision | vs ref |"
              " 3-of-5 decision | vs ref | 2-of-3 → 3-of-5 |")
        print("|---|---|---|---|---|---|---|---|")
        print("\n".join(lines))
        print()
        for name, t in totals.items():
            print(f"- {name}: {t['right']} right, {t['WRONG']} wrong, {t['abstain']} abstentions out of 20 questions")


if __name__ == "__main__":
    main()
