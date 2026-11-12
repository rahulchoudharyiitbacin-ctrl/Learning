# Review 2: "Testing Prompts Like a Pro" (16 chapters)

Date: 2026-11-13. Method: four parallel reviewers (statistics, API/tools/code, consistency/teaching/interview, links), plus my own test runs and spot-checks. No chapter, code or config file was edited. No API key was used and no model API was called. Full worker reports (with more detail) are in the scratchpad: `stats.md`, `api.md`, `consistency.md`, `links.md` (paths in section F).

---

## A) Summary verdict

1. The arithmetic and statistics wording are in good shape: every number recomputed (about 60) is correct, the p-value / CI / paired-vs-randomised wording is right, and all links load.
2. The weak spot is the harness: resume ignores the config hash and treats cut-off or refused replies as valid wrong answers, so the first real run can silently produce stale or biased A/B numbers.
3. The online chapter (11) randomises by user but analyses a per-conversation rate with a two-proportion test, which is the clustering mistake Chapter 9 warns about. Chapters 15 and Q42 repeat it.
4. A learner could likely pass the eval part of an AI Engineer round, but would be at risk in an Evals Engineer round (online-stats depth, safety evals, pairwise ranking, non-inferiority, benchmark validity).
5. 15 of the 22 earlier section-E items are fully fixed; E21 is not fixed and E3, E4, E15, E19 are only partly fixed.

**The 5 most important fixes**
1. `run_experiment.py`: include `config_hash` in the resume key and treat `stop_reason` of `max_tokens` / `refusal` as retryable errors (H1, H2; also fix the Chapter 4 troubleshooting row that promises "Raise `max_tokens`" will help).
2. Chapter 11 (and Ch 15 P1/P2, Q42): analyse at the unit you randomised (per-user metric, or cluster by user / delta method). Ch 15 P2 randomises by agent: say how few clusters that gives.
3. Chapter 3 example `grader: graders/resolved-v2.py` crashes the Chapter 4 lab (`KeyError`); use a registered grader name.
4. Chapter 12 / Q48: pass^k = p^k only for one task with independent trials; give the per-task estimators and add a counterexample. Chapter 9 sends readers to "sequential methods (Chapter 11)" that Chapter 11 does not contain.
5. Chapter 9 (Miller quote) is attached to the wrong kind of cluster; plus `exact_match` rejects "Refund." (first-real-call risk).

---

## B) Issues table

Verification column: R = reviewer reproduced / ran it, G = grep / ls, S = checked at primary source, M = I re-checked it myself.

| ID | Sev | Chapter + page heading | Quote | What is wrong | Suggested fix | How verified |
|---|---|---|---|---|---|---|
| 1 | High | `work/harness/run_experiment.py` (lines 162-168); Ch 4 "Step 4a: the job list"; Ch 3 "The run record" | "The config hash ties each line back to the exact experiment file." | Resume keys on (case, variant, run) only. `config_hash` is written but never compared (line 163 builds `done` from rows without `error`). After editing `v2.txt` the rerun made 0 calls and printed the old v2 numbers. `compare_runs.py`, `error_analysis.py`, `classification_report.py` also mix hashes. | Skip key includes the current hash; summaries filter on it or the script refuses to run on a mixed file; add one sentence in Ch 4. | R: mock run, "0 calls to make (120 already done)" after prompt edit. M: read line 163. |
| 2 | High | `run_experiment.py`; Ch 4 "When something goes wrong" | "Empty `output`, `stop_reason: max_tokens` \| Thinking used up the budget \| Raise `max_tokens`" | A reply cut off at `max_tokens` (thinking only) or a `refusal` is stored as `output=""`, `grade=0`, no `error`. It counts as a real failure and resume treats it as done, so the book's own fix reruns nothing. Penalises whichever variant makes the model think longer. Same in `judge.py`. | Store as error (or `grade=None` + flag), retry it, print `stop_reason` counts; in the table add "delete `records.jsonl` or change `name`". | R: real SDK 2.8.0 against fake local server. |
| 3 | High | Ch 11 "How many users, how long?", "Reading the result"; Ch 15 Prompt 1 / Prompt 2; Q42 | "Online, users are independent, so compare the two groups directly." | Users are randomised, but the primary metric is "Conversations resolved without a human" and is tested as a two-proportion test over conversations. Conversations of one user are correlated: the Ch 9 clustering error, online. `online_tools.py plan/compare` take only counts. Ch 15 P2 randomises by support agent (maybe tens of clusters, badly underpowered). | Add a page "analysis unit = randomisation unit": per-user metric, or cluster by user (delta method / user bootstrap); mention ratio metrics; add "cluster by user" to Q42; note cluster count in Ch 15 P2. | R (two reviewers), read chapters + tool signatures. |
| 4 | Medium | Ch 3 "The experiment file" -> Ch 4 Lab "Lab: run your own experiment" | "grader: graders/resolved-v2.py" | Harness does `GRADERS[cfg["grader"]]` (`run_experiment.py:154`), so a path gives `KeyError`. Lab says "Take your Chapter 3 experiment file". Ch 3 also uses `data/tickets-v3.jsonl` / `prompts/support-bot/` while its Lab and Ch 4 use `cases-v1.jsonl` / `prompts/triage/`. | Use `grader: exact_match`; unify names. | M: grep Ch 3 line 99 + line 154. R: KeyError reproduced. |
| 5 | Medium | Ch 9 "Trap: peeking and a worn-out test set" | "it points to sequential methods (Chapter 11)." | Chapter 11 never covers sequential testing / alpha spending. | Add a short paragraph to Ch 11 or drop the pointer. | M: `grep -il sequential` returns only Ch 9. |
| 6 | Medium | Ch 12 "Agents: repeat and isolate", checkpoint 3; Ch 15 Prompt 4; Q48 | "If an agent succeeds 75% of the time per trial, pass^3 is 0.75^3 = 42%" next to "Trials of one task aren't independent: cluster by task" | p^k holds only for one task with independent trials. Across tasks pass^k is the mean of p_i^k. Half the tasks at 100%, half at 50%: mean 0.75, true pass^3 = 0.5625, not 0.42. Chen et al. call 1-(1-p)^k biased; unbiased per-task estimators exist (C(c,k)/C(n,k) for pass^k). | State the assumption; give per-task estimators; cite Chen et al. and tau-bench in Read more. | S: arXiv 2107.03374, 2406.12045; R: recomputed. |
| 7 | Medium | Ch 9 "Why not use all 2,400 rows?" | "In Anthropic's experience, clustered errors on popular evals can be 'over three times as large as naive standard errors'." | In Miller (arXiv 2411.00640, Table 4) the 3x figure is about groups of related questions (several per passage), not repeated runs of one question. For repeated runs Miller says to average per question. The book's method is right; the quote supports a different point. | Split into two sentences (average runs per question; cluster related-question groups, where the 3x appears). | S: fetched arXiv 2411.00640. M: quote present at did-it-improve.md line 50. |
| 8 | Medium | Ch 8 "Splitting the labels" vs Ch 8 Lab vs Ch 13 "The shape of a good answer" | "30 to 50 PASS and 30 to 50 FAIL ... in dev and in test" / "label at least 60 outputs" / "label 100 to 200 cases" | Three different targets. With 60 labels and 10-20% failures, dev has about 3-5 failures and `judge_validation.py` warns every time. | One rule: 30+ of each label per split (hundreds of labels if failures are rare); 60 = practice minimum that will warn. | R: read, `judge_validation.py:120`. |
| 9 | Medium | Ch 10 "What the pass rate doesn't tell you" | "Feed `pairs.csv` to the paired bootstrap from Chapter 9." | No tool in `work/` reads `pairs.csv` (`compare_runs.py` takes YAML + harness records; drill 2 takes per-call records). Dead end in the lab. | Add `compare_runs.py --pairs` or a 10-line snippet. | R: grep add_argument. |
| 10 | Medium | `work/harness/run_experiment.py` `summarize`; Ch 4 Step 4b | "you can count failures rather than lose them" | Old error rows stay after a resume; summary showed "123 calls, 3 errors" for 120 successful calls. | Keep last row per key, as `judge.py` does. | R: mock with injected errors. |
| 11 | Medium | `work/harness/run_experiment.py` `exact_match`; Ch 4 "Step 3: grade" | `output.strip().lower() == case["expected"].lower()` | "Refund." or "Label: refund" scores 0, while the judge rubric accepts one final full stop. Real-model rate UNVERIFIED (no live call). | Strip one trailing ".", or point to Ch 7 `normalized_match`; add to smoke-test questions. | R: fake-server probe. |
| 12 | Medium | `work/harness/judge.py` (resume ~253-257, `cmd_labelled` ~313-323); Ch 8 scripts | "keep errors as data" | Resume key ignores judge model / effort / output text, so stale verdicts survive; one failed call in `labelled` aborts the run and writes nothing. | Add model, effort and output hash to the skip key; try/except in `labelled`. | R: code reading only. |
| 13 | Medium | Ch 16 Drill 1; `drill1_async_harness/solution.py` | "Retry a 429 with exponential backoff; don't retry other errors." / cache "keyed by model, prompt and run index" | Real API: 529, 5xx and connection errors are retryable; the SDK already retries twice (extra loop multiplies attempts); a real cache key needs system prompt, effort, `max_tokens`, API version. Fine for the fake client. | Add a "real API" note. | S: rate-limits docs; R: SDK retry observed. |
| 14 | Medium | Ch 14 Q4 | "Husain's three levels ... A/B usually suits mature products." | Strong answer drops the strongest reason in the OK answer (too little traffic for the effect size) and has no number; thinner than OK. | Add traffic/power with the 14,751-users example. | R: read. |
| 15 | Medium | Ch 14 Q12; Ch 9 "Step 3: the decision rule" | "Set the largest acceptable loss before testing. Check the paired interval's lower end against it" | Non-inferiority is used in the answer but Ch 9's decision table is superiority-only; taught only in Ch 15 P5, which Q12 does not point to. | Add a "no worse than" row to Ch 9; point Q12 to Ch 15. | R: grep "non-inferior". |
| 16 | Low-Med | Ch 2 teacher's note (E4 regression) | "Online tests then confirm the win with real users." | Ch 1 was fixed; Ch 2 still frames online as confirmation. | "...check whether the offline win changes what real users do." | M: grep line 122. |
| 17 | Low-Med | Ch 14 Q33 | "row-level intervals caught the truth 80% of the time, not 95%." | 80.2% is only the heterogeneous scenario; mild case gave 94.6%. Breaks the "don't present a sample as typical" rule. | "as low as 80% when B's effect varied by case." | R: `test_stats.py` output. |
| 18 | Low | Ch 3 checkpoint answer 3 (E19) | "both variants are affected equally" | Body fixed to "roughly the same conditions"; answer key not. | Same wording. | R: read. |
| 19 | Low | Ch 7 "3. LLM judges" | "Zheng et al. found position, verbosity and self-preference effects" | Zheng et al. say they cannot determine self-enhancement bias; Ch 8 says so correctly. | "...and possible self-preference they could not confirm". | S: PDF text. |
| 20 | Low | Ch 9 "Worked example" / Lab | "sd of d = 0.327 ... 337 / 935 / 2,103" | Computed from unrounded 0.32733; `sample_size.py --sd 0.327` gives 336 / 933 / 2,099. | Print 0.3273 or note rounding. | R: recomputed. |
| 21 | Low | Ch 9 "How many cases? The paired formula" | "2,745 (they disagree on 31.5%, as in the demo)" | 2,745 is for a single run; two pages later the same demo needs 935 (3-run averages). | Say "single run"; link to 935. | R: recomputed. |
| 22 | Low | Ch 9 / Ch 11 / Q36 peeking | "one look at 400 cases gave a false win 3.7% of the time. Eight looks gave 13.0%" | Counts either direction as "win"; 3.7% < 5% because exact McNemar is conservative; neither explained. | Add both notes. | R: `test_stats.py`. |
| 23 | Low | Ch 8 "Judges inside an A/B test" | "Correct intervals after that correction are an active research area." | The estimator is the classic Rogan-Gladen correction; delta / joint bootstrap intervals exist. Naming from reviewer knowledge, UNVERIFIED at a source. | Name it; suggest joint bootstrap. | R: reasoning. |
| 24 | Low | Ch 9 McNemar; Q34 | (omission) | Only the exact binomial form; chi-square `(b-c)^2/(b+c)` and continuity-corrected form never shown (66 vs 60: p = 0.59 uncorrected, 0.66 corrected/exact). | One line. | S: statsmodels docs; R: recomputed. |
| 25 | Low | Ch 9 "Checkpoint" page | (whole page) | About 202 words vs the 170 limit; only page over. | Trim or split. | R: word-count script. |
| 26 | Low | Ch 13 "The practice loop" vs Ch 14 "How to use the bank" | "answer silently in your head" vs "Write the answer in three bullet points" | Two incompatible practice protocols (recall mode, timing, spacing). | Pick one. | R: read. |
| 27 | Low | Ch 13 / Ch 11 (voice leaks) | "the portfolio project we agreed to build" / "My alarm level here is a strict 0.001" / "I haven't checked their current docs" | Internal-note voice leaks to the reader. | Rephrase. | R: read. |
| 28 | Low | Ch 13 "A two-week plan" | "Skim Chapters 1-9." | Q37-Q50 (Ch 10-12) never scheduled. | "Chapters 1-12". | R: read. |
| 29 | Low | Ch 10 Lab step 1 | "Point `build_from_harness.py` at your Chapter 4 prompts and cases" | Script has no arguments; paths hardcoded. | Add flags or say which lines to edit. | R: read. |
| 30 | Low | Ch 10 "What a framework adds" | "A library of ready-made checks \| One grader" | Stale: Ch 7 gave eight more graders. | Reword. | R: read. |
| 31 | Low | Ch 5 "The helper script" | "one row per failing case" | Writes one row per failing (variant, case); 23 rows from 20 cases in mock. | "per failing case and prompt". | R: ran mock. |
| 32 | Low | Ch 11 SRM; Q43 | "p = 4e-10" | CLI prints `p = 0.0000`. | Print scientific notation for small p. | R: ran `online_tools.py srm`. |
| 33 | Low | Ch 9 H1 title, Ch 10 H1 title | H1 "Did it improve? Reading an A/B result honestly" vs contents "The statistics of comparing A and B"; "...and beyond" vs "...and the other tools" | Titles differ from contents.md. | Align. | R: script compare. |
| 34 | Low | Ch 9 "Worked example: Priya's result" | "`compare_runs.py` on the demo's 400 cases x 3 runs" | `demo.py` writes no records, so the learner cannot reproduce that block. | Add `--export`. | R: grep. |
| 35 | Low | Ch 14 Q30, Q34 | "shrink the gap by (TPR + TNR - 1)"; Weak: "A t-test on the two accuracies" | "Shrink by" reads as subtraction (it multiplies); "t-test" ambiguous vs Ch 9's paired t-interval. | "multiply by"; "unpaired t-test". | R: read. |
| 36 | Low | Ch 2 "The six ingredients" | "Kohavi et al. call this the Overall Evaluation Criterion" | "this" follows the whole table. | "call the primary metric the OEC". | R: read. |
| 37 | Low | Ch 4 Step 2 snippet | `**extra,   # effort, if the config sets it` | `effort="low"` as keyword gives `TypeError` (SDK 2.8.0). Correct: `output_config={"effort": "low"}`. | Show it. | R: SDK probe. |
| 38 | Low | Ch 4 "When something goes wrong" | "Error mentioning `temperature` \| Model doesn't accept it" | Current SDK raises `TypeError` before sending; API 400 comes from API version 2026-10-21 (any value) or non-default on Claude 4.7+ under 2023-06-01. The over-broad "current models don't accept temperature" in Ch 3, Ch 8, Ch 13, Ch 16 is practically right. | Footnote. | S: deprecations + migration-2026-10-21 pages. |
| 39 | Low | Ch 4 "Setup"; `requirements.txt` | "pip install anthropic pyyaml" | Tested on `anthropic` 2.8.0, not pinned (promptfoo is). | Pin. | R: wire log. |
| 40 | Low | Ch 3 "Pin the model" | "Avoid names that quietly point to newer versions." | For Claude, dateless IDs are already pinned snapshots; a learner may hunt for a date suffix. | One line. | S: models overview. |
| 41 | Low | `work/harness/mock_interview.py` (lines ~83, 114); Ch 13 | (code) | Sends assistant turns back as text only, dropping thinking blocks between turns. Probably accepted; UNVERIFIED live. | Append full `resp.content`. | R: code reading. |
| 42 | Low | `work/promptfoo/judge-example.yaml` | `max_tokens: 1024` | Below promptfoo's own default (2048) when thinking is on; truncation shows up as grader error. | 2048+. | S: promptfoo Anthropic docs. |
| 43 | Low | Ch 10 "CI traps we hit" | "`~` doesn't work in `PROMPTFOO_CACHE_PATH`." | promptfoo's own CI page uses `~`; add "don't copy it". | One clause. | S: promptfoo CI/CD page. |
| 44 | Low | Ch 10 "The hosted platforms" | LangSmith "self-hosting is an Enterprise add-on"; Braintrust "diff mode", PR-comment Action, BYOC Enterprise | Not on the cited pages. UNVERIFIED, not wrong. | Cite pricing/self-host pages or soften. | S: fetched cited pages. |
| 45 | Low | Read more, 8 chapters citing Hamel's FAQ | "Frequently Asked Questions (About) AI Evals" by Hamel Husain | Page is now "AI Evals: Everything You Need to Know", by Husain and Shankar (2026-09-18). Other title/wording drifts: GrowthBook ("results", not "outputs"), eval-course (free email series + e-books, full course paid), rate-limits (`retry-after` not on every 429), develop-tests (no dedicated "tips for LLM grading" section), platform.claude.com/docs redirects to /docs/en/home. | Update titles / wording. | S: fetched each page. |
| 46 | Low | Ch 6 / Ch 8 / Ch 13 etc. (minor teaching) | see section "Teaching quality" below | Unexplained jargon and missing formulas (z = 0.84, "config hash", `effort`, NLI/chrF/COMET, F1). | See below. | R: read. |

Also noted (Low): E21 ladder caveats still missing in Ch 3; E3 no grader-noise row in the three-sources table; E15 six ingredients not attributed in text.

### Teaching-quality notes (condensed)
- Ch 2: p-value/CI/power have no worked number; add 52% vs 50% on 1,000 users.
- Ch 3: "config hash" and `effort` never defined.
- Ch 4: Step 5 "code" is pseudocode labelled Python; printed sample numbers will never match mock output. Lab asks for "total cost" but harness prints tokens only (no price source).
- Ch 5: checkpoint Q2 answer is guessable from the question.
- Ch 6: formula uses E and 1.96 without naming them.
- Ch 7: NLI, chrF, BLEURT, COMET, F1 appear without a gloss.
- Ch 8: densest chapter (~20 pages); `corrected_fail_rate` has no formula on the page; Wilson interval is better motivated by Drill 3's "Wald has zero width at 0".
- Ch 9: z = 0.84 not explained; "clustered standard errors" recommended but only per-case averaging shown.
- Ch 11: chi-square and two-proportion used as black boxes.
- Ch 14: Strong answers are clipped fragments; write 3-4 as full 60-second spoken answers. Q5, Q14, Q23, Q40, Q45 Strong answers carry no number.
- Ch 15, 16: strongest practice chapters; no complaints beyond items above.

---

## C) Sources verified

Opened by reviewers (R) or me. Everything below returned content; none dead or blocked.

| URL | What was checked | Result |
|---|---|---|
| https://arxiv.org/abs/2306.05685 (+PDF) | Zheng et al.: biases, 65.0% position consistency, 23-answer repetitive-list attack, self-enhancement | Confirmed. Ch 8 correct; Ch 7 overstates self-preference (issue 19) |
| https://arxiv.org/abs/2305.17926 | Wang et al.: Vicuna-13B 66/80 | Confirmed |
| https://arxiv.org/pdf/2107.03374 | Chen et al.: unbiased pass@k estimator; naive form biased | Confirmed; book omits estimator (issue 6) |
| https://arxiv.org/abs/2406.12045 | tau-bench: pass^k definition and estimator | Confirmed |
| https://arxiv.org/html/2411.00640 | Miller: 3x figure context, averaging repeated samples, bootstrap "unnecessary", power formula | Confirmed; context differs from how Ch 9 uses it (issue 7) |
| https://www.anthropic.com/research/statistical-approach-to-model-evals | "over three times", paired differences | Confirmed; page does not name Miller |
| https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents | pass@k/pass^k, 0.75^3 example, capability vs regression, graders | Confirmed |
| https://www.statsmodels.org/stable/generated/statsmodels.stats.contingency_tables.mcnemar.html | `exact=True` default, binomial | Confirmed |
| https://hamel.dev/blog/posts/evals-faq/ | splits, 30-50 per label, TPR/TNR, Likert advice, correction | Confirmed (first 100k of 154k chars read); title changed (issue 45) |
| https://hamel.dev/blog/posts/llm-judge/, /evals/ | judge steps; three levels | Confirmed |
| https://ai.hamel.dev/eval-course | free course claim | Free email series + e-books; full course paid |
| https://platform.claude.com/docs/en/test-and-evaluate/develop-tests | reason-before-score, different grader model, exact match | Confirmed; no "tips" section |
| https://platform.claude.com/docs/en/build-with-claude/effort.md | `output_config.effort`, defaults, thinking counts toward `max_tokens` | Confirmed |
| https://platform.claude.com/docs/en/about-claude/models/overview.md | model IDs valid; dateless IDs are pinned snapshots | Confirmed |
| https://platform.claude.com/docs/en/api/migration-2026-10-21 and /model-deprecations | temperature removed in 2026-10-21; 60-day notice | Confirmed |
| https://platform.claude.com/docs/en/api/rate-limits.md | `retry-after` semantics | Confirmed with caveat (not on every 429) |
| https://www.promptfoo.dev/docs/{configuration/caching, usage/command-line, configuration/expected-outputs, configuration/expected-outputs/model-graded, configuration/test-cases, providers/anthropic, integrations/ci-cd}/ | cache, flags, exit codes, assertions, CSV `__description`, effort, defaults | All confirmed except items 42-43 |
| https://github.com/promptfoo/promptfoo | MIT, local, "part of OpenAI" | Confirmed |
| https://docs.langchain.com/langsmith/evaluation-concepts; https://langfuse.com/docs/evaluation/overview; https://github.com/langfuse/langfuse; https://docs.braintrust.dev/evaluate | feature claims, Langfuse MIT + GitHub Action | Confirmed except issue 44 |
| https://developers.openai.com/api/docs/deprecations | Evals read-only 2026-10-31, shut down 2026-11-30 | Confirmed; Ch 10 wording matches (M: grep frameworks.md line 265) |
| https://docs.github.com/.../using-secrets-in-github-actions; `gh api` releases for checkout / setup-node / cache / upload-artifact | fork-PR secrets rule; action versions in `eval.yml` | Confirmed (v7, v7, v6, v7 exist) |
| https://www.evanmiller.org/how-not-to-run-an-ab-test.html; https://statsig.com/perspectives/abtesting-llms-misleading; https://www.microsoft.com/en-us/research/articles/diagnosing-sample-ratio-mismatch-in-a-b-testing/ | peeking, sequential rules, SRM threshold (Microsoft uses p < 0.0005) | Confirmed |
| Cambridge page for Kohavi et al.; GitHub ToC for Huyen's AI Engineering | chapter titles | Confirmed (Kohavi Ch 1, 2, 3, 7, 15, 17; Huyen Ch 3, 5, 10) |
| All 45 unique "Read more" URLs (arXiv 7, hamel 4, Anthropic docs/posts 7, OpenAI 3, promptfoo 6, Python docs 3, Wikipedia 3, Eugene Yan 2, interview sites 4, others) | loads and title/claim match | Table with per-URL status in `links.md`: 0 dead, 0 blocked; 2 title mismatches, 1 redirect, rest OK |

Section E of `review-opus.md` re-check (quotes in `stats.md`): fixed = E1, E2, E5, E6, E7, E8, E9, E10, E11, E12, E13, E14, E17, E18, E20, E22 (16, counting E12 as fixed with a wording nit); partly = E3, E4, E15, E19; not fixed = E21; E16 unchanged and fine.

---

## D) Test run results

Python 3.11.9, macOS, `PYTHONDONTWRITEBYTECODE=1`, API key unset. I ran these myself.

| Command | Outcome |
|---|---|
| `python3 test_graders.py` (work/harness) | PASS ("all grader tests passed") |
| `python3 test_judge.py` | PASS ("All judge tests passed.") |
| `python3 test_online.py` | PASS (14,751 per arm; power 0.801; compare CI [+0.0021, +0.0579], p 0.0355; false-positive 0.046) |
| `python3 test_rag_metrics.py` | PASS (pass^3 sim 0.4222 vs 0.4219; pass@3 0.9844) |
| `python3 test_stats.py` | PASS (peeking: one look 0.037, 8 looks 0.130) |
| drills 1-4 `test_drillN.py` (solutions) | 12/12, 11/11 (coverage 0.947), 12/12, 14/14 |
| `python3 check_mutants.py` (work/drills) | OK in 31 s; solutions pass, starters fail, mutants caught (final output shown only partially; reviewer reports 26/26) |
| `bash promptfoo/offline/run_offline_checks.sh SCRATCH` after `npm i promptfoo@0.125.1` in scratchpad (node v26.3.0) | Works: A: 111 passed / 9 failed (expected, exit 100), B-v2 0.950 vs A-v1 0.900; B: 120 requests run 1, 120 after cached run 2, 240 after `--no-cache`; sent keys include `temperature` when base URL is non-default (known, documented); C: default host sends no temperature, `127.0.0.1:9` sends `temperature: 0`. |
| `bash ci-example/simulate_ci_locally.sh SCRATCH` | All 5 scenarios as expected (eval-exit 0/100/100/0, errors-check 1 in scenario 4, sync-check 1 in scenario 5) |
| `run_experiment.py --mock` on the sample config | 120 calls, works; accuracy A 0.783 / B 0.867 (fake) |
| `work/ab-prompt-test/demo.py`, `work/system-design-prompts/sd_numbers.py` | Run; outputs match the numbers in chapters (e.g. 2,103 / 526 / 132 cases, 9,493 users) |
| Reviewers' extra runs (copies of `work/` in scratchpad) | Ch 9 demo seed 7 reproduces every figure; harness resume/edit/truncation/refusal probes (issues 1, 2, 10, 11); real `anthropic` 2.8.0 SDK against a fake local Messages server |

The `.sh` check scripts require a scratch directory argument (and `npm i promptfoo@0.125.1` first); the book's README should show this if it does not already.

First-real-call risks, ranked: (1) stale results after edit (issue 1); (2) truncated or refused replies scored wrong (issue 2); (3) "Refund." scores 0 (issue 11); (4) Ch 3 config copied into Ch 4 crashes (issue 4); (5) 429 bursts (low risk: SDK retries); (6) promptfoo temperature behind a non-default base URL (this machine uses the default host, so not affected); (7) unpinned SDK (issue 39). Verified OK for a first call: text extraction skips thinking blocks; request body is just model, `max_tokens`, system, messages, `output_config.effort`; model IDs valid.

---

## E) Interview-readiness gaps (ranked)

Verdict: enough for the eval part of an AI Engineer loop (offline stats, judge validation, error analysis, coding drills are better than most candidates'; question bank has no wrong Strong answer, though Q4/Q12/Q42/Q48 need the fixes above). At risk in an Evals Engineer loop.

1. **Online statistics beyond the basics.** Unit of analysis (issue 3), ratio metrics (cost per conversation), sequential testing (issue 5), variance reduction (CUPED never mentioned). Directly probed ("what is your unit? can you peek?").
2. **Safety and adversarial evals.** Prompt injection, jailbreaks, PII leakage, over/under-refusal, red-teaming appear only as a slice in Ch 15 P3/P4.
3. **Pairwise / preference evaluation at scale.** Everything is pointwise pass/fail. Missing: win rates with ties, Bradley-Terry / Elo, position-swap intervals, ranking 5 prompts or models.
4. **Model-vs-model decisions.** Non-inferiority rule (issue 15), cost-latency-quality trade-offs; the Ch 4 lab never computes cost.
5. **Benchmark design and measurement validity.** Contamination is one line; no construct validity, saturation, or multi-annotator agreement (Krippendorff/Fleiss, adjudication). Runner-up: production monitoring depth (drift, alert thresholds, judge sampling rates).

---

## F) Things not verified

- Any live API behaviour: real output format for the triage prompt, truncation / refusal / 429 frequency, whether history with thinking blocks stripped is accepted (issue 41).
- Rogan-Gladen naming and interval methods (issue 23); Kohavi chapter number for the delta method (probably Ch 18, not fetched); GrowthBook specifics beyond the title; Atil and Sclar figures not re-fetched this round (earlier review verified them).
- The last ~54k characters of Hamel's FAQ and ~53k of the develop-tests page were not read; RAG / agents / multi-turn / CI-vs-monitoring / guardrails claims are confirmed at section-title level only.
- LangSmith / Braintrust enterprise claims (issue 44); promptfoo `--fail-on-error` in 0.125.1; whether promptfoo caches `llm-rubric` grades.
- "Kohavi Ch 1 is a free download"; Huyen Ch 4 "evaluation criteria" wording; DMLS Ch 9 outline; Practical Statistics chapter number.
- URLs that appear only in `notes/` (not in chapters) were not fetched.
- The GitHub workflow running on GitHub itself; Python 3.9 and 3.14 claims (I ran 3.11 only).
- How pages render at desktop and ~400 px widths (reviewers counted words per page; nobody rendered the book).
- Whether `claude-haiku-5-5` / `claude-sonnet-5-5` are pinned (docs say dateless IDs are pinned snapshots, which supports the book).

Scratchpad worker reports: `/private/tmp/claude-501/-Users-rahulchoudhary--claude-spares-spare-dBXhKb/1e06c6b0-ef0c-49bf-8143-294e6e5b717c/scratchpad/{stats,api,consistency,links}.md`
