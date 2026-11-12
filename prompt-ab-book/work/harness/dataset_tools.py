"""Small tools for an eval dataset (JSONL, one case per line).

    python dataset_tools.py check   data/cases-v1.jsonl --labels refund,delivery,account,other
    python dataset_tools.py summary data/cases-v1.jsonl
    python dataset_tools.py split   data/cases-v1.jsonl --dev 0.5 --seed 1
    python dataset_tools.py leak    experiments/ticket-triage-v1-vs-v2.yaml

A case needs: id, input, expected. Optional: slice, source.
"""
import argparse
import json
import random
import re
import sys
from collections import Counter
from pathlib import Path

import yaml


def read_jsonl(path):
    lines = Path(path).read_text().splitlines()
    return [json.loads(x) for x in lines if x.strip()]


def write_jsonl(path, rows):
    Path(path).write_text("".join(json.dumps(r) + "\n" for r in rows))


def norm(text):
    return re.sub(r"\s+", " ", text.strip().lower())


def cmd_check(args):
    cases = read_jsonl(args.data)
    labels = set(args.labels.split(",")) if args.labels else None
    problems = []
    seen_ids, seen_inputs = {}, {}
    for i, c in enumerate(cases, 1):
        for key in ("id", "input", "expected"):
            if not str(c.get(key, "")).strip():
                problems.append(f"line {i}: missing or empty '{key}'")
        if c.get("id") in seen_ids:
            problems.append(f"line {i}: duplicate id {c['id']} (first on line {seen_ids[c['id']]})")
        seen_ids.setdefault(c.get("id"), i)
        n_in = norm(str(c.get("input", "")))
        if n_in in seen_inputs:
            problems.append(f"line {i}: same input as line {seen_inputs[n_in]}")
        seen_inputs.setdefault(n_in, i)
        if labels and c.get("expected") not in labels:
            problems.append(f"line {i}: label {c.get('expected')!r} is not one of {sorted(labels)}")
    print(f"{len(cases)} cases checked")
    for p in problems:
        print("  PROBLEM", p)
    print("OK" if not problems else f"{len(problems)} problem(s)")
    sys.exit(1 if problems else 0)


def cmd_summary(args):
    cases = read_jsonl(args.data)
    print(f"{len(cases)} cases")
    for key in ("expected", "slice", "source"):
        counts = Counter(c.get(key) for c in cases if c.get(key))
        if counts:
            print(f"\nby {key}:")
            for name, n in counts.most_common():
                print(f"  {name:<20}{n:>4}  {n / len(cases):>5.0%}")
    lengths = [len(c["input"]) for c in cases]
    print(f"\ninput length (chars): min {min(lengths)}, max {max(lengths)}")


def cmd_split(args):
    cases = read_jsonl(args.data)
    rng = random.Random(args.seed)
    by_label = {}
    for c in cases:
        by_label.setdefault(c["expected"], []).append(c)
    dev, test = [], []
    for label, group in sorted(by_label.items()):
        rng.shuffle(group)
        k = int(len(group) * args.dev + 0.5)  # round half up
        if len(group) >= 2:
            k = min(max(k, 1), len(group) - 1)  # keep both sides non-empty
        dev += group[:k]
        test += group[k:]
    base = Path(args.data)
    dev_path = base.with_name(base.stem + ".dev.jsonl")
    test_path = base.with_name(base.stem + ".test.jsonl")
    for p in (dev_path, test_path):
        if p.exists() and not args.force:
            raise SystemExit(f"{p} exists; use --force to overwrite")
    write_jsonl(dev_path, sorted(dev, key=lambda c: c["id"]))
    write_jsonl(test_path, sorted(test, key=lambda c: c["id"]))
    print(f"dev  {len(dev):>3} -> {dev_path}")
    print(f"test {len(test):>3} -> {test_path}")
    print("Tune on dev. Look at test rarely. Stratified by 'expected', fixed seed.")


def cmd_leak(args):
    cfg_path = Path(args.config).resolve()
    root = cfg_path.parent.parent
    cfg = yaml.safe_load(cfg_path.read_text())
    cases = read_jsonl(root / cfg["dataset"])
    found = 0
    for variant, rel in cfg["variants"].items():
        prompt = norm((root / rel).read_text())
        for c in cases:
            text = norm(c["input"])
            if text and text in prompt:
                found += 1
                print(f"LEAK: case {c['id']} text appears in prompt {variant} ({rel})")
    print("no leaks found" if not found else f"{found} leak(s): the prompt has seen test cases")
    sys.exit(1 if found else 0)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("check")
    p.add_argument("data")
    p.add_argument("--labels")
    p.set_defaults(fn=cmd_check)
    p = sub.add_parser("summary")
    p.add_argument("data")
    p.set_defaults(fn=cmd_summary)
    p = sub.add_parser("split")
    p.add_argument("data")
    p.add_argument("--dev", type=float, default=0.5)
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--force", action="store_true")
    p.set_defaults(fn=cmd_split)
    p = sub.add_parser("leak")
    p.add_argument("config")
    p.set_defaults(fn=cmd_leak)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
