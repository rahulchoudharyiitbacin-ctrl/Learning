"""Run:  python test_online.py   (plain asserts + small simulations)"""
import math
import random

from online_tools import (assign, chi2_sf, srm_check, two_proportions,
                          users_per_arm)

# ---- assignment: stable, balanced, independent across experiments
assert all(assign("exp1", "user-42") == assign("exp1", "user-42") for _ in range(5))
users = [f"user-{i}" for i in range(100_000)]
arms = [assign("exp1", u) for u in users]
share_b = arms.count("B") / len(arms)
assert abs(share_b - 0.5) < 0.01, share_b
print(f"ok  50/50 split over 100,000 users: B share {share_b:.4f}")

canary = [assign("exp1", u, rollout=0.05) for u in users]
in_test = sum(a is not None for a in canary) / len(canary)
assert abs(in_test - 0.05) < 0.005, in_test
b_in = canary.count("B") / max(1, sum(a is not None for a in canary))
assert abs(b_in - 0.5) < 0.03, b_in
print(f"ok  5% canary: {in_test:.4f} of users in test, B share inside {b_in:.3f}")

# a user in the canary stays in the full test when rollout grows (same hash)
assert all(assign("exp1", u, 1.0) is not None for u in users[:1000])
for u in users[:20000]:
    if assign("exp1", u, 0.05) is not None:
        assert assign("exp1", u, 0.5) == assign("exp1", u, 0.05)  # arm does not change as rollout grows
print("ok  raising the rollout keeps each user's arm")

# different experiments are not correlated (B in exp1 says nothing about B in exp2)
pairs = [(assign("exp1", u), assign("exp2", u)) for u in users[:50000]]
both_b = sum(1 for a, b in pairs if a == "B" and b == "B") / len(pairs)
assert abs(both_b - 0.25) < 0.01, both_b
print(f"ok  two experiments independent: P(B and B) = {both_b:.4f} (expect 0.25)")

# ---- chi-square survival function vs textbook critical values
for x, df, expect in [(3.841, 1, 0.05), (6.635, 1, 0.01), (5.991, 2, 0.05),
                      (7.815, 3, 0.05), (9.488, 4, 0.05), (0.0, 1, 1.0)]:
    got = chi2_sf(x, df)
    assert abs(got - expect) < 5e-4, (x, df, got, expect)
print("ok  chi-square tail probabilities match table values")

# ---- SRM worked example: 5000 vs 5200, planned 50/50 -> chi2 = 3.9216
chi2, p = srm_check([5000, 5200], [0.5, 0.5])
assert abs(chi2 - 2 * 100 ** 2 / 5100) < 1e-12, chi2   # each arm is 100 off the expected 5,100
assert 0.045 < p < 0.05, p
chi2b, pb = srm_check([50000, 52000], [0.5, 0.5])   # same ratio, 10x traffic
assert pb < 1e-4, pb
print(f"ok  SRM: 5,000 vs 5,200 gives p = {p:.4f}; 50,000 vs 52,000 gives p = {pb:.2e}")

# ---- planner: hand-computed value (baseline 10%, +1 point) ~ 14,750 per arm
n = users_per_arm(0.10, 0.01)
assert 14700 <= n <= 14800, n
assert users_per_arm(0.5, 0.05) in range(1560, 1590)   # classic ~1,565 per arm
print(f"ok  planner: 10% baseline, +1 point -> {n:,} users per arm")

# simulation: at that n a real +10 point effect on a 30% baseline is found ~80% of the time
random.seed(7)
n2 = users_per_arm(0.30, 0.10)
wins = 0
reps = 2000
for _ in range(reps):
    a = sum(random.random() < 0.30 for _ in range(n2))
    b = sum(random.random() < 0.40 for _ in range(n2))
    if two_proportions(a, n2, b, n2)["p"] < 0.05:
        wins += 1
power = wins / reps
assert 0.77 < power < 0.83, power
print(f"ok  simulated power at n = {n2} per arm: {power:.3f} (target 0.80)")

# ---- compare: hand-computed 100/1000 vs 130/1000
r = two_proportions(100, 1000, 130, 1000)
se = math.sqrt(0.1 * 0.9 / 1000 + 0.13 * 0.87 / 1000)
assert abs(r["diff"] - 0.03) < 1e-12
assert abs(r["ci"][0] - (0.03 - 1.96 * se)) < 1e-9 and abs(r["ci"][1] - (0.03 + 1.96 * se)) < 1e-9
assert abs(r["p"] - 0.0353) < 0.001, r["p"]
print(f"ok  compare: +3.0 pts, CI [{r['ci'][0]:+.4f}, {r['ci'][1]:+.4f}], p = {r['p']:.4f}")

# no true effect: false-positive rate near 5%
random.seed(11)
fp = sum(two_proportions(sum(random.random() < 0.2 for _ in range(500)), 500,
                         sum(random.random() < 0.2 for _ in range(500)), 500)["p"] < 0.05
         for _ in range(3000)) / 3000
assert 0.035 < fp < 0.065, fp
print(f"ok  no real effect: false-positive rate {fp:.3f} (target 0.05)")

print("\nall online-test checks passed")
