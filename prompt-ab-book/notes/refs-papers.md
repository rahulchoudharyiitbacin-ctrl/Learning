# Reading list: prompt engineering, LLM evals, online experimentation

All URLs below were opened on 2026-11-12 unless marked UNVERIFIED. Takeaways are paraphrased from the opened pages.

## A. Prompt engineering foundations (why-test-prompts)

1. **Chain-of-Thought Prompting Elicits Reasoning in Large Language Models** - Wei, Wang, Schuurmans, Bosma, Ichter, Xia, Chi, Le, Zhou. 2022. arXiv (no peer venue listed on the page; it appeared at NeurIPS 2022 per general knowledge, not confirmed here). https://arxiv.org/abs/2201.11903
   Takeaway: showing worked intermediate reasoning steps in few-shot examples sharply improves LLM reasoning, so prompt wording changes results. Topic: why-test-prompts.
2. **Language Models are Few-Shot Learners (GPT-3)** - Brown, Mann, Ryder, Subbiah, Kaplan, Dhariwal et al. (31 authors). 2020. arXiv:2005.14165. https://arxiv.org/abs/2005.14165
   Takeaway: a large model can do many tasks from instructions and a few in-prompt examples with no fine-tuning, which is the basis of prompting. Topic: why-test-prompts.
3. **The Prompt Report: A Systematic Survey of Prompt Engineering Techniques** - Schulhoff, Ilie, Balepur et al. (31 authors). 2024 (rev. Feb 2025). arXiv:2406.06608. https://arxiv.org/abs/2406.06608
   Takeaway: a survey that names 58 text prompting techniques and gives shared vocabulary and best practices. Topic: why-test-prompts, frameworks.
4. **Quantifying Language Models' Sensitivity to Spurious Features in Prompt Design or: How I learned to start worrying about prompt formatting** - Sclar, Choi, Tsvetkov, Suhr. 2023. ICLR 2024 (per arXiv page). https://arxiv.org/abs/2310.11324
   Takeaway: meaning-preserving formatting changes can swing few-shot accuracy a lot, so a single prompt score is unreliable. Topic: why-test-prompts, noise-and-stats.
5. **Prompt engineering overview** - Anthropic docs. https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview
   Takeaway: before prompt engineering, have success criteria, a way to test against them, and a first draft. Topic: why-test-prompts, experiment-anatomy.
6. **Prompt engineering** - OpenAI developer docs. https://developers.openai.com/api/docs/guides/prompt-engineering (old URL platform.openai.com/docs/guides/prompt-engineering returns a 301 to this)
   Takeaway: write clear instructions, test them, and pin to specific model snapshots as you iterate. Topic: why-test-prompts.
7. **Building effective AI agents** - Erik S. and Barry Zhang, Anthropic. Dec 19, 2024. https://www.anthropic.com/engineering/building-effective-agents
   Takeaway: use the simplest workable design and add complexity only when it measurably improves results. Topic: frameworks, interview.

## B. Evaluation design (eval-dataset, eval-methods, harness, frameworks, failure-analysis)

8. **Define success criteria and build evaluations** - Anthropic docs. https://platform.claude.com/docs/en/test-and-evaluate/develop-tests (old docs.anthropic.com URL 301-redirects here; the page is titled "Define success criteria and build evaluations", the task's "develop test cases" wording is the old URL slug)
   Takeaway: set specific measurable criteria, mirror the real task distribution, include edge cases, and favor automated grading at volume. Topic: eval-dataset, eval-methods, experiment-anatomy.
9. **Working with evals** - OpenAI developer docs. https://developers.openai.com/api/docs/guides/evals
   Takeaway: evals are programmatic tests; define a task, run test data through a prompt, and review results. Topic: harness, eval-methods.
10. **Holistic Evaluation of Language Models (HELM)** - Liang, Bommasani et al. 2022; TMLR 2023 (per arXiv page). https://arxiv.org/abs/2211.09110
    Takeaway: evaluate many models on many scenarios and several metrics (accuracy, fairness, toxicity), not accuracy alone. Topic: eval-methods, frameworks.
11. **Beyond Accuracy: Behavioral Testing of NLP models with CheckList** - Ribeiro, Wu, Guestrin, Singh. 2020. ACL 2020. https://arxiv.org/abs/2005.04118
    Takeaway: borrow software-testing ideas to write capability-based test cases that expose failures held-out accuracy hides. Topic: eval-dataset, failure-analysis.
12. **Ragas: Automated Evaluation of Retrieval Augmented Generation** - Es, James, Espinosa-Anke, Schockaert. 2023 (rev. 2025). arXiv (no peer venue listed; EACL 2024 demo per general knowledge, unconfirmed). https://arxiv.org/abs/2309.15217
    Takeaway: reference-free metrics for the retrieval and generation parts of RAG. Topic: frameworks, eval-methods.
13. **Length-Controlled AlpacaEval: A Simple Way to Debias Automatic Evaluators** - Dubois, Galambosi, Liang, Hashimoto. 2024. COLM 2024. https://arxiv.org/abs/2404.04475
    Takeaway: regressing out length bias makes an LLM-judged benchmark correlate better with Chatbot Arena (0.94 to 0.98). Topic: llm-as-judge, noise-and-stats.
14. **Your AI Product Needs Evals** - Hamel Husain. Mar 29, 2024. https://hamel.dev/blog/posts/evals/
    Takeaway: build domain-specific evals (unit tests, human review, model grading) to iterate quickly beyond demos. Topic: why-test-prompts, harness, failure-analysis.
15. **Task-Specific LLM Evals that Do & Don't Work** - Eugene Yan. Mar 2024. https://eugeneyan.com/writing/evals/
    Takeaway: generic evals often miss real performance, so use task-specific metrics and risk-based thresholds. Topic: eval-methods.
16. **Patterns for Building LLM-based Systems & Products** - Eugene Yan. Date not stated on page (likely about Aug 2023). https://eugeneyan.com/writing/llm-patterns/ (last 3.6k characters of the page not read)
    Takeaway: seven patterns, starting with evals, for turning demos into reliable products. Topic: frameworks, eval-methods.

## C. LLM-as-a-judge (llm-as-judge)

17. **Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena** - Zheng, Chiang, Sheng et al. 2023. NeurIPS 2023 Datasets and Benchmarks. https://arxiv.org/abs/2306.05685
    Takeaway: strong LLM judges agree with human preferences about as often as humans agree with each other, but have documented biases. Topic: llm-as-judge.
18. **G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment** - Liu, Iter, Xu, Wang, Xu, Zhu. 2023. arXiv (no peer venue listed on page). https://arxiv.org/abs/2303.16634
    Takeaway: a form-filling, chain-of-thought GPT-4 scorer that correlates better with humans on summarization. Topic: llm-as-judge.
19. **Large Language Models are not Fair Evaluators** - Wang, Li, Chen et al. 2023. arXiv. https://arxiv.org/abs/2305.17926
    Takeaway: the order of candidates sways LLM judges; calibration methods reduce it. Topic: llm-as-judge, noise-and-stats.
20. **Using LLM-as-a-Judge For Evaluation: A Complete Guide** - Hamel Husain. Oct 29, 2024 (modified Sep 2026 per page). https://hamel.dev/blog/posts/llm-judge/
    Takeaway: have a domain expert label real outputs with critiques first, then validate the judge against those labels. Topic: llm-as-judge, failure-analysis.

## D. Statistics and online experiments (noise-and-stats, how-ab-testing-works, online-ab)

21. **Adding Error Bars to Evals: A Statistical Approach to Language Model Evaluations** - Evan Miller (Anthropic). Nov 2024. arXiv:2411.00640. https://arxiv.org/abs/2411.00640
    Takeaway: treat eval scores as noisy estimates; give formulas for confidence intervals, paired comparisons, and sizing. Topic: noise-and-stats.
22. **Trustworthy Online Controlled Experiments: A Practical Guide to A/B Testing** - Ron Kohavi, Diane Tang, Ya Xu. 2020. Cambridge University Press. https://www.cambridge.org/core/books/trustworthy-online-controlled-experiments/D97B26382EB0EB2DC2019A7A7B518F59
    Takeaway: the standard practitioner book on running reliable A/B tests (Microsoft, Google, LinkedIn authors); only the landing page was read, not the chapters. Topic: how-ab-testing-works, online-ab, noise-and-stats.
23. **A/B testing for LLMs: When statistical significance misleads** - The Statsig Team. Oct 31, 2025. https://statsig.com/perspectives/abtesting-llms-misleading
    Takeaway: early significant wins often fail to hold; fix goals, metrics, and stopping rules up front, size for power, replicate, use guardrails. Topic: online-ab, noise-and-stats. (vendor source)
24. **Beyond prompts: A data-driven approach to LLM optimization** - Anna Yoon, Statsig. Mar 4, 2025. https://statsig.com/blog/llm-optimization-online-experimentation
    Takeaway: test prompts, models, and settings in controlled online experiments measured on user behavior and cost. Topic: online-ab, experiment-anatomy. (vendor source)
25. **How do you A/B test an LLM when results aren't deterministic?** - GrowthBook (author not listed). Jun 5, 2026. https://www.growthbook.io/insights/ab-testing-llms
    Takeaway: use stable user-level assignment, change one variable at a time, run offline evals before live traffic. Topic: how-ab-testing-works, online-ab. (vendor source; last 14k characters not read)

## Not found or not confirmed
- No Microsoft ExP or LinkedIn source on LLM prompt experiments surfaced; search returned only Statsig and GrowthBook vendor material. Kohavi's KDD 2013 paper "Online Controlled Experiments at Large Scale" was not found, so it is UNVERIFIED and not listed.
- Statsig/GrowthBook are vendor blogs, not peer reviewed. A search summary mentioned OpenAI acquiring Statsig from a single secondary source; unconfirmed and not used.
- Opened but not included: Auto-J (arXiv 2310.05470), a judge model paper, weaker fit.
- Venues for Wei et al. (NeurIPS) and Ragas (EACL) are not stated on the opened arXiv pages; verify before printing.
