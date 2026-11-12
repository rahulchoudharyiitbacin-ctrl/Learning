# Question bank

You've learned the work. An interview asks you to **say** it, under questioning, with numbers.

This chapter has 54 questions in the style that AI Engineer and Evals Engineer interviews use. They are not leaked questions. Prep sites list similar scenarios, such as a prompt that got 12% worse after a model upgrade, or a 95% pass rate while users complain. Read more lists those sources and how far to trust them.

Each question shows:
- **Chapters:** where the book teaches the answer.
- **Weak / OK / Strong:** what each level of answer sounds like.
- **Probes:** follow-ups an interviewer might ask next.

The questions follow the book's order, from why to test, through statistics and rollout, to your own story.

<!-- page -->

## How to use the bank

Don't read the rubric first. Cover it, answer, then score yourself.

**Scoring:**
- **Weak = 0.** Buzzwords, or a wrong idea (for example, "the p-value is the chance B is better").
- **OK = 1.** Correct, but anyone could say it.
- **Strong = 2.** Specific. It has a number, a named failure mode, or a trade-off.

**Three passes per question:**
1. **Recall.** Write the answer in three bullet points, no book.
2. **Say it out loud.** Time yourself: aim for 60 to 90 seconds. Record it if you can.
3. **Add numbers.** Put in one real figure from your own labs: cases, runs, an interval, a TPR.

Then answer each probe in one or two sentences. A probe you can't answer caps you at OK.

<!-- page -->

## Track your progress

Keep a small table per question. Score each pass 0, 1 or 2.

| Question | Passes 1 / 2 / 3 | Review again |
|---|---|---|
| Q7 (12% drop) | 1 / 1 / 2 | in 7 days |
| Q26 (94% agree) | 0 / 1 / 1 | tomorrow |
| Q31 (+3 points) | 2 / 2 / 2 | in 14 days |

**Rules of thumb:**
- Any 0: reread the chapter, then retry tomorrow.
- A 1 that won't become 2: you're missing a number. Get it from your labs.
- Three 2s in a row: review in two weeks.

Practise with a friend or an LLM playing interviewer. Give it the question and the probes, and ask it to push back. Score yourself with the rubric, not its praise.

<!-- page -->

## Why test, and A/B basics

**Q1. Why A/B test a prompt change? Why not just try it?**
*Chapters:* 1, 2
- **Weak:** "I try a few inputs and see if it looks better."
- **OK:** Few examples aren't enough, and outputs are random.
- **Strong:** Three sources of variation: the prompt, run noise, and which cases you sampled. Fix everything but the prompt, use a fixed set with repeats, and choose the metric first. Formatting alone moved accuracy up to 76 points on some tasks on LLaMA-2-13B (Sclar).

*Probes:* Isn't temperature 0 deterministic? · Who decides what "better" means?

**Q2. What do you write down before running an A/B test?**
*Chapters:* 2, 3
- **Weak:** "The two prompts and the test set."
- **OK:** A hypothesis and a metric.
- **Strong:** All six: hypothesis with direction and size, unit, one primary metric, guardrails, sample size, decision rule. Frozen before results.

*Probes:* Why freeze it? · Can you explore first?

<!-- page -->

## Why test, and A/B basics

**Q3. How is a prompt A/B test different from testing a button colour?**
*Chapters:* 2
- **Weak:** "It's the same thing."
- **OK:** LLM outputs vary, so you need more samples.
- **Strong:** Output varies even at temperature 0; quality needs a grader; formatting alone can swing results; the model underneath can change; per-request cost joins latency as a guardrail.

*Probes:* What causes variation at temperature 0? · How do you guard against model drift?

**Q4. When is an online A/B test not worth doing?**
*Chapters:* 1, 11
- **Weak:** "Always run one, it's best practice."
- **OK:** When there is too little traffic.
- **Strong:** Husain's three levels: unit tests, model and human eval, then A/B. A/B usually suits mature products. Skip it for throwaway scripts. Most changes are checked offline, at levels 1 and 2.

*Probes:* What does online tell you that offline can't? · How long would it run?

<!-- page -->

## Experiment design and reproducibility

**Q5. How do you make a prompt experiment reproducible?**
*Chapters:* 3
- **Weak:** "I save my notebook."
- **OK:** Version the prompts and pin the model.
- **Strong:** Prompts and datasets as frozen files in git; one experiment file with model ID, settings, dataset, grader, runs, metric and decision rule; raw outputs saved with a config hash.

*Probes:* What if a tested prompt needs a fix? · Why save raw outputs?

**Q6. Prompt B changed the instructions, added examples and switched to JSON. It won. What did you learn?**
*Chapters:* 3
- **Weak:** "B's approach is better."
- **OK:** Only that the bundle won.
- **Strong:** You can't tell which change helped; one may have hurt. Test a ladder, one change at a time, on dev. Confirm the final winner once on test.

*Probes:* What does the ladder cost you? · What happens if you run the ladder on the test set?

<!-- page -->

## Experiment design and reproducibility

**Q7. After a model upgrade, your prompt scores 12% worse on the internal test set. What do you do?**
*Chapters:* 3, 4, 5, 9
- **Weak:** "Roll back and rewrite the prompt."
- **OK:** Compare outputs from the old and new model.
- **Strong:** Confirm it's real: same set and grader, repeats, paired interval. Check settings: rejected parameters, empty outputs at `max_tokens`. Read disagreements: grader (format) or model? Fix on dev, confirm on test.

*Probes:* How would the grader cause it? · Would you pin the old model meanwhile?

**Q8. Why run A and B in the same shuffled batch?**
*Chapters:* 3, 4
- **Weak:** "It's faster."
- **OK:** So conditions are the same.
- **Strong:** If the service changes mid-run, both variants face it. A on Monday and B on Friday can blame the prompt for the model.

*Probes:* Does `seed` make outputs repeatable? · What else do you lock?

<!-- page -->

## Harness and engineering

**Q9. Walk me through a small eval harness you'd build.**
*Chapters:* 4
- **Weak:** "A loop that calls the API and prints accuracy."
- **OK:** Reads cases, calls the model, grades, saves results.
- **Strong:** Experiment file in; cases x variants x runs, shuffled; parallel calls with resume; one record per call (output, grade, tokens, latency, config hash); errors stored; runs averaged per case, then paired.

*Probes:* How do you handle 429s? · Why a mock run first?

**Q10. Your first real run shows many empty outputs. What's going on?**
*Chapters:* 4
- **Weak:** "The model is broken."
- **OK:** Check the error messages.
- **Strong:** Look at `stop_reason`. If it says `max_tokens`, thinking used the budget: raise it. That's why you smoke test 5 cases before 120 calls. Count errors; don't drop them.

*Probes:* What else do you check in a smoke test? · Should empty outputs count as fails?

<!-- page -->

## Harness and engineering

**Q11. Your token bill tripled last month and nobody changed the code. What happened?**
*Chapters:* 3, 4, 8, 11
- **Weak:** "The provider raised prices."
- **OK:** Look at usage logs.
- **Strong:** Split tokens in and out by prompt and model version. Suspects: a model or effort change that thinks longer, retries, longer context, more traffic, new judge calls. Only answerable if every request logs its versions.

*Probes:* What would you log? · How would you alert on it?

**Q12. A cheaper model scores 2 points lower and costs much less. Do you switch?**
*Chapters:* 2, 3, 9
- **Weak:** "Yes, cost wins."
- **OK:** It depends on the business.
- **Strong:** Set the largest acceptable loss before testing. Check the paired interval's lower end against it, plus key slices and p95 latency. A 2-point estimate may hide a 5-point loss.

*Probes:* Who sets the acceptable loss? · Could a better prompt close the gap?

<!-- page -->

## Error analysis

**Q13. Your new prompt scored 3 points lower. What do you do first?**
*Chapters:* 5
- **Weak:** "Tweak the prompt and rerun."
- **OK:** Look at the failures.
- **Strong:** Read failures, then cases where A and B disagree, then a few passes. Note each one. Group into 4 to 8 categories, count, fix the biggest cheap one with one change, rerun.

*Probes:* Why read passing cases? · How many cases would you read?

**Q14. Explain open coding and axial coding.**
*Chapters:* 5
- **Weak:** "Tagging data."
- **OK:** Writing notes, then grouping them.
- **Strong:** Open: one note per failure, describing what you see, first failure only. Axial: merge notes into named categories, keep "other" small. Stop at saturation, when new cases add no new kinds.

*Probes:* Who should write the notes? · When do you redo it?

<!-- page -->

## Error analysis

**Q15. A failing case looks correct to you. Where does the failure live?**
*Chapters:* 5, 7
- **Weak:** "It's a model error."
- **OK:** Maybe the grader is wrong.
- **Strong:** Four places: prompt, model, grader, dataset. Check grader and dataset first, since they're cheap. Exact match failing "Refund." for "refund" is a grader bug. An arguable label is a dataset fix.

*Probes:* How do you test a grader? · What if the label itself is wrong?

**Q16. You have 15 failures. Why not add a prompt rule for each?**
*Chapters:* 5, 6
- **Weak:** "That's how you fix them."
- **OK:** The prompt gets too long.
- **Strong:** You overfit those cases. The prompt grows strange, other cases may break, and the score stops meaning much. Fix the pattern, then turn the failures into test cases.

*Probes:* How do you know a fix didn't break others? · Where do these cases go?

<!-- page -->

## Datasets

**Q17. You have 100,000 user interactions. How do you build a 500-item eval set?**
*Chapters:* 6, 5
- **Weak:** "Take 500 at random; an LLM labels them."
- **OK:** Sample, label, split.
- **Strong:** Strip personal data. Random sample, then target rare failures. Tag slices. An expert labels to a guideline; a second labeller on 20 finds unclear rules. Stratified dev/test. 500 cases measure one accuracy near 80% to about ±3.5 points.

*Probes:* Is 500 enough to compare two prompts? · How do you find rare failures?

**Q18. Your eval shows a 95% pass rate, but users complain. What's wrong?**
*Chapters:* 6, 8, 11, 12
- **Weak:** "Users are never happy."
- **OK:** The test set isn't representative.
- **Strong:** Cases unlike real traffic; a judge with low TPR; a metric users don't value; a saturated suite. Analyse complaints; add them as cases.

*Probes:* How do you check the judge? · What do you measure online?

<!-- page -->

## Datasets

**Q19. Why keep a separate test set? What is leakage?**
*Chapters:* 6, 3
- **Weak:** "It's standard machine learning practice."
- **OK:** So the score isn't biased.
- **Strong:** Tuning against cases makes the prompt fit them. Tune on dev, check test once. Leakage: a test case pasted into the prompt, a judge tuned on test cases, duplicates across dev and test.

*Probes:* What if you've peeked at test often? · How about public benchmarks?

**Q20. B wins by 2 points overall but loses on Hinglish messages. What do you do?**
*Chapters:* 6, 9, 5
- **Weak:** "Ship it, it wins overall."
- **OK:** Look into the Hinglish cases.
- **Strong:** Check the slice's size: slices are exploratory, and 15 cases is noise. Read those failures. If real, fix the prompt or route that slice to A, then confirm on fresh cases.

*Probes:* How many cases make a slice worth reading? · Why can't you test every slice?

<!-- page -->

## Evaluation methods

**Q21. How would you evaluate a summarisation feature?**
*Chapters:* 7, 8
- **Weak:** "ROUGE score against a reference."
- **OK:** An LLM judge for quality.
- **Strong:** Code checks first (length, banned phrases). Then consistency with the source, via NLI or a validated judge. A pass/fail judge per criterion, checked against human labels. ROUGE only as a weak signal: fluent, wrong text can score well.

*Probes:* Why one criterion per judge? · What makes a good reference?

**Q22. A fraud detector is 99% accurate, and fraud is 1% of cases. Good?**
*Chapters:* 7
- **Weak:** "Yes, 99% is great."
- **OK:** Accuracy misleads on imbalanced data.
- **Strong:** Never flagging fraud also scores 99%. Report recall (fraud caught) and precision (flags that are right), with a confusion matrix. Choose the trade-off by the cost of a miss versus a false alarm.

*Probes:* What's F1 for? · Which error costs more here?

<!-- page -->

## Evaluation methods

**Q23. How would you grade a JSON extraction task?**
*Chapters:* 7
- **Weak:** "An LLM judge checks it."
- **OK:** Check it's valid JSON.
- **Strong:** Two scores: all fields right (pass/fail per case) and field accuracy, which shows which field fails. Handle prose and code fences around JSON. A missing field is a fail.

*Probes:* Strict or lenient parsing? · How do you grade numbers?

**Q24. When would you use an LLM judge instead of code, humans or user signals?**
*Chapters:* 7, 8, 11
- **Weak:** "LLM judges for everything; they're flexible."
- **OK:** Judges for subjective things.
- **Strong:** Take the first that works: code check, similarity, judge, human review, user signals. Judges only where reading is needed, and only once validated. User signals are noisy and biased, so investigate them; don't treat them as grades.

*Probes:* Why not a thumbs-up rate as the metric? · What do humans still do?

<!-- page -->

## LLM judges and validation

**Q25. How do you know your LLM judge is right?**
*Chapters:* 8
- **Weak:** "I spot-checked it and it looked good."
- **OK:** Compare it with human labels.
- **Strong:** One criterion. Expert PASS/FAIL labels with critiques. Split train/dev/test; iterate on dev, score test once. Report TPR and TNR, failure as positive, with n and intervals; aim for 30 to 50 of each label.

*Probes:* Why failure as positive? · What if test is much worse than dev?

**Q26. Your judge agrees with the expert 94% of the time. Ship it?**
*Chapters:* 8, 7
- **Weak:** "Yes, 94% is high."
- **OK:** Check kappa too.
- **Strong:** If failures are 5%, an always-PASS judge gets 95%. In the book's example, 94% agreement hid a TPR of 20%: 2 of 10 rude replies caught, kappa 0.22. Report TPR, TNR and kappa.

*Probes:* What does kappa measure? · Which matters more here, TPR or TNR?

<!-- page -->

## LLM judges and validation

**Q27. Binary pass/fail or a 1 to 5 scale for the judge?**
*Chapters:* 8, 7
- **Weak:** "1 to 5, it's more detailed."
- **OK:** Binary is simpler.
- **Strong:** Nobody can say what separates a 3 from a 4, graders drift to the middle, and scales need bigger samples. Use pass/fail with a critique before the verdict. Track progress by splitting into several pass/fail checks.

*Probes:* How do you write the rubric? · Where do examples come from?

**Q28. What biases do LLM judges have, and what do you do about them?**
*Chapters:* 8
- **Weak:** "They're biased, so use humans."
- **OK:** Position bias and length bias.
- **Strong:** Position (Zheng: GPT-4 kept its verdict after a swap only 65% of the time), verbosity, possible self-preference. Run pairwise in both orders; disagreement is a tie. Measure your own judge.

*Probes:* Same model as judge and generator? · How do you test verbosity bias?

<!-- page -->

## LLM judges and validation

**Q29. When do you re-validate a judge?**
*Chapters:* 8, 5
- **Weak:** "Once validated, it's done."
- **OK:** When the model changes.
- **Strong:** After any change to judge model or prompt, new failure modes, or criteria drift (Shankar et al.: grading outputs changes people's criteria). Version the labelled sets so the check reruns fast.

*Probes:* What is criteria drift? · How often would you schedule it?

**Q30. A judge says B beats A by 4 points. What goes next to that number?**
*Chapters:* 8, 9
- **Weak:** "The p-value."
- **OK:** The judge's accuracy.
- **Strong:** The judge's TPR and TNR, with intervals and n, plus how often repeat runs disagree. Same errors on both shrink the gap by (TPR + TNR − 1): 0.8 and 0.9 turn 10 points into 7. Uneven errors can invent a win.

*Probes:* How could it err differently on B? · What do you read by hand?

<!-- page -->

## Statistics

**Q31. B scores +3 points over A. Do you ship?**
*Chapters:* 9, 3
- **Weak:** "Yes, 3 points is a clear win."
- **OK:** Only if significant.
- **Strong:** Not on the point estimate. Paired, case-level interval: lower bound above 0, gain at least the pre-set minimum, guardrails fine. Chapter 9's demo: +3.0, CI −0.2 to +6.2, not proven; needs about 935 cases.

*Probes:* What do you tell your manager? · Why a minimum gain?

**Q32. What does a p-value of 0.03 mean? And a 95% interval?**
*Chapters:* 2, 9
- **Weak:** "97% chance B is better." "95% chance the truth is in the range."
- **OK:** The result is significant.
- **Strong:** If A and B were equal, a gap this big or bigger would appear 3% of the time. The interval's method captures the true gain 95% of the time. Crossing 0 means not shown, not "no effect".

*Probes:* What's power? · Significant but unimportant?

<!-- page -->

## Statistics

**Q33. 300 cases, 5 runs each. A colleague computes the interval over 1,500 rows. Problem?**
*Chapters:* 9, 3
- **Weak:** "More rows, more precise. Fine."
- **OK:** The runs aren't independent.
- **Strong:** Runs of one case are correlated, so the interval is too narrow. Average per case and use 300 differences, or cluster by case. In the book's simulation, row-level intervals caught the truth 80% of the time, not 95%.

*Probes:* More runs or more cases? · Paired vs unpaired width?

**Q34. With pass/fail grades, how do you test the difference?**
*Chapters:* 9
- **Weak:** "A t-test on the two accuracies."
- **OK:** McNemar's test.
- **Strong:** McNemar uses only discordant cases: B-only and A-only passes. Under no difference each is a 50/50 coin flip. Concordant cases carry no information. Add the interval for the size of the gain.

*Probes:* With several runs per case? · Why ignore the ties?

<!-- page -->

## Statistics

**Q35. How many test cases do you need to compare two prompts?**
*Chapters:* 9, 6
- **Weak:** "About 100 is standard."
- **OK:** Depends on the effect size.
- **Strong:** For a paired test it depends on the smallest gain worth shipping and how often the prompts disagree, not accuracy alone. For +3 points: about 870 cases at 10% disagreement, about 2,600 at 30%. Get the rate from a pilot.

*Probes:* What if you have 200 cases? · Halve the gain?

**Q36. You tested five variants and ten metrics. One wins. Believe it?**
*Chapters:* 9, 11
- **Weak:** "Yes, it was significant."
- **OK:** Correct for multiple comparisons.
- **Strong:** Five tests at 5% give up to about 23% chance of a false win. Pre-declare one primary metric, use Bonferroni or Holm, treat slices as leads. Don't peek: 8 looks gave 13% false wins in the book's simulation.

*Probes:* Holm vs Bonferroni? · Why does peeking inflate errors?

<!-- page -->

## Frameworks and CI

**Q37. You use an eval framework. What wouldn't you trust its dashboard for?**
*Chapters:* 10, 9
- **Weak:** "Nothing, the tool handles it."
- **OK:** It may not show significance.
- **Strong:** The pass rate counts every repeat as a test, isn't paired by case, and has no interval. Export per-case results and run the paired analysis. Check what the tool sends and caches: promptfoo added `temperature: 0` through a proxy in the book's test.

*Probes:* What would you export? · How do you check what it sends?

**Q38. You rerun an eval to see variation and every answer is identical. Why?**
*Chapters:* 10, 2
- **Weak:** "The model is deterministic."
- **OK:** Caching.
- **Strong:** Answers were served from the cache, so the rerun isn't a new sample. Use `--no-cache`. Same after fixing a grader: cached grades come back.

*Probes:* When is caching good? · How long does the cache last?

<!-- page -->

## Frameworks and CI

**Q39. Design a CI gate for prompt changes.**
*Chapters:* 10, 12
- **Weak:** "Fail if accuracy drops."
- **OK:** Run the eval on each pull request with a threshold.
- **Strong:** Gate the prompt being shipped, not A and B together. Fail on errors as well as pass rate. Key as a secret. Regression suites should pass nearly always.

*Probes:* How do you avoid flaky gates? · Cost of running it per PR?

**Q40. How would you choose between promptfoo, LangSmith, Langfuse and Braintrust?**
*Chapters:* 10
- **Weak:** "The most popular one."
- **OK:** It depends on team needs.
- **Strong:** Match to the situation: local and git for learning; PR gates; shared review; regulated data means local or self-hosted; production monitoring means hosted tracing. The loop matters more than the tool.

*Probes:* Why not OpenAI Evals now? · What do you lose with a framework?

<!-- page -->

## Online A/B and rollout

**Q41. Your prompt won offline. How do you roll it out?**
*Chapters:* 11
- **Weak:** "Ship to everyone and watch."
- **OK:** Canary first, then an A/B test.
- **Strong:** Shadow; canary of 1 to 5% behind a flag with a kill switch, watching errors, latency, cost, refusals; then 50/50 by user, one primary metric, guardrails, sized in advance, two weeks or more.

*Probes:* What can shadow not tell you? · What's your rollback rule?

**Q42. Offline evals are paired. Online tests are randomised. Explain.**
*Chapters:* 2, 9, 11
- **Weak:** "Both are random splits."
- **OK:** Online splits users; offline uses a test set.
- **Strong:** Offline, every case gets both prompts, so you analyse per-case differences. Online, each user gets one arm by stable hashing, so you compare two independent groups. Randomise by user, not request.

*Probes:* Why does a request split contaminate metrics? · What's the unit offline?

<!-- page -->

## Online A/B and rollout

**Q43. You planned 50/50 and got 52,000 vs 50,000 users. Problem?**
*Chapters:* 11
- **Weak:** "Close enough to 50/50."
- **OK:** Run a chi-square test.
- **Strong:** That's a sample ratio mismatch: p about 4e-10. Something is broken: assignment, logging, bots or crashes in one arm. Don't read results until you find it. The same ratio at 5,000 vs 5,200 gives p about 0.05.

*Probes:* Why does the same ratio differ? · What alarm level?

**Q44. B won offline but is flat online after two weeks. Why?**
*Chapters:* 11, 5, 6
- **Weak:** "The online test was wrong."
- **OK:** Users behave differently.
- **Strong:** Test set not representative; offline metric not what users value; effect diluted to a small share of conversations; novelty early on. Do error analysis on online conversations and feed cases back.

*Probes:* What if it looked strong on day three? · How would you change the offline metric?

<!-- page -->

## RAG, agents, multi-turn

**Q45. How would you evaluate a RAG chatbot?**
*Chapters:* 12, 8
- **Weak:** "Ask a judge if answers are good."
- **OK:** Evaluate retrieval and generation.
- **Strong:** Split it. Retrieval: queries with labelled relevant docs, Recall@k and MRR. Generation: context relevant, answer faithful to context, answer addresses the question, via error analysis and validated judges.

*Probes:* Compute MRR for a hit at rank 3? · Where do relevance labels come from?

**Q46. Retrieval looks fine, but answers are wrong a third of the time. Debug it.**
*Chapters:* 12, 5, 8
- **Weak:** "Use a bigger model."
- **OK:** It's a generation problem.
- **Strong:** Check "fine" means Recall@k on labelled queries. Read wrong answers: was the right document in context? Unfaithful, or not answering the question? Categorise and count. Build and validate a faithfulness judge.

*Probes:* What if the doc ranked low? · Faithfulness at scale?

<!-- page -->

## RAG, agents, multi-turn

**Q47. An agent says "Refund issued" but no refund exists. What went wrong in your eval?**
*Chapters:* 12
- **Weak:** "The agent hallucinated."
- **OK:** Check what it actually did.
- **Strong:** You graded the transcript, not the outcome. Grade the final state, like a refund record in the database. Start each trial in a clean environment, since shared state causes correlated failures.

*Probes:* When do step-level checks matter? · What graders would you use?

**Q48. pass@k or pass^k for an agent?**
*Chapters:* 12
- **Weak:** "They're the same."
- **OK:** pass@k is any success, pass^k all succeed.
- **Strong:** At 75% per trial, pass@3 is about 98%, pass^3 about 42%. Use pass^k when users need it right every time. Trials of one task aren't independent, so cluster by task.

*Probes:* What about at k = 10? · Which suits a coding assistant?

<!-- page -->

## RAG, agents, multi-turn

**Q49. How would you evaluate a multi-turn support conversation?**
*Chapters:* 12, 5
- **Weak:** "Score every turn 1 to 5."
- **OK:** Judge the whole conversation.
- **Strong:** Pass/fail on whether the whole conversation met the user's goal. Find the first upstream failure; later ones cascade. Reproduce it with the simplest test, often one turn. Simulated users or N−1 testing for cases.

*Probes:* What is N−1 testing? · Why the first failure?

**Q50. What's the difference between capability evals and regression evals?**
*Chapters:* 12, 10
- **Weak:** "Regression evals are for regressions."
- **OK:** One tests new skills, one checks old ones.
- **Strong:** Capability: "can it do this at all?", starting low with room to climb. Regression: "does it still do what it did?", passing nearly always, ideal for CI. Mastered capability tasks can graduate into the regression suite.

*Probes:* Which goes in CI? · What does a 100% capability suite tell you?

<!-- page -->

## Behavioural and resume

**Q51. "How do you know your AI feature is good? Not your gut. Your number."**
*Chapters:* 13, 9, 8
- **Weak:** "You can tell when it's working."
- **OK:** "We track accuracy on a test set."
- **Strong:** Your real number with context: metric, n, interval, judge TPR and TNR, what it can't detect. Made-up example: "300 cases, +4 points, CI +1 to +7, judge TPR 0.85."

*Probes:* How was the set built? · What would change your mind?

**Q52. Tell me about a test where the answer was "not proven".**
*Chapters:* 9, 13
- **Weak:** No example, or everything won.
- **OK:** "It wasn't significant, so we didn't ship."
- **Strong:** The interval, why it was wide, the case count you'd need, and what you did: grew the set, tried a bigger change, or kept A. No rerunning until green.

*Probes:* Did anyone push to ship anyway? · What would you change?

<!-- page -->

## Behavioural and resume

**Q53. Tell me about a time a judge or grader disagreed with humans.**
*Chapters:* 8, 5, 13
- **Weak:** "Our judge was always accurate."
- **OK:** "We fixed the rubric until it agreed."
- **Strong:** Which criterion, the TPR or TNR before and after, how many labels, what reading the disagreements showed, and that you tuned on dev and scored test once.

*Probes:* Who labelled? · Did the criteria change while labelling?

**Q54. Your resume says "A/B testing for prompts". Walk me through it.**
*Chapters:* 3, 4, 9, 10, 13
- **Weak:** A polished story with practices you didn't do.
- **OK:** Correct steps with no numbers.
- **Strong:** Only what you did, with your numbers: cases, runs, model pinning, grader and its validation, interval, verdict, cost. Name limits: "200 cases, so only big gains."

*Probes:* Why that many runs? · How did you compute the interval?

<!-- page -->

## Scoring sheet

Score 0 (Weak), 1 (OK) or 2 (Strong), from your third pass.

| Theme | Questions | Your score |
|---|---|---|
| Why test, A/B basics | Q1-4 | __ / 8 |
| Experiment design | Q5-8 | __ / 8 |
| Harness, engineering | Q9-12 | __ / 8 |
| Error analysis | Q13-16 | __ / 8 |
| Datasets | Q17-20 | __ / 8 |
| Evaluation methods | Q21-24 | __ / 8 |

| Theme | Questions | Your score |
|---|---|---|
| LLM judges | Q25-30 | __ / 12 |
| Statistics | Q31-36 | __ / 12 |
| Frameworks, CI | Q37-40 | __ / 8 |
| Online A/B | Q41-44 | __ / 8 |
| RAG, agents, multi-turn | Q45-50 | __ / 12 |
| Behavioural | Q51-54 | __ / 8 |

**Total:** __ / 108. Under half in a theme? Reread its chapters first.

<!-- page -->

## Read more

- **Calibrd**, AI Engineer interview prep: loop shape, eval scenarios (the 12% drop). Says its questions are representative, not reported. [calibrd.com](https://www.calibrd.com/interview-prep/ai-engineer)
- **KORE1** (recruiter blog), *AI engineer interview questions 2026*: "Your number", token bill tripled. [kore1.com](https://www.kore1.com/ai-engineer-interview-questions-2026/)
- **techinterview.org** (unsourced prep site), evals roles: 95% pass but users complain, 500 items from 100K. [techinterview.org](https://www.techinterview.org/post/3233475313/interviewing-ai-eval-engineering-roles-2026/)
- **Anthropic** job post, Research Engineer, Post-Training Model Evaluations. [greenhouse.io](https://job-boards.greenhouse.io/anthropic/jobs/5198255008)
- **Eugene Yan**, *Product Evals in Three Simple Steps*: label, align evaluators (recall on fails, kappa), run on every change. [eugeneyan.com](https://eugeneyan.com/writing/product-evals/)
- **Hamel Husain**, *Frequently Asked Questions About AI Evals*: error analysis, judge alignment, multi-turn. [hamel.dev](https://hamel.dev/blog/posts/evals-faq/)
- **Anthropic**, *Demystifying evals for AI agents*. [anthropic.com](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- **Next chapter:** system-design prompts.
