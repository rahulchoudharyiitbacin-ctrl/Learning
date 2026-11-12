# How A/B testing works, and what changes for LLMs

Before testing prompts, learn the original game. Imagine a shopping app wonders: *"Will a green Buy button get more purchases than the blue one?"*

Guessing isn't good enough, so the team runs an experiment. Half of the users see the blue button, half see the green one, and the team compares purchases.

This is a **controlled experiment**, what most people call an **A/B test**. Ron Kohavi, Diane Tang and Ya Xu wrote the standard book on it, *Trustworthy Online Controlled Experiments*, based on years of running thousands of tests at large tech companies.

The next page shows the shape of every A/B test.

<!-- page -->

## The shape of an A/B test

![Diagram: all users go through a random split into group A, the control, and group B, the treatment. The same metric is measured in both and compared.](images/classic-ab-flow.svg)

The key word is **random**. Because chance decides who sees what, the two groups are alike in everything else: device, mood, time of day. So a difference in results can be credited to the one thing you changed.

<!-- page -->

## The six ingredients

| Ingredient | The question it answers |
|---|---|
| **Hypothesis** | What do we expect, and by how much? |
| **Unit** | What is one data point: user, session or test case? |
| **Primary metric** | What single number decides the winner? |
| **Guardrails** | What must not get worse? |
| **Sample size** | How much data do we need to see a real effect? |
| **Decision rule** | What result makes us ship B, keep A, or wait? |

Kohavi et al. call this the **Overall Evaluation Criterion (OEC)**: the agreed measure (sometimes a blend) of "better".

> **Teacher's note:** Explore first if you need to. Then write all six down and freeze them *before* the test. Picking the metric afterwards is how teams fool themselves.

<!-- page -->

## A prompt example

**Hypothesis:** "Adding three worked examples to the support-bot prompt will raise the share of tickets resolved without a human by at least 2 percentage points."

| Ingredient | Our choice |
|---|---|
| Unit | Each customer conversation |
| Primary metric | % resolved without human hand-off |
| Guardrails | Cost per conversation, response time, refund-complaint rate |
| Decision rule | Ship B only if the gain is clearly above the noise and no guardrail worsens |

Notice the hypothesis names a **direction**, a **metric** and a **size**. "B will be better" is not a hypothesis you can test.

<!-- page -->

## Three ideas in plain words

**Significance (p-value).** If A and B were truly equal, how often would chance alone give a gap at least this big? A small p-value means "rarely", which is evidence against "no difference".

**Confidence interval.** A range of plausible effects. A 95% interval comes from a method that captures the true effect 95% of the time. If it includes zero, you haven't shown a difference.

**Power.** The chance your test spots a real effect when one exists. Halving the effect you want to detect roughly quadruples the data you need.

> **Teacher's note:** A p-value is not "the probability B is better". A common interview probe. Chapter 9 works through all three with real numbers from our demo.

<!-- page -->

## Classic traps

Experienced teams still fall into these:

- **Peeking.** Checking results every day and stopping when it "looks significant". Statsig's guide notes that early looks inflate false positives and advises fixing the goal, primary metric and stop rule before launch.
- **Too many metrics.** Test enough and one will win by luck.
- **Believing a too-good result.** Kohavi's Chapter 3 is named after *Twyman's Law*: a figure that looks surprisingly good is usually wrong. Look for a bug first, a miracle second.
- **Broken splits.** If you planned 50/50 and got a clearly lopsided split, something in the assignment is broken, and the results can't be trusted.

<!-- page -->

## Two designs, one idea

| | **Online A/B** | **Offline eval** |
|---|---|---|
| Who gets A or B? | Different users, chosen at random | **Every** test case gets both |
| What makes it fair? | Randomisation | Pairing: same cases, same conditions |
| Where is the randomness? | Which users landed where | Which cases you sampled, and run-to-run variation |

> **Teacher's note:** This is why Chapter 9 uses *paired* statistics for offline tests. Be precise about this difference in interviews.

<!-- page -->

## What's different for LLMs

A button is the same every time. A prompt isn't. GrowthBook, a testing platform, puts it neatly: with an LLM the treatment "isn't a thing; it's a process."

![Illustration: two overlapping bell curves for Prompt A and Prompt B, showing that each prompt produces a spread of output quality rather than one fixed result.](images/prompt-is-a-spread.svg)

Because the curves overlap, any single output from A or B can mislead you. You need many samples, then compare the *spreads*.

<!-- page -->

## Five differences

| Classic A/B | LLM prompt A/B |
|---|---|
| Variant is **fixed** | Output **can vary**, even at temperature 0 |
| Metric is a count (clicks, purchases) | "Quality" needs a **grader** (Ch 7–8) |
| Wording is one design choice among many | **Formatting** alone can swing results (Ch 1) |
| The product stays put | The **model underneath** can change |
| Latency is a classic guardrail | Per-request **cost** joins it as a core metric |

Atil et al. (2024) tested five hosted LLMs set to be deterministic across 8 tasks and 10 runs. Accuracy still varied by **up to 15%** on some tasks, and none was fully repeatable. A local run of an open model was repeatable, so the cause may lie in how hosted services run requests.

<!-- page -->

## What to do about it

Each difference has a countermeasure, and each gets a chapter:

1. **Randomness:** run each case several times and compare paired results (Ch 4 and 9).
2. **Fuzzy quality:** choose graders deliberately, and check LLM judges against humans (Ch 7–8).
3. **Prompt sensitivity:** change one thing at a time, and keep prompts in version control (Ch 3).
4. **Model drift:** pin an exact model version for the whole test. Statsig warns that the model can quietly update under your feet. Freeze everything else too: no prompt edits during the test.
5. **Cost and latency:** track them as guardrails in every comparison.

> **Teacher's note:** This is why most prompt A/B work happens **offline** first, on a fixed test set. It's fast, and you control the data. Online tests then confirm the win with real users.

<!-- page -->

## Checkpoint

**1.** Why must users be assigned to A or B *randomly*?

**2.** Name three things to decide before running a test.

**3.** Why doesn't setting temperature to 0 make a prompt test deterministic?

<details><summary>Show answers</summary>
1. Random assignment makes the groups alike in everything else, so a difference can be credited to the change.
2. Any three of: hypothesis, unit, primary metric, guardrails, sample size, decision rule.
3. Hosted models can still vary even when configured to be deterministic. Atil et al. saw accuracy swing by up to 15% on some tasks.
</details>

<!-- page -->

## In an interview

*"How would you A/B test a prompt change?"*

*"First I write the hypothesis, one primary metric and guardrails like cost and latency, and I pin the model version. I test offline on a fixed set, running each case several times because outputs vary, and compare A and B on the same cases. If B wins by more than the noise, I roll it out to a small share of real users, randomly assigned, and decide against a stopping rule I set in advance."*

<!-- page -->

## Read more

- **Kohavi, Tang, Xu**, *Trustworthy Online Controlled Experiments* (Cambridge, 2020). Ch 1 is a free download; Ch 2 *Running and Analyzing Experiments*; Ch 3 *Twyman's Law and Experimentation Trustworthiness*; Ch 7 *Metrics for Experimentation and the Overall Evaluation Criterion*.
- **Atil et al. 2024**, *Non-Determinism of "Deterministic" LLM Settings*. [arXiv 2408.04667](https://arxiv.org/abs/2408.04667)
- **GrowthBook**, *How do you A/B test an LLM when outputs aren't deterministic?* [growthbook.io](https://www.growthbook.io/insights/ab-testing-llms) (vendor article)
- **Statsig**, *A/B testing for LLMs: when statistical significance misleads*. [statsig.com](https://statsig.com/perspectives/abtesting-llms-misleading) (vendor article)
- **Bruce, Bruce, Gedeck**, *Practical Statistics for Data Scientists*, the A/B testing section (Ch 3 per search listings; check your edition).
- **Next chapter:** Chapter 3 on setting up a prompt experiment cleanly.
