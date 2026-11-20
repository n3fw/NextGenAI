#!/usr/bin/env python3
"""TD 2, Step 1 (Pair A): contract tests of vote_k_sur_n, written to voting-tests-td2.csv.

Synthetic inputs only (nature = simulation), no network. Columns follow the
template templates/voting-tests-en.csv of the course kit.

    python test-vote.py            # from td2/A-quorum/: prints each test and writes voting-tests-td2.csv
"""
import csv
import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
KIT = HERE.parent.parent / "td1"  # the skeleton with vote_k_sur_n lives with the course kit
spec = importlib.util.spec_from_file_location("skeleton", KIT / "skeleton-multi-llm-en.py")
skeleton = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = skeleton
spec.loader.exec_module(skeleton)


def vote(proposals, k):
    return skeleton.Orchestrateur.vote_k_sur_n(None, proposals, k)


def panel(*members):
    """members: (provider, model, value); value None means error / unavailable."""
    return [SimpleNamespace(provider=p, model_requested=m, value=v,
                            verdict="executed" if v is not None else "error") for p, m, v in members]


A, B, C = ("groq", "openai/gpt-oss-120b"), ("openrouter", "cohere/north-mini-code:free"), ("groq", "qwen/qwen3.8-27b")
D, E = ("groq", "openai/gpt-oss-20b"), ("openrouter", "dots-studio/dots-3-note-preview:free")

# test_id, panel, k, expected (consensus value, or "abstain", or "ValueError")
TESTS = [
    ("T1-agreement", panel((*A, 100), (*B, 100), (*C, 120)), 2, 100),
    ("T2-disagreement", panel((*A, 100), (*B, 110), (*C, 120)), 2, "abstain"),
    ("T3-one-unavailable", panel((*A, 42), (*B, 42), (*C, None)), 2, 42),
    ("T4-two-unavailable", panel((*A, 42), (*B, None), (*C, None)), 2, "abstain"),
    ("T5-slide16-3of5", panel((*A, 42), (*B, 42), (*C, None), (*D, None), (*E, 41)), 3, "abstain"),
    ("T6-wrong-consensus", panel((*A, 0), (*B, 0), (*C, 100)), 2, 0),
    ("T7-duplicate-route", panel((*A, 42), (*A, 42), (*B, 41)), 2, "ValueError"),
    ("T8-k-not-majority", panel((*A, 42), (*B, 42), (*C, 41)), 1, "ValueError"),
    ("T9-k-above-n", panel((*A, 42), (*B, 42), (*C, 42)), 4, "ValueError"),
    ("T10-zero-is-a-value", panel((*A, 0), (*B, 0), (*C, None)), 2, 0),
]


def main():
    rows, failures = [], 0
    for test_id, proposals, k, expected in TESTS:
        try:
            result = vote(proposals, k)
            actual = result["value"] if result["consensus"] else "abstain"
            agreeing = ";".join(result["models"])
            shown = json.dumps(result)
        except ValueError as error:
            actual, agreeing, shown = "ValueError", "", f"ValueError: {error}"
        ok = actual == expected
        failures += not ok
        print(f"{'PASS' if ok else 'FAIL'} {test_id}: {shown}")
        rows.append({
            "test_id": test_id, "nature": "simulation",
            "panel": ";".join(f"{p.provider}:{p.model_requested}" for p in proposals),
            "fixed_n": len(proposals), "k": k,
            "input_values": ";".join("None" if p.value is None else str(p.value) for p in proposals),
            "unavailable_members": ";".join(f"{p.provider}:{p.model_requested}" for p in proposals if p.value is None),
            "expected_result_or_abstention": expected, "actual_result": actual,
            "agreeing_members": agreeing, "evidence_file": "test-vote.py",
        })
    with open(HERE / "voting-tests-td2.csv", "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"\n{len(TESTS) - failures}/{len(TESTS)} passed; written to voting-tests-td2.csv")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
