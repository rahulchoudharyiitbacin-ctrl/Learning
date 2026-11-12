"""Checks for compare_runs.py and sample_size.py (Chapter 9).

    python test_stats.py            # about a minute, no API key, standard library + pyyaml

Part 1: hand-computed examples.  Part 2: simulations that measure how often
each interval captures the true value (coverage) and whether the sample-size
formula delivers the promised power. Measured numbers are printed.
"""
import json
import math
import random
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path

from compare_runs import (binary_outcomes, bootstrap_ci, mcnemar_exact, naive_row_ci, paired_ci,
                          per_case_scores, t_quantile, verdict)
from sample_size import (n_one_accuracy, n_paired_binary, n_paired_means,
                         n_paired_simple, n_unpaired)

HERE = Path(__file__).parent


def close(x, y, tol=1e-3):
    return abs(x - y) <= tol


# ================= Part 1: by hand ==========================
def test_mcnemar_by_hand():
    # 8 cases only B passed, 2 only A passed. n = 10 discordant.
    # P(X <= 2 | n=10, p=1/2) = (1 + 10 + 45) / 1024 = 56/1024; two-sided x2.
    assert close(mcnemar_exact(8, 2), 112 / 1024, 1e-12)
    assert mcnemar_exact(8, 2) == mcnemar_exact(2, 8)       # symmetric
    assert mcnemar_exact(0, 0) == 1.0                        # no discordant pairs
    assert mcnemar_exact(5, 5) == 1.0
    # 6 vs 0: 2 * (1/64) = 0.03125
    assert close(mcnemar_exact(6, 0), 2 / 64, 1e-12)
    # demo.py run 1: 66 vs 60; scipy.stats.binomtest gave 0.6562
    assert close(mcnemar_exact(66, 60), 0.6562, 1e-4)
    print("ok  McNemar exact: 8 vs 2 -> p = 0.1094; 66 vs 60 -> p = 0.6562")


def test_concordant_pairs_do_not_matter():
    # 8 B-only and 2 A-only cases, plus either 5 or 500 cases where A and B agree.
    def table(n_agree):
        t = {f"b{i}": ([0], [1]) for i in range(8)}
        t.update({f"a{i}": ([1], [0]) for i in range(2)})
        t.update({f"s{i}": ([i % 2], [i % 2]) for i in range(n_agree)})
        return t
    ps = []
    for n_agree in (5, 500):
        scores, runs = per_case_scores(records_from(table(n_agree)), "A", "B")
        bo, ao = binary_outcomes(runs, sorted(scores), "A", "B")
        assert (bo, ao) == (8, 2)
        ps.append(mcnemar_exact(bo, ao))
    assert ps[0] == ps[1]
    print("ok  McNemar p is the same with 5 or 500 agreeing cases added")


def test_t_quantile():
    for df, want in ((4, 2.776), (9, 2.262), (19, 2.093), (99, 1.984)):
        assert close(t_quantile(0.975, df), want, 1e-3), (df, t_quantile(0.975, df))
    assert close(t_quantile(0.975, 100000), 1.960, 1e-3)
    print("ok  t quantiles match printed tables (df 4, 9, 19, 99, large)")


def records_from(table):
    """table: {case_id: ([A grades], [B grades])} -> harness-style records."""
    recs = []
    for c, (ga, gb) in table.items():
        recs += [{"case_id": c, "variant": "A", "run": i, "grade": g} for i, g in enumerate(ga)]
        recs += [{"case_id": c, "variant": "B", "run": i, "grade": g} for i, g in enumerate(gb)]
    return recs


def test_tiny_paired_ci_by_hand():
    # 5 cases x 2 runs. Per-case means:
    #   c1 A 0.0 B 0.5 -> d 0.5     c2 A 1.0 B 1.0 -> d 0.0
    #   c3 A 0.0 B 1.0 -> d 1.0     c4 A 0.5 B 1.0 -> d 0.5     c5 A 1 B 1 -> 0
    # mean d = 2.0/5 = 0.4
    # deviations 0.1 -0.4 0.6 0.1 -0.4 ; squares sum 0.70 ; var = 0.70/4 = 0.175
    # sd = 0.41833 ; se = sd/sqrt(5) = 0.18708 ; t(0.975, 4) = 2.7764
    # CI = 0.4 +/- 0.5194 = [-0.1194, 0.9194]
    table = {"c1": ([0, 0], [1, 0]), "c2": ([1, 1], [1, 1]), "c3": ([0, 0], [1, 1]),
             "c4": ([1, 0], [1, 1]), "c5": ([1, 1], [1, 1])}
    scores, runs = per_case_scores(records_from(table), "A", "B")
    diffs = [scores[c][1] - scores[c][0] for c in sorted(scores)]
    assert diffs == [0.5, 0.0, 1.0, 0.5, 0.0]
    m, se, lo, hi = paired_ci(diffs)
    assert close(m, 0.4, 1e-12) and close(se, 0.18708, 1e-5)
    assert close(lo, -0.1194, 1e-3) and close(hi, 0.9194, 1e-3)
    # Naive rows: (c,run) diffs 1,0, 0,0, 1,1, 0,1, 0,0 -> mean 0.4, sd 0.5164, n 10
    nm, nse, nlo, nhi, nrows = naive_row_ci(runs, sorted(scores), "A", "B")
    assert nrows == 10 and close(nm, 0.4, 1e-12) and close(nse, 0.5164 / math.sqrt(10), 1e-4)
    assert nse < se          # the naive SE is smaller: it pretends to have 10 cases
    print(f"ok  tiny paired CI by hand: 0.4 [{lo:+.4f}, {hi:+.4f}]; naive SE {nse:.4f} < {se:.4f}")


def test_bootstrap_basics():
    d = [0.0, 1 / 3, -1 / 3, 1.0, 0.0, 2 / 3, 0.0, -1 / 3]
    assert bootstrap_ci(d, seed=1) == bootstrap_ci(d, seed=1)          # fixed seed
    assert bootstrap_ci([0.25] * 30) == (0.25, 0.25)                  # no spread
    lo, hi = bootstrap_ci(d, seed=1)
    assert lo < statistics.mean(d) < hi
    print("ok  bootstrap: repeatable with a seed, zero width for constant data")


def test_verdicts():
    assert verdict(0.01, 0.06, 0.035, 0.02).startswith("SHIP")
    assert verdict(0.001, 0.02, 0.01, 0.02).startswith("NOT WORTH")
    assert verdict(-0.003, 0.061, 0.03, 0.02).startswith("NOT PROVEN")
    assert verdict(-0.08, -0.01, -0.04, 0.02).startswith("WORSE")
    assert verdict(0.01, 0.06, 0.035, 0.02, guard_ok=False).startswith("DON'T")
    print("ok  verdict rule: ship / not worth it / not proven / worse / guardrail")


def test_cli_end_to_end():
    """Runs compare_runs.py as a learner would, on a fake experiment."""
    rng = random.Random(3)
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "experiments").mkdir()
        (root / "runs" / "t").mkdir(parents=True)
        (root / "experiments" / "t.yaml").write_text(
            "name: t\nvariants:\n  A: a.txt\n  B: b.txt\nmin_gain: 0.02\n"
            "guardrail_max_increase:\n  tokens: 0.10\n")
        recs = []
        for i in range(300):
            pa = rng.choice([0.2, 0.6, 0.95])
            pb = min(1.0, pa + 0.15)
            for v, p, tok in (("A", pa, 100), ("B", pb, 105)):
                for r in range(3):
                    recs.append({"case_id": f"c{i}", "variant": v, "run": r,
                                 "grade": int(rng.random() < p), "tokens_in": tok,
                                 "tokens_out": 3, "latency_ms": 500})
        recs.append({"case_id": "c0", "variant": "A", "run": 9, "error": "Timeout"})
        (root / "runs" / "t" / "records.jsonl").write_text(
            "\n".join(json.dumps(r) for r in recs))
        out = subprocess.run([sys.executable, str(HERE / "compare_runs.py"),
                              str(root / "experiments" / "t.yaml")],
                             capture_output=True, text=True, check=True).stdout
    assert "300 cases" in out and "1 error rows skipped" in out
    assert "VERDICT: SHIP B" in out and "limit +10% -> ok" in out
    print("ok  CLI end to end: 300 cases, error row skipped, verdict SHIP B")


def test_sample_size_formulas():
    # By hand: pd 0.15, delta 0.03, z 1.95996, 0.84162
    # (1.95996*0.38730 + 0.84162*0.38614)^2 / 0.0009 = (0.75908+0.32499)^2/0.0009 = 1305.8
    assert n_paired_binary(0.15, 0.03) == 1306
    assert n_paired_simple(0.15, 0.03) == 1301
    # Chapter 6 table: 80% accuracy, +/-5 points -> 246; 50% -> 385
    assert n_one_accuracy(0.80, 0.05) == 246 and n_one_accuracy(0.50, 0.05) == 385
    # demo.py: sd of per-case differences 0.3273 -> 2103 cases for +2 points
    assert n_paired_means(0.3273, 0.02) == 2103
    # Same accuracy gap, different discordance -> very different n
    assert n_paired_binary(0.05, 0.03) < n_paired_binary(0.30, 0.03) / 5
    assert n_unpaired(0.70, 0.73) > 2 * n_paired_binary(0.15, 0.03)
    print("ok  sample-size formulas match hand values (1306, 246, 385, 2103)")


# ================= Part 2: simulations =======================
def simulate_cases(types, n, k, rng):
    """types: list of (weight, pA, pB). Returns runs dict and case ids."""
    weights = [t[0] for t in types]
    runs, cases = {}, []
    for i in range(n):
        _, pa, pb = rng.choices(types, weights)[0]
        c = f"c{i}"
        cases.append(c)
        runs[("A", c)] = [float(rng.random() < pa) for _ in range(k)]
        runs[("B", c)] = [float(rng.random() < pb) for _ in range(k)]
    return runs, cases


def coverage(types, n=100, k=3, sims=1000, n_boot=1000, seed=11):
    truth = sum(w * (pb - pa) for w, pa, pb in types) / sum(w for w, _, _ in types)
    rng = random.Random(seed)
    hit = {"t": 0, "boot": 0, "naive": 0}
    for s in range(sims):
        runs, cases = simulate_cases(types, n, k, rng)
        d = [statistics.mean(runs[("B", c)]) - statistics.mean(runs[("A", c)]) for c in cases]
        _, _, lo, hi = paired_ci(d)
        hit["t"] += lo <= truth <= hi
        lo, hi = bootstrap_ci(d, n_boot=n_boot, seed=s)
        hit["boot"] += lo <= truth <= hi
        _, _, lo, hi, _ = naive_row_ci(runs, cases, "A", "B")
        hit["naive"] += lo <= truth <= hi
    return {k_: v / sims for k_, v in hit.items()}


# Scenario H (heterogeneous): B reliably fixes some cases and breaks others.
HETERO = [(0.3, 0.05, 0.95), (0.1, 0.95, 0.05), (0.3, 0.90, 0.90), (0.3, 0.10, 0.10)]
# Scenario M (mild): B helps a little everywhere, cases differ in difficulty.
MILD = [(0.25, 0.30, 0.36), (0.25, 0.60, 0.66), (0.25, 0.80, 0.84), (0.25, 0.95, 0.97)]


def test_coverage_simulation():
    sims = 1000
    mc_se = math.sqrt(0.95 * 0.05 / sims)
    for name, types in (("heterogeneous", HETERO), ("mild", MILD)):
        cov = coverage(types, sims=sims)
        print(f"    {name:13s} 100 cases x 3 runs, {sims} sims: "
              f"t {cov['t']:.3f}  case-bootstrap {cov['boot']:.3f}  "
              f"naive rows {cov['naive']:.3f}   (MC s.e. ~{mc_se:.3f})")
        assert abs(cov["boot"] - 0.95) <= 0.025, cov
        assert abs(cov["t"] - 0.95) <= 0.025, cov
        if name == "heterogeneous":
            assert cov["naive"] < 0.88, cov
        else:
            assert cov["naive"] > 0.90, cov
    print("ok  case-level intervals near 95%; naive rows undercover when case effects differ")


def power_sim(p01, p10, n, sims, rng):
    exact = z = 0
    zc = 1.959964
    for _ in range(sims):
        b = c = 0
        for _ in range(n):
            u = rng.random()
            if u < p01:
                b += 1
            elif u < p01 + p10:
                c += 1
        exact += mcnemar_exact(b, c) < 0.05
        z += (b + c) > 0 and abs(b - c) / math.sqrt(b + c) > zc
    return exact / sims, z / sims


def test_power_simulation():
    rng = random.Random(5)
    sims = 2000
    for pd, delta in ((0.15, 0.05), (0.30, 0.10), (0.10, 0.03)):
        n = n_paired_binary(pd, delta)
        p01, p10 = (pd + delta) / 2, (pd - delta) / 2
        ex, z = power_sim(p01, p10, n, sims, rng)
        print(f"    disc {pd:.0%}, effect {delta:+.0%}: n = {n}; simulated power "
              f"z-test {z:.3f}, exact McNemar {ex:.3f}  (target 0.80)")
        assert abs(z - 0.80) <= 0.03, z
        assert 0.74 <= ex <= 0.83, ex     # exact test is a little conservative
    n = n_paired_binary(0.15, 0.05)
    ex, z = power_sim(0.075, 0.075, n, sims, rng)
    print(f"    no real effect, n = {n}: false-positive rate z {z:.3f}, exact {ex:.3f}  (target <= 0.05)")
    assert ex <= 0.05 + 0.012 and z <= 0.05 + 0.015
    print("ok  sample-size formula gives about 80% power in simulation")


def test_peeking_simulation():
    """No real difference, discordance 30%. Look after every 50 cases up to 400
    and stop at the first p < 0.05, versus one look at the end."""
    rng = random.Random(1)
    sims, peek, once = 4000, 0, 0
    for _ in range(sims):
        b = c = 0
        hit = False
        for i in range(1, 401):
            u = rng.random()
            if u < 0.15:
                b += 1
            elif u < 0.30:
                c += 1
            if i % 50 == 0 and mcnemar_exact(b, c) < 0.05:
                hit = True
        peek += hit
        once += mcnemar_exact(b, c) < 0.05
    print(f"    false wins with no real effect: one look {once / sims:.3f}, "
          f"8 looks {peek / sims:.3f}")
    assert once / sims <= 0.06 and peek / sims > 2 * once / sims
    print("ok  peeking at 8 points inflates false wins")


if __name__ == "__main__":
    test_mcnemar_by_hand()
    test_concordant_pairs_do_not_matter()
    test_t_quantile()
    test_tiny_paired_ci_by_hand()
    test_bootstrap_basics()
    test_verdicts()
    test_cli_end_to_end()
    test_sample_size_formulas()
    print("simulations (takes a minute):")
    test_coverage_simulation()
    test_power_simulation()
    test_peeking_simulation()
    print("\nall checks passed")
