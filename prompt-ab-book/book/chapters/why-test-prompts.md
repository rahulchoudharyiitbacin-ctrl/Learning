# Why test prompts, and why A/B?

Imagine you built a support bot for a food-delivery app. Its prompt is **version A**.

One evening you rewrite the prompt as **version B** and try it on five customer messages. All five answers look better. You ship it.

Two days later, refund complaints have doubled.

Nothing crashed. No error appeared. The bot just got worse in a way you couldn't see from five examples.

That is the core problem of this book: **a prompt change is a code change, but it comes with no compiler and no test suite.** Unless you build the tests yourself, you're shipping on gut feeling.

<!-- page -->

## Prompts are fragile

You might think small wording changes don't matter much. Research says otherwise.

Sclar et al. (ICLR 2024) took few-shot tasks and changed only the *formatting* of the prompt: separators, spacing, casing. The meaning stayed the same. On LLaMA-2-13B, accuracy differed by **up to 76 points** between formats on some tasks.

It didn't go away with bigger models, more examples or instruction tuning. Their advice: report a *range* of results across plausible formats, not a single score.

> **Teacher's note:** That study used open-source models, so don't assume your model is immune, and don't assume it's equally fragile either. The professional move is to **measure it on your own task**.

<!-- page -->

## Three sources of variation

When B scores differently from A, three things could be responsible:

| Source | What it is | Can you control it? |
|---|---|---|
| **The prompt** | The text you changed | This is what you want to test |
| **The model's randomness** | Same prompt, same input, different output on each run | Partly: repeated runs |
| **The examples you tried** | Which inputs you happened to look at | Partly: a fixed set helps; more cases shrink the noise but never remove it |

With five hand-picked examples, run once, the second and third sources can outweigh the first.

**A/B testing controls the second and third as far as it can, and measures what is left, so a difference can be credited to the prompt.**

<!-- page -->

## The fair setup

![Diagram: model, settings, test set and grader are held fixed; only Prompt A versus Prompt B changes, producing Score A and Score B.](images/ab-fixed-vs-changed.svg)

Everything in the grey box is locked. Only the prompt differs, so any gap between Score A and Score B points back to the prompt.

<!-- page -->

## What A/B testing means

In general: you run **two versions** (A and B) under the **same conditions**, measure them with a metric you chose **before** looking, and use statistics to decide whether the difference is real.

For prompts, there are two places to do it:

- **Offline:** a fixed test set, before anyone sees the change.
- **Online:** real users split between A and B.

![Diagram: offline runs a fixed test set through A and B and grades the scores before launch; online splits real users between A and B and compares an outcome metric after launch.](images/offline-vs-online.svg)

Most daily work is offline. Online shows whether the win moves real user outcomes.

<!-- page -->

## Where A/B fits in the evaluation ladder

Hamel Husain, who writes widely on evals, describes three levels of evaluation:

![Diagram: a three-step ladder from unit tests (seconds, almost free) to human and model evaluation (minutes to hours) to A/B tests with real users (days to weeks).](images/eval-ladder.svg)

| Level | What it is |
|---|---|
| **1. Unit tests** | Quick automatic checks (valid JSON, contains the order ID) |
| **2. Model and human eval** | People or an LLM judge score outputs; includes debugging |
| **3. A/B testing** | Real users see different versions |

In practice, most changes are checked at levels 1 and 2. Husain says level 3 usually suits more mature products.

<!-- page -->

## When do you need it?

**Test seriously when:**
- the prompt runs in production and a wrong answer costs money, trust or safety
- several people edit the same prompt
- you're about to switch to a new model version
- you plan to say "this prompt is better" in a review, or in an interview

**Skip the ceremony when** it's a throwaway script or a one-off task you'll check by eye.

One more rule before any test: **decide what "better" means first.** Anthropic's prompt engineering docs say the same: have clear success criteria, a way to test against them, and a first draft before you start tuning. Otherwise you'll pick the metric that makes B look good. Reading real outputs first often reveals the criteria; freeze them before you compare A and B.

<!-- page -->

## What you'll be able to do

By the end of this book you should be able to:

1. Explain how classic A/B testing works and what changes for LLMs.
2. Set up a prompt experiment with everything except the prompt held fixed.
3. Build an evaluation dataset and choose the right evaluation method for the task.
4. Use an LLM as a judge without being fooled by its biases.
5. Write a small Python harness, then run the same experiment in promptfoo.
6. Decide with confidence intervals whether B really improved.
7. Roll out online and explain it all in an interview.

<!-- page -->

## Checkpoint

You tested a new prompt on 5 questions and it looked better. Name three reasons that isn't enough.

<details><summary>Show answer</summary>
1. Too few examples, so luck can explain the result.
2. One run each, but LLM outputs vary from run to run.
3. You chose the examples yourself, so they may suit B. Also, you didn't define "better" in advance.
</details>

<!-- page -->

## In an interview

A strong answer to *"Why do you A/B test prompts?"* sounds like this:

*"Prompts are fragile. Small changes can swing results, and outputs are random, so judging a change by a few examples is unreliable. I fix everything except the prompt, run both versions on the same test set, and use a metric chosen in advance. I only promote the new prompt if the difference is larger than the noise."*

<!-- page -->

## Read more

- **Sclar et al. (ICLR 2024)**, *Quantifying Language Models' Sensitivity to Spurious Features in Prompt Design*. [arXiv 2310.11324](https://arxiv.org/abs/2310.11324)
- **Hamel Husain**, *Your AI Product Needs Evals* (the three levels). [hamel.dev/blog/posts/evals](https://hamel.dev/blog/posts/evals/)
- **Anthropic**, *Prompt engineering overview*. [platform.claude.com](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview)
- **Chip Huyen**, *AI Engineering* (O'Reilly, 2025), Ch 5 *Prompt Engineering*, for the full range of prompting techniques.
- **Next chapter:** Kohavi, Tang and Xu, *Trustworthy Online Controlled Experiments*, Ch 1 (free download).
