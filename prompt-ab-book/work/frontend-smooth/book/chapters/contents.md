# Testing Prompts Like a Pro

> A/B testing for AI engineers, one page at a time

<!--
HOW THIS FILE WORKS
- This list IS the book's order. The book reads it top to bottom.
- Each entry: a numbered line with [Chapter name](file.md), then one indented line describing what the chapter teaches.
- To add a chapter: write the .md file, read the descriptions below, and insert its entry
  right after the chapter it builds on. Numbers don't need to be correct; order of lines is what counts.
- The flow of the book: the problem → a fair setup → test data → grading → noise → decision → production → career.
-->

1. [Why test prompts, and why A/B?](why-test-prompts.md)
   The problem: prompts are fragile and outputs are random, so a few examples prove nothing. What A/B testing is, offline vs online, and the three levels of evaluation.

2. [How A/B testing works, and what changes for LLMs](how-ab-testing-works.md)
   Classic A/B testing from scratch: random assignment, the six ingredients, p-values, confidence intervals, power, common traps. Then the five ways LLM prompts differ.

3. [Anatomy of a prompt experiment](prompt-experiment-anatomy.md)
   Turning a test into a reproducible experiment: what to vary, lock and record. Versioning prompts, pinning the model, the experiment file and the run record.

4. [Hands-on: a minimal A/B harness in Python](python-ab-harness.md)
   Build and run a ~100-line harness with real API calls: job list, parallel calls, grading, saved run records, resume, summary. Includes a free mock run and a smoke-test habit.

5. [Error analysis: read your outputs first](error-analysis.md)
   What to do after you get a score: read failures, write notes, group them into categories, count them, find where each failure lives (prompt, model, grader or dataset), and fix the biggest one. Includes a helper script.

6. [Building the eval dataset](eval-dataset.md)
   Where cases come from, how to label them, tagging slices, how many you need, the dev/test split, leakage, versioning. Includes a dataset helper script.

7. [Evaluation methods: what exists and when to use which](eval-methods.md)
   The toolbox: code checks, classification metrics and confusion matrices, similarity metrics, LLM judges, human review and user signals, matched to task types. Includes more graders and a classification report.

8. [LLM-as-judge in depth, and validating the judge](llm-as-judge.md)
   Writing a judge (one criterion, pass/fail with critique), its biases, and the key skill: proving it is right with human labels, TPR/TNR, kappa, a dev/test split and re-validation. Includes judge and validation scripts.

9. [Did it improve? The statistics of comparing A and B](did-it-improve.md)
   Paired comparison by case, why repeated runs must be clustered, confidence intervals, McNemar, minimum gain, sample size for paired data, multiple comparisons, peeking. Includes a comparison script and simulations.

10. [Frameworks: the same experiment in promptfoo, in CI, and the other tools](frameworks.md)
   Your Chapter 4 experiment as a promptfoo config, running it on every change in CI (with the gotchas found in testing), then a vendor-neutral look at LangSmith, Langfuse, Braintrust and the Anthropic Console, and how to choose.

11. [Online A/B: shadow, canary, split](online-ab.md)
   Rolling a prompt out safely: shadow, canary, a 50/50 test randomised by user, metrics and guardrails, sample size and duration, sample ratio mismatch, reading the result, and what to do when offline and online disagree. Includes online-test tools.

12. [Beyond single prompts: a short brief](beyond-single-prompts.md)
   A map for RAG, agents and multi-turn systems: split the system into parts, grade retrieval and answers, check outcomes not words, repeat trials (pass@k vs pass^k), find the first failure. A brief; a full treatment needs its own book.

13. [The interview practice system](practice-system.md)
   Turning the book into interview skill: what interviews seem to test (and how good the evidence is), the shape of a strong answer, a practice loop, a two-week plan, a mock-interview protocol with an LLM interviewer, and how to defend your own project honestly.

14. [Question bank](question-bank.md)
   54 interview-style questions with chapter pointers, a Weak/OK/Strong rubric and follow-up probes, grouped by theme, with a self-scoring method and tracking sheet.

15. [System-design prompts: designing an eval system](system-design-prompts.md)
   A framework and timing guide for 'design the eval for X', then five worked prompts: support bot, summariser, RAG over documents, a refunds agent and a model migration, each with rubric, pitfalls and probes.

16. [Coding drills](coding-drills.md)
   Four timed drills with tested starters and reference solutions: an async harness with caching, a paired case-level bootstrap, judge-agreement metrics, and structured-output validation. Tests tell you whether your own solution is right.
