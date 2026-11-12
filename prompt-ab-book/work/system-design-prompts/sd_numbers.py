"""Numbers used in Chapter 15 (system-design prompts), computed with the book's own helpers."""
import sys
sys.path.insert(0, "/Users/rahulchoudhary/Desktop/Experiment/prompt-ab-book/work/harness")
import online_tools as ot, sample_size as ss

# Check we reproduce Chapter 11's figure
print("ch11 check 10%->11%:", ot.users_per_arm(0.10, 0.01))
# Support bot: resolution baseline 40%, smallest gain worth shipping 2 points
for b, m in [(0.40, 0.02), (0.40, 0.03), (0.60, 0.02)]:
    print(f"users/arm baseline {b} mde {m}:", ot.users_per_arm(b, m))
# Paired offline (Chapter 9 table)
for disc, eff in [(0.10, 0.02), (0.10, 0.03), (0.10, 0.05), (0.20, 0.05)]:
    print(f"paired disc {disc} eff {eff}:", ss.n_paired_binary(disc, eff), ss.n_paired_simple(disc, eff))
# pass^k and pass@k for p=0.75 (Chapter 12), and 0.9
for p in (0.75, 0.9):
    for k in (3,):
        print(f"p={p} k={k} pass^k={p**k:.3f} pass@k={1-(1-p)**k:.3f}")
# Non-inferiority, paired, true diff 0, margin 2 pts, disc 10%: (z.975+z.8)^2*disc/margin^2
from statistics import NormalDist
z = NormalDist().inv_cdf
for disc, margin in [(0.10, 0.02), (0.05, 0.02), (0.10, 0.03)]:
    n = (z(0.975) + z(0.8))**2 * disc / margin**2
    print(f"noninferiority disc {disc} margin {margin}: {n:.0f}")
# Judge: measured gap shrink with TPR/TNR
print("shrink 0.8/0.9:", 0.10*(0.8+0.9-1))
# Smallest no-worse-than margin detectable (80% power, true diff 0) for n cases
for disc in (0.10, 0.20):
    for n in (200, 400):
        print(f"margin for n={n} disc={disc}: {(z(0.975)+z(0.8))*(disc/n)**0.5:.3f}")
print("days for 2*9493 at 2000/day:", 2*9493/2000)
