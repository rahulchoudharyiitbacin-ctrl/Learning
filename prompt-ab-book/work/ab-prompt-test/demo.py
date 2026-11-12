"""
A/B prompt test, offline stage, on SIMULATED data (no API key needed).

Story: a support-ticket classifier. Prompt A = current production prompt.
Prompt B = new prompt with few-shot examples. Both run on the SAME 400-case
golden set, 3 samples each (LLMs are non-deterministic). A grader marks each
output correct/incorrect.

Swap `simulate()` for real model calls + a real grader and the stats are unchanged.
"""
import numpy as np
from scipy.stats import binomtest, norm

rng = np.random.default_rng(7)
N, K = 400, 3                       # test cases, samples per case

def simulate(true_gain=0.04):
    # Each case has its own difficulty -> A and B succeed/fail on the SAME cases.
    difficulty = rng.normal(0, 1.5, N)
    pA = 1 / (1 + np.exp(-(1.0 - difficulty)))            # ~70% baseline
    pB = 1 / (1 + np.exp(-(1.0 + true_gain * 6 - difficulty)))
    A = rng.random((N, K)) < pA[:, None]
    B = rng.random((N, K)) < pB[:, None]
    return A, B

A, B = simulate()
a, b = A.mean(1), B.mean(1)                # per-case score averaged over K runs
print(f"Accuracy  A={a.mean():.3f}  B={b.mean():.3f}  diff={b.mean()-a.mean():+.3f}\n")

# 1) Naive UNPAIRED standard error (treats A and B as different samples) -- wrong here
se_unpaired = np.sqrt(a.var(ddof=1)/N + b.var(ddof=1)/N)
# 2) PAIRED standard error (same cases) -- correct, and much tighter
d = b - a
se_paired = d.std(ddof=1) / np.sqrt(N)
z = norm.ppf(0.975)
print(f"Unpaired 95% CI: {d.mean():+.3f} ± {z*se_unpaired:.3f}")
print(f"Paired   95% CI: {d.mean():+.3f} ± {z*se_paired:.3f}   (corr(A,B) per case = {np.corrcoef(a,b)[0,1]:.2f})")

# 3) Paired bootstrap: resample CASES, keep A/B pairing
boots = np.array([d[rng.integers(0, N, N)].mean() for _ in range(10_000)])
lo, hi = np.percentile(boots, [2.5, 97.5])
print(f"Paired bootstrap 95% CI: [{lo:+.3f}, {hi:+.3f}]")

# 4) McNemar exact test on first sample: only DISAGREEING cases carry signal
a1, b1 = A[:, 0], B[:, 0]
b_only, a_only = int((b1 & ~a1).sum()), int((a1 & ~b1).sum())
p = binomtest(b_only, b_only + a_only, 0.5).pvalue
print(f"McNemar (run 1): B-only wins={b_only}, A-only wins={a_only}, p={p:.4f}")

# 5) Run-to-run noise: same prompt, different samples
print(f"Prompt A accuracy per run: {[round(float(x),3) for x in A.mean(0)]}  <- noise you must beat")

# 6) How many cases do I need? (paired, alpha=0.05, power=0.8)
def n_needed(effect, sd_diff):
    return int(np.ceil(((norm.ppf(0.975) + norm.ppf(0.8)) * sd_diff / effect) ** 2))
sd = d.std(ddof=1)
for eff in (0.02, 0.04, 0.08):
    print(f"Cases needed to detect a {eff:.0%} gain: ~{n_needed(eff, sd)}")
