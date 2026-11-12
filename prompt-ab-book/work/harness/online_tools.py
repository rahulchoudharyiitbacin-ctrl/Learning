"""Small tools for an ONLINE A/B test (standard library only).

    python online_tools.py assign  --experiment support-v2 --rollout 0.05 u1 u2 u3
    python online_tools.py srm     --counts A=5000,B=5200 [--expected 0.5,0.5]
    python online_tools.py plan    --baseline 0.10 --mde 0.01 --daily-users 4000
    python online_tools.py compare  --a 1000/10000 --b 1100/10000

Online tests are randomised between USERS (unlike offline evals, which are paired by case).
"""
import argparse
import hashlib
import math
from statistics import NormalDist

N = NormalDist()


# ---- assignment: stable, stateless, per experiment ---------
def _unit(experiment, user_id, salt):
    """Map (experiment, user) to a number in [0, 1), deterministically."""
    digest = hashlib.sha256(f"{experiment}:{salt}:{user_id}".encode()).digest()
    return int.from_bytes(digest[:8], "big") / 2**64


def assign(experiment, user_id, rollout=1.0, split=0.5):
    """Return 'A', 'B', or None (user not in the experiment).

    rollout: share of users who take part at all (a canary uses a small value).
    split:   share of participating users who get B.
    """
    if _unit(experiment, user_id, "in") >= rollout:
        return None
    return "B" if _unit(experiment, user_id, "arm") < split else "A"


# ---- sample ratio mismatch (SRM) ---------------------------
def _gammainc_upper(a, x):
    """Regularised upper incomplete gamma Q(a, x)."""
    if x <= 0:
        return 1.0
    gln = math.lgamma(a)
    if x < a + 1:  # series for P, then 1 - P
        term = total = 1.0 / a
        ap = a
        for _ in range(1000):
            ap += 1
            term *= x / ap
            total += term
            if abs(term) < abs(total) * 1e-14:
                break
        return 1.0 - total * math.exp(-x + a * math.log(x) - gln)
    b = x + 1.0 - a  # continued fraction for Q
    c = 1.0 / 1e-300
    d = 1.0 / b
    h = d
    for i in range(1, 1000):
        an = -i * (i - a)
        b += 2.0
        d = an * d + b
        d = 1e-300 if abs(d) < 1e-300 else d
        c = b + an / c
        c = 1e-300 if abs(c) < 1e-300 else c
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-14:
            break
    return math.exp(-x + a * math.log(x) - gln) * h


def chi2_sf(x, df):
    """P(chi-square with df degrees of freedom >= x)."""
    return _gammainc_upper(df / 2.0, x / 2.0)


def srm_check(counts, expected_shares):
    """Chi-square goodness of fit of observed arm sizes vs the planned split."""
    total = sum(counts)
    chi2 = sum((o - total * s) ** 2 / (total * s) for o, s in zip(counts, expected_shares))
    return chi2, chi2_sf(chi2, len(counts) - 1)


# ---- planning: users per arm for a conversion metric -------
def users_per_arm(baseline, mde, alpha=0.05, power=0.8):
    """Two-proportion test, equal arms. mde is an ABSOLUTE difference."""
    p1, p2 = baseline, baseline + mde
    pbar = (p1 + p2) / 2
    za, zb = N.inv_cdf(1 - alpha / 2), N.inv_cdf(power)
    num = za * math.sqrt(2 * pbar * (1 - pbar)) + zb * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))
    return math.ceil(num**2 / mde**2)


# ---- analysis: two proportions -----------------------------
def two_proportions(a_succ, a_n, b_succ, b_n):
    pa, pb = a_succ / a_n, b_succ / b_n
    diff = pb - pa
    pooled = (a_succ + b_succ) / (a_n + b_n)
    se0 = math.sqrt(pooled * (1 - pooled) * (1 / a_n + 1 / b_n))
    z = diff / se0
    p = 2 * (1 - N.cdf(abs(z)))
    se = math.sqrt(pa * (1 - pa) / a_n + pb * (1 - pb) / b_n)
    return {"pa": pa, "pb": pb, "diff": diff, "z": z, "p": p,
            "ci": (diff - 1.96 * se, diff + 1.96 * se)}


def _frac(text):
    s, n = text.split("/")
    return int(s), int(n)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("assign")
    p.add_argument("--experiment", required=True)
    p.add_argument("--rollout", type=float, default=1.0)
    p.add_argument("--split", type=float, default=0.5)
    p.add_argument("users", nargs="+")
    p = sub.add_parser("srm")
    p.add_argument("--counts", required=True, help="A=5000,B=5200")
    p.add_argument("--expected", help="0.5,0.5 (default: equal)")
    p = sub.add_parser("plan")
    p.add_argument("--baseline", type=float, required=True)
    p.add_argument("--mde", type=float, required=True, help="absolute, e.g. 0.01 = 1 point")
    p.add_argument("--daily-users", type=float, required=True, help="eligible users per day, all arms")
    p.add_argument("--alpha", type=float, default=0.05)
    p.add_argument("--power", type=float, default=0.8)
    p = sub.add_parser("compare")
    p.add_argument("--a", required=True, help="successes/users, e.g. 1000/10000")
    p.add_argument("--b", required=True)
    args = ap.parse_args()

    if args.cmd == "assign":
        for u in args.users:
            print(u, assign(args.experiment, u, args.rollout, args.split) or "not in experiment")
    elif args.cmd == "srm":
        pairs = [kv.split("=") for kv in args.counts.split(",")]
        counts = [int(v) for _, v in pairs]
        shares = [float(x) for x in args.expected.split(",")] if args.expected else [1 / len(counts)] * len(counts)
        chi2, p = srm_check(counts, shares)
        print(f"counts {dict(zip([k for k, _ in pairs], counts))}  chi-square {chi2:.3f}  p = {p:.4f}")
        print("SRM ALERT: the split is off. Do not trust the results until you find out why." if p < 0.001
              else "No sample ratio alarm at the strict threshold used here (p < 0.001, chosen because this check runs often).")
    elif args.cmd == "plan":
        n = users_per_arm(args.baseline, args.mde, args.alpha, args.power)
        days = math.ceil(2 * n / args.daily_users)
        weeks = max(2, math.ceil(days / 7))
        print(f"users per arm: {n:,}  (total {2 * n:,})")
        print(f"days of traffic needed: {days}; plan for {weeks} whole weeks (never less than 2)")
        print(f"conversions per arm at baseline: about {round(n * args.baseline):,}")
    elif args.cmd == "compare":
        r = two_proportions(*_frac(args.a), *_frac(args.b))
        print(f"A {r['pa']:.4f}   B {r['pb']:.4f}   B - A {r['diff']:+.4f}")
        print(f"95% CI [{r['ci'][0]:+.4f}, {r['ci'][1]:+.4f}]   z {r['z']:.2f}   p {r['p']:.4f}")


if __name__ == "__main__":
    main()
