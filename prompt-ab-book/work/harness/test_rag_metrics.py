"""Run:  python test_rag_metrics.py   (hand-computed examples)"""
import random

from rag_metrics import (mrr, pass_at_k, pass_pow_k, precision_at_k,
                         recall_at_k, reciprocal_rank)

# Query 1: ranked results d1..d5, relevant = {d1, d3, d9}
r1 = ["d1", "d2", "d3", "d4", "d5"]
rel1 = {"d1", "d3", "d9"}
assert abs(recall_at_k(r1, rel1, 5) - 2 / 3) < 1e-12       # found 2 of 3
assert abs(precision_at_k(r1, rel1, 5) - 2 / 5) < 1e-12    # 2 of the 5 retrieved
assert abs(recall_at_k(r1, rel1, 1) - 1 / 3) < 1e-12
assert abs(precision_at_k(r1, rel1, 3) - 2 / 3) < 1e-12
assert reciprocal_rank(r1, rel1) == 1.0                    # first relevant is rank 1

# Query 2: first relevant document is at rank 3
r2 = ["x1", "x2", "x3", "x4"]
rel2 = {"x3"}
assert abs(reciprocal_rank(r2, rel2) - 1 / 3) < 1e-12

# Query 3: nothing relevant retrieved
assert reciprocal_rank(["a", "b"], {"z"}) == 0.0
assert recall_at_k(["a", "b"], {"z"}, 2) == 0.0

# MRR over queries 1 and 2 = (1 + 1/3) / 2
assert abs(mrr([(r1, rel1), (r2, rel2)]) - (1 + 1 / 3) / 2) < 1e-12

# an empty relevant set is an error, not a silent 0
try:
    recall_at_k(["a"], set(), 1)
    raise SystemExit("expected ValueError")
except ValueError:
    pass

# repeated trials: Anthropic's example, 75% per trial and 3 trials -> 0.75**3 = 0.421875
assert abs(pass_pow_k(0.75, 3) - 0.421875) < 1e-12
assert abs(pass_at_k(0.75, 3) - (1 - 0.25 ** 3)) < 1e-12
assert pass_at_k(0.75, 1) == pass_pow_k(0.75, 1) == 0.75    # identical at k = 1
assert pass_at_k(0.75, 10) > 0.999 and pass_pow_k(0.75, 10) < 0.06   # they diverge

# simulation agrees with the formulas
random.seed(5)
trials = 200_000
all3 = sum(all(random.random() < 0.75 for _ in range(3)) for _ in range(trials)) / trials
any3 = sum(any(random.random() < 0.75 for _ in range(3)) for _ in range(trials)) / trials
assert abs(all3 - 0.421875) < 0.005 and abs(any3 - (1 - 0.25 ** 3)) < 0.005
print(f"simulated pass^3 {all3:.4f} (formula 0.4219), pass@3 {any3:.4f} (formula {1 - 0.25 ** 3:.4f})")
print("all rag/trial metric checks passed")
