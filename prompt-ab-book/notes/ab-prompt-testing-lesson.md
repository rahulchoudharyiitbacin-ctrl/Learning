# A/B testing prompts, the way professionals do it

## 0. The one-sentence idea
Change **one thing** (the prompt), hold **everything else fixed** (model, temperature, tools, data), measure on **the same inputs**, and only ship if the difference is **bigger than the noise**.

## 1. The pipeline (two stages, not one)

| Stage | What | Why |
|---|---|---|
| **Offline A/B** (eval) | Run prompt A and B on a fixed *golden set* (100–1000 real, labelled cases), grade both, compare paired | Cheap, fast, safe, repeatable. Catches regressions before users see them |
| **Shadow / canary** | B runs on live traffic but users still see A (shadow), or B goes to 1–5% (canary) | Real input distribution, latency, cost, edge cases |
| **Online A/B** | Randomly split users 50/50 via a feature flag, measure product metrics for days/weeks | Only this tells you if users are actually better off |

Most "prompt A/B testing" in practice is **offline**. Online is for prompts that touch a business metric.

## 2. Offline A/B, step by step
1. **Define success first.** What does "better" mean? Accuracy on a label, JSON validity, faithfulness to the source, tone, refusal rate, latency, tokens/cost. Write it down *before* looking at outputs.
2. **Build the golden set.** Real production inputs (sampled, anonymised), plus hard cases and past bugs. Split by slice (language, ticket type, length) so you can see *where* B wins or loses.
3. **Pick graders, cheapest first:**
   - Code checks: exact match, regex, JSON schema, "contains the order ID".
   - LLM-as-judge with a rubric for fuzzy qualities. Known biases: **position** (prefers first answer), **verbosity** (prefers longer), **self-preference** (prefers its own model family). Fixes: run both orders and swap, score against a rubric instead of "which is better?", use a different model as judge, and calibrate the judge against ~50–100 human labels.
   - Humans for the final call on subjective tasks.
4. **Control the variables.** Same model version (pin it, e.g. a dated snapshot), same temperature, same tools/context. Version prompts in git like code.
5. **Run multiple samples** per case (3–5) at your production temperature. Same prompt, same data, different run = different score (see demo: A scored 74.3%, 69.0%, 69.5% across 3 runs).
6. **Compare paired, report a confidence interval**, not just two numbers.
7. **Look at the diffs.** Read the cases where A and B disagree. That's where you learn *why*.
8. **Check guardrails too:** B may win accuracy but cost 2x tokens or add 800 ms latency.

## 3. The statistics you actually need
- **Paired, not unpaired.** A and B saw the *same* cases, so compare per-case differences. Easy cases are easy for both; pairing removes that noise. In the demo, pairing shrinks the 95% CI from ±4.4 to ±3.2 points.
- **McNemar test** (binary pass/fail): ignore cases where both pass or both fail; only the disagreements matter. If B-only wins ≈ A-only wins, there's no real difference.
- **Paired bootstrap:** resample *cases* 10,000 times, recompute the mean difference, take the 2.5th–97.5th percentile. Works for any metric.
- **Sample size:** n ≈ ((1.96 + 0.84) × sd_diff / effect)². Demo: to detect a 2-point gain you need ~2,100 cases; 4 points ~530; 8 points ~130. **Small eval sets can only detect big improvements.**
- **Don't fish.** Testing 20 prompt variants and shipping the best one finds a "winner" by luck. Hold out a fresh test set for the final check.

### Demo result (`../work/ab-prompt-test/demo.py`)
B looked better: 73.9% vs 70.9% (+3.0 points). But the paired bootstrap CI is [−0.3, +6.1] and McNemar p = 0.66. **Verdict: not proven.** A junior engineer ships B; a professional says "promising, need ~500+ cases or a bigger effect."

## 4. Online A/B (the production stage)
- **Randomise by user (or session), not by request**, so one person doesn't see both prompts.
- Use a feature-flag / experimentation tool to assign and log the variant with every request.
- **Primary metric** (one!): task success, resolution rate, thumbs-up rate, conversion.
  **Guardrails:** latency p95, cost per request, error/refusal rate, escalation to human.
- Decide duration and sample size **in advance**; don't stop the moment it looks good (peeking inflates false positives).
- Log prompt version + model version + inputs/outputs so you can debug and rebuild the eval set from real traffic.

## 5. How to say it in an interview
> "I treated prompts like code: versioned in git, evaluated against a golden set of ~N real cases. For each change I ran an offline A/B with the model and temperature pinned, 3 samples per case, graded with deterministic checks plus a rubric-based LLM judge that I calibrated against human labels. I compared variants with a paired bootstrap CI and only promoted a prompt if it beat baseline outside the noise without regressing cost or latency. Winners went to a canary behind a feature flag, where we tracked [metric]."

Be ready for follow-ups: *How big was your eval set? How did you know the judge was right? What effect size could you detect? What happened when B won on average but lost on a slice?*

## 6. Common mistakes
- Testing on 10–20 hand-picked examples and eyeballing.
- Changing prompt *and* model at the same time.
- One run per case at temperature > 0.
- Using the same examples to tune the prompt and to evaluate it (overfitting).
- Reporting only an average; hiding the slice where B got worse.
- Trusting an uncalibrated LLM judge.

## Sources (verified by coordinator)
- LLM-judge biases (position, verbosity, self-enhancement) and the swap-order fix; GPT-4 judges agree with humans >80% of the time, about the same as humans agree with each other: Zheng et al. 2023, *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena*. https://arxiv.org/abs/2306.05685
- Report standard errors, use clustered SEs for grouped questions (they can be more than 3x the naive SE), use paired differences when comparing two systems on the same questions, and run a power analysis to size the eval: Miller (Anthropic) 2024, *Adding Error Bars to Evals*. https://arxiv.org/abs/2411.00640 · https://www.anthropic.com/research/statistical-approach-to-model-evals

## 7. Tools you'd name in an interview (Nov 2026)
| Stage | Tool | What it does for A/B |
|---|---|---|
| Offline | **promptfoo** (open source, CLI) | Runs prompt variants × test cases side by side from a YAML config; works in CI |
| Offline + online | **LangSmith**, **Langfuse** (open source), **Braintrust** | Hold the datasets, run experiments, compare variants, judge pairs; score live traces |
| Offline | **Anthropic Console Evaluate tab** | Runs prompt versions side by side on test cases, with grading |
| Online | **GrowthBook** (open source), **LaunchDarkly AI Configs**, **Statsig** | Feature flags that assign users to variants, roll changes out gradually and roll them back |

Heads-up: **OpenAI Evals** goes read-only on 31 Oct 2026 and shuts down on 30 Nov 2026 ([OpenAI deprecations](https://developers.openai.com/api/docs/deprecations)). Don't list it as your current tool.

On online metrics: pick one primary metric. With 5 metrics each tested at α = 0.05, there's about a 23% chance at least one shows a false win (1 − 0.95⁵).

Full reading notes, with sources: `notes/reading-ab-prompt-testing.md` (written by the reader; vendor claims are marked where they're unverified).
