"""Helper for error analysis on the records the harness saved.

    python error_analysis.py show     EXPERIMENT.yaml [--mock] [--variant B] [--limit 20]
    python error_analysis.py show     EXPERIMENT.yaml --disagree        # A and B differ
    python error_analysis.py show     EXPERIMENT.yaml --sample-pass 5   # check the grader
    python error_analysis.py template EXPERIMENT.yaml [--mock]          # writes notes.csv
    python error_analysis.py tally    EXPERIMENT.yaml                   # counts notes.csv
"""
import argparse
import csv
import json
import random
import statistics
from collections import Counter
from pathlib import Path

import yaml

COLUMNS = ["case_id", "variant", "outputs", "what_went_wrong", "category", "where"]


def read_jsonl(path):
    lines = Path(path).read_text().splitlines()
    return [json.loads(x) for x in lines if x.strip()]


def load(args):
    cfg_path = Path(args.config).resolve()
    root = cfg_path.parent.parent
    cfg = yaml.safe_load(cfg_path.read_text())
    cases = {c["id"]: c for c in read_jsonl(root / cfg["dataset"])}
    out_dir = root / "runs" / cfg["name"]
    name = "records-mock.jsonl" if getattr(args, "mock", False) else "records.jsonl"
    records = [r for r in read_jsonl(out_dir / name) if "error" not in r]
    # group: (variant, case_id) -> list of records
    groups = {}
    for r in records:
        groups.setdefault((r["variant"], r["case_id"]), []).append(r)
    return cfg, cases, groups, out_dir


def mean_grade(recs):
    return statistics.mean(r["grade"] for r in recs)


def print_block(key, recs, cases):
    variant, cid = key
    case = cases[cid]
    outs = " | ".join(repr(r["output"]) for r in sorted(recs, key=lambda r: r["run"]))
    print(f"[{variant}] {cid}  grade {mean_grade(recs):.2f} over {len(recs)} runs")
    print(f"  input:    {case['input']}")
    print(f"  expected: {case['expected']}")
    print(f"  outputs:  {outs}\n")


def cmd_show(args):
    cfg, cases, groups, _ = load(args)
    keys = sorted(groups)
    if args.sample_pass:
        passes = [k for k in keys if mean_grade(groups[k]) == 1]
        random.Random(1).shuffle(passes)
        keys = passes[: args.sample_pass]
        print(f"{len(keys)} random PASSING cases (does the grader agree with you?)\n")
    elif args.disagree:
        ids = {c for (_, c) in groups}
        a, b = list(cfg["variants"])[:2]
        keys = [(v, c) for c in sorted(ids) for v in (a, b)
                if (a, c) in groups and (b, c) in groups
                and mean_grade(groups[(a, c)]) != mean_grade(groups[(b, c)])]
    else:
        keys = [k for k in keys if mean_grade(groups[k]) < 1]
        if args.variant:
            keys = [k for k in keys if k[0] == args.variant]
    for key in keys[: args.limit]:
        print_block(key, groups[key], cases)
    print(f"showing {min(len(keys), args.limit)} of {len(keys)}")


def cmd_template(args):
    cfg, cases, groups, out_dir = load(args)
    path = out_dir / "notes.csv"
    if path.exists() and not args.force:
        raise SystemExit(f"{path} exists; use --force to overwrite")
    rows = []
    for key in sorted(groups):
        if mean_grade(groups[key]) < 1:
            outs = " | ".join(r["output"] for r in sorted(groups[key], key=lambda r: r["run"]))
            rows.append({"case_id": key[1], "variant": key[0], "outputs": outs,
                         "what_went_wrong": "", "category": "", "where": ""})
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {len(rows)} rows to {path}")
    print("Fill in what_went_wrong first. Add category and where after you have read them all.")


def cmd_tally(args):
    cfg_path = Path(args.config).resolve()
    cfg = yaml.safe_load(cfg_path.read_text())
    out_dir = cfg_path.parent.parent / "runs" / cfg["name"]
    rows = list(csv.DictReader(open(out_dir / "notes.csv", newline="")))
    blank = [r["case_id"] for r in rows if not r["category"].strip()]
    rows = [r for r in rows if r["category"].strip()]
    print(f"{len(rows)} categorised notes ({len(blank)} still blank)\n")
    for col in ("category", "where"):
        by = Counter((r[col].strip(), r["variant"]) for r in rows if r[col].strip())
        names = sorted({n for n, _ in by}, key=lambda n: -sum(c for (m, _), c in by.items() if m == n))
        variants = sorted({v for _, v in by})
        print(f"{col:<28}" + "".join(f"{v:>6}" for v in variants) + "   total")
        for n in names:
            counts = [by.get((n, v), 0) for v in variants]
            print(f"{n:<28}" + "".join(f"{c:>6}" for c in counts) + f"   {sum(counts)}")
        print()


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, fn in (("show", cmd_show), ("template", cmd_template), ("tally", cmd_tally)):
        p = sub.add_parser(name)
        p.add_argument("config")
        p.add_argument("--mock", action="store_true")
        p.set_defaults(fn=fn)
        if name == "show":
            p.add_argument("--variant")
            p.add_argument("--limit", type=int, default=20)
            p.add_argument("--disagree", action="store_true")
            p.add_argument("--sample-pass", type=int, default=0)
        if name == "template":
            p.add_argument("--force", action="store_true")
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
