"""Tests for Drill 3. Plain asserts, standard library only.

    python test_drill3.py               # tests solution.py
    python test_drill3.py my_drill3.py  # tests your file
    DRILL_FILE=my_drill3.py python test_drill3.py
"""
import importlib.util
import math
import os
import sys
import tempfile
import time
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load_module():
    arg = (sys.argv[1] if len(sys.argv) > 1
           else os.environ.get("DRILL_FILE", "solution.py"))
    path = Path(arg)
    if not path.exists():
        path = HERE / arg
    sys.path.insert(0, str(path.resolve().parent))
    spec = importlib.util.spec_from_file_location("drill3_under_test",
                                                  path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    print(f"Testing {path}")
    return mod


M = None


def table(tp, fn, fp, tn, extra=()):
    """Rows for a confusion table, failure = positive."""
    rows = ([("FAIL", "FAIL")] * tp + [("FAIL", "PASS")] * fn
            + [("PASS", "FAIL")] * fp + [("PASS", "PASS")] * tn
            + list(extra))
    return [{"id": str(i), "human": h, "judge": j}
            for i, (h, j) in enumerate(rows)]


def undefined(x):
    return x is None or (isinstance(x, float) and math.isnan(x))


def close(a, b, tol=5e-4):
    return a is not None and abs(a - b) < tol


def close_ci(ci, lo, hi, tol=5e-4):
    return ci is not None and close(ci[0], lo, tol) and close(ci[1], hi, tol)


# ------------------------------------------------------------------
def test_chapter8_table_by_hand():
    # Chapter 8: TP 12, FN 8, FP 6, TN 74.
    # po = 0.86; pe = 0.20*0.18 + 0.80*0.82 = 0.692
    # kappa = 0.168 / 0.308 = 0.54545
    r = M.agreement_report(table(12, 8, 6, 74))
    assert (r["tp"], r["fn"], r["fp"], r["tn"]) == (12, 8, 6, 74), r
    assert close(r["tpr"], 0.6) and close(r["tnr"], 0.925), r
    assert close(r["agreement"], 0.86), r
    assert close(r["kappa"], 0.168 / 0.308, 1e-9), r["kappa"]


def test_wilson_matches_hand_values():
    # Wilson, z = 1.96. 12/20 and 74/80 are Chapter 8's numbers.
    assert close_ci(M.wilson(12, 20), 0.3866, 0.7812)
    assert close_ci(M.wilson(74, 80), 0.8458, 0.9651)
    # k = 0: lower bound exactly 0, upper = z^2/(n + z^2) = 0.2775.
    z2 = 1.96 ** 2
    assert close_ci(M.wilson(0, 10), 0.0, z2 / (10 + z2), 1e-9)
    assert close_ci(M.wilson(10, 10), 1 - z2 / (10 + z2), 1.0, 1e-9)
    lo, hi = M.wilson(1, 1)
    assert 0 <= lo <= hi <= 1


def test_report_includes_wilson_intervals():
    r = M.agreement_report(table(12, 8, 6, 74))
    assert close_ci(r["tpr_ci"], 0.3866, 0.7812), r["tpr_ci"]
    assert close_ci(r["tnr_ci"], 0.8458, 0.9651), r["tnr_ci"]


def test_imbalanced_table_kappa_low_despite_high_agreement():
    # TP 2, FN 8, FP 4, TN 186. Agreement 0.94 but kappa ~0.22.
    # pe = 0.05*0.03 + 0.95*0.97 = 0.923
    r = M.agreement_report(table(2, 8, 4, 186))
    assert close(r["agreement"], 0.94)
    assert close(r["kappa"], (0.94 - 0.923) / (1 - 0.923), 1e-9), r["kappa"]
    assert close(r["tpr"], 0.2)


def test_always_pass_judge():
    # Catches nothing: agreement 95%, TPR 0, kappa exactly 0.
    r = M.agreement_report(table(0, 10, 0, 190))
    assert close(r["agreement"], 0.95)
    assert r["tpr"] == 0 and close(r["kappa"], 0.0, 1e-12), r
    assert close_ci(r["tpr_ci"], 0.0, 1.96 ** 2 / (10 + 1.96 ** 2), 1e-9)


def test_no_positives_is_undefined_not_zero():
    r = M.agreement_report(table(0, 0, 3, 47))
    assert undefined(r["tpr"]), f"no human FAILs: TPR undefined, got {r['tpr']}"
    assert r["tpr_ci"] is None or all(undefined(x) for x in r["tpr_ci"])
    assert close(r["tnr"], 0.94)
    assert close(r["kappa"], 0.0, 1e-12), "pe = 0.94 = po, so kappa = 0"


def test_one_label_everywhere_kappa_undefined():
    r = M.agreement_report(table(0, 0, 0, 50))
    assert undefined(r["kappa"]), f"pe = 1: kappa is 0/0, got {r['kappa']}"
    assert close(r["agreement"], 1.0) and close(r["tnr"], 1.0)


def test_messy_labels_and_skipped_judge_rows():
    rows = [{"id": "1", "human": " fail", "judge": "FAIL "},
            {"id": "2", "human": "Pass", "judge": "pass"},
            {"id": "3", "human": "PASS", "judge": ""},
            {"id": "4", "human": "FAIL", "judge": "ERROR"},
            {"id": "5", "human": "PASS", "judge": None}]
    r = M.agreement_report(rows)
    assert (r["tp"], r["tn"], r["fp"], r["fn"]) == (1, 1, 0, 0), r
    assert r["skipped"] == 3, "unlabelled judge rows: count, don't drop silently"
    assert r["n"] == 2


def test_bad_human_label_raises():
    try:
        M.agreement_report([{"id": "9", "human": "maybe", "judge": "PASS"}])
    except ValueError:
        return
    raise AssertionError("a human label that is not PASS/FAIL is a data error")


def test_positive_class_can_be_switched():
    r = M.agreement_report(table(12, 8, 6, 74), positive="PASS")
    assert close(r["tpr"], 0.925) and close(r["tnr"], 0.6), r
    assert close(r["kappa"], 0.168 / 0.308, 1e-9), "kappa is symmetric"


def test_load_csv_with_bom_and_spaces():
    text = ("﻿id,human_label,judge_label\n"
            "a, FAIL ,fail\n"
            "b,pass,PASS\n"
            "c,PASS,\n")
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "l.csv"
        p.write_text(text, encoding="utf-8")
        rows = M.load_labels(str(p))
    assert len(rows) == 3 and rows[0]["id"] == "a", rows
    r = M.agreement_report(rows)
    assert (r["tp"], r["tn"], r["skipped"]) == (1, 1, 1), r


def test_sample_file():
    r = M.agreement_report(M.load_labels(str(HERE / "labels.csv")))
    assert (r["tp"], r["fn"], r["fp"], r["tn"]) == (12, 8, 6, 74), r
    assert r["skipped"] == 3


# ------------------------------------------------------------------
def main():
    global M
    M = load_module()
    tests = [(n, f) for n, f in globals().items()
             if n.startswith("test_") and callable(f)]
    failed = 0
    t0 = time.monotonic()
    for name, fn in tests:
        try:
            fn()
            print(f"PASS  {name}")
        except Exception as e:
            failed += 1
            msg = str(e) or type(e).__name__
            print(f"FAIL  {name}: {msg}")
            if os.environ.get("VERBOSE"):
                traceback.print_exc()
    print(f"\n{len(tests) - failed}/{len(tests)} passed "
          f"in {time.monotonic() - t0:.1f}s")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
