# Plan: teach professional A/B prompt testing

Goal: a lesson Rahul can use to explain (and actually do) "A/B testing for prompts" as on his resume.

Sub-problems
1. Industry practice & tooling (reading) -> `reader` (Sonnet 5.5). Offline evals vs online A/B, tools (promptfoo, LangSmith, Braintrust, etc.), LLM-as-judge pitfalls. Sources required.
2. Runnable demo (small; coordinator does it): simulated paired offline eval of prompt A vs B, with McNemar test, paired bootstrap CI, sample-size estimate. `../work/ab-prompt-test/`.
3. Synthesis (coordinator): `notes/ab-prompt-testing-lesson.md` + findings.

No research-worker (Opus) needed: the stats demo is a few tool calls.
