"""Tests for Drill 2. Plain asserts, standard library only.

    python test_drill2.py               # tests solution.py
    python test_drill2.py my_drill2.py  # tests your file
    DRILL_FILE=my_drill2.py python test_drill2.py
"""
import importlib.util
import math
import os
import random
import statistics
import sys
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
    spec = importlib.util.spec_from_file_location("drill2_under_test",
                                                  path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    print(f"Testing {path}")
    return mod


M = None


def recs(case_id, variant, grades):
    return [{"case_id": case_id, "variant": variant, "run": i, "grade": g}
            for i, g in enumerate(grades)]


def from_diffs(ds):
    """Records whose per-case difference B - A equals each value in
    ds (values in [-1, 1], one run each)."""
    out = []
    for i, d in enumerate(ds):
        a = 0.0 if d >= 0 else -d
        out += recs(f"k{i:03d}", "A", [a]) + recs(f"k{i:03d}", "B", [a + d])
    return out


# Hand example: unequal runs per case.
#   c1: A 1 0 1 (0.667)  B 1 1 1 (1.0)       d = +1/3
#   c2: A 0     (0.0)    B 1 0   (0.5)       d = +1/2
#   c3: A 1 1   (1.0)    B 0 1 1 1 (0.75)    d = -1/4
# Case-level mean = (1/3 + 1/2 - 1/4) / 3 = 0.19444...
# Pooling rows instead gives 7/9 - 4/6 = 0.1111 (wrong).
HAND = (recs("c1", "A", [1, 0, 1]) + recs("c1", "B", [1, 1, 1])
        + recs("c2", "A", [0]) + recs("c2", "B", [1, 0])
        + recs("c3", "A", [1, 1]) + recs("c3", "B", [0, 1, 1, 1]))


def test_case_diffs_hand_computed():
    d, dropped = M.case_diffs(HAND, "A", "B")
    assert set(d) == {"c1", "c2", "c3"}, d
    assert abs(d["c1"] - 1 / 3) < 1e-12, d
    assert abs(d["c2"] - 0.5) < 1e-12, d
    assert abs(d["c3"] + 0.25) < 1e-12, d
    assert dropped == []


def test_mean_is_case_level_not_row_level():
    res = M.paired_bootstrap(HAND, "A", "B", n_boot=200, seed=0)
    want = (1 / 3 + 1 / 2 - 1 / 4) / 3
    assert abs(res["mean_diff"] - want) < 1e-12, \
        f"got {res['mean_diff']:.4f}, want {want:.4f} (0.1111 = pooled rows)"
    assert res["n_cases"] == 3


def test_drops_cases_missing_a_variant_or_all_errors():
    data = HAND + recs("c4", "A", [1, 1]) \
        + recs("c5", "A", [1]) + recs("c5", "B", [None, None]) \
        + recs("c6", "A", [None, 1]) + recs("c6", "B", [1])
    d, dropped = M.case_diffs(data, "A", "B")
    assert sorted(dropped) == ["c4", "c5"], dropped
    assert abs(d["c6"] - 0.0) < 1e-12, "a None grade is skipped, not 0"
    res = M.paired_bootstrap(data, "A", "B", n_boot=200)
    assert res["n_cases"] == 4
    assert sorted(res["dropped_cases"]) == ["c4", "c5"]


def test_ignores_other_variants():
    data = HAND + recs("c1", "C", [0, 0, 0])
    d, _ = M.case_diffs(data, "A", "B")
    assert abs(d["c1"] - 1 / 3) < 1e-12


def test_bootstrap_exact_small_case_two_values():
    # d = [0, 1]: resampled means are 0, 0.5, 1 with prob 1/4, 1/2, 1/4.
    res = M.paired_bootstrap(from_diffs([0, 1]), n_boot=5000, seed=1)
    assert (res["ci_low"], res["ci_high"]) == (0.0, 1.0), res


def test_bootstrap_exact_small_case_four_values():
    # d = [0, 0, 0, 1]. Number of 1s in 4 draws ~ Binomial(4, 1/4).
    # P(mean = 1)    = 0.0039  (< 2.5%)
    # P(mean >= .75) = 0.0508  (> 2.5%)  -> 97.5th percentile = 0.75
    # P(mean = 0)    = 0.316   (> 2.5%)  ->  2.5th percentile = 0.0
    res = M.paired_bootstrap(from_diffs([0, 0, 0, 1]), n_boot=5000, seed=3)
    assert res["ci_low"] == 0.0, res
    assert abs(res["ci_high"] - 0.75) < 1e-12, res
    assert abs(res["mean_diff"] - 0.25) < 1e-12


def test_runs_are_clustered_not_resampled():
    # 60 cases x 5 runs, runs identical within a case (fully
    # correlated). Case-level width ~ 2 * 1.96 * sd(d) / sqrt(60).
    # Resampling rows gives about 1/sqrt(5) of that.
    rng = random.Random(11)
    data, ds = [], []
    for i in range(60):
        ga, gb = int(rng.random() < 0.5), int(rng.random() < 0.6)
        ds.append(gb - ga)
        data += recs(f"x{i}", "A", [ga] * 5) + recs(f"x{i}", "B", [gb] * 5)
    want = 2 * 1.96 * statistics.stdev(ds) / math.sqrt(60)
    res = M.paired_bootstrap(data, n_boot=4000, seed=0)
    width = res["ci_high"] - res["ci_low"]
    assert 0.8 * want < width < 1.25 * want, \
        f"width {width:.3f}, expected about {want:.3f}"
    assert res["ci_low"] <= res["mean_diff"] <= res["ci_high"]


def test_same_seed_same_answer_any_record_order():
    rng = random.Random(5)
    data = from_diffs([rng.choice([-1, 0, 0, 1]) for _ in range(50)])
    r1 = M.paired_bootstrap(data, n_boot=2000, seed=42)
    shuffled = data[:]
    rng.shuffle(shuffled)
    r2 = M.paired_bootstrap(shuffled, n_boot=2000, seed=42)
    assert r1 == r2, "sort cases before resampling so order can't matter"
    r3 = M.paired_bootstrap(data, n_boot=2000, seed=43)
    assert abs(r3["ci_low"] - r1["ci_low"]) < 0.06
    assert abs(r3["ci_high"] - r1["ci_high"]) < 0.06


def test_no_difference_gives_zero_interval():
    res = M.paired_bootstrap(from_diffs([0] * 10), n_boot=500)
    assert res["mean_diff"] == 0 and res["ci_low"] == 0 == res["ci_high"]


def test_too_few_cases_raises():
    try:
        M.paired_bootstrap(from_diffs([0.5]), n_boot=100)
    except ValueError:
        return
    raise AssertionError("one case: raise ValueError, don't return a CI")


def test_coverage_simulation():
    # True gain is known. 40 cases x 3 runs, B fixes 30% of cases and
    # breaks 20%. A careful method covers the truth ~95% of the time;
    # treating runs as independent covers ~80%.
    def p_pair(rng):
        pa = rng.uniform(0.2, 0.8)
        u = rng.random()
        pb = min(1, pa + 0.4) if u < 0.3 else \
            max(0, pa - 0.4) if u < 0.5 else pa
        return pa, pb

    big = random.Random(0)
    truth = statistics.fmean(pb - pa for pa, pb in
                             (p_pair(big) for _ in range(200_000)))
    rng = random.Random(1)
    hits, reps = 0, 1000
    for rep in range(reps):
        data = []
        for i in range(40):
            pa, pb = p_pair(rng)
            data += recs(f"s{i}", "A", [int(rng.random() < pa)
                                        for _ in range(3)])
            data += recs(f"s{i}", "B", [int(rng.random() < pb)
                                        for _ in range(3)])
        res = M.paired_bootstrap(data, n_boot=1000, seed=rep)
        hits += res["ci_low"] <= truth <= res["ci_high"]
    cov = hits / reps
    print(f"      coverage {cov:.3f} (truth {truth:+.4f}, {reps} reps)")
    assert 0.92 <= cov <= 0.98, f"coverage {cov:.3f}, want about 0.95"


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
