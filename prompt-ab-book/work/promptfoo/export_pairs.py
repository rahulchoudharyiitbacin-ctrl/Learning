"""Turn a promptfoo results.json into per-case paired data.

promptfoo reports a pass rate per prompt. For an A/B verdict you
need the paired, per-case view of Chapter 9: average the repeats
of each case first, then compare A and B on the same case.

  python export_pairs.py results.json --a A-v1 --b B-v2 \
      [--out pairs.csv] [--gate B-v2 --min 0.90]

Writes one row per case: case, mean_a, mean_b, diff (b - a).
--gate makes the script exit 1 if that prompt's accuracy
(mean of per-case means) is below --min. Useful in CI.
No statistics here on purpose: feed pairs.csv to Chapter 9.
"""
import argparse
import csv
import json
import sys
from collections import defaultdict
from statistics import mean


def load(path):
    data = json.load(open(path))["results"]
    labels = [p.get("label") or p.get("raw") for p in data["prompts"]]
    grades = defaultdict(list)          # (label, case) -> [0/1, ...]
    errors = 0
    for r in data["results"]:
        label = labels[r["promptIdx"]]
        case = (r.get("testCase") or {}).get("description") \
            or f"test{r['testIdx']}"
        if r.get("error") and not r.get("gradingResult"):
            errors += 1              # count, do not grade as wrong
            continue
        grades[(label, case)].append(1 if r["success"] else 0)
    return labels, grades, errors


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("results")
    ap.add_argument("--a", required=True)
    ap.add_argument("--b", required=True)
    ap.add_argument("--out", default="pairs.csv")
    ap.add_argument("--gate")
    ap.add_argument("--min", type=float)
    args = ap.parse_args()

    labels, grades, errors = load(args.results)
    for lab in (args.a, args.b):
        if lab not in labels:
            sys.exit(f"prompt label {lab!r} not in {labels}")
    cases = sorted({c for (_, c) in grades})
    rows, acc = [], {}
    for lab in (args.a, args.b):
        means = [mean(grades[(lab, c)]) for c in cases
                 if grades[(lab, c)]]
        acc[lab] = mean(means) if means else float("nan")
    for c in cases:
        a, b = grades[(args.a, c)], grades[(args.b, c)]
        if a and b:                      # pair only complete cases
            rows.append((c, mean(a), mean(b), mean(b) - mean(a)))

    with open(args.out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["case", "mean_a", "mean_b", "diff"])
        for c, ma, mb, d in rows:
            w.writerow([c, f"{ma:.4f}", f"{mb:.4f}", f"{d:.4f}"])

    wins = sum(d > 0 for *_, d in rows)
    losses = sum(d < 0 for *_, d in rows)
    print(f"{args.a}: accuracy {acc[args.a]:.3f}")
    print(f"{args.b}: accuracy {acc[args.b]:.3f}")
    print(f"paired cases: {len(rows)}  B wins {wins}, loses {losses}, "
          f"ties {len(rows) - wins - losses}")
    if rows:
        print(f"mean diff (B - A): {mean(d for *_, d in rows):+.3f}")
    print(f"errors skipped: {errors}   wrote {args.out}")

    if args.gate:
        if args.gate not in acc or args.min is None:
            sys.exit("--gate needs a known label and --min")
        if not acc[args.gate] >= args.min:
            print(f"GATE FAILED: {args.gate} {acc[args.gate]:.3f} "
                  f"< {args.min}")
            sys.exit(1)
        print(f"gate passed: {args.gate} >= {args.min}")


if __name__ == "__main__":
    main()
