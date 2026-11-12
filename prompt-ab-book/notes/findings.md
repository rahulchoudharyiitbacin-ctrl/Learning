# Findings: A/B prompt testing lesson (2026-11-12)

**Established (verified)**
- Paired comparison on the same eval set is the correct design. In the simulated demo it shrank the 95% CI from ±4.4 to ±3.2 pts (../work/ab-prompt-test/output.txt). Anthropic's "Adding Error Bars to Evals" (arXiv 2411.00640) also recommends paired comparison.
- LLM judges show position, verbosity and self-preference bias. Mitigations: swap the answer order, use a different judge model, calibrate against human labels (Zheng et al., arXiv 2306.05685).
- A 400-case eval can only reliably detect gains of about 4+ points. Detecting 2 points needs about 2,100 cases (demo power calculation).
- OpenAI Evals shuts down on 30 Nov 2026 (OpenAI deprecations page).

**Uncertain**
- The offline -> shadow -> canary -> split sequence has only one vendor source (GrowthBook). It is still standard practice.
- Braintrust and Statsig feature details were seen only in search summaries.
- Demo data is simulated. Results with a real model and grader will differ.

**Try next**
- Rebuild the demo on real calls: 2 prompts × 100 real cases × 3 runs with Haiku 5.5, graded by code checks.
