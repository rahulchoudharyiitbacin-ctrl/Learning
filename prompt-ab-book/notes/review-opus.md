# Review: "Testing Prompts Like a Pro" as interview preparation

Reviewer stance: skeptical senior interviewer for AI Engineer (LLM application) and Evals Engineer roles.
Date: 2026-11-12. Scope: outline, contents, chapters 1-3 (new), old drafts (skimmed), references.md.
No book files were modified.

---

## (A) Evidence on what interviews test

### A.1 Sources I actually opened

Credibility scale: **High** = employer's own posting, primary research, or a recognised eval educator's own writing. **Medium** = practitioner/recruiter content with a named author and a clear incentive, or summaries of primary material. **Low** = anonymous prep sites or repos with no sourcing. Prep-site and repo content describes what companies *reportedly* ask; none of it is a first-hand candidate report.

| # | URL (opened) | Type | Credibility | What it contributes |
|---|---|---|---|---|
| 1 | https://job-boards.greenhouse.io/anthropic/jobs/5198255008 | Job description (Anthropic, Research Engineer, Post-Training Model Evaluations) | High | Requirements: designed/ran/analysed ML evals at scale, "measurement quality", investigate production regressions, dashboards and alerts, strong Python. Nice-to-have: statistics and experimental design, robust eval metrics. |
| 2 | https://builtin.com/job/ai-research-engineer-enterprise-evaluations/7684106 | Job description (Scale AI, Evals Engineer, Applied AI; mirror, marked removed May 2026) | High-Medium (mirror of employer text) | Gold human-rated datasets and expert rubrics, annotator feedback loops, LLM-as-judge autoraters for agent outputs, eval pipelines, statistical analysis, annotator guidelines, observability for agents. |
| 3 | https://hamel.dev/blog/posts/evals/ | Educator (Husain) | High | Three levels; Level 3 A/B "usually only appropriate for more mature products"; unit tests on every change; trace logging; judge-human agreement. |
| 4 | https://hamel.dev/blog/posts/llm-judge/ | Educator (Husain) | High | Judge-building procedure: domain expert, binary pass/fail with critiques, iterate, measure with TPR/TNR, not raw agreement. |
| 5 | https://hamel.dev/blog/posts/evals-faq/ | Educator (Husain and Shankar) | High | Topic list of what practitioners actually wrestle with: error analysis (open/axial coding), binary vs Likert, judge alignment, RAG, agents, multi-turn, CI vs monitoring, synthetic data, guardrails vs evaluators. |
| 6 | https://ai.hamel.dev/eval-course | Educator course page | High (for syllabus) | Analyze-Measure-Improve, error analysis first, synthetic data, custom evaluators, RAG, agents, multi-turn. |
| 7 | https://eugeneyan.com/writing/product-evals/ | Educator (Yan, Nov 2025) | High | Label small set, align evaluator (precision/recall on fail class, Cohen's kappa, dev/held-out split), run harness on every config change. |
| 8 | https://eugeneyan.com/writing/evals/ | Educator (Yan, Mar 2024) | High | Task-specific metrics: classification (P/R, ROC-AUC), summarisation (NLI factual consistency), translation, toxicity, copyright. |
| 9 | https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents | Company engineering blog (Anthropic) | High | Agent evals: code/model/human graders, pass@k vs pass^k, capability vs regression suites, outcome vs transcript grading, 20-50 tasks to start, multiple trials, environment isolation, saturation. |
| 10 | https://developers.openai.com/api/docs/guides/evaluation-best-practices | Company docs (OpenAI) | High | Architecture-specific evals (single-turn, workflow, single-agent tool selection/args, multi-agent handoffs), continuous eval, calibrate judges, control for length bias. |
| 11 | https://arxiv.org/abs/2404.12272 | Paper (Shankar et al., "Who Validates the Validators?") | High | "Criteria drift": grading outputs changes the criteria; criteria cannot be fully fixed in advance. |
| 12 | https://newsletter.pragmaticengineer.com/p/evals | Practitioner (Orosz and Husain, Dec 2025), partly paywalled | High (visible part only) | Review 100+ traces, cluster into 5-10 failure themes, code evals for deterministic failures, judges for subjective ones, data partitioning, TPR/TNR, CI/CD. |
| 13 | https://www.calibrd.com/interview-prep/ai-engineer | Prep site | Medium-Low (says "representative", not reported) | Loop shape (screen, build/take-home, AI system design, eval + product sense, behavioural); eval scenario questions (12% drop after model upgrade; design eval for call summarisation; ship/rollback criteria). |
| 14 | https://www.kore1.com/ai-engineer-interview-questions-2026/ | Recruiter blog (named author, paid on placement) | Medium | Questions: "How do you know your AI feature is good? ... Your number."; token bill tripled; prompt tweak helped one type and hurt another; what you log. Red flags: "you can tell when it's working". |
| 15 | https://github.com/bicced/ai-engineer-interview-handbook/blob/main/topics/06-evals.md | Community repo | Low-Medium (author-written questions, no reports) | Error analysis, JSON-extraction metric, RAG retrieval vs generation, judge bias, TPR/TNR, pass^k, overfitting to eval set. |
| 16 | https://github.com/keshav-07/awesome-ai-engineer-interview | Community repo by a job-matching company | Low (claims provenance labels; I saw none on the landing page) | Loop: coding, take-home RAG/agent app with written eval section, AI system design ("eval pipeline" is one of 10 worked designs), behavioural incl. safety debate at Anthropic. |
| 17 | https://www.techinterview.org/post/3233475313/interviewing-ai-eval-engineering-roles-2026/?format=md | Prep site, unsourced | Low | Evals-engineer loop: Python + eval design screen, 2-4 h take-home eval harness with LLM grading, onsite eval system design and eval data design; "95% pass rate but users complain"; "build a 500-item eval set from 100K interactions"; contamination/leakage; async harness design. |

Also opened for accuracy checks (Section E): arXiv 2310.11324 (Sclar), arXiv 2408.04667 abstract and HTML v5 (Atil), Anthropic prompt-engineering overview and develop-tests pages, OpenAI prompt-engineering guide, Cambridge ToC page for Kohavi et al., Statsig and GrowthBook articles.

### A.2 UNVERIFIED (could not open, or seen only in search snippets)

- https://openai.com/interview-guide/ : HTTP 403. A search summary says OpenAI uses a "skills-based assessment (pair coding, take-home project, or technical test - varies by team)". **UNVERIFIED.**
- Anthropic Forward Deployed / Applied AI Engineer postings (e.g. greenhouse job 4985877008): page rendered only the job index. Search snippets say they ask for "prompt engineering, agent development, evaluation frameworks". **UNVERIFIED.**
- https://www.techinterview.org/post/3233476828/llm-eval-prompt-interview-questions/ ("the eval round is the new system design interview"), https://tianpan.co/blog/2026-04-27-ai-engineer-interview-eval-design, https://prachub.com/resources/llm-evaluation-interview-questions-evals-llm-as-judge-drift-and-production-quality : search snippets only. **UNVERIFIED.**
- Kohavi Ch 1 Bing headline example (12% revenue lift from a small change; "small changes can have a big impact"): confirmed only via search summaries of the Cambridge excerpt and the HBR article. **Secondary.**

No first-hand candidate write-up (Reddit/HN/blog "I interviewed at X") was found in my searches. That is a real limitation of this evidence base.

### A.3 Question types that recur (synthesis)

| Type | Concrete examples seen | Sources |
|---|---|---|
| **Conceptual: why evals / offline vs online** | "Why are evals critical vs deterministic software?"; offline evals miss novel inputs, online tracks task completion/escalation | 3, 13, 15, 17 |
| **Conceptual: statistics** | non-determinism, significance, confidence intervals, how many examples, "is the difference real?" | 1 (nice-to-have), 2, 7, 17 |
| **Conceptual: judges** | judge biases (position, verbosity, self-preference); "how do you know the judge is any good?"; binary vs Likert; TPR/TNR, kappa | 4, 5, 7, 10, 12, 15 |
| **Conceptual: task-specific metrics** | classification P/R and ROC-AUC; summarisation faithfulness; RAG retrieval (recall@k, MRR, nDCG) vs generation (faithfulness, relevance); JSON extraction metric | 8, 10, 15 |
| **Conceptual: agents** | pass@k vs pass^k; outcome vs trajectory grading; tool selection/argument accuracy; capability vs regression suites | 9, 10, 15, 16 |
| **Error analysis** | where to start with a new feature: read traces, open/axial coding, failure taxonomy | 5, 6, 12, 15 |
| **Debugging scenarios** | prompt drops 12% after model upgrade; 95% pass but users complain; token bill tripled; retrieval fine but answer wrong a third of the time; prompt tweak helped one type, hurt another | 13, 14, 17 |
| **Eval data design** | build a 500-item set from 100K interactions; golden set composition; who labels; slices (typical, edge, adversarial, regression); contamination/leakage | 2, 13, 17 |
| **Coding (live)** | Python exercise; eval harness API, async/parallel runs with caching; pandas/SQL analysis | 13, 16, 17 |
| **Take-home** | small RAG/agent/classifier app plus an eval script that prints accuracy and cost; README with trade-offs; review conversation where you defend every line | 13, 14, 16, 17 |
| **System design** | "Design the eval system for call summarisation: golden set, labellers, what blocks a release"; doc Q&A over millions of pages incl. evals and cost per query; tool-using support agent and how it is tested; eval pipeline with CI gates | 13, 16, 17 |
| **Production / monitoring** | CI vs production monitoring; what you log; dashboards and alerts; investigate regressions | 1, 5, 14 |
| **Behavioural / resume deep-dive** | "How do you know your AI feature is good? Your number."; explain business impact; red flag "you can tell when it's working"; safety debate (Anthropic) | 14, 16 |
| **Evals-engineer specific** | measurement quality, eval saturation, annotator guidelines and inter-annotator agreement, autoraters for agents, regression triage during training | 1, 2, 9 |

Takeaway: interviews for both roles centre on **designing and defending an eval system for a realistic product (often RAG or an agent)**, **validating LLM judges against humans**, **error analysis**, and **debugging regressions**, tested through system-design conversations, a take-home with an eval script, and a resume deep-dive. Classical A/B statistics appears, but as one supporting skill, not the centre.

---

## (B) Coverage map

Legend: **Full** = planned chapter should cover it adequately if written as described; **Partial** = mentioned but too thin for interview depth; **None** = not planned.

| Question type / topic | Planned chapter | Coverage | What is missing |
|---|---|---|---|
| Why test prompts; offline vs online | 1, 2 | Full | Hamel's point that online A/B is for mature products; criteria drift (you often discover criteria by reading outputs). |
| Classic A/B mechanics (randomisation, OEC, guardrails, SRM, peeking) | 2, 11 | Full | Name SRM explicitly; Kohavi Ch 2 is the right citation for the design checklist. |
| p-values, CIs, power, MDE, sample size | 2 (intro), 8 | Partial | Correct p-value wording; MDE as a design input; **clustered standard errors when running each case k times** (Miller 2024); multiple comparisons across variants and slices; paired tests (McNemar / paired bootstrap) with code. |
| Non-determinism and repeated runs | 2, 3, 8 | Partial | Why (batching, serving infra), how many runs, how to aggregate; pass@k vs pass^k. |
| Prompt versioning, reproducibility, model pinning | 3 | Full | Model-upgrade migration as a scenario ("12% drop after upgrade"). |
| Building the eval dataset | 4 | Partial | Sampling from production logs (stratified), synthetic data generation and its limits, contamination/leakage, dataset staleness, balancing fail cases (Yan: 50-100 fails in 200+), labelling guidelines. |
| Error analysis (open/axial coding, failure taxonomy) | 10 | **Partial and late** | This is the most-cited practitioner skill and comes first in Husain/Shankar's workflow. It is planned for Ch 10, after methods, judges and stats. |
| Evaluation methods by task (exact match, P/R, ROC-AUC, NLI, similarity metrics, structured-output validation) | 5 | Partial | Needs an explicit per-task table and code; structured output (schema validity, field-level accuracy) must be a worked case since it is a common take-home. |
| **RAG evaluation** (retrieval recall@k/MRR/nDCG vs generation faithfulness/relevance; Ragas) | 5, 9 (Ragas mention) | **Partial, thin** | Component vs end-to-end evals, building labelled query-doc pairs, "retrieval fine but answer wrong" debugging. Very common system-design topic. |
| **Agent evaluation** (tool selection/args, trajectory vs outcome, pass^k, environment isolation) | None | **None** | Needs its own chapter or half-chapter; Anthropic and OpenAI docs both cover it. |
| **Multi-turn / conversation evals** | None | **None** | Simulated users, conversation-level vs turn-level grading, handoff detection. |
| LLM-as-judge: biases and mitigations | 6 | Full (planned) | — |
| **Building a judge and measuring agreement** (TPR/TNR, precision/recall on fail class, Cohen's kappa, dev/test split for the judge, re-validation when anything changes) | 6 | Partial | Old draft says "check how often the judge agrees", i.e. raw agreement, which Husain explicitly warns is misleading for rare failures. Needs metrics, code, and the held-out split. |
| Human annotation (guidelines, inter-annotator agreement, single domain expert) | 6 | Partial | Evals-engineer roles (Scale) ask for annotator guidelines explicitly. |
| Hands-on harness (async, caching, retries, cost logging) | 7 | Full (planned) | Should come much earlier; should include caching, concurrency, rate limits, cost per query. |
| Frameworks (promptfoo, LangSmith, Langfuse, Braintrust) | 9 | Full | Keep tool-agnostic interview framing; interviewers care about why, not which. |
| **Regression testing in CI** (gates, thresholds, flaky-test handling with stochastic outputs) | 10 | Partial | Needs a worked CI config with a pass threshold and how to avoid flaky gates; capability vs regression suites. |
| Online A/B: shadow, canary, split, guardrails | 11 | Full | Interleaving / implicit feedback signals; user-level randomisation (GrowthBook). |
| **Drift / production monitoring** (input drift, model updates, online evaluators on sampled traces, alerting) | 11 (implicitly) | **Partial** | No planned treatment of continuous monitoring separate from A/B. JD #1 asks for dashboards and alerts. |
| **Cost / latency trade-offs** (cost-quality frontier, model routing, caching, cheaper model + better prompt) | 2, 3 (as guardrails) | Partial | Only listed as guardrails. "Token bill tripled" type questions and "pick a model" trade-offs need a worked example. |
| **Safety / red-team evals** (jailbreaks, prompt injection, refusal rate, harmful output, adversarial sets) | None | **None** | Relevant for both roles and especially Anthropic loops. |
| Benchmarks vs product evals; saturation; contamination | None | None | Evals-engineer interviews ask this; one section would do. |
| System design ("design an eval system for X") | 12 | Partial | One prompt in Ch 12 is not enough; needs 4-6 worked designs with a rubric. |
| Coding drills (live) | 7 | Partial | No timed drills. |
| Take-home | None | None | No take-home practice or portfolio project planned. |
| Behavioural / resume deep-dive | 12 | Partial | Old draft offers a polished resume story; it must be built from the learner's real experiment, with numbers. |

---

## (C) Teaching-approach assessment

**What works.**
- Chapters 1-3 are clear, short, well-paced and mostly well-sourced. The "vary / lock / record" frame (Ch 3), the run-record JSON and the experiment YAML are exactly the habits interviewers probe for.
- Every chapter ending in a model interview answer is a good idea: it forces the author to compress each idea into something sayable.

**What does not get the learner to interview-ready.**
1. **Checkpoints are recall, interviews are generation.** Checkpoint questions are answerable from the page just read, with the answer one click away. Interview questions are open-ended ("design the eval for X"), followed by 3-5 probing follow-ups. Reading plus recall builds recognition, not the ability to produce a design under pressure.
2. **Model answers invite memorisation.** A 60-word polished answer is easy to recite and easy for an interviewer to puncture ("why three runs?", "how did you compute the CI with repeated runs?", "what was your judge's TNR?"). The book needs follow-up chains, not just first answers.
3. **The learner's resume line is the main risk.** "A/B testing for prompts" will be deep-dived. The old interview chapter supplies a story ("rubric-based LLM judge that I checked against human labels... paired bootstrap... canary") that the learner may not have done. The fix is a real project producing real numbers they can defend.
4. **Hands-on comes too late.** The harness is Ch 7 of 12. With a real API key available, every chapter from Ch 3 onward should end with a lab that runs on the same project.
5. **Sequence fights the practitioner workflow.** Husain/Shankar, Yan and the Pragmatic Engineer piece all start with *looking at data / error analysis*, then building evaluators, then measuring. The book does methods (5) and judges (6) before error analysis (10). Interviewers who know this literature will ask "where do you start?" and expect "read traces, build a failure taxonomy".
6. **Scope is offline prompt comparison; interviews are about systems.** The book's centre of gravity (two prompts, one dataset, one metric) is a sub-case of "evaluate an LLM system". RAG and agent evals, which dominate system-design rounds, are thin or absent.

**Suggested order (12 chapters become 14 plus a practice section):**

1. Why test prompts (keep)
2. How A/B testing works (keep; fix stats wording)
3. Anatomy of an experiment (keep)
4. **Hands-on harness v0** (moved from 7; real calls, run record, cost logging)
5. **Look at your data: error analysis** (moved from 10, first half)
6. Building the eval dataset (incl. sampling, synthetic data, leakage)
7. Evaluation methods by task, incl. structured output (code checks first)
8. LLM-as-judge and judge validation (TPR/TNR, kappa, held-out split)
9. Did it improve? Statistics (paired, clustered, power, multiple comparisons)
10. **Evaluating RAG, agents and multi-turn systems** (new)
11. Frameworks and CI regression gates (merge planned 9 and second half of 10)
12. Online A/B, monitoring and drift (expand 11)
13. **Safety, red-team and robustness evals** (new, can be short)
14. Interview playbook (question bank, system design, behavioural)
- **Practice section** (new, parallel track): drills, mock interviews, portfolio project.

---

## (D) Recommended changes

### MUST

| # | Change | Reason |
|---|---|---|
| M1 | **Portfolio project as the spine of the book.** One real task (e.g. support-ticket triage with structured output, or small RAG Q&A), ~200 cases, two prompt variants, real API calls, saved run records, validated judge, paired CI, promptfoo config running in CI, one-page write-up in a public repo. Each chapter adds one piece. | Converts the resume claim into something defensible with real numbers; take-homes look exactly like this (sources 13, 14, 16, 17). |
| M2 | **Move the harness to Ch 4 and add a lab to every chapter from Ch 3 on.** | Learner has an API key and Python; hands-on is the cheapest way to make the knowledge generative. |
| M3 | **Move error analysis before methods and judges** (open coding, axial coding, failure taxonomy, counting). | It is the first step in every credible practitioner source (3, 5, 6, 12) and a stock interview question ("where do you start?"). |
| M4 | **Add a chapter on evaluating RAG, agents and multi-turn systems.** Retrieval vs generation metrics; tool selection and argument accuracy; outcome vs trajectory grading; pass@k vs pass^k; environment isolation; simulated users. | Dominant system-design topic; currently None/Partial (sources 9, 10, 13, 15, 16). |
| M5 | **Judge validation with real metrics** in the judge chapter: TPR/TNR (or precision/recall on the fail class), Cohen's kappa, judge dev/test split, re-validation triggers, criteria drift. Replace "check how often the judge agrees". | "How do you know the judge is right?" is the most consistent follow-up across sources (4, 7, 12, 15). Raw agreement is explicitly warned against by Husain. |
| M6 | **Turn Ch 12 into a practice system:** a question bank of ~60 questions across the types in A.3, each with a 3-level scoring rubric (weak / OK / strong) and 3 follow-up probes; 5 worked system-design prompts (support bot, summarisation, RAG over docs, tool-using agent, model migration) with a rubric; 4 timed coding drills (async harness with caching; paired bootstrap with clustering by case; judge-agreement metrics from a labels CSV; schema validation and field-level accuracy); a mock-interview protocol using an LLM as interviewer with the rubric. | Reading + checkpoint recall does not transfer to open-ended rounds. |
| M7 | **Fix the statistics foundations** (see Section E): p-value wording; offline comparison is paired, not randomised; clustered SEs when running each case k times; multiple comparisons. | These are the exact questions interviewers use to separate real experience from buzzwords. |

### SHOULD

| # | Change | Reason |
|---|---|---|
| S1 | Add production monitoring and drift to the online chapter: sampled online evaluators, input distribution shift, model-update detection, alerts, feedback loops into the dataset. | JD #1 asks for dashboards, alerts, regression investigation; KORE1 asks "what do you log?". |
| S2 | CI regression gating chapter section: capability vs regression suites, thresholds, handling stochastic flakiness (repeat runs, tolerance bands), cost of CI evals. | Common follow-up; Anthropic agent-evals post. |
| S3 | Cost/latency trade-off worked example: quality vs cost frontier across 2-3 models and prompts; caching; routing. | "Token bill tripled" and "pick a model" questions. |
| S4 | Short safety/red-team chapter: prompt injection, jailbreak sets, refusal over/under rates as a guardrail pair, adversarial slices. | Relevant to both roles; Anthropic loops reportedly include safety discussion (source 16, low credibility). |
| S5 | Debugging-scenario drills ("12% drop after model upgrade", "95% pass but users complain", "retrieval fine but answers wrong") with model walk-throughs. | These appear across several sources (13, 14, 17) and test judgement, not recall. |
| S6 | Behavioural page built from the learner's own project: 3 STAR stories (a test that showed "not proven", a judge that disagreed with humans, a regression caught), each with a real number. Remove the template resume story or label it "only say this if you did it". | Resume deep-dives punish borrowed stories. |
| S7 | Make checkpoints harder: at least one "explain to an interviewer" or "what would you do if" question per chapter, answer hidden until the learner writes one; add spaced-review cards. | Moves from recognition to production. |

### NICE

| # | Change | Reason |
|---|---|---|
| N1 | Evals-engineer appendix: benchmark design, saturation, contamination detection, annotator guidelines and inter-annotator agreement, eval for training runs. | Covers the research-engineer flavour (JD #1, #2) without bloating the main path. |
| N2 | Pairwise preference evaluation (win rates, Bradley-Terry/Elo) as an alternative to absolute scoring. | Common in model comparison; OpenAI recommends pairwise or pass/fail judges. |
| N3 | One-page "glossary of terms interviewers use" (OEC, SRM, MDE, pass^k, TPR/TNR, kappa, faithfulness, golden set). | Fast review before an interview. |
| N4 | Factorial or ablation designs as an alternative to one-change-at-a-time. | Ch 3's ladder advice is fine for beginners but interviewers may ask about interactions. |

---

## (E) Accuracy issues in chapters 1-3

Verified at primary source (how):
1. **Sclar et al.** - opened https://arxiv.org/abs/2310.11324. Abstract: "performance differences of up to 76 accuracy points when evaluated using LLaMA-2-13B"; "Sensitivity remains even when increasing model size, the number of few-shot examples, or performing instruction tuning"; ICLR 2024 camera-ready. **Claim supported.**
2. **Atil et al.** - opened https://arxiv.org/abs/2408.04667 (v5, 2 Apr 2025) and the HTML v5. "accuracy variations up to 15% across naturally occurring runs", five LLMs, eight tasks, 10 runs; settings "temperature at 0, top-p at 1, and fix the seed"; models GPT-3.5 Turbo, GPT-4o, Llama-3-70B/8B-Instruct, Mixtral-8x7B, all behind APIs; a local Llama-3-8B run was deterministic. **Claim supported, with nuances below.**
3. **Husain three levels** - opened https://hamel.dev/blog/posts/evals/. Levels are "Unit Tests", "Model & Human Eval (this includes debugging)", "A/B testing"; Level 3 "usually only appropriate for more mature products". **Supported, with an omission below.**
4. **Kohavi chapter titles** - opened the Cambridge book page ToC. Ch 3 "Twyman's Law and Experimentation Trustworthiness" and Ch 7 "Metrics for Experimentation and the Overall Evaluation Criterion" match references.md and Ch 2's Read-more. Ch 15 and Ch 17 titles also match references.md. Ch 21 not visible (listing stopped at Ch 18), so references.md's "Secondary" label for SRM stays correct.
5. Also checked: Anthropic prompt-engineering overview (success criteria, ways to test, first draft: **supported**); Anthropic develop-tests ("Specific", "Measurable", "held-out test set" in the sentiment example: **supported**); OpenAI pinning snapshots (**supported**, exact quote matches); Statsig (peeking, stop rule, "updates under your feet", freeze: **supported**); GrowthBook "The treatment isn't a thing; it's a process." (**supported**; Ch 2 paraphrases it as a quote, see below).

### Issues found

| # | File : line | Quote | Problem | Severity | Suggested fix |
|---|---|---|---|---|---|
| E1 | how-ab-testing-works.md:55 | "A small p-value says 'very surprising', so the gap is probably real." | This is the very misreading the teacher's note on line 61 warns against. A p-value is P(data at least this extreme given no difference), not P(difference is real). Also omits "or bigger". | **High** (interview trap) | "If A and B were truly equal, how often would chance alone produce a gap at least this big? A small p-value means rarely, which is evidence against 'no difference'. It is not the probability that B is better." |
| E2 | how-ab-testing-works.md:26 and :17 ; why-test-prompts.md:39 | Unit "a test case"; "The key word is random"; "A/B testing is the discipline of controlling the second and third..." | Offline prompt comparison does not randomly assign cases to A or B; every case gets both. Its validity comes from **pairing** under identical conditions, and its inference is about **generalising from the test set to the input population**. Calling the test case the "unit of assignment" conflates the two designs. Interviewers with an experimentation background will notice. | **High** (conceptual) | Add a box: "Online A/B = randomised, between-subjects. Offline eval = paired, within-case. Randomness that matters offline is which cases you sampled and model run-to-run noise." |
| E3 | why-test-prompts.md:35 | "The examples you tried ... Can you control it? Yes: use a fixed, larger test set" | A fixed set removes the A-vs-B selection difference, but the set is still a sample; sampling error shrinks with size but never disappears, which is exactly what CIs in Ch 8 measure. "Yes" overclaims. Also missing a fourth source: **grader noise** (LLM judge variance), and serving-side drift. | Medium | "Partly: same fixed set for both reduces bias; a larger set reduces, but does not remove, sampling noise." Add grader noise row. |
| E4 | why-test-prompts.md:62 | "Most daily work is offline. Online confirms the win is real." | Online measures a different thing (user outcomes), and offline wins often do not transfer; it is not mere confirmation. Husain also says Level 3 is usually only for mature products, which the chapter omits. | Medium | "Online tells you whether the offline win moves real user outcomes. Many teams only reach this stage once the product is mature (Husain)." |
| E5 | why-test-prompts.md:68-78 | "Hamel Husain ... describes three levels"; "Teams climb the ladder: most changes are filtered out cheaply at levels 1 and 2, and only the promising ones reach level 3." | Level 2 name is "Model & Human Eval (includes debugging)". The funnel sentence is the author's interpretation, presented right after the attribution; Husain frames the levels by cadence and cost (unit tests on every change), not as a filter funnel. | Low | Use his label; mark the funnel as "In practice, ...". |
| E6 | why-test-prompts.md:19 | "took the same few-shot task ... On LLaMA-2-13B, accuracy differed by up to 76 points" | 76 is the **maximum** spread across many tasks, not typical. "the same few-shot task" suggests a single task study. Readers may quote 76 points as a general fact. | Low-Medium | "Across dozens of classification tasks, the spread between formats reached up to 76 points on one task with LLaMA-2-13B; typical spreads were smaller." (Check the paper body for the typical spread before printing.) |
| E7 | why-test-prompts.md:19 vs :132 | "Sclar et al. (2023, ICLR 2024)" vs Read more "Sclar et al. 2024" | Inconsistent year. | Low | Use "Sclar et al. (ICLR 2024)" in both. |
| E8 | how-ab-testing-works.md:96 and :125 | "Atil et al. (2024) tested five LLMs configured to be deterministic ... Accuracy still varied by up to 15% between runs, and no model was fully repeatable." / "Production systems still produce varying outputs" | Supported, but: (a) "up to 15%" is the maximum, the paper text says "5-15% differences on some tasks"; (b) all were hosted API models, and the authors' local Llama-3-8B run was deterministic, pointing at serving infrastructure, not the model; (c) the paper does not say clearly whether 15% is percentage points. | Low-Medium | Add "on some tasks" and one sentence on the cause (serving-side batching/optimisations). That is also a good interview talking point. |
| E9 | how-ab-testing-works.md:90 | "Output is random, even at temperature 0" | Fine as stated, but pair it with E8's nuance: non-determinism at temperature 0 varies by provider and is not "random" in the sampling sense. | Low | "can still vary, even at temperature 0". |
| E10 | how-ab-testing-works.md:92 | "Small copy changes rarely matter much" (classic A/B) | Kohavi's own Ch 1 opens with a small Bing ad-headline change worth a 12% revenue lift and states "small changes can have a big impact" (confirmed via search summaries of the Cambridge excerpt; **Secondary**). The contrast with LLMs is overstated. | Medium | "In classic A/B, small changes occasionally have big effects (Kohavi's Bing headline example). With LLMs, small formatting changes routinely shift results." |
| E11 | how-ab-testing-works.md:94 | "Cost is rarely a metric" (classic) vs "Cost and latency are core metrics" (LLM) | Latency is a standard guardrail in classic experimentation (Kohavi Ch 5 is "Speed Matters", per the Cambridge ToC). Only per-request **cost** is new. | Low-Medium | "Per-request cost becomes a first-class metric; latency was already a classic guardrail." |
| E12 | how-ab-testing-works.md:32 | "Kohavi et al. call the primary metric the Overall Evaluation Criterion (OEC)" | Kohavi's OEC can be a single metric **or a combination** of metrics. Minor simplification. | Low | "the OEC, the agreed measure (sometimes a combination of metrics) that stands for 'better'". |
| E13 | how-ab-testing-works.md:57 | "Confidence interval. The range of effects that fit your data." | Acceptable plain-language gloss, but interviewers ask the frequentist definition. Missing: a 95% CI comes from a procedure that captures the true effect 95% of the time; it is not "95% probability the true effect is in this range". | Low-Medium | Add one sentence; save the details for Ch 8. |
| E14 | how-ab-testing-works.md:59 | "Power. ... Small effects need a lot more data." | Correct. Missing the link to MDE and alpha (required sample grows with 1/effect squared). | Low | Add "Halving the effect you want to detect roughly quadruples the cases needed." |
| E15 | how-ab-testing-works.md:21-30 | "The six ingredients" table | Not attributed. Kohavi Ch 2 ("Running and Analyzing Experiments") is the natural source; the Read-more cites Ch 1, 3, 7 only. | Low | Cite Ch 2 (title verified on Cambridge page). |
| E16 | how-ab-testing-works.md:78 | GrowthBook "puts it neatly: with an LLM the treatment 'isn't a thing; it's a process.'" | Exact source sentence is "The treatment isn't a thing; it's a process." The quote is accurate in substance; the attributed paraphrase prefix is fine. Vendor source is labelled. | OK | — |
| E17 | how-ab-testing-works.md:61 | "Interviewers love asking about this one." | Plausible, unsupported. | Low | Keep as voice, or soften to "a common interview probe". |
| E18 | prompt-experiment-anatomy.md:98-102 | `runs_per_case: 3` ... `decision: ship B if CI lower bound > 0` | Two problems: (a) with 3 runs per case, a CI computed over 3N rows treats correlated runs as independent and comes out too narrow; it must average per case first or cluster by case (Miller 2024, already in references); (b) the rule ignores guardrails and practical significance (a +0.1 pt win with CI lower bound 0.01 would "ship"). | **High** (it is the template the learner will copy) | `decision: ship B if paired CI (clustered by case) lower bound > 0 AND gain >= MDE AND no guardrail worse than threshold`. Flag Ch 8 to teach clustering. |
| E19 | prompt-experiment-anatomy.md:57 | "Statsig warns that models can update under your feet; if that happens mid-test, both variants are hit equally." | Statsig's warning is in an online-test context. Running together reduces, but does not guarantee equal exposure (requests interleave over time; rate limits, retries). | Low | "...both variants are exposed to roughly the same conditions." |
| E20 | prompt-experiment-anatomy.md:112 and :143 | "Anthropic's eval guide asks for exactly this: criteria that are specific and measurable, tested on a held-out set" / "Anthropic's guide suggests a held-out test set." | "Specific" and "Measurable" are verified. "held-out test set" appears in the worked sentiment example (with a footnote to a later section I could not read in full). "asks for exactly this" overstates the match to an experiment-file practice. | Low | "Anthropic's guide asks for specific, measurable criteria; its worked example uses a held-out test set." |
| E21 | prompt-experiment-anatomy.md:28 and :32 | "which change helped? You can't say." / ladder A → B1 → B2 → B3 | Correct for a single bundled comparison, but the ladder has its own problems: order dependence, interactions, and repeated testing against the same set (overfitting the test set). | Low | Mention ablation/factorial as alternatives; run the ladder on the dev set and confirm the final winner on the held-out set. |
| E22 | why-test-prompts.md:92 and how-ab-testing-works.md:34 | "decide what 'better' means first" / "Write all six down before the test." | Right for the A/B comparison itself, but Shankar et al. (arXiv 2404.12272) show criteria drift: people discover criteria by grading outputs. Presenting it as absolute contradicts the error-analysis-first workflow the book will need. | Medium | "Discover criteria by reading outputs first (Ch on error analysis); then freeze them before the A/B comparison." |

Kohavi references in Ch 2 Read-more (Ch 1 free, Ch 3, Ch 7) all match references.md and the Cambridge ToC. The Practical Statistics chapter number remains Secondary, and the chapter already hedges it ("check your edition"). No invented citations found in Ch 1-3.

Old drafts (not in scope, flagged for the rewrite): the-interview.md resume story claims practices the learner may not have done; who-marks-the-answers.md recommends checking "how often the judge agrees" (raw agreement); the-exam-paper.md sample-size table omits the baseline rate and pairing assumptions behind its numbers.

---

## (F) Bottom line

**Readiness as designed.** If all 12 chapters are written well, the learner would handle the *offline prompt A/B* slice of interviews confidently: reproducibility, versioning, judge biases, CIs, rollout. That is a real but narrow slice. They would be **underprepared** for (1) system-design rounds on RAG and agent evaluation, (2) the "how do you know your judge is right" follow-up chain with actual metrics, (3) live coding and take-homes, and (4) a resume deep-dive where every number must be theirs. For Evals Engineer roles, measurement-science depth (clustered errors, annotator agreement, benchmark saturation, contamination) is also thin. My judgement: ready for a first-round conceptual screen; not yet ready for an onsite loop.

**Biggest gap.** The book teaches *about* evaluation but never makes the learner *do and defend* one end to end. Without a real project, real numbers, and practice producing answers under questioning, the resume line "A/B testing for prompts" is the weakest point in the learner's interview, not the strongest.

**Five highest-impact changes (in order):**
1. **Build a real portfolio project through the book** (M1 + M2): harness by Ch 4, real API calls, validated judge, paired clustered CI, CI gate, public write-up. It also becomes the take-home rehearsal and the behavioural story.
2. **Add RAG / agent / multi-turn evaluation** (M4), including pass^k, trajectory vs outcome, retrieval vs generation metrics, and structured output.
3. **Error analysis first, judge validation with real metrics** (M3 + M5): open/axial coding, TPR/TNR, kappa, judge held-out split, criteria drift.
4. **Replace the reading-only interview chapter with a practice system** (M6 + S5 + S7): rubric-scored question bank with follow-up chains, 5 system-design prompts, 4 timed coding drills, debugging scenarios, LLM-run mock interviews.
5. **Fix the statistics core** (M7, E1, E2, E18): correct p-value wording, paired-vs-randomised framing, clustering for repeated runs, MDE and practical significance in the decision rule, multiple comparisons. Then add monitoring/drift and cost trade-offs (S1, S3).
