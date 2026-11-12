"""Did B beat A? Paired, case-level statistics for a finished run (Chapter 9).

Usage:
    python compare_runs.py experiments/ticket-triage-v1-vs-v2.yaml          # runs/<name>/records.jsonl
    python compare_runs.py experiments/ticket-triage-v1-vs-v2.yaml --mock   # runs/<name>/records-mock.jsonl
    python compare_runs.py experiments/X.yaml --records some/other.jsonl

Standard library + pyyaml only. No API key needed.

What it does, in order:
  1. Average the repeated runs of each case into ONE score per case and variant.
     The test case is the unit of analysis.
  2. Paired difference per case: d_i = score_B(i) - score_A(i).
  3. Mean of d with a t-interval (the normal approximation with a small-sample
     correction; at 100+ cases the multiplier is about 1.96). This is the
     PRIMARY interval and the one the verdict uses.
  4. A paired bootstrap that resamples CASES (fixed seed), as a cross-check.
  5. For contrast only: an unpaired interval (wastes the pairing, too
     wide) and a naive interval that treats every (case, run) row as
     independent. With several runs per case it is usually too narrow.
  6. McNemar's exact test on per-case MAJORITY outcomes (a case counts as
     passed if more than half of its runs passed; exactly half counts as failed).
     Use --mcnemar first to use only run 0 instead. Only for 0/1 grades.
  7. Verdict: SHIP only if CI lower bound > 0 AND mean gain >= min_gain
     AND no configured guardrail is worse than allowed.

Optional YAML keys (besides min_gain):
    alpha: 0.05                     # two-sided; default 0.05 -> 95% intervals
    guardrail_max_increase:         # relative increase B vs A allowed
      tokens: 0.10                  # mean tokens_in + tokens_out per call
      latency_ms: 0.20              # median latency per call
"""
import argparse
import json
import math
import random
import statistics
from pathlib import Path

NORMAL = statistics.NormalDist()


# ---- t distribution quantile (standard library only) -------
def _betacf(a, b, x):
    """Continued fraction for the incomplete beta (Numerical Recipes 6.4)."""
    tiny = 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > tiny else tiny)
    h = d
    for m in range(1, 300):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-12:
            break
    return h


def _betainc(a, b, x):
    """Regularized incomplete beta I_x(a, b)."""
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    lbt = (math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
           + a * math.log(x) + b * math.log(1 - x))
    if x < (a + 1) / (a + b + 2):
        return math.exp(lbt) * _betacf(a, b, x) / a
    return 1.0 - math.exp(lbt) * _betacf(b, a, 1 - x) / b


def t_cdf(t, df):
    p = 0.5 * _betainc(df / 2, 0.5, df / (df + t * t))
    return 1 - p if t > 0 else p


def t_quantile(q, df):
    """Inverse of t_cdf by bisection. q in (0, 1)."""
    lo, hi = -1e3, 1e3
    for _ in range(200):
        mid = (lo + hi) / 2
        if t_cdf(mid, df) < q:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


# ---- Step 1-2: per-case means and paired differences --------
def read_jsonl(path):
    lines = Path(path).read_text().splitlines()
    return [json.loads(x) for x in lines if x.strip()]


def per_case_scores(records, a, b):
    """Return {case_id: (mean_A, mean_B)} for cases that have both variants,
    plus {(variant, case_id): [grades by run order]}."""
    runs = {}
    for r in records:
        if "error" in r or r.get("grade") is None or r["variant"] not in (a, b):
            continue
        runs.setdefault((r["variant"], r["case_id"]), []).append(
            (r.get("run", 0), float(r["grade"])))
    for k in runs:
        runs[k] = [g for _, g in sorted(runs[k])]
    cases = sorted({c for (_, c) in runs})
    scores = {c: (statistics.mean(runs[(a, c)]), statistics.mean(runs[(b, c)]))
              for c in cases if (a, c) in runs and (b, c) in runs}
    return scores, runs


# ---- Step 3: the primary interval ---------------------------
def paired_ci(diffs, alpha=0.05):
    """Mean paired difference with a t-interval. Returns (mean, se, lo, hi)."""
    n = len(diffs)
    m = statistics.mean(diffs)
    se = statistics.stdev(diffs) / math.sqrt(n)
    mult = t_quantile(1 - alpha / 2, n - 1)
    return m, se, m - mult * se, m + mult * se


# ---- Step 4: paired bootstrap over CASES --------------------
def bootstrap_ci(diffs, alpha=0.05, n_boot=5000, seed=0):
    """Percentile interval. Each resample draws whole cases with replacement,
    so A and B stay paired and a case's runs stay together."""
    rng = random.Random(seed)
    n = len(diffs)
    means = sorted(sum(rng.choices(diffs, k=n)) / n for _ in range(n_boot))
    lo = means[int(math.floor(alpha / 2 * n_boot))]
    hi = means[int(math.ceil((1 - alpha / 2) * n_boot)) - 1]
    return lo, hi


# ---- Step 5: the WRONG interval, for contrast ----------------
def naive_row_ci(runs, cases, a, b, alpha=0.05):
    """Pairs rows by (case, run) and treats all of them as independent.
    Ignores that runs of the same case are correlated -> too narrow."""
    rows = []
    for c in cases:
        ra, rb = runs[(a, c)], runs[(b, c)]
        rows += [y - x for x, y in zip(ra, rb)]
    m = statistics.mean(rows)
    se = statistics.stdev(rows) / math.sqrt(len(rows))
    z = NORMAL.inv_cdf(1 - alpha / 2)
    return m, se, m - z * se, m + z * se, len(rows)


# ---- Step 6: McNemar exact ----------------------------------
def mcnemar_exact(b_only, a_only):
    """Two-sided exact McNemar p-value from the discordant counts only.
    Under 'no difference' each discordant case is a fair coin flip."""
    n = b_only + a_only
    if n == 0:
        return 1.0
    k = min(b_only, a_only)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def binary_outcomes(runs, cases, a, b, mode="majority"):
    out = []
    for c in cases:
        ra, rb = runs[(a, c)], runs[(b, c)]
        if mode == "first":
            out.append((ra[0] >= 0.5, rb[0] >= 0.5))
        else:
            out.append((statistics.mean(ra) > 0.5, statistics.mean(rb) > 0.5))
    b_only = sum(1 for x, y in out if y and not x)
    a_only = sum(1 for x, y in out if x and not y)
    return b_only, a_only


# ---- Step 7: verdict ----------------------------------------
def verdict(lo, hi, mean, min_gain, guard_ok=True):
    if hi < 0:
        return "WORSE: B is reliably worse than A. Keep A."
    if lo > 0 and mean >= min_gain and guard_ok:
        return "SHIP B: gain is above zero, at least min_gain, guardrails ok."
    if lo > 0 and mean < min_gain:
        return ("NOT WORTH IT: B is probably better, but the gain is "
                "below min_gain. Keep A.")
    if lo > 0 and not guard_ok:
        return "DON'T SHIP: B is better but breaks a guardrail."
    return ("NOT PROVEN: the interval includes zero. Keep A, "
            "or test more cases.")


def guardrails(records, a, b, limits):
    """Returns (lines, ok). Limits are relative increases allowed."""
    def stats_for(v):
        rows = [r for r in records if r.get("variant") == v and "error" not in r]
        tok = [r.get("tokens_in", 0) + r.get("tokens_out", 0) for r in rows]
        lat = [r["latency_ms"] for r in rows if "latency_ms" in r]
        return {"tokens": statistics.mean(tok) if tok else None,
                "latency_ms": statistics.median(lat) if lat else None}
    sa, sb = stats_for(a), stats_for(b)
    lines, ok = [], True
    for key, label in (("tokens", "mean tokens/call"), ("latency_ms", "median latency ms")):
        if sa[key] is None or sb[key] is None or sa[key] == 0:
            continue
        change = sb[key] / sa[key] - 1
        lim = (limits or {}).get(key)
        flag = ""
        if lim is not None:
            bad = change > lim
            ok = ok and not bad
            flag = f"  limit +{lim:.0%} -> {'FAIL' if bad else 'ok'}"
        lines.append(f"  {label}: A {sa[key]:.0f}  B {sb[key]:.0f}  ({change:+.0%}){flag}")
    if not limits:
        lines.append("  (no guardrail_max_increase in the YAML: check these by eye)")
    return lines, ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--records", help="path to a records .jsonl (overrides the default)")
    ap.add_argument("--mcnemar", choices=["majority", "first"], default="majority")
    ap.add_argument("--boot", type=int, default=5000)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    import yaml
    cfg_path = Path(args.config).resolve()
    cfg = yaml.safe_load(cfg_path.read_text())
    root = cfg_path.parent.parent
    path = Path(args.records) if args.records else (
        root / "runs" / cfg["name"] / ("records-mock.jsonl" if args.mock else "records.jsonl"))
    records = read_jsonl(path)
    a, b = list(cfg["variants"])[:2]
    alpha = float(cfg.get("alpha", 0.05))
    min_gain = cfg.get("min_gain")
    level = f"{1 - alpha:.0%}"

    scores, runs = per_case_scores(records, a, b)
    cases = sorted(scores)
    n = len(cases)
    if n < 2:
        raise SystemExit(f"Need at least 2 cases with both {a} and {b}; found {n}.")
    k = [len(runs[(a, c)]) for c in cases]
    diffs = [scores[c][1] - scores[c][0] for c in cases]
    errors = sum(1 for r in records if "error" in r)

    print(f"{cfg['name']}  ({path.name})")
    print(f"{n} cases, runs per case {min(k)}-{max(k)}, {errors} error rows skipped")
    print(f"{a}: {statistics.mean(s[0] for s in scores.values()):.3f}   "
          f"{b}: {statistics.mean(s[1] for s in scores.values()):.3f}   (mean of per-case means)")
    print(f"Cases: {b} better {sum(d > 0 for d in diffs)}, "
          f"{a} better {sum(d < 0 for d in diffs)}, tie {sum(d == 0 for d in diffs)}")

    m, se, lo, hi = paired_ci(diffs, alpha)
    blo, bhi = bootstrap_ci(diffs, alpha, args.boot, args.seed)
    print(f"\nMean paired difference {b}-{a}: {m:+.4f}  (SE {se:.4f}, "
          f"SD of per-case differences {statistics.stdev(diffs):.4f})")
    print(f"  {level} CI, paired t (PRIMARY):      [{lo:+.4f}, {hi:+.4f}]")
    print(f"  {level} CI, case bootstrap (seed {args.seed}): [{blo:+.4f}, {bhi:+.4f}]")
    if (lo > 0) != (blo > 0):
        print("  Note: the two intervals disagree about zero. Treat as borderline.")

    sa = [scores[c][0] for c in cases]
    sb = [scores[c][1] for c in cases]
    use = math.sqrt(statistics.variance(sa) / n + statistics.variance(sb) / n)
    z = NORMAL.inv_cdf(1 - alpha / 2)
    print(f"  {level} CI, unpaired (ignores pairing, too wide): "
          f"[{m - z * use:+.4f}, {m + z * use:+.4f}]")
    if max(k) > 1:
        nm, nse, nlo, nhi, nrows = naive_row_ci(runs, cases, a, b, alpha)
        print(f"  {level} CI, naive {nrows} rows as independent (WRONG): "
              f"[{nlo:+.4f}, {nhi:+.4f}]  SE ratio {se / nse:.2f}x")

    grades = {g for v in runs.values() for g in v}
    if grades <= {0.0, 1.0}:
        bo, ao = binary_outcomes(runs, cases, a, b, args.mcnemar)
        p = mcnemar_exact(bo, ao)
        print(f"\nMcNemar exact ({args.mcnemar} outcome per case): "
              f"{b}-only passes {bo}, {a}-only passes {ao}, p = {p:.4f}")
    else:
        print("\nMcNemar skipped: grades are not all 0/1.")

    g_lines, g_ok = guardrails(records, a, b, cfg.get("guardrail_max_increase"))
    print("\nGuardrails:")
    print("\n".join(g_lines))

    if min_gain is None:
        print("\nmin_gain missing from the YAML: using 0. Set it before you run.")
        min_gain = 0.0
    print(f"\nmin_gain {min_gain:+.3f}: gain {m:+.4f} -> "
          f"{'meets it' if m >= min_gain else 'below it'}")
    print(f"VERDICT: {verdict(lo, hi, m, min_gain, g_ok)}")
    if args.mock or "mock" in path.name:
        print("*** MOCK DATA: the code is tested, the numbers mean nothing ***")


if __name__ == "__main__":
    main()
