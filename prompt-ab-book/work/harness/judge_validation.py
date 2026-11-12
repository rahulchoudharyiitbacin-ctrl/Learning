"""Check an LLM judge against human labels (Chapter 8).

Usage:
    # split human-labelled examples, stratified by label
    python judge_validation.py split labelled.csv --seed 1
        -> labelled.train.csv, labelled.dev.csv, labelled.test.csv

    # compare the judge with the human, on dev (while iterating) or
    # once on test (at the end). CSV columns: id,human_label,judge_label
    python judge_validation.py report dev-judged.csv

"Positive" means the failure is present (label FAIL), as in Husain's
evals FAQ. TPR = share of real failures the judge catches.
TNR = share of real passes the judge passes.
"""
import argparse
import csv
import math
import random
import sys
from pathlib import Path

POS, NEG = "FAIL", "PASS"


# ---- counts --------------------------------------------------
def confusion(human, judge, pos=POS):
    """Return dict tp, fn, fp, tn. Rows where the judge gave no
    PASS/FAIL count as 'none' and are left out of the four cells."""
    c = {"tp": 0, "fn": 0, "fp": 0, "tn": 0, "none": 0}
    for h, j in zip(human, judge):
        h, j = h.strip().upper(), j.strip().upper()
        if h not in (POS, NEG):
            raise ValueError(f"human label must be PASS or FAIL, got {h!r}")
        if j not in (POS, NEG):
            c["none"] += 1
        elif h == pos:
            c["tp" if j == pos else "fn"] += 1
        else:
            c["fp" if j == pos else "tn"] += 1
    return c


def _div(a, b):
    return a / b if b else float("nan")


def tpr(c):
    return _div(c["tp"], c["tp"] + c["fn"])


def tnr(c):
    return _div(c["tn"], c["tn"] + c["fp"])


def precision_fail(c):
    return _div(c["tp"], c["tp"] + c["fp"])


def agreement(c):
    n = c["tp"] + c["fn"] + c["fp"] + c["tn"]
    return _div(c["tp"] + c["tn"], n)


def cohens_kappa(c):
    """(observed agreement - chance agreement) / (1 - chance agreement)."""
    n = c["tp"] + c["fn"] + c["fp"] + c["tn"]
    if not n:
        return float("nan")
    po = (c["tp"] + c["tn"]) / n
    h_fail, j_fail = (c["tp"] + c["fn"]) / n, (c["tp"] + c["fp"]) / n
    pe = h_fail * j_fail + (1 - h_fail) * (1 - j_fail)
    return _div(po - pe, 1 - pe) if pe != 1 else float("nan")


def wilson(k, n, z=1.96):
    """Wilson score interval for k successes out of n (95% by default)."""
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    den = 1 + z * z / n
    mid = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (max(0.0, mid - half), min(1.0, mid + half))


def corrected_fail_rate(observed_fail, tpr_, tnr_):
    """Estimate the true failure rate from the judge's observed one.

    observed = TPR * true + (1 - TNR) * (1 - true), so
    true = (observed + TNR - 1) / (TPR + TNR - 1).
    A point estimate only: it ignores the uncertainty in TPR and TNR,
    and it is useless when TPR + TNR is close to 1. Clipped to [0, 1].
    """
    j = tpr_ + tnr_ - 1
    if j <= 0:
        raise ValueError("TPR + TNR must exceed 1 (judge better than chance)")
    return min(1.0, max(0.0, (observed_fail + tnr_ - 1) / j))


def report(c, out=print):
    n = c["tp"] + c["fn"] + c["fp"] + c["tn"]
    out(f"{n} rows compared" + (f" ({c['none']} with no judge verdict, left out)"
                                if c["none"] else ""))
    out("")
    out("                 judge FAIL  judge PASS")
    out(f"human FAIL  {c['tp']:>12} {c['fn']:>11}")
    out(f"human PASS  {c['fp']:>12} {c['tn']:>11}")
    out("")
    lo, hi = wilson(c["tp"], c["tp"] + c["fn"])
    out(f"TPR    {tpr(c):.3f}  95% CI {lo:.3f}-{hi:.3f}  n={c['tp'] + c['fn']}")
    lo, hi = wilson(c["tn"], c["tn"] + c["fp"])
    out(f"TNR    {tnr(c):.3f}  95% CI {lo:.3f}-{hi:.3f}  n={c['tn'] + c['fp']}")
    out(f"Kappa  {cohens_kappa(c):.3f}")
    out(f"Agree  {agreement(c):.3f}  (misleading if imbalanced)")
    out(f"Precision on FAIL  {precision_fail(c):.3f}")
    out("TPR: share of human FAILs the judge caught.")
    out("TNR: share of human PASSes the judge passed.")
    small = [name for name, k in (("FAIL", c["tp"] + c["fn"]),
                                   ("PASS", c["tn"] + c["fp"])) if k < 30]
    if small:
        out(f"Note: under 30 human {' and '.join(small)} examples,")
        out("so the intervals are wide.")


# ---- stratified split ---------------------------------------
def stratified_split(rows, label_key="human_label", train=0.15, dev=0.425,
                     seed=1):
    """Split rows into train/dev/test with the same label mix in each.
    Defaults follow Husain's FAQ: 10-20% train (may appear in the
    judge prompt as examples), 40-45% dev, 40-45% test."""
    if not 0 <= train < 1 or not 0 < dev < 1 or train + dev >= 1:
        raise ValueError("need 0 <= train, 0 < dev, train + dev < 1")
    rng = random.Random(seed)
    by = {}
    for r in rows:
        by.setdefault(r[label_key].strip().upper(), []).append(r)
    parts = {"train": [], "dev": [], "test": []}
    for label in sorted(by):
        group = by[label][:]
        rng.shuffle(group)
        n = len(group)
        n_train = int(round(n * train + 1e-9))
        n_dev = int(round(n * dev + 1e-9))
        parts["train"] += group[:n_train]
        parts["dev"] += group[n_train:n_train + n_dev]
        parts["test"] += group[n_train + n_dev:]
    for p in parts.values():
        rng.shuffle(p)
    return parts


def read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path, rows):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def cmd_split(args):
    rows = read_csv(args.csv)
    parts = stratified_split(rows, train=args.train, dev=args.dev,
                             seed=args.seed)
    base = Path(args.csv)
    for name, part in parts.items():
        if not part:
            print(f"{name}: empty, not written")
            continue
        path = base.with_suffix(f".{name}.csv")
        write_csv(path, part)
        n_fail = sum(r["human_label"].strip().upper() == POS for r in part)
        print(f"{name}: {len(part)} rows ({n_fail} FAIL, "
              f"{len(part) - n_fail} PASS) -> {path}")
    print("Iterate the judge prompt on dev only. Score test once, at the end.")


def cmd_report(args):
    rows = read_csv(args.csv)
    if not rows:
        sys.exit("empty file")
    c = confusion([r["human_label"] for r in rows],
                  [r["judge_label"] for r in rows])
    report(c)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Validate an LLM judge.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("split")
    s.add_argument("csv")
    s.add_argument("--train", type=float, default=0.15)
    s.add_argument("--dev", type=float, default=0.425)
    s.add_argument("--seed", type=int, default=1)
    r = sub.add_parser("report")
    r.add_argument("csv")
    args = ap.parse_args(argv)
    {"split": cmd_split, "report": cmd_report}[args.cmd](args)


if __name__ == "__main__":
    main()
