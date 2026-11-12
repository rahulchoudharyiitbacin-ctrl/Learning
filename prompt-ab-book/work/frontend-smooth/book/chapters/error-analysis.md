# Error analysis: read your outputs first

Your harness just told you: A scored 78%, B scored 74%. Now what?

A score says *how much* is wrong. It says nothing about *what* is wrong, so it can't tell you what to fix. Is B confusing two labels? Adding extra words? Hitting a test case with a bad label?

The only way to find out is to open the failures and read them. It's unglamorous, and it's the most useful thing you can do with an eval. Hamel Husain, who teaches evals widely, calls error analysis the most important activity in evals.

<!-- page -->

## Why read before you measure

Husain's advice for a team that doubts evals is not to argue for them. It's to look at 50 to 100 real conversations yourself and find the most common ways the product fails. The findings make the case.

Researchers found something deeper. Shankar et al. (2024) saw that people **need criteria to grade outputs, but grading outputs helps them define the criteria.** They named it *criteria drift*.

So "decide what better means first" (Chapter 1) is only half the story. You often discover what "better" means by reading outputs. Then you freeze it.

<!-- page -->

## The method

![Diagram: a funnel from raw outputs to notes to categories to counts, ending in fix and re-run, with a dashed arrow back to the top to repeat until nothing new appears.](images/error-analysis-loop.svg)

Qualitative researchers call the middle steps **open coding** (write notes) and **axial coding** (group the notes). Husain's evals FAQ adapts them for LLM products.

<!-- page -->

## Step 1: choose what to read

Read these three groups, in this order:

1. **Failures:** cases where the grade was below 1.
2. **Disagreements:** cases where A and B scored differently. They show what the change really did.
3. **A few passes:** a random handful of *passing* cases. If you disagree with the grader on any, the grader is the problem.

**How many?** Husain suggests annotating at least 30 yourself, with a pool of roughly 100 diverse cases as a working guide. The sample set in this book has only 20, so read all the failures.

Do this on your **dev** set outputs, not your final test set (Chapter 3).

<!-- page -->

## The helper script

Three commands in `work/harness/error_analysis.py`:

```
python error_analysis.py show EXP.yaml
python error_analysis.py show EXP.yaml --disagree
python error_analysis.py show EXP.yaml --sample-pass 5
python error_analysis.py template EXP.yaml
python error_analysis.py tally EXP.yaml
```

`show` prints input, expected answer and every run's output. `template` writes a `notes.csv` with one row per failing case. `tally` counts your categories at the end.

Add `--mock` to practise on fake records first.

<!-- page -->

## Step 2: open coding

Write **one short note per failure**. Describe what you *see*, not why you think it happened.

| Good note | Weak note |
|---|---|
| Output was "Label: refund", not "refund" | Model is bad at formats |
| Message mentions a charge *and* a late order | Confusing case |
| Replied "other" to a promo-code question | Wrong |

Tips from Husain's FAQ:
- It's like journaling. Don't categorize yet.
- Note the **first** failure in a case; the rest may follow from it.
- Ideally one person with domain knowledge does it, and does at least 30 notes before getting help from an AI assistant.

<!-- page -->

## Where does the failure live?

Not every failure is the prompt's fault. Ask where it lives:

| Place | Sign | Fix |
|---|---|---|
| **Prompt** | Instructions unclear or missing | Improve the prompt |
| **Model** | Understood but still wrong | Different model or settings |
| **Grader** | Answer is fine, score is 0 | Fix the grader |
| **Dataset** | Expected label is wrong or arguable | Fix or remove the case |

> **Teacher's note:** Check the grader and dataset first. They're cheap to fix, and a grader bug can make a good prompt look bad. An exact-match grader will fail "Refund." for "refund", and that's the grader's problem, not the model's.

<!-- page -->

## Step 3: axial coding

Now group your notes. Look for notes that describe the same kind of failure, and give each group a name.

Rules of thumb:
- Aim for **4 to 8** categories.
- Name them by *what happened*: "extra words in output", "mixed-intent message".
- Keep "other" small. If it's big, you haven't found the pattern yet.
- Rename and merge freely. Husain calls this the most important step.

Then add the category and the "where" (prompt, model, grader, dataset) to `notes.csv`.

<!-- page -->

## Step 4: count

```
python error_analysis.py tally EXP.yaml
```

```
category          A     B   total
...
where             A     B   total
...
```

You get counts per category, split by prompt, and per "where".

Counting turns "it fails in lots of ways" into "40% of failures are one thing". The count, not the loudest example, tells you what to fix first.

<!-- page -->

## Step 5: choose a fix

Pick the category that is **big and cheap to fix**. Then:

1. Make **one** change (Chapter 3).
2. Re-run the experiment with the harness.
3. Check that the category shrank and others didn't grow.

What *not* to do: add a prompt rule for every single failure. You'll overfit to those cases, and the prompt gets longer and stranger. Fix the pattern, not the example.

Failures you've understood make excellent **new test cases** (Chapter 6).

<!-- page -->

## When to stop

Keep reading until new cases **stop revealing new kinds of failure**, or stop changing the categories you have. Husain calls this theoretical saturation.

Then revisit the process now and then: after prompt changes, model upgrades, and when real user data arrives. Failure modes move.

Where this leads:
- **Categories** become the criteria for judges (Chapter 8).
- **Failures** become test cases (Chapter 6).
- **Counts** show where to spend effort.

Once you know the criteria, freeze them before the final A/B comparison.

<!-- page -->

## Lab: analyse your own run

1. Take the `records.jsonl` from your Chapter 4 lab (or practise with `--mock`).
2. Run `show` and read every failure. Then `--disagree`, then `--sample-pass 5`.
3. Run `template` and write a note for each failure.
4. Group the notes into 4 to 8 categories. Fill in `category` and `where`.
5. Run `tally`. Which category is biggest? Did any failure turn out to be the grader's or the dataset's fault?
6. Make **one** fix and re-run. Compare the tallies.

Write down one sentence you now believe about your prompt that you didn't before.

<!-- page -->

## Checkpoint

**1.** Why start with error analysis instead of building metrics?

**2.** A failure shows the model answered "refund" and the expected label was "refund". Where does it live?

**3.** You write a new prompt rule for each of your 15 failures. What goes wrong?

<details><summary>Show answers</summary>
1. A score doesn't say what to fix. Reading failures finds the failure modes that are specific to your application, and those decide which evals are worth writing.
2. In the grader. The answer was right but scored wrong, perhaps because of case, spaces or punctuation.
3. You overfit the prompt to those exact cases. It gets long, may hurt other cases, and your test score stops meaning anything. Fix the pattern behind the failures instead.
</details>

<!-- page -->

## In an interview

*"Your new prompt scored 3 points lower than the old one. What do you do?"*

*"I don't change anything yet. I read the failures, especially cases where old and new disagree, and write a short note on each. I check whether the grader or the dataset is at fault before blaming the prompt. Then I group the notes into a few failure categories and count them, so I fix the biggest one with a single change and re-run. I keep going until new failures stop teaching me anything."*

<!-- page -->

## Read more

- **Hamel Husain**, *Frequently Asked Questions (and Answers) About AI Evals*, the section on error analysis, open and axial coding. [hamel.dev/blog/posts/evals-faq](https://hamel.dev/blog/posts/evals-faq/)
- **Husain and Shankar**, free evals course and e-books. [ai.hamel.dev/eval-course](https://ai.hamel.dev/eval-course)
- **Shankar et al. 2024**, *Who Validates the Validators?* (criteria drift). [arXiv 2404.12272](https://arxiv.org/abs/2404.12272)
- **Hamel Husain**, *Your AI Product Needs Evals*. [hamel.dev/blog/posts/evals](https://hamel.dev/blog/posts/evals/)
- **Next chapter:** building the eval dataset, where your understood failures become test cases.
