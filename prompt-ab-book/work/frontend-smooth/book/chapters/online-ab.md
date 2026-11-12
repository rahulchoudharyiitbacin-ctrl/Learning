# Online A/B: shadow, canary, split

Your new prompt won offline. B beat A on the test set, with an interval that cleared zero (Chapter 9). You ship it to everyone.

A month later, the numbers that matter to the business haven't moved. Customers neither noticed nor cared.

The test set was a sample of the world. Real users are the world. Online testing is how you find out whether an offline win becomes a real-world win.

Hamel Husain notes that A/B testing is usually only appropriate for more mature products. Many teams stop at offline evals. This chapter is for when you're ready for the next level.

<!-- page -->

## The rollout ladder

![Diagram: five stages from offline eval, where nobody is affected, to shadow where B runs silently, canary where 1 to 5% of users see B, an A/B test at 50/50 by user for two weeks or more, and full rollout. Bars show the share of users who see B: 0, 0, about 5, 50 and 100 percent. Every stage can roll back with a kill switch.](images/rollout-ladder.svg)

Each stage lets you fail **cheaply** before the next one puts more users at risk.

<!-- page -->

## Offline vs online

| | **Offline eval** | **Online A/B** |
|---|---|---|
| Who it uses | A fixed test set | Real users |
| Design | **Paired**: every case gets both prompts | **Randomised**: each user gets one |
| Speed | Minutes | Days to weeks |
| Cost of a bad prompt | None | Real users affected |
| Measures | Output quality you define | What users actually do |

Chapter 9's paired statistics are for the left column. This chapter's statistics are for the right.

<!-- page -->

## Stage 1: shadow

In **shadow** mode, B runs on live traffic but users only ever see A's answer. You score both silently and compare.

GrowthBook, an experimentation vendor, describes this as running both variants against live traffic and scoring them before any user sees a difference.

**What it tells you:** latency, cost, errors, and how B's answers differ on *real* inputs. Score a sample with your judge (Chapter 8).

**What it can't tell you:** what users *do*. They never saw B.

It costs extra model calls, and it handles real user data, so apply the same privacy rules as your logs.

<!-- page -->

## Stage 2: canary

A **canary** shows B to a small slice of users first. GrowthBook's guidance is 1 to 5% of traffic, watched for 24 to 48 hours (vendor advice, but a common pattern).

Watch the guardrails:
- errors and empty outputs
- latency (p95)
- cost per conversation
- refusals
- complaints

Have a **kill switch**: a feature flag that sends everyone back to A instantly.

A canary catches disasters. It can't prove a small improvement. That takes the full test.

<!-- page -->

## Randomise by user

If you randomise per **request**, one customer can get A in one message and B in the next. That contaminates every behavioural metric.

The unit is the **user**, with a stable assignment: the same user always gets the same arm.

GrowthBook describes this as consistent hashing of the user ID, with no stored state. You can write the idea in a few lines:

```python
def assign(experiment, user_id, split=0.5):
    key = f"{experiment}:{user_id}"
    h = hashlib.sha256(key.encode()).digest()
    x = int.from_bytes(h[:8], "big") / 2**64
    return "B" if x < split else "A"
```

<!-- page -->

## Test your assignment

Assignment bugs ruin experiments silently, so test them. In `online_tools.py` (tested by `test_online.py`):

- **Stable:** the same user gets the same arm every time.
- **Balanced:** over 100,000 users the split came out 49.95% B.
- **Canary-safe:** raising the rollout from 5% keeps every user's arm.
- **Independent:** two experiments use different salts, so being in B for one says nothing about the other (P(B and B) = 0.2498).

```
python online_tools.py assign \
  --experiment support-v2 u1 u2 u3
```

<!-- page -->

## Choosing metrics

Use three kinds, decided **before** launch:

| Kind | Support-bot example |
|---|---|
| **Primary** (one) | Conversations resolved without a human |
| **Guardrails** | Cost per conversation, p95 latency, error and refusal rate, complaints |
| **Diagnostics** | Thumbs up/down, conversation length, retries |

Kohavi et al. call the primary metric the **Overall Evaluation Criterion** (Chapter 2).

GrowthBook argues that output text is a poor primary metric. Prefer behaviour: task completion, retention, conversion. Judge scores are for *diagnosing*.

<!-- page -->

## How many users, how long?

Online metrics like "resolved or not" are rates, so a two-proportion calculation applies.

```
python online_tools.py plan \
  --baseline 0.10 --mde 0.01 \
  --daily-users 4000
```

For a 10% baseline and a 1-point gain, it says **14,751 users per arm** (checked by hand and by simulation). At 4,000 eligible users a day, that's 8 days, so plan **two weeks**.

Small effects are expensive: halve the gain you want to detect and you need about four times the users.

<!-- page -->

## Run long enough, then stop

GrowthBook suggests two weeks as the floor for LLM experiments, partly because of **novelty effects**: users may react differently to a new style at first.

- Run whole weeks, so each day of the week counts equally.
- Decide the duration and metric **before** you start.
- Don't stop when it first looks significant.

In Chapter 9's simulation, with no real effect, one look gave 3.7% false wins, and looking 8 times gave 13%. The same trap applies here, and it's one reason a flat or fading effect after a strong first few days is a warning, not a win.

<!-- page -->

## Sample ratio mismatch

You planned 50/50. You got 5,000 vs 5,200. Is that alarming? A chi-square test says how surprising it is.

```
python online_tools.py srm \
  --counts A=5000,B=5200
```

p = 0.048. At 50,000 vs 52,000 (the same ratio, ten times the traffic) p = 4e-10.

That second case means **something is broken**: assignment, logging, bots, or crashes in one arm. Don't read the results until you find out why.

My alarm level here is a strict 0.001, because the check runs often.

<!-- page -->

## Reading the result

Online, users are independent, so compare the two groups directly. Illustrative numbers: A resolved 100 of 1,000, B resolved 130 of 1,000.

```
python online_tools.py compare \
  --a 100/1000 --b 130/1000
```

B − A = +3.0 points, 95% CI [+0.2, +5.8], p = 0.036.

Then check: Did the guardrails hold? Is `min_gain` met? Did the SRM check pass?

Slices (new users, Hinglish) are **exploratory**. And remember Chapter 9: more metrics and slices mean more chances for a false win.

<!-- page -->

## When offline and online disagree

B won offline and is flat online. Don't just shrug. The usual suspects:

- **The test set isn't representative.** Real traffic differs from your cases.
- **The metric isn't what users value.** A better-sounding answer didn't change outcomes.
- **The effect is diluted.** It only helps a small share of conversations.
- **Novelty or timing** muddied the early days.

Do error analysis (Chapter 5) on online conversations, add what you learn to the dataset (Chapter 6), and update the metric if it was the wrong one.

<!-- page -->

## After launch

Launching is not the end:
- **Log** the prompt version and model version on every request (Chapter 3).
- **Sample** live conversations and score them with a validated judge.
- **Watch** for drift: inputs change, and models get updated.
- **Feed back:** failures become test cases.

Huyen's *AI Engineering* Ch 10 covers monitoring and observability, and user feedback. The frameworks in Chapter 10 can score live traces too.

> **Teacher's note:** Keep your kill switch tested. A rollback you've never practised is a hope, not a plan.

<!-- page -->

## Tools

You need three things from a platform: **sticky user-level assignment**, **percentage rollouts with a kill switch**, and **metrics tied to the assignment**.

Feature-flag and experimentation platforms offer these. GrowthBook (open source) describes all three in its guide. Statsig and LaunchDarkly are other well-known options. I haven't checked their current docs, so check yours, since features and pricing change.

You can also build the assignment yourself, as in this chapter, if your product is small. The hard part isn't the hashing. It's the discipline: one primary metric, a fixed duration, and honest guardrails.

<!-- page -->

## Lab: plan an online test

1. Pick your primary metric and two guardrails.
2. Find your real baseline rate and the smallest gain worth shipping (`min_gain`).
3. Run `plan` with your daily traffic. How many weeks?
4. Write your rollout plan: shadow length, canary share and duration, A/B duration.
5. Write the **rollback rule** now: "If p95 latency rises more than X% or errors exceed Y%, switch to A."
6. Run `srm` on a made-up outcome where the split is 52/48 in 100,000 users. What do you conclude?

<!-- page -->

## Checkpoint

**1.** Why randomise by user instead of by request?

**2.** You planned 50/50 and see 52,000 vs 50,000 users. What do you do?

**3.** Your A/B test looks strongly positive after three days. Should you stop?

<details><summary>Show answers</summary>
1. A request-level split lets one user see both prompts, which contaminates behavioural metrics. User-level assignment keeps each person's experience consistent.
2. Treat it as a possible sample ratio mismatch. A chi-square test gives p about 4e-10, so something is broken (assignment, logging, bots or crashes). Investigate before trusting any result.
3. No. Early results can come from novelty or from peeking. Run the planned duration, at least two weeks, with the metric chosen in advance.
</details>

<!-- page -->

## In an interview

*"You have a prompt that wins offline. How do you roll it out?"*

*"I'd run it in shadow on live traffic and score a sample, then a small canary of a few percent behind a feature flag with a kill switch, watching errors, latency, cost and refusals. If that's clean, I'd run a 50/50 test randomised by user with one primary metric and guardrails fixed in advance, sized for the gain I care about and run for at least two weeks. I'd check for a sample ratio mismatch first, then read the interval against my minimum gain. If it's flat, I'd investigate the offline-online gap."*

<!-- page -->

## Read more

- **GrowthBook**, *How do you A/B test an LLM when outputs aren't deterministic?* Shadow scoring, canary, user-level randomisation, duration. [growthbook.io](https://www.growthbook.io/insights/ab-testing-llms) (vendor article)
- **Statsig**, *A/B testing for LLMs: when statistical significance misleads*. [statsig.com](https://statsig.com/perspectives/abtesting-llms-misleading) (vendor article)
- **Kohavi, Tang, Xu**, *Trustworthy Online Controlled Experiments* (Cambridge, 2020): Ch 7 on metrics and the OEC, and Ch 15 *Ramping Experiment Exposure: Trading Off Speed, Quality, and Risk*.
- **Chip Huyen**, *AI Engineering* (O'Reilly, 2025), Ch 10: monitoring and observability, user feedback. Her *Designing Machine Learning Systems* Ch 9, *Continual Learning and Test in Production*, is for classical ML; a third-party outline lists shadow deployment, A/B testing and canary release there.
- **Hamel Husain**, *Your AI Product Needs Evals*, on the three levels. [hamel.dev/blog/posts/evals](https://hamel.dev/blog/posts/evals/)
- **Next chapter:** beyond single prompts, a short brief on RAG, agents and multi-turn evals.
