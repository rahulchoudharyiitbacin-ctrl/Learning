"""Drill 3 reference solution: judge-agreement metrics.

    python solution.py labels.csv

"Positive" = the failure is present (label FAIL), as in Chapter 8.
Undefined numbers (no examples to divide by) are None, never 0.
"""
import csv
import math
import sys

LABELS = ("PASS", "FAIL")


def load_labels(path):
    """Read id,human_label,judge_label. utf-8-sig drops an Excel BOM."""
    with open(path, newline="", encoding="utf-8-sig") as f:
        return [{"id": r["id"].strip(), "human": r["human_label"],
                 "judge": r["judge_label"]} for r in csv.DictReader(f)]


def confusion(rows, positive="FAIL"):
    """Count tp, fn, fp, tn. A judge label that is not PASS/FAIL
    (blank, ERROR) is skipped and counted. A bad human label is a
    data error: raise."""
    c = {"tp": 0, "fn": 0, "fp": 0, "tn": 0, "skipped": 0}
    for r in rows:
        h = (r["human"] or "").strip().upper()
        j = (r["judge"] or "").strip().upper()
        if h not in LABELS:
            raise ValueError(f"row {r.get('id')}: human label {h!r}")
        if j not in LABELS:
            c["skipped"] += 1
        elif h == positive:
            c["tp" if j == positive else "fn"] += 1
        else:
            c["fp" if j == positive else "tn"] += 1
    return c


def ratio(a, b):
    return a / b if b else None


def wilson(k, n, z=1.96):
    """Wilson score interval for k successes in n. None if n == 0."""
    if n == 0:
        return None
    p = k / n
    den = 1 + z * z / n
    mid = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (max(0.0, mid - half), min(1.0, mid + half))


def kappa(c):
    """Cohen's kappa. None when chance agreement is 1 (both raters
    gave one label only): 0/0 is undefined."""
    n = c["tp"] + c["fn"] + c["fp"] + c["tn"]
    if n == 0:
        return None
    po = (c["tp"] + c["tn"]) / n
    h_pos = (c["tp"] + c["fn"]) / n
    j_pos = (c["tp"] + c["fp"]) / n
    pe = h_pos * j_pos + (1 - h_pos) * (1 - j_pos)
    return None if pe >= 1 else (po - pe) / (1 - pe)


def agreement_report(rows, positive="FAIL"):
    c = confusion(rows, positive)
    pos, neg = c["tp"] + c["fn"], c["tn"] + c["fp"]
    n = pos + neg
    return {**c, "n": n, "n_pos": pos, "n_neg": neg,
            "tpr": ratio(c["tp"], pos), "tnr": ratio(c["tn"], neg),
            "agreement": ratio(c["tp"] + c["tn"], n),
            "kappa": kappa(c),
            "tpr_ci": wilson(c["tp"], pos),
            "tnr_ci": wilson(c["tn"], neg)}


def fmt(x):
    return "n/a" if x is None else f"{x:.3f}"


def fmt_ci(ci):
    return "n/a" if ci is None else f"{ci[0]:.3f}-{ci[1]:.3f}"


if __name__ == "__main__":
    rep = agreement_report(load_labels(sys.argv[1] if len(sys.argv) > 1
                                       else "labels.csv"))
    print(f"{rep['n']} rows compared, {rep['skipped']} skipped")
    print(f"          judge FAIL  judge PASS")
    print(f"human FAIL {rep['tp']:>9} {rep['fn']:>11}")
    print(f"human PASS {rep['fp']:>9} {rep['tn']:>11}")
    print(f"TPR   {fmt(rep['tpr'])}  95% CI {fmt_ci(rep['tpr_ci'])}"
          f"  n={rep['n_pos']}")
    print(f"TNR   {fmt(rep['tnr'])}  95% CI {fmt_ci(rep['tnr_ci'])}"
          f"  n={rep['n_neg']}")
    print(f"Kappa {fmt(rep['kappa'])}")
    print(f"Agree {fmt(rep['agreement'])}  (misleading if imbalanced)")
