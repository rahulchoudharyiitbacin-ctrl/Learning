# Chapter 15 sources (fetched 2026-11-13)

Each entry: URL, what the page says (paraphrased; short quotes only), what the chapter uses it for.

## Opened at the source

- **Anthropic, Demystifying evals for AI agents** : https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
  Says: "20-50 simple tasks drawn from real failures is a great start"; transcript = complete record of a trial, outcome = final state in the environment (flight-booking example); requiring a specific tool-call sequence is "too rigid", better to "grade what the agent produced, not the path it took"; pass@k (at least one of k) vs pass^k (all k succeed), pass^k for customer-facing consistency; each trial isolated from a clean environment, shared state causes correlated failures; capability evals start at a low pass rate, regression evals near 100%, capability tasks can "graduate"; read transcripts so failures "seem fair"; conversational agents often need a second LLM to simulate the user, success checked by state check + turn limit + tone rubric; reference solution proves a task is solvable and graders work; an example where a model "failed" an eval as written but found a better solution.
  Used: Prompt 4 (tasks, slices, isolation, graders, pass^k, suites, probe 2); Prompt 1 tone/escalation framing.

- **Husain, Frequently Asked Questions About AI Evals** : https://hamel.dev/blog/posts/evals-faq/ (read in two parts)
  Says: generic metrics such as helpfulness "create false confidence" as quality measures; guardrails are inline checks in the request path, evaluators measure qualities rules cannot; CI evals favour deterministic checks, production tracks intervals; agents: end-to-end success first, then step-level checks (tool choice, parameter extraction); transition matrix "rows represent the last successful state and columns represent where the first failure occurred"; RAG: retrieval is a search problem (IR metrics), generation needs judges validated on human labels; warns against switching models without evidence from error analysis. Week-1 numbers (about 100 traces, at least the first 30 annotated yourself) and synthetic query-document pairs were already verified for Chapters 5, 6 and 12 (see references.md).
  Used: framework week 1, Prompt 1 pitfall, Prompt 3 retrieval, Prompt 4 transition matrix.

- **OpenAI, Evaluation best practices** : https://developers.openai.com/api/docs/guides/evaluation-best-practices
  Says: single-agent evals for tool selection ("select the correct tool") and data precision ("calls the tool with the correct arguments"); continuous evaluation on every change; calibrate judges with human feedback; control for length bias; process: define objective, collect dataset, define metrics, run and compare, continuously evaluate. Nothing on model migration.
  Used: Prompt 4 diagnostics (tool selection, argument accuracy).

- **Eugene Yan, Task-Specific LLM Evals that Do & Don't Work** : https://eugeneyan.com/writing/evals/
  Says: summarisation factual consistency via NLI, source document as premise and summary as hypothesis, contradiction probability as the signal; relevance via finetuned NLI or reward model; length checks are straightforward; author finds ROUGE/METEOR, BERTScore and G-Eval unreliable or impractical.
  Used: Prompt 2 methods (NLI alternative, ROUGE as a weak signal).

- **Anthropic, Model deprecations** : https://platform.claude.com/docs/en/about-claude/model-deprecations
  Says: at least 60 days' notice before retirement for publicly released models; test applications with newer models well before the retirement date; requests to retired models fail; `temperature`, `top_p`, `top_k` removed in API version 2026-10-21 (400 error).
  Used: Prompt 5 clarifying questions.

- **Calibrd, AI engineer interview prep** : https://www.calibrd.com/interview-prep/ai-engineer (prep site)
  Says: system-design Q "Design the evaluation system for an LLM feature that summarises customer calls"; technical Q "Our prompt got 12% worse on the internal test set after a model upgrade"; practice prompt on ship and rollback criteria for summarisation; questions are "Representative of what companies ask at this level", not reported.
  Used: chapter opening, Prompt 2 wording (adapted), Prompt 5 teacher's note.

## Numbers and where they come from

All computed with the book's own helpers by `/Users/rahulchoudhary/Desktop/Experiment/work/system-design-prompts/sd_numbers.py`:
- `online_tools.users_per_arm(0.10, 0.01)` = 14,751 (matches Chapter 11, sanity check); `users_per_arm(0.40, 0.02)` = **9,493** per arm (Prompt 1); 2 x 9,493 / 2,000 a day = 9.5 days, so two weeks.
- `sample_size.n_paired_binary(0.10, 0.05)` = **312** (Prompt 2; same as Chapter 9's table).
- Paired no-worse-than sizing, true difference 0, 95%/80%: (1.96 + 0.84)^2 x 0.10 / 0.02^2 = **1,962**, "about 2,000" (Prompt 5). Smallest margin ruled out with 400 cases: 0.044 at 10% disagreement, 0.063 at 20%, so "4 to 5 points" (stated for the 10% case; at 20% disagreement it would be about 6).
- pass^3 at 0.75 = 0.422, at 0.9 = 0.729 (Prompt 4).

## Design choices that are the book's own (not sourced)

The 40-minute timing split, the 0/1/2 self-scoring, the support-bot baseline (40%, 2,000 users a day), the summary format (three parts, 120 words), the refund shadow mode (agent proposes, humans decide), the permissions zero-failure gate, the −2-point no-worse-than margin. All are labelled as assumptions or examples in the text.

## Left out (not verified)

- Specific "good" TPR/TNR thresholds for judges (no primary source; the chapter says "a bar set in advance").
- Claims about how often candidates forget particular steps (removed).
- Jason Liu's "There Are Only 6 RAG Evals" was not re-opened; the chapter only refers back to Chapter 12's three relationships.
- Third-party claims about which companies ask which system-design prompts (review-opus.md A.2 lists them as unverified).
