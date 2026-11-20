#!/usr/bin/env python3
"""TD 2, Step 3 (Pair C): the routing rule of the sub-group, exercised on a simulator.

Adapted from the supplied atelier-routage.py. Still no API call and no key.
Final version of Pair C: merge of the two drafts of the pair (Fabien, Rayan).

What changed compared with the supplied version:
- RESOURCES are the five TD 1 models (free routes, from portefeuille-modeles-en),
  plus one subscription route (G1), the paid OpenRouter route of gpt-oss-120b (same model
  as the free Groq route measured in TD 1, G4) and one pay-per-token route (G3) for escalation.
- The eligibility of a model is no longer an abstract level 1/2/3: it is the exact
  correct / cases ratio of that model on the question family, read from traces-td1.csv.
- Every decision carries a reason that cites the TD 1 cells (C01..C20) behind it.
- The check depends on the use: internal dashboard, figure shown to a customer,
  amount paid out.

Usage:
    (from the repository root; on Windows use "python" instead of "python3")
    python td2/C-routing/step3-atelier-routage.py --original                          # supplied rule, before adaptation
    python td2/C-routing/step3-atelier-routage.py --traces td1/traces-td1.csv          # TD 1 rates, then our scenarios
    python td2/C-routing/step3-atelier-routage.py --traces td1/traces-td1.csv --scenario deferrable
    python td2/C-routing/step3-atelier-routage.py --traces td1/traces-td1.csv --rates-only
"""
import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

# ---------------------------------------------------------------------------
# 1. Question families (questions-td1-en.md)
# ---------------------------------------------------------------------------
FAMILIES = {
    "F1 period": ["C01", "C04", "C05", "C06", "C07", "C20"],
    "F2 age on a date": ["C02", "C08", "C09", "C11"],
    "F2b age at the order": ["C10"],
    "F3 product list": ["C03", "C12", "C13", "C14"],
    "Combined (period/age/products)": ["C15", "C16", "C17", "C18", "C19"],
}
FAMILY_OF = {case: fam for fam, cases in FAMILIES.items() for case in cases}

# The five TD 1 models: all on a free route, price 0 (portefeuille-modeles-2026-09-28.csv, G5
# for Groq; the two OpenRouter :free routes are free as well).
TD1_MODELS = [
    ("groq", "openai/gpt-oss-120b"),
    ("groq", "openai/gpt-oss-20b"),
    ("groq", "qwen/qwen3.8-27b"),
    ("openrouter", "cohere/north-mini-code:free"),
    ("openrouter", "dots-studio/dots-3-note-preview:free"),
]

# Checks, from the cheapest to the strictest.
CHECKS = ["none", "2-of-3 quorum", "3-of-5 quorum", "3-of-5 quorum + reference", "reference + human review"]


# ---------------------------------------------------------------------------
# 2. TD 1 rates per model and per family, read from the stored traces
# ---------------------------------------------------------------------------
def load_rates(path: Path, nature: str = "real"):
    """Return rates[(provider, model)][family] = {"correct": [...], "wrong": [...], "cases": [...]}.

    For each cell (model, question) only the LAST attempt counts, like atelier-vote.py.
    Denominator = number of questions of the family: an error or an unavailability (429)
    counts as a non-correct case, it is not removed from the denominator.
    """
    with path.open(encoding="utf-8", newline="") as handle:
        rows = [r for r in csv.DictReader(handle) if r.get("nature", "real") == nature]
    rows.sort(key=lambda r: r.get("date_utc", ""))  # merged files: sort by date, the last attempt wins
    last = {}
    for r in rows:
        last[(r["provider"], r["model_requested"], r["case_id"])] = r
    rates = defaultdict(lambda: defaultdict(lambda: {"correct": [], "wrong": [], "cases": []}))
    for (provider, model) in TD1_MODELS:
        for fam, cases in FAMILIES.items():
            cell = rates[(provider, model)][fam]
            for case in cases:
                cell["cases"].append(case)
                r = last.get((provider, model, case))
                verdict = r["verdict"] if r else "missing"
                (cell["correct"] if verdict == "correct" else cell["wrong"]).append(f"{case}:{verdict}")
    return rates


def ratio(cell):
    return len(cell["correct"]) / len(cell["cases"])


def print_rates(rates):
    print("# TD 1 accuracy per family (correct / cases, last attempt per cell)")
    for fam, cases in FAMILIES.items():
        line = {"family": fam, "cells": cases}
        for (provider, model) in TD1_MODELS:
            cell = rates[(provider, model)][fam]
            line[model] = f"{len(cell['correct'])}/{len(cell['cases'])}"
        print(json.dumps(line))


# ---------------------------------------------------------------------------
# 3. Resources
# ---------------------------------------------------------------------------
POLICY_VERSION = "p2"  # p1 = first push (15:14); p2 = after the sub-group cross-review (see step3-policy.md)

# Portfolio level (Lecture 2, slide 30): level 1 = G5 and G4, level 2 = G3 and G2, level 3 = G1.
LEVEL_OF_GROUP = {"G5": 1, "G4": 1, "G3": 2, "G2": 2, "G1": 3}


def build_resources(rates):
    """Free TD 1 models with their per-family TD 1 rate, then three escalation routes.

    Eligibility is derived from TD 1: accuracy[fam] = correct / cases on the family.
    The portfolio level (group) is kept for information: it is a description, not a result
    on our questions (Lecture 2, slide 33), so it never replaces a TD 1 rate.
    Routes never measured in TD 1 have accuracy None: they never run without a check.
    """
    resources = []
    for (provider, model) in TD1_MODELS:
        resources.append({
            "id": model, "model": model, "provider": provider, "access": "free", "group": "G5",
            "available": True, "cash": 0.0, "allocation": 0.0, "reset_minutes": None,
            "accuracy": {fam: ratio(rates[(provider, model)][fam]) for fam in FAMILIES},
            "evidence": {fam: rates[(provider, model)][fam] for fam in FAMILIES},
            "total": sum(len(rates[(provider, model)][fam]["correct"]) for fam in FAMILIES),
            "assumed": False,
        })
    # Subscription already paid (G1, claude-opus-5-5#claude, "retenu" in the portfolio). Not measured in TD 1.
    resources.append({"id": "claude-opus-5-5 (subscription)", "model": "claude-opus-5-5", "provider": "claude",
                      "access": "subscription", "group": "G1",
                      "available": True, "cash": 0.0, "allocation": 0.04, "reset_minutes": None,
                      "accuracy": {fam: None for fam in FAMILIES}, "evidence": {}, "assumed": False})
    # Paid route of the SAME model as the free Groq gpt-oss-120b (G4, gpt-oss-120b#openrouter,
    # 0.15 / 0.60 USD per M tokens). Cost per request = TD 1 median tokens of gpt-oss-120b
    # (638 input, 186 output) x price = ~0.00021 USD.
    # ASSUMPTION: its TD 1 rates are those of the Groq route (same model, same prompt).
    # The OpenRouter route itself was not measured in TD 1, so it never runs with check 'none'.
    g120 = rates[("groq", "openai/gpt-oss-120b")]
    resources.append({"id": "openai/gpt-oss-120b (openrouter, tokens)", "model": "openai/gpt-oss-120b",
                      "provider": "openrouter", "access": "tokens", "group": "G4",
                      "available": True, "cash": 0.00021, "allocation": 0.30, "reset_minutes": None,
                      "accuracy": {fam: ratio(g120[fam]) for fam in FAMILIES},
                      "evidence": {fam: g120[fam] for fam in FAMILIES},
                      "total": sum(len(g120[fam]["correct"]) for fam in FAMILIES), "assumed": True})
    # Pay-per-token (G3, deepseek-v4.1-flash#openrouter, 0.035 / 0.29 USD per M tokens).
    # Same token envelope: 638 x 0.035e-6 + 186 x 0.29e-6 = ~0.00008 USD per request.
    # Cheaper than gpt-oss-120b on OpenRouter, but never measured in TD 1: used only after a measured route.
    resources.append({"id": "deepseek/deepseek-v4.1-flash (tokens)", "model": "deepseek/deepseek-v4.1-flash",
                      "provider": "openrouter", "access": "tokens", "group": "G3",
                      "available": True, "cash": 0.00008, "allocation": 0.30, "reset_minutes": None,
                      "accuracy": {fam: None for fam in FAMILIES}, "evidence": {}, "assumed": False})
    for r in resources:
        r["level"] = LEVEL_OF_GROUP[r["group"]]
    return resources


# ---------------------------------------------------------------------------
# 4. The rule
# ---------------------------------------------------------------------------
def perfect_models(resources, fam):
    """Number of distinct TD 1 models at 100 % on the family: a 3-of-5 quorum needs at least 3."""
    return sum(1 for r in resources if r["access"] == "free" and r["accuracy"][fam] == 1.0)


def required_check(use, accuracy, n_perfect=5):
    """The check depends on what an error costs, and on the TD 1 rate of the first model.

    - 'none' only for an internal dashboard AND a model at 100 % on the family in TD 1;
    - dashboard with at least one TD 1 error, or a model never measured: 2-of-3 quorum;
    - figure shown to a customer: 3-of-5 quorum;
    - amount paid out: 3-of-5 quorum AND a deterministic reference query.
    If fewer than 3 TD 1 models were right on every cell of the family, a 3-of-5 quorum
    can abstain or even keep a wrong value: customer and payout uses then need the
    deterministic reference query and a human review.
    """
    if use in ("customer", "payout") and n_perfect < 3:
        return "reference + human review"
    if use == "payout":
        return "3-of-5 quorum + reference"
    if use == "customer":
        return "3-of-5 quorum"
    if accuracy == 1.0:
        return "none"
    return "2-of-3 quorum"


def voters(resources, fam, min_acc):
    """Distinct models that can vote now: free, available, measured >= min_acc on the family.

    A duplicate model on another route is not a second vote (vote_k_sur_n raises ValueError).
    Paid routes do not vote: their cost would have to be added to the request.
    """
    return sorted({r["model"] for r in resources if r["access"] == "free" and r["available"]
                   and r["accuracy"][fam] is not None and r["accuracy"][fam] >= min_acc})


def feasible_check(check, chosen, resources, fam, min_acc):
    """Make the check feasible NOW, or replace it by a deterministic one.

    - a quorum needs n voters available (2-of-3: 3, 3-of-5: 5); otherwise the quorum is
      replaced by the reference query (exact SQL written without a model);
    - a route whose TD 1 rate is assumed (not measured on that route) never gets 'none'.
    Returns (check, note).
    """
    note = ""
    need = 3 if check.startswith("2-of-3") else 5 if check.startswith("3-of-5") else 0
    if need:
        v = voters(resources, fam, min_acc)
        if len(v) < need:
            extra = " + reference" if check.endswith("+ reference") else ""
            check = "reference query" + (" + human review" if extra else "")
            note = (f"; quorum impossible now: only {len(v)} free eligible voter(s) available "
                    f"({', '.join(v) or 'none'}), replaced by the reference query")
        else:
            note = f"; voters available: {', '.join(v)}"
    if check == "none" and chosen.get("assumed"):
        check = "reference query"
        note += ("; assumption: same model as the Groq route measured in TD 1, "
                 "the OpenRouter route itself was not measured, so a reference query is added")
    return check, note


def cite(resource, fam):
    ev = resource["evidence"].get(fam)
    if not ev:
        return (f"{resource['id']} not measured in TD 1 on {fam} "
                f"(portfolio {resource['group']}, level {resource['level']}: a description, not a result)")
    return (f"{resource['id']} {len(ev['correct'])}/{len(ev['cases'])} on {fam} in TD 1 "
            f"(correct: {', '.join(c.split(':')[0] for c in ev['correct']) or 'none'}; "
            f"not correct: {', '.join(ev['wrong']) or 'none'})")


def choose(request, resources):
    """Same priority order as the supplied rule, applied to our TD 1 evidence (policy p2).

    1. run on included capacity (free or already paid subscription, cash == 0), best TD 1 rate first;
    2. otherwise defer, if the request can wait and a free route refills before the deadline;
    3. otherwise run on a paid route within the budget, a route measured in TD 1 first;
    4. otherwise abstain: no figure is better than an unchecked figure.
    A model below min_accuracy on the family is never used, even at price zero (no silent fallback).
    """
    fam, use = request["family"], request["use"]
    if fam not in FAMILIES:
        return {"action": "abstain", "resource": None, "cash": 0, "checks": "-",
                "reason": f"family '{fam}' not covered by the TD 1 evidence: no model can be declared eligible"}
    n_perfect = perfect_models(resources, fam)
    min_acc = request.get("min_accuracy", 0.75)
    measured = [r for r in resources if r["accuracy"][fam] is not None and r["accuracy"][fam] >= min_acc]
    unmeasured = [r for r in resources if r["accuracy"][fam] is None]

    included = [r for r in measured if r["available"] and r["cash"] == 0]
    if included:
        chosen = min(included, key=lambda r: (-r["accuracy"][fam], -r["total"], r["id"]))
        check, note = feasible_check(required_check(use, chosen["accuracy"][fam], n_perfect),
                                     chosen, resources, fam, min_acc)
        return {"action": "run", "resource": chosen["id"], "cash": 0, "checks": check,
                "reason": f"cheapest eligible free route, best TD 1 rate: {cite(chosen, fam)}; "
                          f"{chosen['total']}/20 overall in TD 1; {n_perfect} TD 1 models at 100 % on the family; "
                          f"use = {use}{note}"}
    sub = [r for r in unmeasured if r["available"] and r["cash"] == 0]
    if sub:
        chosen = min(sub, key=lambda r: (r["allocation"], r["id"]))
        check, note = feasible_check(required_check(use, None, n_perfect), chosen, resources, fam, min_acc)
        return {"action": "run", "resource": chosen["id"], "cash": 0, "checks": check,
                "reason": f"no free TD 1 model >= {min_acc:.0%} on {fam} is available; "
                          f"included subscription capacity used; {cite(chosen, fam)}; use = {use}{note}"}
    waiting = [r for r in measured if not r["available"] and r["cash"] == 0
               and r["reset_minutes"] is not None
               and 0 < r["reset_minutes"] <= request["deadline_minutes"]]
    if waiting and request["can_wait"]:
        chosen = min(waiting, key=lambda r: (r["reset_minutes"], -r["accuracy"][fam]))
        check = required_check(use, chosen["accuracy"][fam], n_perfect)
        return {"action": "defer", "resource": chosen["id"], "cash": 0, "checks": check,
                "reason": f"free quota exhausted, refill announced in {chosen['reset_minutes']} min <= deadline; "
                          f"a refill time is a promise, not a fact: availability and voters are measured again "
                          f"at wake-up; {cite(chosen, fam)}",
                "wake_in_minutes": chosen["reset_minutes"]}
    paid = [r for r in measured + unmeasured if r["available"] and 0 < r["cash"] <= request["budget"]]
    if paid:
        chosen = min(paid, key=lambda r: (r["accuracy"][fam] is None, -(r["accuracy"][fam] or 0), r["cash"], r["id"]))
        check, note = feasible_check(required_check(use, chosen["accuracy"][fam], n_perfect),
                                     chosen, resources, fam, min_acc)
        return {"action": "run", "resource": chosen["id"], "cash": chosen["cash"], "checks": check,
                "reason": f"no free or included route in time; paid route within budget, measured route first; "
                          f"{cite(chosen, fam)}; use = {use}{note}"}
    return {"action": "abstain", "resource": None, "cash": 0, "checks": "-",
            "reason": f"no eligible route for {fam} within deadline and budget: abstain, no invented figure"}


# ---------------------------------------------------------------------------
# 5. Scenarios (the seven situations of the supplied file, expressed with our families, then ours)
# ---------------------------------------------------------------------------
def scenarios(resources):
    """ASSUMPTION for the 60-minute refill: taken from the supplied scenarios (reset_minutes=60),
    e.g. an hourly or daily quota. It is NOT the per-minute Groq limit seen in TD 1 (HTTP 429 on qwen),
    which cleared within seconds (qwen succeeded on its second attempt)."""
    base = {"family": "F1 period", "use": "dashboard", "can_wait": True,
            "deadline_minutes": 120, "budget": 0.30}
    free_down = [dict(r, available=False, reset_minutes=60) if r["access"] == "free" else dict(r)
                 for r in resources]
    all_down = [dict(r, available=False, reset_minutes=60) if r["access"] in ("free", "subscription") else dict(r)
                for r in resources]
    groq_down = [dict(r, available=False, reset_minutes=None) if r["provider"] == "groq" else dict(r)
                 for r in resources]
    model_429 = [dict(r, available=False, reset_minutes=1) if r["id"] == "openai/gpt-oss-120b" else dict(r)
                 for r in resources]
    return [
        ("simple", base, resources),
        ("complex", {**base, "family": "F2 age on a date"}, resources),
        ("deferrable", {**base, "family": "F2 age on a date"}, all_down),
        ("urgent", {**base, "family": "F2 age on a date", "can_wait": False, "deadline_minutes": 5}, all_down),
        ("budget exhausted", {**base, "family": "F2 age on a date", "can_wait": False, "budget": 0}, all_down),
        ("high impact", {**base, "family": "F2 age on a date", "use": "payout"}, resources),
        ("unknown capability", {**base, "family": "F4 not in TD 1"}, resources),
        ("preferred model in 429", {**base, "family": "F2 age on a date"}, model_429),
        ("groq down, F1", {**base, "family": "F1 period"}, groq_down),
        ("groq down, F2", {**base, "family": "F2 age on a date"}, groq_down),
        ("customer figure", {**base, "family": "F3 product list", "use": "customer"}, resources),
        ("customer figure, weak family", {**base, "family": "F2b age at the order", "use": "customer"}, resources),
        ("combined, payout", {**base, "family": "Combined (period/age/products)", "use": "payout"}, resources),
        ("free routes down", {**base, "family": "F1 period"}, free_down),
        ("deferrable, customer figure", {**base, "family": "F2 age on a date", "use": "customer"}, all_down),
    ]


def run_original():
    """The supplied rule, unchanged, for the 'before adaptation' output."""
    import importlib.util
    here = Path(__file__).resolve().parent
    for candidate in (here / "step3-atelier-routage-original.py", here / "atelier-routage-original.py",
                      here.parent / "td1" / "atelier-routage.py", here / "kit-td1" / "atelier-routage.py"):
        if candidate.exists():
            spec = importlib.util.spec_from_file_location("orig", candidate)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            for name, request, res in mod.scenarios():
                print(json.dumps({"scenario": name, "nature": "simulation", "request": request,
                                  "result": mod.choose(request, res)}))
            return 0
    print("Copy the supplied file next to this one as step3-atelier-routage-original.py")
    return 2


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--traces", type=Path, default=Path("traces-td1.csv"))
    parser.add_argument("--scenario", help="show only the named scenario")
    parser.add_argument("--original", action="store_true", help="run the supplied rule (before adaptation)")
    parser.add_argument("--rates-only", action="store_true", help="print only the TD 1 rates per family")
    args = parser.parse_args()
    if args.original:
        return run_original()
    rates = load_rates(args.traces)
    if args.rates_only:
        print_rates(rates)
        return 0
    if not args.scenario:
        print_rates(rates)
        print("# Decisions of our rule (simulation, no call)")
    resources = build_resources(rates)
    found = False
    for name, request, res in scenarios(resources):
        if args.scenario and name != args.scenario:
            continue
        found = True
        print(json.dumps({"scenario": name, "nature": "simulation", "policy": POLICY_VERSION,
                          "request": request, "result": choose(request, res)}, ensure_ascii=False))
    if not found:
        parser.error("unknown scenario")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
