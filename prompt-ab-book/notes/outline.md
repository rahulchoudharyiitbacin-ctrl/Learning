# Book outline (revised 2026-11-12 after the Opus review) and status

Focus: how to do A/B testing for prompts, how to evaluate, which frameworks, what to say in interviews. Rahul has an API key and is comfortable with Python, so hands-on chapters use real model calls. promptfoo is the main framework walkthrough. Cover both LLM-app and evals-engineer roles. Each chapter ends with a "Read more" page; claims name their sources (see `references.md`). The full review is in `review-opus.md`.

## Decisions (Rahul, 2026-11-12)

- **Adopted:** harness moved up to Chapter 4 with a lab page in every chapter from Chapter 3 on (M2); error analysis moved before methods and judges (M3); judge validation with real metrics (M5); interview chapter becomes a practice system (M6); statistics fixes (M7), including the Chapter 1-3 accuracy fixes.
- **Not a full chapter:** RAG, agent and multi-turn evals. Only a short brief (3-4 pages) that points to a future separate book (M4 narrowed).
- **Deferred until the book is done:** the portfolio project (M1). Plan: assemble it from the chapter labs and update the book with the real numbers it produces.
- **Not yet decided:** SHOULD and NICE items in `review-opus.md` (monitoring and drift, CI gating, cost/latency example, safety evals, debugging drills, STAR stories, harder checkpoints, appendix ideas). Discuss before adding.

## Status

All 16 chapters written and published (2026-11-13). Next: the portfolio project (deferred by the user until the book is done), then decide on the SHOULD/NICE items. No live API call has been made for any code yet.

## Chapters

| # | Chapter | Status |
|---|---|---|
| 1 | Why test prompts, and why A/B | **Written**, accuracy fixes applied |
| 2 | How A/B testing works, and what changes for LLMs | **Written**, accuracy fixes applied, adds "online is randomised, offline is paired" |
| 3 | Anatomy of a prompt experiment (variables, versioning, config) | **Written**, accuracy fixes applied, lab page added |
| 4 | Hands-on: a minimal A/B harness in Python (real API calls); runs the Chapter 3 experiment file | **Written**; code in `work/harness/`, tested in mock mode and against the real SDK with a fake server; the first real-API run is the learner's lab |
| 5 | Error analysis: read your outputs first (open coding, categories, counting); how criteria emerge | **Written**; helper `work/harness/error_analysis.py` tested on mock records |
| 6 | Building the eval dataset | **Written** (replaced old "The exam paper"); helper `work/harness/dataset_tools.py` tested incl. failure cases |
| 7 | Evaluation methods: what exists, when to use which, by task type | **Written**; `graders.py` + `test_graders.py` + `classification_report.py` tested (hand-computed math checks) |
| 8 | LLM-as-judge in depth, and validating the judge (TPR/TNR, kappa, dev/test split, re-validation, criteria drift) | **Written** by an Opus worker (replaced old "Who marks the answers?"); `judge.py`, `judge_validation.py`, `test_judge.py`; real-SDK path tested only against a fake server |
| 9 | Did it improve? Paired comparison, clustering by case, confidence intervals, minimum gain and sample size, multiple comparisons | **Written** by an Opus worker (replaced old "Luck vs skill" and "Reading the verdict"); `compare_runs.py`, `sample_size.py`, `test_stats.py`; simulations verify CI coverage |
| 10 | Frameworks: the same experiment in promptfoo (and in CI), then LangSmith / Langfuse / Braintrust | **Written** by an Opus worker; `work/promptfoo/`, `work/ci-example/`; tested offline (promptfoo 0.125.1 with fake providers), CI gate logic replayed locally; no real API or GitHub run |
| 11 | Online A/B: shadow, canary, split, metrics, guardrails | **Written** (replaced old "Going live"); `online_tools.py` + `test_online.py` (hand-checked values, power and false-positive simulations) |
| 12 | Beyond single prompts: a short brief on RAG, agent and multi-turn evals | **Written** (11 pages, a brief; points to a future separate book); `rag_metrics.py` + `test_rag_metrics.py` |
| 13 | Interview practice system: study plan, answer shape, mock-interview protocol and tool, defending your own project | **Written** (replaced old "Saying it in an interview"); `mock_interview.py` tested |
| 14 | Question bank (48-60 questions with rubrics and probes) | **Written** by an Opus worker: 54 questions, 32 pages; numbers recomputed by the coordinator |
| 15 | System-design prompts (5 worked prompts) | **Written** by an Opus worker: 26 pages, 3 diagrams; numbers recomputed (`work/system-design-prompts/sd_numbers.py`) |
| 16 | Coding drills (4 timed drills with tested solutions in `work/drills/`) | **Written** by an Opus worker: 27 pages; all solutions pass, all starters fail, 26 mutants caught (rerun by coordinator) |

Every chapter from 3 on has a **Lab** page (something the learner does), before the checkpoint.

**Old chapters still in the book:** none. They get rewritten or removed as their new chapters are written. `contents.md` only lists files that exist.
