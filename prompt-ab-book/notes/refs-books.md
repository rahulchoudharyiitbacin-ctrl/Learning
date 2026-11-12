# Book references for LLM eval, prompt engineering, A/B testing

Verification key: [OPENED] = I fetched the page and read the text. [SNIPPET] = search-result snippet or third-party page only. UNVERIFIED = could not confirm.
Note: oreilly.com pages returned HTTP 403 to my fetcher, so no O'Reilly page was opened directly. O'Reilly chapter numbers below come from the author's GitHub or search snippets.

## 1. Chip Huyen, "AI Engineering: Building Applications with Foundation Models"
- Publisher/year: O'Reilly, 2025 (author's books page, https://huyenchip.com/books/ [OPENED]). The subtitle is from memory of the cover; it was not shown on a page I opened. Mark UNVERIFIED.
- Pages opened: https://huyenchip.com/books/ ; full ToC at https://github.com/chiphuyen/aie-book/blob/main/ToC.md [OPENED]
- Free version: none found. The ToC and resources are free on GitHub (https://github.com/chiphuyen/aie-book).
- Chapter-level ToC [OPENED, GitHub ToC.md]:
  - Ch 3 "Evaluation Methodology": Challenges of Evaluating Foundation Models; Understanding Language Modeling Metrics; Exact Evaluation (Functional Correctness, Similarity Measurements Against Reference Data, Introduction to Embedding); AI as a Judge (Why, How to Use, Limitations, What Models Can Act as Judges); Ranking Models with Comparative Evaluation. Tags: eval-methods, llm-as-judge.
  - Ch 4 "Evaluate AI Systems": Evaluation Criteria; Model Selection; Design Your Evaluation Pipeline (Step 1 Evaluate All Components, Step 2 Create an Evaluation Guideline, Step 3 Define Evaluation Methods and Data). Tags: eval-dataset, harness, frameworks.
  - Ch 5 "Prompt Engineering": Introduction to Prompting; Prompt Engineering Best Practices (includes "Iterate on Your Prompts", "Evaluate Prompt Engineering Tools", "Organize and Version Prompts"); Defensive Prompt Engineering. Tags: why-test-prompts.
  - Ch 6 "RAG and Agents": includes "Agent Failure Modes and Evaluation". Tag: failure-analysis (secondary).
  - Ch 8 "Dataset Engineering": Data Curation, Data Augmentation and Synthesis. Tag: eval-dataset (secondary; the chapter is about training data).
  - Ch 10 "AI Engineering Architecture and User Feedback": Monitoring and Observability; User Feedback (Extracting Conversational Feedback, Feedback Design, Feedback Limitations). Tags: online-ab (feedback and monitoring only; it has no A/B testing section in the ToC), failure-analysis.
- Correction to the brief: the ToC has no chapter titled "Evaluating AI Systems". It is Ch 4 "Evaluate AI Systems". LLM-as-judge and comparative evaluation sit in Ch 3, not Ch 4.

## 2. Chip Huyen, "Designing Machine Learning Systems: An Iterative Process for Production-Ready Applications"
- Publisher/year: O'Reilly, 2022 (https://huyenchip.com/books/ [OPENED]). Subtitle from a Barnes & Noble search-result title [SNIPPET].
- Pages opened: https://huyenchip.com/books/ ; https://github.com/chiphuyen/dmls-book/blob/main/summary.md [OPENED] (chapter list); https://aiden-jeon.github.io/blog/p/chapter-9.-continual-learning-and-test-in-production [OPENED, third-party notes]
- Free version: none found. The GitHub repo has the ToC and chapter summaries.
- Chapter list [OPENED, summary.md]: 1 Overview of Machine Learning Systems; 2 Introduction to ML Systems Design; 3 Data Engineering Fundamentals; 4 Training Data; 5 Feature Engineering; 6 Model Development and Offline Evaluation; 7 Model Deployment and Prediction Service; 8 Data Distribution Shifts and Monitoring; 9 Continual Learning and Test in Production; 10 Infrastructure and Tooling for MLOps; 11 The Human Side of Machine Learning.
- Relevant chapters:
  - Ch 9 "Continual Learning and Test in Production". "Test in Production" subsections are Shadow Deployment, A/B Testing, Canary Release, Interleaving Experiments, Bandits [OPENED, third-party notes; also in a search snippet]. Page numbers (Test in Production p. 281, Bandits p. 287) are from a search snippet only [SNIPPET]. Tags: online-ab, how-ab-testing-works.
  - Ch 6 "Model Development and Offline Evaluation": tag eval-methods (title only; sections not opened, UNVERIFIED).
  - Ch 8 "Data Distribution Shifts and Monitoring": tag failure-analysis (title only).
- Caveat: this is classical ML, not LLM-specific. Use it only for the online-testing taxonomy.

## 3. Ron Kohavi, Diane Tang, Ya Xu, "Trustworthy Online Controlled Experiments: A Practical Guide to A/B Testing"
- Publisher/year: Cambridge University Press, 2020 [OPENED].
- Pages opened: https://experimentguide.com/ (authors' site); https://www.cambridge.org/core/books/trustworthy-online-controlled-experiments/D97B26382EB0EB2DC2019A7A7B518F59 (ToC, first page only).
- Free version: Chapter 1 is a free download (https://bit.ly/ExPGuideChapter1, per experimentguide.com). Full book is not free.
- Chapters confirmed on the Cambridge ToC page [OPENED]:
  - Part I: 1 Introduction and Motivation (how-ab-testing-works, why-test-prompts; free sample); 2 Running and Analyzing Experiments (experiment-anatomy; the book's end-to-end example); 3 Twyman's Law and Experimentation Trustworthiness (noise-and-stats, failure-analysis); 4 Experimentation Platform and Culture (frameworks).
  - Part II: 5 Speed Matters; 6 Organizational Metrics; 7 Metrics for Experimentation and the Overall Evaluation Criterion (experiment-anatomy; OEC); 8 Institutional Memory and Meta-Analysis; 9 Ethics in Controlled Experiments.
  - Part III: 10 Complementary Techniques; 11 Observational Causal Studies.
  - Part IV: 12 Client-Side Experiments; 13 Instrumentation; 14 Choosing a Randomization Unit; 15 Ramping Experiment Exposure: Trading Off Speed, Quality, and Risk (online-ab); 16 Scaling Experiment Analyses.
  - Part V: 17 The Statistics behind Online Controlled Experiments (pp. 185-192; noise-and-stats); 18 Variance Estimation and Improved Sensitivity: Pitfalls and Solutions (pp. 193-199; noise-and-stats).
- Later chapters, from a search snippet [SNIPPET] that I could not confirm on the ToC page (it was split over two pages and the second was not returned): 19 The A/A Test; 20 Triggering for Improved Sensitivity; 21 Sample Ratio Mismatch and Other Trust-Related Guardrail Metrics (Cambridge listing pp. 219-225); 22 Leakage and Interference between Variants. A Cambridge chapter page for SRM exists (https://www.cambridge.org/core/books/trustworthy-online-controlled-experiments/sample-ratio-mismatch-and-other-trustrelated-guardrail-metrics/8DBB0F59AC7729D7BC6B94690DB9CCD5) but returned HTTP 500 when I fetched it. Chapter 23 (long-term effects) is UNVERIFIED.
- Sample size, power and peeking: secondary summaries (not the book text) place power, sample size, peeking and multiple testing in Ch 17 [SNIPPET]. The chapter-to-topic mapping is likely but not directly confirmed. Treat as UNVERIFIED until someone checks the chapter text or index.
- SRM is Ch 21 (SNIPPET-level confirmation: two consistent hits, chapter title plus page range).

## 4. Jay Alammar and Maarten Grootendorst, "Hands-On Large Language Models: Language Understanding and Generation"
- Publisher/year: O'Reilly, September 2024 (from a search snippet on the O'Reilly Ch 12 preview [SNIPPET]; subtitle from an agendabookshop search result title [SNIPPET]).
- Pages opened: https://github.com/HandsOnLLM/Hands-On-Large-Language-Models (chapter list [OPENED]). The O'Reilly page returned 403.
- Free version: code is free on GitHub. The book is not free.
- Chapters [OPENED]: 1 Introduction to Language Models; 2 Tokens and Embeddings; 3 Looking Inside Transformer LLMs; 4 Text Classification; 5 Text Clustering and Topic Modeling; 6 Prompt Engineering; 7 Advanced Text Generation Techniques and Tools; 8 Semantic Search and Retrieval-Augmented Generation; 9 Multimodal Large Language Models; 10 Creating Text Embedding Models; 11 Fine-tuning Representation Models for Classification; 12 Fine-tuning Generation Models.
- Relevant: Ch 6 Prompt Engineering (why-test-prompts; section list not opened). Evaluation: I could NOT confirm any evaluation section, including whether Ch 12 covers benchmarks or LLM-as-judge. UNVERIFIED. The book is weak for evals. Recommend it only for prompting basics.

## 5. Peter Bruce, Andrew Bruce, Peter Gedeck, "Practical Statistics for Data Scientists: 50+ Essential Concepts Using R and Python" (2nd ed.)
- Publisher/year: O'Reilly, 2nd edition. Year 2020 is from memory; UNVERIFIED. Subtitle is from a slideshare result title [SNIPPET].
- Pages I could not open (403): https://www.oreilly.com/library/view/practical-statistics-for/9781492072935/
- Free version: none confirmed. The companion code is at https://github.com/gedeck/practical-statistics-for-data-scientists (appeared in search results; not opened).
- From search snippets [SNIPPET]: Ch 1 Exploratory Data Analysis; Ch 2 Data and Sampling Distributions (includes The Bootstrap, p. 61, and Resampling Versus Bootstrapping, p. 65); Ch 3 Statistical Experiments and Significance Testing. Ch 3 sections reported by a third-party outline: A/B Testing, Hypothesis Tests, Resampling (permutation test), Statistical Significance and P-Values, t-Tests, Multiple Testing, Degrees of Freedom, ANOVA, Chi-Square Test, Multi-Arm Bandit Algorithm. Edition for that outline is not stated. "Power and Sample Size" is also in the book from my memory but was not confirmed.
- Tags: Ch 3 = how-ab-testing-works, noise-and-stats. Ch 2 (bootstrap) = noise-and-stats. Correction to the brief: bootstrap is in Ch 2, not Ch 3.

## 6. Evals-specific

### a. Hamel Husain and Shreya Shankar, "Evals for AI Engineers" (O'Reilly)
- Source: search snippets only; the O'Reilly page returned 403. URL from search results: https://www.oreilly.com/library/view/evals-for-ai/9798341660717/ [SNIPPET]
- Snippets say the O'Reilly publication date is October 2026 (225 or 240 pages, sources differ; a bookseller says Oct 31, 2026). It is an early-release title with a provisional ToC. Today is 2026-11-12, so it may have since shipped, but I could not check.
- Early-release chapters named in a snippet: 1 Introduction; 2 LLMs and Evaluation Basics; 3 Error Analysis; 4 Collaborative Evaluation Practices; Part IV is "Production and Improvement". Chapter numbering beyond this is UNVERIFIED. Topics reported: error analysis, synthetic data generation, LLM-as-judge, production monitoring, cost optimization.
- Suggested tags if confirmed: failure-analysis (Error Analysis), eval-dataset (synthetic data), llm-as-judge, online-ab (production monitoring). Do not cite chapter numbers until verified.
- The exact title "Application-Centric AI Evals for Engineers and Technical Product Managers" returned no results. I did not find that title.

### b. Husain and Shankar, free email course "Ship AI Products with Confidence"
- URL opened: https://ai.hamel.dev/eval-course [OPENED]. It is a free 17-email course with two free e-books (an LLM Evals FAQ and a RAG optimization guide). It has no lesson-by-lesson list.
- The paid Maven course is at https://maven.com/parlance-labs/evals (search result; not opened).
- Evals FAQ PDF (search result, not opened): https://hamel.dev/blog/posts/evals-faq/evals-faq.pdf

### c. Anthropic, "Prompt Engineering Interactive Tutorial"
- URL opened: https://github.com/anthropics/prompt-eng-interactive-tutorial [OPENED]
- Free: public repo. The page does not state a license; I could not confirm.
- Chapters [OPENED]: 1 Basic Prompt Structure; 2 Being Clear and Direct; 3 Assigning Roles; 4 Separating Data from Instructions; 5 Formatting Output & Speaking for Claude; 6 Precognition (Thinking Step by Step); 7 Using Examples; 8 Avoiding Hallucinations; 9 Building Complex Prompts (Industry Use Cases); Appendix: Beyond Standard Prompting (Chaining Prompts, Tool Use, Search & Retrieval). Tag: why-test-prompts (prompt techniques). It uses Claude 3 Haiku, so it is dated.

## Not found
- No O'Reilly page was readable (403), so publisher-page URLs for items 1, 2, 4, 5, 6a were not opened; I used author GitHub, Cambridge and huyenchip.com instead.
- Kohavi chapters 19 to 23: the ToC page was split and only page 1 was returned. Chapter 19-22 titles are snippet-level.
- Where Kohavi's book treats sample size, power and peeking: not directly confirmed.
- Evaluation content in Hands-On LLMs: not confirmed.
- Practical Statistics 2e: chapter sections (including power and sample size) not directly confirmed; publication year unverified.
- No book found covering "interview" topic specifically. Untagged: interview.
- Not searched: other evals books, Google prompting guides, Kohavi's free material beyond Ch 1.
