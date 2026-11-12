# References and where each belongs in the book

Status key: **Verified** = opened at the source by the coordinator or a reader. **Secondary** = confirmed only through a third-party page or search snippet. **Unverified** = do not cite a chapter number yet.
Full details (authors, URLs, takeaways) are in `refs-papers.md` and `refs-books.md`.

## Start here: the 5 best things to read

1. **Chip Huyen, *AI Engineering* (O'Reilly, 2025).** Ch 3 *Evaluation Methodology* (exact evaluation, AI as a Judge, comparative evaluation), Ch 4 *Evaluate AI Systems* (see "Design Your Evaluation Pipeline"), Ch 5 *Prompt Engineering*. Verified against the author's ToC: https://github.com/chiphuyen/aie-book/blob/main/ToC.md
2. **Ron Kohavi, Diane Tang, Ya Xu, *Trustworthy Online Controlled Experiments* (Cambridge, 2020).** The standard book on A/B testing. Ch 1 is a free download. Ch 2, 3, 7, 15, 17 verified on the Cambridge page.
3. **Zheng et al. 2023, *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena*.** https://arxiv.org/abs/2306.05685
4. **Miller (Anthropic) 2024, *Adding Error Bars to Evals*.** https://arxiv.org/abs/2411.00640
5. **Hamel Husain, *Your AI Product Needs Evals*** (https://hamel.dev/blog/posts/evals/) and his LLM-judge guide (https://hamel.dev/blog/posts/llm-judge/).

## Mapping to the 12 planned chapters

| # | Chapter | Read this |
|---|---|---|
| 1 | Why test prompts, why A/B | Sclar et al. 2024 on prompt-formatting sensitivity (arXiv 2310.11324, ICLR 2024); Husain, *Your AI Product Needs Evals*; Anthropic, *Prompt engineering overview* |
| 2 | How A/B testing works | Kohavi et al. Ch 1–3 (Ch 3 is *Twyman's Law and Experimentation Trustworthiness*); *Practical Statistics for Data Scientists* Ch 3, A/B testing section (**Secondary**); GrowthBook's post on A/B testing non-deterministic LLMs (vendor) |
| 3 | Anatomy of a prompt experiment | Anthropic, *Define success criteria and build evaluations*; OpenAI prompt engineering guide (pinning model snapshots); Huyen, *AI Engineering* Ch 4 |
| 4 | Building the eval dataset | Anthropic docs (above); Ribeiro et al. 2020, *CheckList* (arXiv 2005.04118); Huyen Ch 4, "Design Your Evaluation Pipeline" |
| 5 | Evaluation methods | Huyen Ch 3, "Exact Evaluation"; Eugene Yan, *Task-Specific LLM Evals that Do & Don't Work*; Liang et al., *HELM* (arXiv 2211.09110); Es et al., *Ragas* (arXiv 2309.15217) |
| 6 | LLM-as-judge in depth | Zheng et al. 2023; Wang et al. 2023, *LLMs are not Fair Evaluators* (position bias); Liu et al. 2023, *G-Eval*; Dubois et al. 2024, *Length-Controlled AlpacaEval* (arXiv 2404.04475); Huyen Ch 3, "AI as a Judge"; Husain's LLM-judge guide |
| 7 | Hands-on harness | OpenAI, *Working with evals*; Anthropic eval docs; Husain, *Your AI Product Needs Evals* |
| 8 | Did it improve? (stats) | Miller 2024; Sclar et al. 2024; *Practical Statistics* Ch 2 for the bootstrap (**Secondary**); Kohavi Ch 17 *The Statistics behind Online Controlled Experiments* |
| 9 | Frameworks | promptfoo, LangSmith, Langfuse, Braintrust docs (fetched fresh when we write the chapter); Ragas for RAG |
| 10 | Failure analysis and iteration | Husain's posts; *CheckList*; Husain and Shankar's free evals course: https://ai.hamel.dev/eval-course |
| 11 | Online A/B | Kohavi Ch 15 *Ramping Experiment Exposure*; Huyen, *Designing Machine Learning Systems* Ch 9, *Continual Learning and Test in Production* (**Secondary** for subsections; classical ML, not LLM-specific); Huyen, *AI Engineering* Ch 10, "User Feedback"; Statsig and GrowthBook posts (vendor) |
| 12 | Interview prep | Anthropic, *Building effective AI agents*; all of the above for answers you can defend |

## Cautions (what not to over-claim)

- **Kohavi power, sample size and peeking:** which chapter covers them is **Unverified**. Cite the book generally for those until we check a copy. Ch 21 *Sample Ratio Mismatch* is **Secondary** (search snippets).
- **Huyen, *AI Engineering* Ch 10** covers user feedback, but has no A/B testing section. Don't send readers there for A/B.
- ***Hands-On LLMs*** (Alammar and Grootendorst): Ch 6 is *Prompt Engineering*. No evaluation chapter was found, so use it for prompting basics only.
- ***Practical Statistics for Data Scientists*:** pages could not be opened. Chapter numbers come from search snippets; publication year and the sample-size section are **Unverified**.
- **Husain and Shankar, *Evals for AI Engineers* (O'Reilly):** appears to be in early release (snippets only). Don't cite chapter numbers yet. The free course above is verified.
- **Vendor posts** (Statsig, GrowthBook) are useful but not peer reviewed. Label them as vendor views.
- **Venues** for Wei et al. (chain-of-thought) and Ragas weren't stated on the arXiv pages the reader opened. Leave the venue off, or check before printing.
- **Anthropic's Prompt Engineering Interactive Tutorial** (https://github.com/anthropics/prompt-eng-interactive-tutorial) is useful practice, but it uses an old model, so treat it as dated.
- O'Reilly pages returned 403 to the reader, so book details come from the authors' GitHub, Cambridge and publisher-adjacent pages.

## Added while writing Chapter 2 (verified by the coordinator on 2026-11-12)

- **Atil et al. 2024**, *Non-Determinism of "Deterministic" LLM Settings*, arXiv 2408.04667. Abstract opened: five LLMs configured to be deterministic, eight tasks, 10 runs; accuracy varied by up to 15% across runs, and no model was consistently repeatable. https://arxiv.org/abs/2408.04667
- **GrowthBook** article on A/B testing non-deterministic LLMs (vendor): the "treatment is a process, not a thing" framing and the stable-treatment assumption. Opened first ~7k characters.
- **Statsig** "When statistical significance misleads" (vendor, 31 Oct 2025): fix goal, primary metric and stop rule before launch; peeking inflates false positives; freeze the experience during the test; models can update quietly. Opened first ~7k characters.

## Added while writing Chapter 3 (verified by the coordinator on 2026-11-12)

- **OpenAI prompt engineering guide**: "even different snapshots of models within the same family could produce different results"; strongly recommends pinning production applications to specific model snapshots (example given: gpt-4.1-2025-04-14). https://developers.openai.com/api/docs/guides/prompt-engineering
- **Anthropic, Define success criteria and build evaluations**: criteria should be specific and measurable (worked sentiment-analysis example with an F1 target on a held-out test set); design evals that mirror the real task distribution including edge cases; favor automated grading. https://platform.claude.com/docs/en/test-and-evaluate/develop-tests
- **Huyen, AI Engineering Ch 4**: "Design Your Evaluation Pipeline" has Step 2 (Create an Evaluation Guideline) and Step 3 (Define Evaluation Methods and Data); confirmed from the author's ToC.

## Added while writing Chapter 4 (verified by the coordinator on 2026-11-13)

- **Claude API behaviour used in the harness** (from the bundled claude-api skill docs): Messages API call shape (`model`, `max_tokens`, `system`, `messages`, `output_config.effort`); `temperature`, `top_p` and `top_k` are not accepted by current models, and the newest API version rejects them everywhere; Haiku 5.5 runs adaptive thinking by default and defaults to `medium` effort.
- Harness tested with `anthropic` 2.8.0 against a fake local server; real-API behaviour of `claude-haiku-5-5` with `effort: low` is **not** tested live.

## Added while writing Chapter 5 (verified by the coordinator on 2026-11-13)

- **Husain, Frequently Asked Questions (and Answers) About AI Evals** (https://hamel.dev/blog/posts/evals-faq/): error analysis called the most important activity in evals; process = gather representative traces, open coding ("journaling", adapted from qualitative research; note the first failure in a trace; start with at least 30 traces yourself), axial coding into a failure taxonomy (count per category), iterate until theoretical saturation; a working pool of roughly 100 diverse traces; "look at 50 to 100 real user conversations" to find the most common failures.
- **Husain and Shankar, free evals course** (https://ai.hamel.dev/eval-course): lists error analysis (analyze failures before building complex evaluation infrastructure) among its principles; 17 lessons plus two free e-books.
- **Shankar et al. 2024, Who Validates the Validators?** (arXiv 2404.12272, 18 Apr 2024): abstract confirms "criteria drift": users need criteria to grade outputs, but grading outputs helps users define criteria.

## Added while writing Chapter 6 (verified by the coordinator on 2026-11-13)

- **Husain FAQ, "How many examples do I need for an eval?"**: three stages. Error discovery: 100 diverse traces, annotate at least the first 30 yourself. LLM judges: label 100 to 200 examples per failure mode; split 10-20% train (may appear in the prompt), 40-45% dev, 40-45% final test; 30-50 Pass and 30-50 Fail in dev and in test where possible. Repeatable eval set: important workflows plus confirmed failures; often grows to 100 or more; coverage determines size; cheap enough to run often.
- **Husain FAQ, synthetic data**: define dimensions first; write 20 tuples by hand; generate tuples then queries; run through the real system. Caveats: cannot show how common a failure is; unreliable in specialized domains, low-resource languages, high-stakes domains, underrepresented groups; compare with real data when available; do not generate data for issues you can fix immediately.
- **Husain FAQ, sampling traces**: start with random sampling, then target rare failures with signals.
- **Anthropic develop-tests page** (re-checked): mirror the real-world task distribution, include edge cases, automate grading where possible.
- Sample-size table in Chapter 6 computed by the coordinator: n = 1.96^2 p(1-p)/E^2 (p=0.8: E=0.10 -> 62, 0.05 -> 246, 0.03 -> 683; p=0.5, E=0.05 -> 385). This is for estimating ONE accuracy, not for comparing A and B (Chapter 9).

## Added while writing Chapter 7 (verified by the coordinator on 2026-11-13)

- **Huyen, AI Engineering, Ch 3 "Evaluation Methodology"** (ToC from the author's repo): Exact Evaluation (Functional Correctness; Similarity Measurements Against Reference Data; Introduction to Embedding); AI as a Judge (Why, How to Use, Limitations, What Models Can Act as Judges); Ranking Models with Comparative Evaluation. **Ch 4 "Evaluate AI Systems"**: Evaluation Criteria (Domain-Specific, Generation, Instruction-Following, Cost and Latency); Design Your Evaluation Pipeline (Steps 1-3).
- **Anthropic develop-tests page**: exact match "perfect for tasks with clear-cut, categorical answers" (sentiment example, after normalizing whitespace and case); cosine similarity of embeddings for consistency (FAQ bot); ROUGE-L for summaries (longest common subsequence); Likert scales as an option; automate grading where possible; "more questions with slightly lower signal automated grading is better than fewer questions with high-quality human hand-graded evals".
- **Yan, Task-Specific LLM Evals that Do & Don't Work** (title confirmed): classification/extraction: recall, precision, ROC-AUC, PR-AUC, separation of distributions; summarization: consistency via NLI, relevance via reward model, length checks; translation: chrF, BLEURT, COMET, COMETKiwi; "accuracy is too coarse a metric to be useful ... separate it into recall and precision at minimum".
- **Husain, "Using LLM-as-a-Judge For Evaluation: A Complete Guide"** (title confirmed): warns against uncalibrated 1-5 scales across dimensions; recommends a binary pass/fail judgment with a written critique from a domain expert.
- **Husain/Shankar course page**: a single domain expert is often more effective than a committee for annotation and review.
- Math in the chapter (95/5 imbalance; 8/10 recall and 8/12 precision) verified by hand-computed assertions in a test run.

## Chapters 8, 9, 10 (written by Opus workers; verification details in their own notes)

- Chapter 8 sources and checks: `notes/refs-ch8.md`.
- Chapter 9 sources and where every number comes from: `notes/refs-ch9.md`.
- Chapter 10 sources (promptfoo, LangSmith, Langfuse, Braintrust docs; OpenAI deprecations; GitHub Actions): `notes/refs-ch10.md`.
- Coordinator spot-checks: Chapter 8 kappa example recomputed independently (0.86 / 0.60 / 0.925 / 0.545); Husain's "always predicts Pass ... 95% agreement" line confirmed. Chapter 9 McNemar exact p (8 vs 2 = 0.109375; 6 vs 0 = 0.03125), single-accuracy sample size (246), the 934-case figure for the demo, and the CI chart's numbers confirmed. Chapter 10 CI simulation rerun by the coordinator (5 scenarios as expected).

## Added while writing Chapter 11 (verified by the coordinator on 2026-11-13)

- **GrowthBook, How do you A/B test an LLM when outputs aren't deterministic?** (vendor; full page read): shadow scoring (run both variants on live traffic, score silently); small traffic flight; feature flags with percentage rollouts and instant kill switches; consistent user bucketing (MurmurHash3, no stored state); randomise on users, not requests; duration 1-2 weeks as a typical minimum, two weeks as the floor for LLM experiments, novelty effects; canary 1-5% of traffic for 24-48 hours; "at least 200 conversion events per variation" rule of thumb; output text is a poor primary metric; Statsig quote "Do not wait for perfection. Move from sandbox to production when gaps narrow, not vanish."
- **Husain, Your AI Product Needs Evals** (re-confirmed): level 3 (A/B testing) usually only appropriate for more mature products.
- **Huyen, AI Engineering Ch 10** (author's ToC): "Monitoring and Observability" and "User Feedback" sections.
- Chapter 11's numbers come from `work/harness/online_tools.py` and `test_online.py` (hand-checked), and the peeking numbers (3.7% vs 13.0%) from the Chapter 9 simulation.
- **Not verified:** Statsig and LaunchDarkly current docs; the SRM alarm threshold 0.001 is the book's own stated choice, not attributed.

## Added while writing Chapter 12 (verified by the coordinator on 2026-11-13)

- **Husain FAQ**: RAG = retrieval (IR metrics Recall@k, Precision@k, MRR; synthetic query-document pairs) + generation (error analysis, human labels, validated judges); credits Jason Liu's "There Are Only 6 RAG Evals" (context relevance C|Q, faithfulness A|C, answer relevance A|Q). Multi-turn: whole-conversation pass/fail, annotate the first upstream failure, reproduce with the simplest case, simulate users or N-1 testing, trace IDs. Agentic workflows: end-to-end task success first, then step-level diagnostics.
- **Anthropic, Demystifying evals for AI agents** (full page read): trial, grader, transcript/trajectory vs outcome (flight-booking example), code/model/human graders, capability vs regression evals, pass@k vs pass^k (75% per trial, 3 trials -> 0.75^3 = 42%), isolated clean environments per trial, conversational agents graded on state check + turn constraint + tone rubric.
- **Ragas** (arXiv 2309.15217): reference-free evaluation of RAG retrieval and generation (abstract confirmed earlier by the reader).
- Chapter 12 numbers (Recall@5 = 2/3, Precision@5 = 2/5, MRR = 2/3, pass^3 = 0.4219, pass@3 = 0.9844) from `rag_metrics.py` tests, simulation-confirmed.

## Chapters 13-16 (written by me and three Opus workers; details in their own notes)

- Chapter 13 sources checked by the coordinator: Anthropic Research Engineer (Post-Training Model Evaluations) public posting; the recruiter article's red-flag answer "I've never really had to evaluate it, you can tell when it's working" (kore1.com, a source with a placement incentive).
- Chapter 14: `notes/refs-ch14.md`. Chapter 15: `notes/refs-ch15.md`. Chapter 16: `notes/refs-ch16.md`.
- Coordinator checks: question bank numbers recomputed (+/-3.5 points at 500 cases near 80%; paired n 870 and 2,614; pass^3 = 0.4219); system-design numbers recomputed (9,493 users per arm; 1,960 cases for a 2-point non-inferiority margin; 4.4 and 6.3 points detectable with 400 cases; pass^3 at 90% = 0.729); Anthropic deprecations page confirms at least 60 days' notice before retirement and temperature/top_p/top_k removed in API version 2026-10-21; all four drills rerun (solutions pass, starters fail, mutant checker OK in 31 s).
