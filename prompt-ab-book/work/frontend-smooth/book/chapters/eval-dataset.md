# Building the eval dataset

Imagine you wrote 20 test questions for your support bot yourself. They're clean, polite, and clearly worded. The new prompt gets 95%. You ship it.

Real customers write things like "order cold!! money back or i report u" and "hi, 2 things: my login AND the promo".

Your test set measured how good the prompt is at *your* questions. Everything you conclude from an eval, every A/B result and every confidence interval, is only as good as the cases underneath it.

<!-- page -->

## What a good set looks like

Anthropic's evals guide gives the core advice: design evals that mirror your **real-world task distribution**, and don't forget **edge cases**.

A good eval set is:
- **Representative:** it looks like what real users send.
- **Covering:** important workflows and known failures are all present.
- **Labelled well:** the expected answers are right.
- **Cheap enough to run often.** Husain notes that coverage, not a magic number, decides the size.

<!-- page -->

## Where cases come from

![Diagram: four sources feed one eval set: a real traffic sample, failures you understood, hand-written edge cases, and synthetic cases. The eval set is labelled, tagged by slice, frozen and versioned, then split into dev for tuning and test for a final check.](images/eval-set-flow.svg)

Then you split it: **dev** is for tuning, **test** is for the final check.

<!-- page -->

## Trust the sources differently

| Source | Trust | Watch out for |
|---|---|---|
| **Real traffic sample** | High | Remove personal data. Sample randomly first |
| **Failures you understood** (Chapter 5) | High | They are *hard* cases, so don't use only these |
| **Hand-written edge cases** | Medium | Your imagination, not users' |
| **Synthetic cases** | Lower | Can't tell you how common anything is |

Start from real traffic whenever you can. Husain's advice for sampling is to begin with a random sample, and only then target rare failures with specific signals.

<!-- page -->

## Synthetic data, done properly

No data yet? Synthetic cases can get you started. The common mistake is asking an LLM to "give me test queries", which gives generic, repetitive ones.

Husain's FAQ suggests defining **dimensions** first. For a support bot, these could be:
- **Issue type:** refund, delivery, account
- **Tone:** calm, angry, rushed
- **Complexity:** one issue, two issues

Write about 20 combinations by hand, then have a model turn each into a realistic message. Run them through your real system and review the outputs.

<!-- page -->

## When synthetic data misleads

Husain's FAQ warns that synthetic data:
- cannot tell you **how common** a failure is in production
- often misses detail in **specialized domains**
- can be unrealistic for **low-resource languages** or dialects
- is risky in **high-stakes** areas such as medicine or law

Compare it with real data as soon as real data exists. And if a failure is something you can simply fix in the prompt, fix it. Don't build test cases around it first.

<!-- page -->

## Labels: who decides "expected"?

Every case needs a trusted expected answer.

1. **Write a labelling guideline.** "If the customer asks for money back, the label is refund, even if the order was also late." Huyen's *AI Engineering* lists creating an evaluation guideline as a step of its evaluation pipeline.
2. **Use someone who knows the domain.**
3. **Have a second person label 20 cases.** Where you disagree, the guideline is unclear.
4. **When a label is arguable, fix the dataset**, not the model (Chapter 5). Make the guideline decide.

<!-- page -->

## Tag your slices

Add a `slice` to each case: intent, language, difficulty, length, or whatever matters to your product.

```
{"id": "t07", "input": "...",
 "expected": "account", "slice": "hinglish",
 "source": "prod"}
```

A slice shows **where** B wins and loses. An overall +2 points can hide "much better on short messages, worse on Hinglish".

Don't over-slice. A slice with 4 cases gives you noise, not insight.

<!-- page -->

## How many cases?

A rough guide to how precisely a set measures **one prompt's accuracy** (95% confidence, accuracy about 80%): n is roughly 1.96² × p × (1 − p) ÷ E².

| You want | Cases needed |
|---|---|
| ±10 points | about 62 |
| ±5 points | about 246 |
| ±3 points | about 683 |

(At 50% accuracy, ±5 points needs about 385.)

Comparing A with B **on the same cases** needs a different calculation, which depends on how often they disagree. Chapter 9 shows it.

<!-- page -->

## Start small, grow steadily

The numbers above are for firm conclusions. You don't need them to begin.

- Start with **50 to 100** well-chosen cases. Husain notes purpose-built eval sets often grow past 100.
- Read failures with error analysis (Chapter 5) and add what you learn.
- Add cases when production surprises you, not on a schedule.

A small set that you *understand* beats a big one you've never read. But a small set can only detect big differences, so be honest about that in your write-up.

<!-- page -->

## Dev and test

Split your set in two:
- **Dev:** where you tune prompts and read failures.
- **Test:** opened only when you're ready to decide.

Why: every time you tweak a prompt after looking at a case, the prompt learns that case. A score on cases you tuned against is optimistic.

A simple rule of thumb is 50/50 or 60/40, stratified so each label appears on both sides. If you peek at the test set often, it has become a dev set. Add fresh cases.

<!-- page -->

## Leakage

Leakage means test cases sneak into the prompt:
- you paste a failing case into the prompt as an example
- you tune a judge on the same cases you test with
- the same message appears in both dev and test

Each makes your score look better than reality. A cheap guard: a script that checks whether any case text appears verbatim in a prompt file.

> **Teacher's note:** Public benchmarks have another risk: they may appear in a model's training data. This is one reason private, task-specific cases matter.

<!-- page -->

## Version and freeze

From Chapter 3: a tested dataset **never changes in place**.

- `cases-v1.jsonl` is frozen once you've used it for a comparison.
- Fixes and additions go into `cases-v2.jsonl`, with a changelog line.
- Keep case IDs stable across versions.
- The experiment file names the exact dataset, so you can always tell what a result was measured on.

If you fix a wrong label, say so, and re-run old comparisons if they matter.

<!-- page -->

## The helper script

`work/harness/dataset_tools.py` has four commands:

```
python dataset_tools.py check DATA --labels a,b,c
python dataset_tools.py summary DATA
python dataset_tools.py split DATA --dev 0.5
python dataset_tools.py leak EXPERIMENT.yaml
```

- `check`: missing fields, duplicate ids or inputs, labels outside the allowed list.
- `summary`: counts by label, slice and source.
- `split`: stratified dev/test files with a fixed seed.
- `leak`: finds case text inside your prompts.

<!-- page -->

## Lab: build your v1 set

1. Collect 30 to 50 cases for your own task. Aim to include real examples and at least 5 edge cases.
2. Write your labelling guideline in 5 sentences.
3. Add `slice` and `source` to each case.
4. Run `check`, then `summary`. Is any label or slice badly lopsided?
5. Run `split`, and update your experiment file to use the dev file.
6. Run `leak` on your experiment.

Keep a note of which cases you were unsure how to label. Those are your most valuable cases.

<!-- page -->

## Checkpoint

**1.** Your 20 test cases were all written by you. What's the risk?

**2.** Why keep a test set apart from the dev set?

**3.** You have 62 cases and 80% accuracy. Roughly how precise is that number?

<details><summary>Show answers</summary>
1. They won't match what real users send, so the score can look good while real behavior is worse. Real samples and edge cases fix this.
2. Tuning against cases makes the prompt fit them, so scores on those cases are optimistic. A separate test set gives an honest check.
3. Roughly plus or minus 10 percentage points at 95% confidence. Not precise enough to see small differences.
</details>

<!-- page -->

## In an interview

*"How would you build an eval set for a new LLM feature?"*

*"I'd start with a random sample of real inputs, remove personal data, and read them to find failure modes. I'd add hand-written edge cases and, if I lacked data, synthetic cases generated across defined dimensions, checked against real data later. A domain expert labels them against a written guideline, and I tag slices. I'd split dev and test, freeze each version, and check for leakage into prompts. I'd start around 50 to 100 cases and grow it with every failure I understand."*

<!-- page -->

## Read more

- **Anthropic**, *Define success criteria and build evaluations*: real-task distribution, edge cases, automated grading. [platform.claude.com](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)
- **Hamel Husain**, *Frequently Asked Questions About AI Evals*: "How many examples do I need?", synthetic data with dimensions, sampling traces. [hamel.dev/blog/posts/evals-faq](https://hamel.dev/blog/posts/evals-faq/)
- **Chip Huyen**, *AI Engineering* (O'Reilly, 2025), Ch 4, "Design Your Evaluation Pipeline", Steps 2 and 3.
- **Next chapter:** evaluation methods: what exists and when to use which.
