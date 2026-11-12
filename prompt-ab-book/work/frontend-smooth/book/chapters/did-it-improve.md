# Did it improve? Reading an A/B result honestly

Priya ran her new prompt on 400 test cases, three runs each. Prompt B scored **73.9%**. Prompt A scored **70.9%**. Three points better. She wrote "B wins, shipping Monday" in the team channel.

Her lead asked one question: *"How sure are you?"*

Priya didn't know. Three points sounds like a lot. But Prompt A alone moved by more than five points between three runs of the *same* prompt. Was B better, or was this a lucky afternoon?

This chapter answers her lead's question with four tools: the **paired difference**, the **confidence interval**, the **minimum gain** and the **sample size**. By the end you'll know exactly what to write in that channel. (Spoiler: "not proven yet" was the honest answer.)

Priya is made up. Her numbers come from the simulated demo in `work/ab-prompt-test/`, so you can check every one.

<!-- page -->

## The unit is the test case

Chapter 2 drew the line between two designs. Keep it sharp:

![Diagram: online, users are split at random into group A and group B, so each user sees one prompt. Offline, every test case is run through both A and B, giving one difference d per case.](images/paired-vs-randomised.svg)

Offline, nothing is randomised between A and B. **Every case gets both prompts.** That is a **paired** design. It is fair because both prompts face the same cases under the same conditions.

So the question is not "is group B better than group A?". It is "**on a typical case from the kind of inputs my test set represents, does B score higher than A?**"

That makes the **test case** the unit of analysis. Runs, rows and tokens are not units. Cases are.

<!-- page -->

## Step 1: one score per case, then a difference

Each case ran three times per prompt. First, average the runs into **one score per case and prompt**. Then subtract.

| Case | A runs | B runs | A score | B score | d = B − A |
|---|---|---|---|---|---|
| 1 | 1 0 1 | 1 1 1 | 0.67 | 1.00 | +0.33 |
| 2 | 0 0 0 | 0 0 1 | 0.00 | 0.33 | +0.33 |
| 3 | 1 1 1 | 1 1 1 | 1.00 | 1.00 | 0 |
| 4 | 1 1 0 | 0 1 0 | 0.67 | 0.33 | −0.33 |

(Illustrative cases.) Now you have one number per case, **d**. Everything else in this chapter is about the list of d values: their mean, how much they spread, and how many there are.

> **Teacher's note:** Pairing is a gift. Case 3 is easy for both prompts and case 2 is hard for both. Subtracting removes that difficulty, so only the prompt's effect is left. In the demo, the unpaired interval was **about 37% wider** than the paired one.

<!-- page -->

## Why not use all 2,400 rows?

400 cases x 3 runs x 2 prompts is 2,400 rows. Treating them as independent is tempting, and wrong. Three runs of a case are not three new cases. They share how much B helps *on that case*. Count them separately and you claim three times the evidence.

Miller (Anthropic, 2024) says to cluster standard errors on the unit that was sampled. In Anthropic's experience, clustered errors on popular evals can be "over three times as large as naive standard errors".

![Chart: in a simulation with 100 cases and 3 runs, where B fixes some cases and breaks others, the case-level t-interval caught the true gain 94.3% of the time and the case bootstrap 93.7%. Treating rows as independent caught it only 80.2% of the time, against a 95% target.](images/stats-coverage.svg)

Here B fixed some cases and broke others. When B helped a little everywhere, the row-level interval did fine (94.6%). You can't know which in advance, so **average per case first**. `compare_runs.py` prints both intervals and their ratio.

<!-- page -->

## Step 2: the confidence interval

With n per-case differences:

```python
m  = mean(d)              # the gain
sd = stdev(d)             # spread of d
se = sd / sqrt(n)         # standard error
lo = m - 1.96 * se
hi = m + 1.96 * se        # 95% interval
```

The **standard error** says how much the mean gain would wobble if you drew a fresh set of n cases. It shrinks with the square root of n: four times the cases, half the width.

`compare_runs.py` uses the *t* multiplier instead of 1.96. It is 1.97 at 400 cases and 2.09 at 20. For small sets that slightly wider interval is more honest.

Miller (summarised in Anthropic's post) recommends reporting, for every comparison, the mean difference, its standard error, the interval and the correlation between the two prompts' scores.

<!-- page -->

## Step 2b: the paired bootstrap

The formula leans on the mean being roughly bell-shaped. A **bootstrap** checks that by brute force: resample whole **cases**, recompute the mean d, repeat.

```python
rng = random.Random(0)        # fixed seed
means = sorted(
    mean(rng.choices(d, k=len(d)))
    for _ in range(5000))
lo = means[125]               # 2.5% point
hi = means[4874]              # 97.5% point
```

The key detail: you resample **d values**, one per case. Each draw keeps A and B paired and keeps a case's runs together. Resampling individual rows would repeat the mistake from the last page.

> **Teacher's note:** Miller regards the bootstrap as unnecessary for a simple mean like this one. The formula is enough. Use the bootstrap as a cross-check, and for metrics with no easy formula (medians, F1, ratios). If the two disagree, the result is borderline.

<!-- page -->

## What 95% means, and what it doesn't

**What it means.** The method has a property: if you repeated the whole experiment many times with fresh cases from the same population, about 95% of the intervals it builds would contain the true gain. Your one interval either does or doesn't. You don't get to know which.

**What it does not mean:**

- Not "a 95% probability the true gain is in this range".
- Not "95% of cases improved".
- Not a promise about users, other models or next month's traffic. It covers cases like the ones in your test set.

**What a p-value is.** If A and B were truly equal, how often would chance give a gap at least this big? It is **not** the probability that B is better.

If the interval includes 0, you haven't shown a difference. That is different from showing there is none.

<!-- page -->

## Step 3: the decision rule

Chapter 3's experiment file ended with this line:

```yaml
min_gain: 0.02
decision: CI low > 0, gain >= min_gain,
          guardrails ok
```

Now you can read it. **Ship B only if all three hold:**

| Result | Verdict |
|---|---|
| CI lower bound > 0, gain ≥ min_gain, guardrails ok | **Ship B** |
| CI lower bound > 0, gain < min_gain | Real but too small: keep A |
| CI lower bound > 0, a guardrail breaks | Don't ship |
| CI includes 0 | **Not proven** |
| CI upper bound < 0 | B is worse |

<!-- page -->

## Step 3b: min_gain and guardrails

**min_gain** is the smallest gain worth the switch: new prompt, more tokens, more review. You choose it *before* the test. Guardrails are cost and latency (and anything else that must not get worse).

> **Teacher's note:** A stricter team asks for the *lower bound* to clear min_gain. Either rule is fine if it's written down first.

<!-- page -->

## Pass/fail grades: McNemar's test

With pass/fail grades, every case lands in one of four boxes:

| | B passes | B fails |
|---|---|---|
| **A passes** | both (concordant) | **A only** |
| **A fails** | **B only** | neither (concordant) |

**McNemar's exact test** uses only the two **discordant** boxes. If A and B were equally good, each discordant case would be a coin flip: B-only or A-only, 50/50. The test asks how unusual your split is for a fair coin.

Concordant cases tell you nothing about *which* prompt is better. A case both prompts pass would look the same under either answer. Add 500 of them and the p-value doesn't move (`test_stats.py` checks this).

With one run per case, d is just +1, 0 or −1, and McNemar agrees closely with the paired interval. With several runs, `compare_runs.py` uses each case's majority outcome (or run 0 with `--mcnemar first`). The interval adds what the p-value lacks: **how big** the gain is.

<!-- page -->

## How many cases? The paired formula

Call **pd** the share of cases where A and B disagree (the discordance rate) and **δ** the smallest gain you want to detect. For 95% confidence and 80% power:

```
n = (1.96·√pd + 0.84·√(pd − δ²))² / δ²
```

Accuracy doesn't appear. Two prompts at 70% and 73% can need 870 cases (they disagree on 10% of cases) or 2,745 (they disagree on 31.5%, as in the demo). The derivation is in `sample_size.py`. Simulated power at the formula's n was 0.80 to 0.82 for the simple test. It was 0.77 to 0.78 for exact McNemar, which is a little conservative.

| Disagree | +2 pts | +3 pts | +5 pts |
|---|---|---|---|
| 10% | 1,960 | 870 | 312 |
| 20% | 3,923 | 1,742 | 626 |
| 30% | 5,885 | 2,614 | 940 |

Chapter 6's formula answers a different question: how precisely one prompt's accuracy is measured. Comparing on *separate* cases instead of the same ones would need about 3,500 cases **per prompt** for 71% vs 74%.

<!-- page -->

## More runs or more cases?

With several runs per case, use the spread of d from a pilot instead:

```
n = (1.96 + 0.84)² · sd_d² / δ²
```

The spread of d has two parts. One is **case noise**: B's real gain differs from case to case. The other is **run noise**: the same prompt answers the same case differently. Averaging k runs divides run noise by k. **Case noise only shrinks with more cases.**

Miller makes the same point: resampling lowers the noise inside each question, but the variation between questions can't be removed that way.

In the demo, almost all the noise was run noise. That's because the simulation flips a fresh coin for every answer. Going from 1 to 3 runs shrank the interval from ±5.5 to ±3.2 points. Real models are often more stable within a case, so case noise dominates. Check yours: compare the interval from run 0 alone with the averaged one.

<!-- page -->

## Worked example: Priya's result

`compare_runs.py` on the demo's 400 cases x 3 runs (trimmed; McNemar on run 0 via `--mcnemar first`):

```
A: 0.709   B: 0.739
Cases: B better 115, A better 85, tie 200
Mean paired difference B-A: +0.0300
  95% CI, paired t:   [-0.0022, +0.0622]
  95% CI, bootstrap:  [-0.0017, +0.0617]
  95% CI, unpaired:   [-0.0142, +0.0742]
McNemar exact (run 0): 66 vs 60, p = 0.66
VERDICT: NOT PROVEN
```

![Chart: B minus A in accuracy points. All three intervals centre on +3.0. Unpaired runs from −1.4 to +7.4, paired from −0.2 to +6.2, bootstrap from −0.2 to +6.2. All cross zero; a dashed line marks the min gain of +2.](images/ci-forest.svg)

The gain of +3.0 clears min_gain (+2). But the interval runs from about −0.2 to +6.2 points. It includes zero, so the verdict is **not proven**. (The demo's own numpy bootstrap gave [−0.3, +6.1]. Bootstraps differ slightly with the random draws.)

<!-- page -->

## Worked example: what Priya should do

Here is the twist. The simulation *built* B to be better, by about 3.7 points on these cases. "Not proven" was still the right call. With 400 cases, this test had only about a **45%** chance of detecting a true 3-point gain. It was a coin flip before it started.

Her options, from `sample_size.py` with the demo's spread (sd of d = 0.327, 3 runs per case):

| To detect | Cases needed |
|---|---|
| +5 points | 337 |
| +3 points | 935 |
| +2 points | 2,103 |

So the honest message to the channel is: *"B is +3.0 points, 95% CI −0.2 to +6.2. Not proven. To confirm a 3-point gain I need about 935 cases; I have 400. I'll grow the set, or look for a bigger change."*

> **Teacher's note:** Don't rerun the same 400 cases until you get a green light. That is peeking (two pages ahead).

<!-- page -->

## Trap: many variants, many metrics

Test five prompt variants against A at the 5% level. If none is truly better, the chance that at least one "wins" anyway is up to about **23%** (1 − 0.95⁵). It is slightly less because the comparisons share A. Track ten metrics and it gets worse.

Two standard fixes:

- **Bonferroni.** With m comparisons, demand p < 0.05 / m. For five, that's 0.01, or 99% intervals (set `alpha: 0.01` in the YAML).
- **Holm.** Sort the p-values. Test the smallest against 0.05/m, the next against 0.05/(m−1), and so on. Stop at the first that fails. It never rejects less than Bonferroni.

The cheapest fix comes first: **pre-declare one primary metric** in the experiment file. Everything else is a guardrail or a note.

**Slices are exploratory.** "B wins on refund tickets" from 40 cases is a lead for the next test on fresh cases, not a result.

<!-- page -->

## Trap: peeking and a worn-out test set

**Peeking.** Checking after every 50 cases and stopping at the first p < 0.05 inflates false wins. In our simulation with no real difference, one look at 400 cases gave a false win **3.7%** of the time. Eight looks gave **13.0%** (`test_stats.py`). Statsig advises fixing the goal, primary metric and stop rule before launch. For online tests that must look early, it points to sequential methods (Chapter 11).

**A worn-out test set.** Each time you tweak a prompt and check it on the test set, you pick the version that happens to suit those cases. After twenty rounds, the test score flatters you. This is **overfitting the test set**. Chapter 6's fix: tune on **dev**, and run the held-out **test** set once, for the final comparison. If you've peeked at test often, it has become dev. Add fresh cases.

<!-- page -->

## Trap: significant is not the same as important

**Practical vs statistical significance.** With 20,000 cases, a +0.3 point gain can have an interval well above zero. It is real, and probably not worth a longer, costlier prompt. That is why the rule has min_gain. Statsig makes the same point: ask for effect sizes and intervals, not just significance.

**Honesty with small sets.** Your Chapter 4 lab has 20 cases. In one mock run the interval was **−13 to +20 points**. No 20-case test can confirm a 3-point gain. That's fine. Say so.

"Not proven" is a valid, professional verdict. It is not a failure. The failures are claiming a win the data can't support, and quietly changing the metric until one appears.

> **Teacher's note:** Other noise sources add to all of this. An LLM judge that grades inconsistently (Chapter 8) widens your intervals too.

<!-- page -->

## Lab: judge your own run

1. Take the `records.jsonl` from your Chapter 4 lab (or practise on `--mock`).
2. Run:
   ```
   cd work/harness
   python compare_runs.py \
     experiments/ticket-triage-v1-vs-v2.yaml
   ```
3. Read each line. How wide is the interval? Does the naive row interval come out narrower? By how much?
4. Add `guardrail_max_increase: {tokens: 0.10}` to the YAML and rerun. Does B pass?
5. Take the printed "SD of per-case differences" and run `python sample_size.py --sd <SD> --effect 0.02`. How many cases would a 2-point gain need?
6. Run `python test_stats.py` and look at the coverage numbers.

Write the one-line message you'd send Priya's lead about your own result.

<!-- page -->

## Checkpoint

**1.** Your eval has 300 cases x 5 runs. A colleague computes the interval from all 1,500 rows per prompt as independent. What's wrong, and what do you do?

**2.** B beats A on 30 cases, A beats B on 10, and both pass on 450. Which numbers does McNemar's test use, and why?

**3.** Two prompt pairs both score 70% vs 73%. One pair disagrees on 10% of cases, the other on 30%. Which needs more test cases to confirm the gain?

<details><summary>Show answers</summary>
1. Runs of the same case are correlated, so the interval comes out too narrow and claims too much. Average each case's runs into one score, take per-case differences B − A, and compute the interval over the 300 differences (or use clustered standard errors).
2. Only 30 and 10, the discordant cases. Under "no difference" each one is a 50/50 coin flip. Cases where A and B agree look the same whichever prompt is better, so they carry no information about the difference.
3. The pair that disagrees on 30%. Paired sample size depends on the discordance rate and the gain, not on accuracy: about 2,600 cases versus 870 for a 3-point gain.
</details>

<!-- page -->

## In an interview

*"What does a 95% confidence interval mean?"*

*"It comes from a procedure that captures the true value 95% of the time across repeated experiments. It isn't a 95% probability that this particular interval contains it. If it includes zero, I haven't shown a difference."*

*"How many test cases do you need?"*

*"It depends on the smallest gain worth shipping and on how often the two prompts disagree, not on accuracy alone. For a paired test I use a pilot run's discordance rate or spread of differences. In one demo, confirming a 3-point gain needed about 935 cases."*

*"Your A/B shows +3 points. Do you ship?"*

*"Not on the point estimate. I check the paired, case-level interval: is its lower bound above zero? Is the gain at least our pre-declared minimum, and are cost and latency within guardrails? If the interval crosses zero, the verdict is not proven, and I'd size a larger test."*

<!-- page -->

## Read more

- **Miller 2024**, *Adding Error Bars to Evals*: clustered standard errors, resampling, paired analysis, power analysis. [arXiv 2411.00640](https://arxiv.org/abs/2411.00640)
- **Anthropic**, *A statistical approach to model evaluations* (the plain-language summary of Miller's paper). [anthropic.com](https://www.anthropic.com/research/statistical-approach-to-model-evals)
- **Statsig**, *A/B testing for LLMs: when statistical significance misleads*: peeking, stop rules, effect sizes. [statsig.com](https://statsig.com/perspectives/abtesting-llms-misleading) (vendor article)
- **Kohavi, Tang, Xu**, *Trustworthy Online Controlled Experiments* (Cambridge, 2020), Ch 17 *The Statistics behind Online Controlled Experiments*.
- **statsmodels**, `mcnemar` docs: the exact version uses the binomial distribution on the discordant counts. [statsmodels.org](https://www.statsmodels.org/stable/generated/statsmodels.stats.contingency_tables.mcnemar.html)
- **Holm–Bonferroni method**, overview with the original 1979 reference. [Wikipedia](https://en.wikipedia.org/wiki/Holm%E2%80%93Bonferroni_method)
- **Next chapter:** Chapter 10, frameworks: the same experiment in promptfoo and in CI, then LangSmith, Langfuse and Braintrust.
