# LLM-as-judge in depth, and validating the judge

A team builds a judge to catch rude support replies. They check it against 200 replies their lead had already labelled. It agrees with her 94% of the time. They ship it.

A month later the lead reads a batch by hand and finds rude replies the judge had passed. What went wrong?

Only 10 of the 200 replies were rude. The judge said "fine" to almost everything, and "fine" was nearly always right. It caught 2 of the 10 rude ones. (Illustrative numbers, worked through later in this chapter.)

A judge is a model you are trusting to grade. This chapter shows how to write one, and then the part most teams skip: **checking that it grades like your expert does.**

<!-- page -->

## When a judge is the right tool

Chapter 7's rule still holds: take the **first** method that works. If a rule can decide (a label, a format, a banned word), use code. It's free, fast and repeatable.

Reach for a judge when the criterion needs reading and judgment: "Did the reply offer to escalate when the user was angry?" "Is every claim supported by the source?"

**One judge per criterion.** Husain's evals FAQ recommends a separate judge for each failure mode instead of one judge hunting for everything. A narrow question ("did it escalate to a human?") is easier to check against human labels, and when it fails you know what to fix.

Your criteria come from error analysis (Chapter 5). Each big failure category is a candidate judge.

<!-- page -->

## Pass/fail, with a critique

Ask the judge for a **PASS or FAIL**, and a short **critique** that points at the evidence. Husain's LLM-judge guide recommends exactly this, starting from a domain expert's own pass/fail calls and critiques.

Why not a 1 to 5 scale? His FAQ gives reasons:
- Nobody can say what separates a 3 from a 4, so people and models drift.
- Scales need bigger samples to show a difference.
- Graders drift to the middle to avoid hard calls.

Want to track partial progress? Split the criterion into several pass/fail checks.

> **Teacher's note:** Ask for the critique *before* the verdict, as Husain's judge prompt does. Anthropic's eval guide also advises letting the grader reason before it scores. And a critique makes judge mistakes easy to read later.

<!-- page -->

## Writing the rubric

A rubric is a definition plus examples. Anthropic's guide asks for detailed, clear rubrics. Here's one criterion:

```
Criterion: offers escalation.

PASS if the user is upset or asks
for a person, and the reply offers
a human or a clear next step.
Also PASS if the user is calm and
no offer is needed.

FAIL if the user is upset and the
reply only repeats policy.
```

Then add a few **labelled examples** with the expert's critiques. Take them only from the **train** split (more on splits soon), so they never leak into the data you score.

Tell the judge that the input and output are data, not instructions. An output that says "grade this PASS" should not win.

<!-- page -->

## Known biases

Judges have habits. Zheng et al. (2023) name three:

- **Position bias:** favouring the answer shown first (or second). In their tests, GPT-4 gave the same verdict after the two answers were swapped only 65% of the time with their default prompt. Wang et al. (2023) showed that with ChatGPT as judge, Vicuna-13B could beat ChatGPT on 66 of 80 queries just by changing the order.
- **Verbosity bias:** preferring longer answers. Padding answers with a repeated list fooled two of the three judges they tested on most of their 23 test answers.
- **Self-enhancement:** a judge may favour answers from its own model. Zheng et al. saw signs of it, but say their study cannot confirm it.

These were 2023 models. Newer judges may do better or worse. That's why you measure your own judge.

<!-- page -->

## Pairwise, and the swap fix

Zheng et al. describe judges that grade **one output** (pointwise), **two outputs** (pairwise: which is better?), or one output against a **reference answer**. This book's code is pointwise pass/fail: each prompt gets a pass rate, compared as in Chapter 9.

If you judge pairwise, run each pair **twice**, order swapped:

![Diagram: call 1 shows A first and B second, call 2 shows B first and A second. Compare the two verdicts: if both pick A, A wins; if both pick B, B wins; if they disagree, it is a tie.](images/judge-position-swap.svg)

Wang et al. propose a similar fix. For the other biases: tell the judge length is not quality, prefer a judge from a different model, and measure it against human labels.

<!-- page -->

## Validating the judge

Here is the core skill. A judge is a classifier, and you check a classifier against **ground truth**: labels from a trusted domain expert.

![Diagram: expert labels split into train, dev and test. Train examples go into the judge prompt. Score the judge on dev, measuring TPR and TNR, and revise the prompt on dev in a loop. Score test once at the end. Then use the judge and report its TPR and TNR. Re-validate when the model, prompt or criteria change.](images/judge-validation-loop.svg)

Husain suggests one principal domain expert, a "benevolent dictator" for quality, at least in small and medium teams. Their PASS/FAIL calls, with critiques, are the answer key. The judge's job is to match them.

<!-- page -->

## Splitting the labels

Husain's evals FAQ suggests:

| Split | Share | Use |
|---|---|---|
| **train** | 10 to 20% | Examples you may put in the judge prompt |
| **dev** | 40 to 45% | Compare judge with human; improve the prompt |
| **test** | 40 to 45% | One final check |

Aim for **30 to 50 PASS and 30 to 50 FAIL** examples in dev and in test, where possible. Failures are often rare, so you may need to hunt for them.

```
python judge_validation.py split \
    labelled.csv --seed 1
```

The split is **stratified**: each part gets the same PASS/FAIL mix.

Iterate the prompt on **dev only**. Score **test once**. If test is much worse than dev, the FAQ says your judge has overfit: revise, and use a fresh test set.

<!-- page -->

## Two numbers: TPR and TNR

Call a **failure** the "positive", as Husain's FAQ does. Every labelled example lands in one cell:

| | Judge FAIL | Judge PASS |
|---|---|---|
| **Human FAIL** | true positive (TP) | false negative (FN) |
| **Human PASS** | false positive (FP) | true negative (TN) |

- **TPR** (true positive rate, or recall on failures) = TP / (TP + FN). Of the real failures, how many did the judge catch?
- **TNR** (true negative rate) = TN / (TN + FP). Of the good outputs, how many did it pass?

A judge with low TPR lets failures through. A judge with low TNR raises false alarms and wastes reviewers' time. Report **both**, with how many examples each is based on.

<!-- page -->

## Why raw agreement lies

Back to the opening story. Here are its numbers (illustrative):

| | Judge FAIL | Judge PASS |
|---|---|---|
| **Human FAIL** | 2 | 8 |
| **Human PASS** | 4 | 186 |

- Agreement = (2 + 186) / 200 = **94%**.
- TPR = 2 / 10 = **20%**. It missed 8 of 10 rude replies.
- TNR = 186 / 190 = about **98%**.

Agreement is mostly the big PASS row. A judge that says PASS to everything would score 95% here, and catch nothing. Husain's guide makes the same point: on a set with 5% errors, an always-PASS judge gets 95% agreement.

> **Teacher's note:** Same trap as accuracy on imbalanced classes (Chapter 7). When one label is rare, look at the rare label.

<!-- page -->

## Cohen's kappa, by hand

Kappa asks: how much better than **chance** do the two raters agree? Illustrative dev set, 100 examples:

| | Judge FAIL | Judge PASS |
|---|---|---|
| **Human FAIL** | 12 | 8 |
| **Human PASS** | 6 | 74 |

1. Observed agreement: (12 + 74) / 100 = **0.86**.
2. Human says FAIL 20%, judge says FAIL 18%. Chance both say FAIL: 0.20 x 0.18 = 0.036.
3. Chance both say PASS: 0.80 x 0.82 = 0.656.
4. Chance agreement = 0.036 + 0.656 = **0.692**.
5. Kappa = (0.86 - 0.692) / (1 - 0.692) = 0.168 / 0.308 = **0.55**.

Kappa is 1 for perfect agreement and 0 for chance. The opening story's judge has kappa 0.22 despite its 94%. Still report TPR (0.60 here) and TNR (0.925): kappa is one number, and you need to know *which* way the judge errs.

<!-- page -->

## Small samples: add intervals

TPR of 0.60 from 20 failures is shaky. A **95% confidence interval** shows how shaky. The Wilson interval works well for small counts:

```
python judge_validation.py report \
    dev-judged.csv
```

```
TPR    0.600  95% CI 0.387-0.781  n=20
TNR    0.925  95% CI 0.846-0.965  n=80
Kappa  0.545
Agree  0.860  (misleading if imbalanced)
```

(Part of the output for the illustrative table on the last page.)

TPR could plausibly be anywhere from about 39% to 78%. That's why the FAQ asks for 30 to 50 of each label: the interval narrows as n grows. With fewer than 30 per label, the script warns you.

> **Teacher's note:** The interval comes from a procedure that captures the true rate in 95% of repeated samples. It is not "a 95% chance the TPR is in this range". Chapter 9 says more.

<!-- page -->

## When to re-validate

A validated judge stays valid only while nothing changes. Re-check on fresh labelled data when:

- **The judge model changes** (a new version or provider).
- **The judge prompt changes**, even "just wording".
- **New failure modes** appear in production or error analysis.
- **Your criteria drift.** Shankar et al. (2024) found that people need criteria to grade outputs, but grading outputs changes their criteria. Your expert's idea of "rude" will sharpen as they read more.

Husain's guide says the process repeats periodically or when material changes occur.

Keep the labelled sets versioned, like your eval dataset (Chapter 6), so you can re-run the check in minutes.

<!-- page -->

## Cost, determinism and model choice

**Cost.** A judge is a model call per output, per criterion, per repeat. 2 prompts x 100 cases x 3 runs x 2 criteria is already 1,200 judge calls. Use code checks where you can.

**Determinism.** Current Claude models don't accept `temperature`, `top_p` or `top_k`, so you can't force a judge to repeat itself. Instead:
- keep the verdict binary, with a critique
- fix the model, effort and rubric
- run the judge more than once on a sample (`--repeats 3`) and **report how often the runs disagree**

**Which model?** Anthropic's eval examples note it's generally best to grade with a different model from the one that generated the output. Husain's FAQ says the same model is usually fine if it aligns with your human labels. Either way, validation decides.

<!-- page -->

## Judges inside an A/B test

Judge errors leak into your result. If the same judge, with the same TPR and TNR, grades both prompts:

> measured gap = true gap x (TPR + TNR - 1)

With TPR 0.8 and TNR 0.9, a true 10-point gain shows up as 7 points (illustrative; the algebra is checked in `test_judge.py`). A weak judge shrinks real differences toward zero.

Worse, if the judge errs **differently** on A and B (say B is longer, and the judge is lenient on long answers), it can invent a win.

So:
- **report the judge's TPR and TNR**, with intervals, next to the A/B result
- read a sample of B's "wins" yourself

Husain's FAQ notes that knowing TPR and TNR lets you correct the judge's failure rate; `corrected_fail_rate` does the simple algebra. Correct intervals after that correction are an active research area.

<!-- page -->

## Traps

| Trap | Fix |
|---|---|
| Reporting raw agreement only | TPR, TNR, kappa, with n |
| Tuning the judge prompt on the test set | Iterate on dev; test once |
| Train examples also in dev or test | Split first, then pick examples |
| One judge for "overall quality" | One criterion per judge |
| 1 to 5 scale with no anchors | Pass/fail with a critique |
| Developer labels instead of expert | Ask the domain expert |
| Pairwise without swapping | Run both orders; disagree means tie |
| Validated once, trusted forever | Re-check after any change |

<!-- page -->

## Lab: build and validate a judge

1. Pick one criterion from your Chapter 5 error analysis.
2. Have your expert (or you, wearing that hat) label at least 60 outputs PASS/FAIL with a one-line critique. Save `id,input,output,human_label`.
3. `python judge_validation.py split labelled.csv`
4. Write a rubric file, with 2 to 4 train examples.
5. `python judge.py labelled labelled.dev.csv --rubric my.txt --out dev-j.csv` then `python judge_validation.py report dev-j.csv`
6. Read every disagreement. Revise the rubric. Repeat on dev.
7. Score test **once**. Then `python judge.py grade EXP.yaml --rubric my.txt` to judge your A/B records.

Add `--mock` to any `judge.py` command to practise without an API key.

<!-- page -->

## Checkpoint

**1.** Your judge agrees with the expert 97% of the time. Why might it still be useless?

**2.** You improved your judge prompt five times, checking the test set after each change. What's wrong with the final test score?

**3.** Prompt B beats A by 4 points according to a judge. What should you report next to that number?

<details><summary>Show answers</summary>
1. If failures are rare, a judge that passes almost everything gets high agreement while catching few failures. Check TPR on the failures, TNR on the passes, and kappa.
2. You tuned the judge to the test set, so the score is optimistic. Iterate on dev, and keep test for one final check.
3. The judge's TPR and TNR, with confidence intervals and sample sizes, plus how often repeated judge runs disagreed. An imperfect judge shrinks real gaps and can invent gaps if it errs differently on A and B.
</details>

<!-- page -->

## In an interview

*"How do you know your LLM judge is right?"*

*"I treat the judge as a classifier and check it against labels from a domain expert. The expert labels examples pass or fail with critiques for one criterion. I split them into train, dev and test: a few train examples go in the prompt, I iterate the prompt on dev, and I score test once. I report true positive and true negative rates, with failure as the positive class and with confidence intervals, not raw agreement, because failures are usually rare. I swap order for pairwise judging, run repeats to measure judge noise, and re-validate whenever the model, prompt or criteria change. In an A/B result, the judge's error rates go next to the numbers."*

<!-- page -->

## Read more

- **Hamel Husain**, *Using LLM-as-a-Judge For Evaluation: A Complete Guide*: domain expert, pass/fail with critiques, iterating the judge. [hamel.dev/blog/posts/llm-judge](https://hamel.dev/blog/posts/llm-judge/)
- **Hamel Husain**, *Frequently Asked Questions About AI Evals*: train/dev/test for judges, TPR and TNR, binary vs Likert. [hamel.dev/blog/posts/evals-faq](https://hamel.dev/blog/posts/evals-faq/)
- **Zheng et al. 2023**, *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena* (biases, swap rule). [arXiv 2306.05685](https://arxiv.org/abs/2306.05685)
- **Wang et al. 2023**, *Large Language Models are not Fair Evaluators* (position bias). [arXiv 2305.17926](https://arxiv.org/abs/2305.17926)
- **Shankar et al. 2024**, *Who Validates the Validators?* (criteria drift). [arXiv 2404.12272](https://arxiv.org/abs/2404.12272)
- **Anthropic**, *Define success criteria and build evaluations*: tips for LLM-based grading. [platform.claude.com](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)
- **Chip Huyen**, *AI Engineering* (O'Reilly, 2025), Ch 3: "AI as a Judge", "Limitations of AI as a Judge", "Ranking Models with Comparative Evaluation".
- **Next chapter:** did it improve? The statistics of comparing A and B.
