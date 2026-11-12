"""Precision, recall, F1 and a confusion matrix from saved records.

    python classification_report.py experiments/ticket-triage-v1-vs-v2.yaml [--mock]

Every saved run counts as one prediction. Outputs are cleaned (case, spaces,
end punctuation) before comparing, so 'Refund.' counts as 'refund'.
"""
import argparse
import json
import re
from collections import Counter
from pathlib import Path

import yaml


def clean(text):
    text = text.strip().strip("\"'`*").strip()
    return re.sub(r"[.!?,;:]+$", "", text).lower()


def report(pairs):
    """pairs: list of (expected, predicted). Returns dict of stats."""
    labels = sorted({e for e, _ in pairs})
    stats = {}
    for lab in labels:
        tp = sum(1 for e, p in pairs if e == lab and p == lab)
        fp = sum(1 for e, p in pairs if e != lab and p == lab)
        fn = sum(1 for e, p in pairs if e == lab and p != lab)
        prec = tp / (tp + fp) if tp + fp else 0.0
        rec = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
        stats[lab] = {"precision": prec, "recall": rec, "f1": f1, "support": tp + fn}
    accuracy = sum(1 for e, p in pairs if e == p) / len(pairs)
    return {"labels": labels, "stats": stats, "accuracy": accuracy}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("--mock", action="store_true")
    args = ap.parse_args()
    cfg_path = Path(args.config).resolve()
    root = cfg_path.parent.parent
    cfg = yaml.safe_load(cfg_path.read_text())
    cases = {}
    for line in (root / cfg["dataset"]).read_text().splitlines():
        if line.strip():
            c = json.loads(line)
            cases[c["id"]] = c["expected"].lower()
    name = "records-mock.jsonl" if args.mock else "records.jsonl"
    rows = [json.loads(x) for x in (root / "runs" / cfg["name"] / name).read_text().splitlines() if x.strip()]
    for variant in cfg["variants"]:
        pairs = [(cases[r["case_id"]], clean(r["output"]))
                 for r in rows if r["variant"] == variant and "error" not in r]
        if not pairs:
            continue
        rep = report(pairs)
        print(f"\n=== Prompt {variant}: accuracy {rep['accuracy']:.3f} over {len(pairs)} predictions")
        print(f"{'label':<12}{'precision':>10}{'recall':>8}{'f1':>6}{'support':>9}")
        for lab in rep["labels"]:
            s = rep["stats"][lab]
            print(f"{lab:<12}{s['precision']:>10.2f}{s['recall']:>8.2f}{s['f1']:>6.2f}{s['support']:>9}")
        confusion = Counter(pairs)
        cols = sorted({p for _, p in pairs} | set(rep["labels"]))
        print("\nrows = expected, columns = predicted")
        print(f"{'':<12}" + "".join(f"{c[:9]:>10}" for c in cols))
        for lab in rep["labels"]:
            print(f"{lab:<12}" + "".join(f"{confusion.get((lab, c), 0):>10}" for c in cols))


if __name__ == "__main__":
    main()
