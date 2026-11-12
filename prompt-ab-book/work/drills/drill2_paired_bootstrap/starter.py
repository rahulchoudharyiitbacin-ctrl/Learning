"""Drill 2 starter: paired bootstrap, clustered by case.

Copy this file to my_drill2.py, fill in the TODOs, then run
    python test_drill2.py my_drill2.py

Read README.md for the full task. Standard library only.
"""
import json
import math
import random
import sys


def case_diffs(records, a="A", b="B"):
    """Return (diffs, dropped).

    records: iterable of dicts with case_id, variant, run, grade.
             grade is a number in [0, 1], or None for an API error.
    diffs:   {case_id (str): mean grade of b - mean grade of a}
    dropped: sorted list of case_ids that lack a graded run for
             a or for b.
    """
    # TODO
    raise NotImplementedError


def paired_bootstrap(records, a="A", b="B", n_boot=5000, seed=0,
                     alpha=0.05):
    """Return {"mean_diff", "ci_low", "ci_high", "n_cases",
    "dropped_cases"}.

    Percentile bootstrap that resamples cases (their d values) with
    replacement, n_boot times, using random.Random(seed). After
    sorting the n_boot means:
        ci_low  = means[int(alpha / 2 * n_boot)]
        ci_high = means[math.ceil((1 - alpha / 2) * n_boot) - 1]
    Raise ValueError if fewer than 2 cases remain.
    """
    # TODO
    raise NotImplementedError


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "records.jsonl"
    with open(path) as f:
        recs = [json.loads(x) for x in f if x.strip()]
    print(paired_bootstrap(recs))
