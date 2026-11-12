"""How many test cases do I need? Paired sample size (Chapter 9).

Usage:
    python sample_size.py --disc 0.15 --effect 0.03        # binary, paired
    python sample_size.py --sd 0.33 --effect 0.03          # per-case means, paired
    python sample_size.py --accuracy 0.70 --effect 0.03    # contrasts only
    python sample_size.py --table                          # a small lookup table

Standard library only.

---------------------------------------------------------------------
Derivation (binary pass/fail, one outcome per case per prompt)
---------------------------------------------------------------------
Each case lands in one of four cells:
    both pass, both fail          (concordant: d = 0)
    only B passes  (prob p01)     (d = +1)
    only A passes  (prob p10)     (d = -1)
where d = B - A for that case.

    effect      delta = p01 - p10           (B's accuracy minus A's)
    discordance pd    = p01 + p10           (share of cases where they disagree)
    E[d] = delta,     Var(d) = pd - delta^2

Test "no difference" (p01 = p10) at two-sided level alpha. With n cases the
mean of d is roughly Normal. Under the null its variance is pd/n; under the
alternative it is (pd - delta^2)/n. Requiring power 1 - beta gives

    delta = z_{1-alpha/2} * sqrt(pd/n) + z_{1-beta} * sqrt((pd - delta^2)/n)

    n = ( z_{1-alpha/2} * sqrt(pd) + z_{1-beta} * sqrt(pd - delta^2) )^2 / delta^2

(This is the usual normal-approximation formula for McNemar's test; the
simpler form n = (z_a + z_b)^2 (pd - delta^2) / delta^2 gives almost the
same answer.) Accuracy itself does not appear: only pd and delta do.
test_stats.py checks the formula by simulation.

Per-case MEANS (several runs per case): n = (z_a + z_b)^2 * sd_d^2 / delta^2,
with sd_d the standard deviation of the per-case differences from a pilot
run (compare_runs.py prints it).

Contrasts:
    Chapter 6, measuring ONE accuracy to +/- E:  n = z^2 p (1 - p) / E^2
    Two INDEPENDENT groups (not paired), per group:
        n = (z_a + z_b)^2 [pA(1 - pA) + pB(1 - pB)] / delta^2
"""
import argparse
import math
from statistics import NormalDist

Z = NormalDist().inv_cdf


def n_paired_binary(disc, effect, alpha=0.05, power=0.80):
    if not 0 < abs(effect) <= disc <= 1:
        raise ValueError("need 0 < |effect| <= discordance <= 1")
    za, zb = Z(1 - alpha / 2), Z(power)
    return math.ceil((za * math.sqrt(disc) + zb * math.sqrt(disc - effect ** 2)) ** 2
                     / effect ** 2)


def n_paired_simple(disc, effect, alpha=0.05, power=0.80):
    za, zb = Z(1 - alpha / 2), Z(power)
    return math.ceil((za + zb) ** 2 * (disc - effect ** 2) / effect ** 2)


def n_paired_means(sd_d, effect, alpha=0.05, power=0.80):
    za, zb = Z(1 - alpha / 2), Z(power)
    return math.ceil((za + zb) ** 2 * sd_d ** 2 / effect ** 2)


def n_one_accuracy(p, margin, alpha=0.05):
    """Chapter 6: cases to measure ONE prompt's accuracy to +/- margin."""
    return math.ceil(Z(1 - alpha / 2) ** 2 * p * (1 - p) / margin ** 2)


def n_unpaired(pa, pb, alpha=0.05, power=0.80):
    """Per group, if A and B were run on DIFFERENT random cases."""
    za, zb = Z(1 - alpha / 2), Z(power)
    return math.ceil((za + zb) ** 2 * (pa * (1 - pa) + pb * (1 - pb)) / (pb - pa) ** 2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--disc", type=float, help="discordance rate, e.g. 0.15")
    ap.add_argument("--sd", type=float, help="SD of per-case differences (pilot)")
    ap.add_argument("--effect", type=float, help="smallest gain worth detecting")
    ap.add_argument("--accuracy", type=float, help="baseline accuracy, for contrasts")
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--power", type=float, default=0.80)
    ap.add_argument("--table", action="store_true")
    a = ap.parse_args()
    print(f"alpha {a.alpha} (two-sided), power {a.power}")
    if a.disc and a.effect:
        print(f"Paired, binary: discordance {a.disc:.0%}, effect {a.effect:+.1%}: "
              f"{n_paired_binary(a.disc, a.effect, a.alpha, a.power)} cases "
              f"(simple form {n_paired_simple(a.disc, a.effect, a.alpha, a.power)})")
    if a.sd and a.effect:
        print(f"Paired, per-case means: sd_d {a.sd:.3f}, effect {a.effect:+.1%}: "
              f"{n_paired_means(a.sd, a.effect, a.alpha, a.power)} cases")
    if a.accuracy and a.effect:
        p = a.accuracy
        print(f"Contrast, unpaired groups {p:.0%} vs {p + a.effect:.0%}: "
              f"{n_unpaired(p, p + a.effect, a.alpha, a.power)} cases PER GROUP")
        print(f"Contrast, Chapter 6 (one accuracy {p:.0%} to +/-{a.effect:.1%}): "
              f"{n_one_accuracy(p, a.effect, a.alpha)} cases")
    if a.table:
        effects = (0.02, 0.03, 0.05, 0.10)
        print("discordance | " + " | ".join(f"{e:+.0%}" for e in effects))
        for d in (0.05, 0.10, 0.15, 0.20, 0.30):
            cells = [str(n_paired_binary(d, e, a.alpha, a.power)) if e <= d else "-"
                     for e in effects]
            print(f"{d:>11.0%} | " + " | ".join(cells))


if __name__ == "__main__":
    main()
