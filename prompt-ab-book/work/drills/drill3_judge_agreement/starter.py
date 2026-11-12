"""Drill 3 starter: judge-agreement metrics from a labels CSV.

Copy this file to my_drill3.py, fill in the TODOs, then run
    python test_drill3.py my_drill3.py

Read README.md for the full task. Standard library only.
"Positive" means the failure is present (label FAIL).
"""
import csv
import math
import sys


def load_labels(path):
    """Read a CSV with columns id,human_label,judge_label.
    Return a list of {"id", "human", "judge"} dicts."""
    # TODO
    raise NotImplementedError


def wilson(k, n, z=1.96):
    """Wilson score interval (lo, hi) for k successes out of n.
    Return None if n == 0."""
    # TODO
    raise NotImplementedError


def agreement_report(rows, positive="FAIL"):
    """Return a dict with:
    tp, fn, fp, tn, skipped, n, n_pos, n_neg,
    tpr, tnr, agreement, kappa, tpr_ci, tnr_ci.
    Use None for any number that is undefined (0 in a denominator).
    """
    # TODO 1: normalise labels; raise ValueError on a bad human label
    # TODO 2: skip (and count) rows where the judge gave no PASS/FAIL
    # TODO 3: confusion counts, TPR, TNR, raw agreement
    # TODO 4: Cohen's kappa, with the pe == 1 case
    # TODO 5: Wilson intervals for TPR and TNR
    raise NotImplementedError


if __name__ == "__main__":
    rows = load_labels(sys.argv[1] if len(sys.argv) > 1 else "labels.csv")
    print(agreement_report(rows))
