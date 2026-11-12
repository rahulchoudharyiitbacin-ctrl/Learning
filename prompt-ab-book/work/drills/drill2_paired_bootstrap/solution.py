"""Drill 2 reference solution: paired bootstrap, clustered by case.

    python solution.py records.jsonl [A] [B]
"""
import json
import math
import random
import sys
from collections import defaultdict


def case_diffs(records, a="A", b="B"):
    """Return ({case_id: mean_B - mean_A}, dropped_case_ids).

    Runs are averaged per case and variant FIRST. Records with grade
    None (API errors) are skipped. A case without at least one graded
    run for both variants is dropped and listed.
    """
    grades = defaultdict(lambda: {a: [], b: []})
    seen = set()
    for r in records:
        cid = str(r["case_id"])
        seen.add(cid)
        if r["variant"] in (a, b) and r.get("grade") is not None:
            grades[cid][r["variant"]].append(float(r["grade"]))
    diffs, dropped = {}, []
    for cid in sorted(seen):
        ga, gb = grades[cid][a], grades[cid][b]
        if ga and gb:
            diffs[cid] = sum(gb) / len(gb) - sum(ga) / len(ga)
        else:
            dropped.append(cid)
    return diffs, dropped


def paired_bootstrap(records, a="A", b="B", n_boot=5000, seed=0,
                     alpha=0.05):
    """Mean paired difference (B - A) and a percentile bootstrap CI
    that resamples CASES. Same seed -> same answer, whatever the
    order of the records."""
    diffs, dropped = case_diffs(records, a, b)
    if len(diffs) < 2:
        raise ValueError("need at least 2 cases with both variants")
    d = [diffs[c] for c in sorted(diffs)]   # fixed order for the seed
    n = len(d)
    rng = random.Random(seed)
    means = sorted(sum(rng.choices(d, k=n)) / n for _ in range(n_boot))
    lo = means[int(alpha / 2 * n_boot)]
    hi = means[math.ceil((1 - alpha / 2) * n_boot) - 1]
    return {"mean_diff": sum(d) / n, "ci_low": lo, "ci_high": hi,
            "n_cases": n, "dropped_cases": dropped}


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "records.jsonl"
    a = sys.argv[2] if len(sys.argv) > 2 else "A"
    b = sys.argv[3] if len(sys.argv) > 3 else "B"
    with open(path) as f:
        recs = [json.loads(x) for x in f if x.strip()]
    res = paired_bootstrap(recs, a, b)
    print(f"{b} - {a}: {res['mean_diff']:+.3f}  95% CI "
          f"[{res['ci_low']:+.3f}, {res['ci_high']:+.3f}]  "
          f"n={res['n_cases']} cases, dropped {len(res['dropped_cases'])}")
