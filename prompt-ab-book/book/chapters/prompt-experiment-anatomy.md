# Anatomy of a prompt experiment

Three months from now, your manager asks: *"Why did we switch to prompt v2? Can you show me the test?"*

If your answer is "I tried it in a notebook, I think it was better", you have a problem. The notebook has been edited. The test questions were changed. Nobody remembers which model you used.

An experiment you can't **reproduce** is an anecdote. This chapter is about turning your tests into proper experiments: every part named, fixed, written down and saved.

<!-- page -->

## Three buckets

![Diagram: a prompt experiment has three groups. What you vary: Prompt A and Prompt B. What you lock: model ID, settings, test set version, grader version, tools and context, runs per case. What you record: every raw output, scores, tokens and cost, latency.](images/experiment-anatomy.svg)

Everything about an experiment goes into one of three buckets: what you **vary**, what you **lock**, and what you **record**.

<!-- page -->

## Vary one thing

A prompt looks like one thing, but it's really a bundle:

- the instructions
- the worked examples
- the output format
- the order, separators and spacing

If B changes the instructions, adds examples *and* switches to JSON output, and B wins, which change helped? You can't say. One may have helped and another hurt.

Formatting alone can swing results a lot (Sclar et al., Chapter 1), so it counts as a variable too.

> **Teacher's note:** With several ideas, test them one at a time in a ladder: A → B1 → B2 → B3. Slower, but you learn what works.

<!-- page -->

## Lock the rest

| Lock this | Why |
|---|---|
| **Model ID** | Even snapshots of the same model family can behave differently |
| **Sampling and length settings** | Temperature (where allowed), effort and max tokens change how random, deep and long outputs are |
| **Tools and retrieved context** | B must not get extra information |
| **Test set version** | A and B must take the same exam |
| **Grader and its prompt** | A different examiner means different marks |
| **Runs per case** | Fewer runs means noisier scores |

Use the same settings you use in production, so the test reflects real behavior. Newer Claude models no longer accept `temperature`, `top_p` or `top_k`, so there you lock `effort` and `max_tokens` instead. With providers that allow it, lock temperature too.

<!-- page -->

## Pin the model

OpenAI's prompt engineering guide notes that even different snapshots of a model within the same family can produce different results. It strongly recommends pinning production applications to specific model snapshots.

The rule for experiments: use the **most specific model ID** your provider offers. Avoid names that quietly point to newer versions.

Also **run A and B together**, in the same batch and in shuffled order, not A on Monday and B on Friday. Statsig warns that models can update under your feet; if that happens mid-test, both variants face roughly the same conditions.

> **Teacher's note:** Some providers offer a `seed` setting. Don't treat it as a guarantee. Atil et al. (Chapter 2) found outputs still varied under settings meant to be deterministic.

<!-- page -->

## Version prompts like code

Keep prompts as **files in git**, not strings buried in code. One file per version:

```
prompts/
  support-bot/
    v1.txt
    v2.txt
    CHANGELOG.md
data/
  tickets-v3.jsonl
experiments/
  2026-11-12-v1-vs-v2.yaml
runs/
```

The changelog gets one line per version: *what changed, and why.* Never edit a prompt file after it has been tested. Make a new version instead. Same for the test set: `tickets-v3` stays frozen, and fixes become `tickets-v4`.

<!-- page -->

## The experiment file

Write the whole setup in one small file, before you run anything:

```yaml
name: support-bot-v1-vs-v2
hypothesis: v2 lifts resolution by 2+ pts
model: <exact model ID>
effort: low
max_tokens: 1024
variants:
  A: prompts/support-bot/v1.txt
  B: prompts/support-bot/v2.txt
dataset: data/tickets-v3.jsonl
runs_per_case: 3
grader: graders/resolved-v2.py
primary_metric: resolved_rate
guardrails: [cost_per_case, p95_latency]
min_gain: 0.02
decision: CI low > 0, gain >= min_gain, guardrails ok
```

<!-- page -->

## Why this file matters

- **Honesty.** The hypothesis, metric and decision rule are fixed *before* you see results (Chapter 2's six ingredients).
- **Reproducibility.** Anyone can rerun the test from this file.
- **Comparison.** Next month's test is a copy with one line changed.
- **Specific and measurable.** Anthropic's eval guide asks for specific, measurable criteria; its worked example tests on a held-out set.
- **Careful with repeats.** Three runs per case aren't three independent cases. Average them per case before computing the interval (Chapter 9).

Chapter 4 builds a harness that reads a file like this and runs it. Chapter 10 shows the same thing in promptfoo.

<!-- page -->

## The run record

For every single model call, save one line:

```json
{"case_id": "t-0412", "variant": "B",
 "run": 2, "output": "...", "grade": 1,
 "tokens_in": 812, "tokens_out": 143,
 "latency_ms": 1830, "config_hash": "9f3c1a"}
```

Saving **raw outputs**, not only scores, is the habit that separates pros from beginners. When B loses on some cases, the outputs show you *why* (Chapter 5). Token counts and latency give you cost and speed for free. The config hash ties each line back to the exact experiment file.

<!-- page -->

## Mistakes that ruin experiments

- Editing the test set after seeing results
- Changing the grader prompt between A's run and B's run
- Different settings or model for A and B
- Running A last week and B today
- Putting test questions inside the prompt's examples (leakage)
- Saving only the average score
- Several changes bundled into B

> **Teacher's note:** Anthropic's worked example uses a held-out test set. Tune on a dev set, then confirm the winner once on the test set. Tuning on the cases you test on makes the score look great but proves little.

<!-- page -->

## Before you press run

A quick checklist:

1. One sentence hypothesis, with direction, metric and size
2. Exactly one difference between A and B
3. Model ID pinned, settings identical
4. Test set and grader frozen and versioned
5. Primary metric and guardrails chosen
6. Runs per case decided
7. Decision rule written down
8. Output folder ready for raw outputs

<!-- page -->

## Lab: your own experiment file

Pick a small task you know, like labelling emails or summarising tickets. Then:

1. Create the folder layout from this chapter.
2. Write `v1.txt` (your current prompt) and `v2.txt` (**one** change).
3. Add a changelog line: what changed and why.
4. Write the experiment file: hypothesis, metric, guardrails, minimum gain.
5. Put 10 test cases in `data/cases-v1.jsonl` for now.

You'll run this file in Chapter 4, so keep the folder.

<!-- page -->

## Checkpoint

**1.** B changes the instructions, adds examples and switches the output format, and wins. What can you conclude?

**2.** Why save raw outputs and not just scores?

**3.** Why run A and B in the same batch?

<details><summary>Show answers</summary>
1. Only that the bundle of changes did better. You can't say which change caused it, so test them one at a time.
2. Scores say *that* B lost cases; raw outputs show *why*. They also let you regrade later with a better grader.
3. If the model changes or the service has an off day, both variants are affected equally. Running them at different times can blame the prompt for a change in the model.
</details>

<!-- page -->

## In an interview

*"How do you make a prompt experiment reproducible?"*

*"I treat it like code. Prompts and test sets are versioned files that never change once tested. Each experiment is a config file with the hypothesis, pinned model ID, settings, dataset version, grader, metric and decision rule. I run both variants in the same batch, and I save every raw output with a config hash, so anyone can rerun it or dig into failures."*

<!-- page -->

## Read more

- **OpenAI**, *Prompt engineering guide*: the advice on pinning model snapshots. [developers.openai.com](https://developers.openai.com/api/docs/guides/prompt-engineering)
- **Anthropic**, *Define success criteria and build evaluations*: specific, measurable criteria and held-out test sets. [platform.claude.com](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)
- **Chip Huyen**, *AI Engineering* (O'Reilly, 2025), Ch 4, "Design Your Evaluation Pipeline", Steps 2 and 3 (create an evaluation guideline; define evaluation methods and data).
- **Sclar et al. 2024**, formatting sensitivity: [arXiv 2310.11324](https://arxiv.org/abs/2310.11324)
- **Atil et al. 2024**, non-determinism: [arXiv 2408.04667](https://arxiv.org/abs/2408.04667)
- **Next chapter:** a hands-on harness in Python that runs your experiment file.
