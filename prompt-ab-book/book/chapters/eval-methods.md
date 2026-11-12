# Evaluation methods: what exists and when to use which

Suppose you build a bot that summarises support tickets, and you grade it with exact match against a reference summary. Score: 0%. Not one summary is word-for-word identical, and every summary is fine.

Now suppose you grade a ticket *router* with an LLM judge and a 1 to 10 scale. It works, but it's slow, costly, and noisy, for a task a one-line check could grade perfectly.

There is no best metric. There's a method that fits the task. This chapter is your toolbox.

<!-- page -->

## Choosing, in one picture

![Diagram: a decision list. Can a rule check it? Use a code check. Reference answer with varying wording? Use similarity. Needs judgment? Use an LLM judge. High stakes, or checking the judge? Use human review. Real users in production? Use user signals.](images/choose-a-method.svg)

Go down the list and take the **first** "yes". Cheap and deterministic beats expensive and fuzzy.

<!-- page -->

## 1. Code checks

When a rule can decide, use the rule. Husain's FAQ says to use a code-based eval when an objective rule can identify the failure.

| Check | Example |
|---|---|
| Exact match | Label equals "refund" |
| Normalized match | Same, ignoring case and end punctuation |
| Contains / not contains | Mentions the order ID, never says "guarantee" |
| Regex | A date in the form 2026-11-13 |
| JSON checks | Valid JSON, right keys and values |
| Numbers | Within a tolerance |
| Length limits | At most 80 words |
| Run the code | Generated code passes its tests |

<!-- page -->

## Why code checks first

- **Free and fast**, so you can run thousands.
- **Consistent**: the same output always gets the same grade.
- **Debuggable**: you can see exactly why something failed.

Anthropic's evals guide calls exact match perfect for tasks with clear-cut, categorical answers, such as sentiment analysis, after normalizing whitespace and case.

Their limit: they check form, not meaning. And a too-strict check marks good answers wrong (Chapter 5's "Refund." problem). Test your graders as carefully as your prompts.

<!-- page -->

## Structured output

Many apps need JSON. Grade it in two ways:

1. **All fields right?** One pass/fail per case.
2. **What fraction of fields are right?** A softer score that shows *which* field fails.

Watch the traps:
- Prose around the JSON ("Here is the JSON: ...") fails parsing.
- Code fences around it need stripping.
- A missing field is a failure, not a pass.
- In Python, `True == 1`. Compare types too.

The harness has `json_all_fields` and `json_field_accuracy` for exactly this.

<!-- page -->

## Classification: accuracy lies

Say 95 of 100 messages are fine and 5 are abusive. A model that calls every message "fine" scores **95% accuracy**, and catches **0** abusive messages.

That's why classification needs more than accuracy:
- **Recall:** of the real positives, how many did you catch?
- **Precision:** of the ones you flagged, how many were right?
- **F1:** one number that balances the two.

Eugene Yan writes that accuracy is too coarse a metric, and that you should separate it into recall and precision at minimum.

<!-- page -->

## The confusion matrix

A table of *expected* (rows) against *predicted* (columns):

```
          account delivery other refund
account        13        0     0      2
delivery        0       15     0      0
other           2        2    10      1
refund          1        0     1     13
```

(Mock records, not real results.)

The big off-diagonal numbers show **which pairs get mixed up**. That's a direct to-do list for your prompt, and it pairs well with error analysis (Chapter 5).

`classification_report.py` prints precision, recall, F1 and this matrix for each prompt.

<!-- page -->

## 2. Similarity metrics

For free text there's no single right answer. Similarity metrics compare the output to a **reference**:

| Metric | Idea | Source |
|---|---|---|
| **ROUGE-L** | Longest shared word sequence | Anthropic's guide, for summaries |
| **Embedding similarity** | Closeness of meaning vectors | Anthropic (consistency); Huyen Ch 3 |
| **NLI consistency** | Does the summary contradict the source? | Yan, for summaries |
| **chrF, BLEURT, COMET** | Translation quality | Yan, for translation |

<!-- page -->

## Using similarity wisely

- Overlap metrics reward **matching words**, not truth. A fluent, wrong summary can score well.
- They need **good references**. Bad references give bad scores.
- Treat them as a **cheap signal**, not a verdict, and read some outputs to see what a "high" score looks like.
- Consistency checks (does the summary contradict the source?) are often more useful than overlap for summaries.

Huyen's *AI Engineering* Ch 3 covers exact evaluation, functional correctness and similarity measurements against reference data, including embeddings.

<!-- page -->

## 3. LLM judges

When there's no rule and no single reference, a second model can grade against a **rubric**: tone, helpfulness, faithfulness to a source.

Two styles:
- **Pointwise:** score one answer. Husain recommends simple **pass/fail with a written critique**, and warns against uncalibrated 1 to 5 scales where nobody knows what a 3 means.
- **Pairwise:** "which is better, A or B?" Huyen's Ch 3 covers comparative evaluation.

Judges are biased (Zheng et al. found position, verbosity and self-preference effects) and must be **validated** against human labels. That's Chapter 8.

<!-- page -->

## 4. Human review

People are the gold standard for subjective quality, and they're slow, costly, and not always consistent.

Use them for:
- **final calls** on hard or high-stakes cases
- **calibrating** an LLM judge
- **error analysis** (Chapter 5)

Husain's advice: one domain expert tends to work better than a committee for annotation and review. Sample a small, regular batch instead of grading everything.

<!-- page -->

## 5. User signals

In production, users tell you things:
- thumbs up and down
- edits to the answer
- retries and regenerations
- escalations to a human
- task completion

They show real outcomes, but they're **noisy and biased**: only some users respond, and a thumbs-down may have nothing to do with the prompt. Treat them as signals to investigate, not as a grade.

Huyen's Ch 10 covers user feedback. Chapter 11 covers online tests.

<!-- page -->

## Method by task

| Task | Good starting methods |
|---|---|
| Classification, routing | Code check, precision/recall/F1, confusion matrix |
| Extraction, JSON | Schema check, field accuracy |
| Short answer with a known truth | Normalized match; judge for free-form |
| Summarisation | Length rules, consistency check or judge, overlap as a weak signal |
| Translation | chrF/COMET-style metrics, human spot checks |
| Chat, tone, helpfulness | Judge with rubric, human sample |
| Code generation | Run the tests |
| RAG, agents | Chapter 12 (short brief) |

<!-- page -->

## Layer your methods

Anthropic's guide says to automate grading when possible, and that more questions with slightly lower-signal automated grading beat fewer hand-graded ones.

A common layering:
1. **Code checks as gates:** valid format, banned phrases, length.
2. **A judge** for the criteria code can't see.
3. **Humans** on a sample, and on disagreements.

Grade **one criterion at a time** (correct, polite, grounded) instead of one vague "quality" score. When B fails, you'll know *what* it failed.

<!-- page -->

## Add a grader to the harness

In `graders.py`:

```python
def max_words(case, output):
    n = len(output.split())
    return int(n <= case["max_words"])

EXTRA_GRADERS = {"max_words": max_words}
```

In your experiment file:

```
grader: max_words
```

and put `"max_words": 80` in each case. Available now: `normalized_match`, `contains_all`, `contains_none`, `regex_match`, `max_words`, `numeric_close`, `json_all_fields`, `json_field_accuracy`. `python test_graders.py` checks them.

<!-- page -->

## Lab: pick and test your methods

1. List your task's success criteria (from error analysis).
2. For each one, choose the **first** method from the diagram that works.
3. Implement any new code grader in `graders.py`, and add asserts to `test_graders.py` for tricky outputs.
4. Run the harness, then `classification_report.py` if your task is classification.
5. Find a case where your cheap grader is **wrong**. Fix the grader or note the limit.

Write one sentence: which criterion will you need a judge for?

<!-- page -->

## Checkpoint

**1.** Why not grade a summariser with exact match?

**2.** A fraud detector is "99% accurate" and fraud is 1% of cases. Why isn't that enough?

**3.** Why grade one criterion at a time instead of one overall quality score?

<details><summary>Show answers</summary>
1. Good summaries are worded differently from any reference, so exact match fails almost all of them. Use a consistency check, a judge, or overlap as a weak signal.
2. A model that never flags fraud gets 99% accuracy. You need recall (how much fraud it catches) and precision (how many flags are right).
3. A single score hides what failed. Separate criteria show where B is better or worse, and each can use the cheapest method that works.
</details>

<!-- page -->

## In an interview

*"How would you evaluate a summarisation feature?"*

*"I'd start with code checks: length limits and banned phrases. Then I'd check consistency, meaning the summary doesn't contradict the source, using an NLI model or a validated LLM judge. For overall usefulness I'd use a pass/fail judge with a rubric, checked against human labels, and have a domain expert review a sample. Overlap metrics like ROUGE would be only a weak signal. I'd grade each criterion separately."*

<!-- page -->

## Read more

- **Anthropic**, *Define success criteria and build evaluations*: exact match, cosine similarity, ROUGE-L, Likert scales, automated grading. [platform.claude.com](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)
- **Eugene Yan**, *Task-Specific LLM Evals that Do & Don't Work*: classification, summarisation, translation. [eugeneyan.com/writing/evals](https://eugeneyan.com/writing/evals/)
- **Hamel Husain**, *Using LLM-as-a-Judge For Evaluation: A Complete Guide*: pass/fail with critiques. [hamel.dev/blog/posts/llm-judge](https://hamel.dev/blog/posts/llm-judge/)
- **Chip Huyen**, *AI Engineering* (O'Reilly, 2025), Ch 3 (exact evaluation, AI as a judge, comparative evaluation) and Ch 4 (evaluation criteria).
- **Next chapter:** LLM-as-judge in depth, and how to check a judge is right.
