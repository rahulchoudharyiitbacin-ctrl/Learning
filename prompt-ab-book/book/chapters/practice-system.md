# The interview practice system

You've now read twelve chapters. If someone asked "how do you know your LLM judge is right?" you'd probably nod, because you'd *recognise* the answer.

An interview doesn't ask you to recognise. It asks you to **produce** the answer, out loud, in your own words, and then it probes: "What number? What would go wrong? What would change your mind?"

Reading builds recognition. Only practice builds production.

This chapter is the plan for turning the book into interview skill. The next three chapters are the practice material.

<!-- page -->

## What interviews seem to test

Here is what the evidence says, and how much to trust it.

**Stronger evidence:**
- Employer postings, such as Anthropic's public posting for a Research Engineer on post-training model evaluations, ask for experience designing, running and analysing evals.
- Expert educators like Hamel Husain and Eugene Yan publish what practitioners wrestle with: error analysis, judge validation, RAG and agent evals.

**Weaker evidence:** interview-prep sites describe "typical" loops. They aren't first-hand reports, and I found no first-hand candidate write-ups. Treat their lists as hints.

<!-- page -->

## The shape of a loop

Prep sites commonly describe a loop with these parts. Treat it as *reported*, not confirmed:

- a **technical screen** with conceptual questions
- a **coding** round (often an eval harness or analysis)
- a **take-home** with an eval script
- **system design**: "design the eval for X"
- a **resume deep-dive** and behavioural questions

Across the sources I checked, the same themes recur: designing and defending an eval system, validating judges against humans, error analysis, and debugging regressions. Classical A/B statistics appears too, but as one supporting skill.

<!-- page -->

## Four skills, four chapters

| Skill | Practice material |
|---|---|
| **Explain** concepts under probing | Ch 14: question bank with rubrics |
| **Design** an eval system | Ch 15: system-design prompts |
| **Build** small tools fast | Ch 16: timed drills (code in `work/drills/`) |
| **Defend** your own work | This chapter: the resume deep-dive |

Plus a loop that ties them together: the **mock interview** (later in this chapter).

You need all four. Most people over-practise "explain" because it feels like studying.

<!-- page -->

## The shape of a good answer

Under pressure, people ramble. Use a four-part shape for any answer:

1. **Answer** in one sentence.
2. **How:** the steps, in order.
3. **Number:** a concrete figure or example.
4. **Trade-off:** what could go wrong, or what you give up.

Example, for "How do you know your judge is right?":

*"I check it against human labels. I'd have a domain expert label 100 to 200 cases, split into train, dev and test, and measure TPR and TNR on the test set. For instance, 60% TPR would worry me even at 90% agreement. The risk is noisy labels, so I'd re-check when the model or criteria change."*

<!-- page -->

## What Weak, OK and Strong mean

Every question in Chapter 14 has a three-level rubric:

| Level | Sounds like |
|---|---|
| **Weak** | Buzzwords, or a confident wrong answer |
| **OK** | Correct but generic: it would fit any company |
| **Strong** | Specific, quantified, and names a trade-off or failure mode |

The jump from OK to Strong is almost always the same: **a number and a trade-off.**

When you score yourself, be harsh. Interviewers will be.

<!-- page -->

## The practice loop

Take each question through three passes:

1. **Recall:** answer silently in your head. Check the rubric.
2. **Say it:** answer aloud, to a timer, for 90 seconds. Recording yourself helps. Your words will be worse than your thoughts.
3. **Add numbers:** answer again, this time with a figure, an example and a trade-off.

Then log it in a tracking table: question, date, level (Weak, OK or Strong), what was missing.

Repeat any question you scored below Strong after two days. Spaced repeats beat one long cram.

<!-- page -->

## A two-week plan (my suggestion)

| Days | Focus |
|---|---|
| 1–3 | Skim Chapters 1–9. Bank questions, pass 1 and 2 |
| 4–5 | Coding drills 1 and 2 |
| 6–7 | Coding drills 3 and 4. Rest |
| 8–9 | System-design prompts 1 to 3 |
| 10 | System-design prompts 4 and 5 |
| 11–12 | Mock interviews, one a day |
| 13 | Your resume story, out loud |
| 14 | Weak spots only. Sleep |

This plan is my own, not sourced. Adjust it to your date and your gaps.

<!-- page -->

## The mock interview protocol

A mock interview works best as three roles:

- **Interviewer:** asks the question and probes.
- **You:** answer under time.
- **Scorer:** grades against the rubric.

You can play the interviewer with a friend, or let an LLM do it. In this book's tool, an LLM plays the interviewer and scores you at the end.

**Protocol (30 minutes, one question):**
1. 2 min: read the question and rubric label, not the rubric.
2. 15 min: answer and take probes.
3. 5 min: write your own score *before* seeing the scorecard.
4. 8 min: compare, note gaps, redo the weakest part.

<!-- page -->

## The mock-interview tool

```
python mock_interview.py \
  --question "How do you know your LLM judge is right?" \
  --rubric "Weak: ... OK: ... Strong: ..."
```

- An LLM asks your question, then up to three short probes.
- Type each answer, then a line with only `/end`. Type `/done` to stop early.
- At the end it prints a scorecard: level, evidence, what a strong answer adds, and one drill.

Add `--mock` for a free dry run with a fake interviewer. The tool never sends a temperature, because current Claude models don't accept one.

<!-- page -->

## Don't over-trust the scorecard

An LLM scorer is a judge, and Chapter 8 taught you to distrust judges until they're validated.

- **Score yourself first**, then compare. If you often disagree with the LLM, find out who's right.
- It can be too kind, or too harsh on style.
- It doesn't know your industry's norms.
- Use it for **probes and practice reps**. Use humans for calibration.

Try one mock with a friend who knows the field. If the friend and the tool score you differently, trust the friend and tune the rubric.

<!-- page -->

## Defend your own work

If "A/B testing for prompts" is on your resume, expect a deep-dive. A typical sequence:

1. What exactly did you test, and why?
2. How many cases, and where did they come from?
3. How did you grade? Did you validate the grader?
4. What numbers did you get, and how sure were you?
5. What went wrong, and what did you change?

Every answer needs a real number. This is why the portfolio project we agreed to build after this book matters: it gives you real figures to defend.

> **Teacher's note:** Only claim what you did. Interviewers dig, and an honest "we had 150 cases, so we could only detect big gains" beats a polished story you can't defend.

<!-- page -->

## Your story skeleton

Fill this in with **your own** facts. Never use numbers you didn't measure.

- **Task:** ______ (what the prompt does)
- **Change tested:** ______ (one change)
- **Test set:** ____ cases, from ______
- **Grading:** ______, validated by ______ (TPR/TNR ____)
- **Result:** B − A = ____ points, 95% CI [____, ____]
- **Decision:** ______, because ______
- **What surprised you:** ______
- **What you'd do next:** ______

If a blank is empty, that's a gap to close before the interview, not a fact to invent.

<!-- page -->

## Signals interviewers notice

A recruiter-written article lists the answer "I've never really had to evaluate it, you can tell when it's working" as a red flag. That source has an incentive, so treat it as a hint. It matches common sense:

**Stronger signals**
- a number, and how you got it
- "not proven" when it isn't
- a failure you found and fixed
- trade-offs: cost, latency, quality

**Weaker signals**
- "it felt better"
- one run, five examples
- tool names with no method
- certainty about everything

<!-- page -->

## Before the interview

**The day before**
- Redo your two weakest questions aloud.
- Re-read your story skeleton.
- Prepare 3 questions to ask them about *their* evals: how they know a change helped, what blocks a release.

**In the room**
- Ask a clarifying question before designing anything.
- Say your structure first: "I'll cover goals, data, grading, rollout."
- Name uncertainty out loud. It reads as honesty, not weakness.
- If you don't know, say how you'd find out.

<!-- page -->

## Lab: one full mock

1. Pick one question from Chapter 14 that you scored OK or lower.
2. Run `mock_interview.py` with its rubric (or use a friend).
3. Before reading the scorecard, write your own level and one gap.
4. Compare. Where did you and the scorecard differ?
5. Redo the weakest part of your answer aloud, adding a number and a trade-off.
6. Repeat the same question in two days.

Log both attempts in your tracking table.

<!-- page -->

## Checkpoint

**1.** Why isn't reading enough to prepare?

**2.** What turns an OK answer into a Strong one?

**3.** Why not trust an LLM scorecard blindly?

<details><summary>Show answers</summary>
1. Reading builds recognition. Interviews need you to produce answers aloud and survive follow-up probes.
2. A concrete number or example, plus the trade-off or failure mode.
3. It's a judge, and judges are biased and unvalidated until checked (Chapter 8). Score yourself first and compare, and calibrate with a human.
</details>

<!-- page -->

## In an interview

*"Tell me about an eval that gave you a wrong answer."*

Use this skeleton, with your own details:

*"We tested ____ and the score said ____. When I read the failures I found ____, which meant the problem was in the ____ (grader, dataset, prompt). I changed ____, re-ran, and the score moved to ____. What I took from it: ____."*

A story where **you** caught the problem by reading outputs (Chapter 5) is exactly what interviewers hope to hear.

<!-- page -->

## Read more

- **Anthropic**, public job posting for a Research Engineer, Post-Training Model Evaluations, as an example of what employers ask for. [job-boards.greenhouse.io/anthropic/jobs/5198255008](https://job-boards.greenhouse.io/anthropic/jobs/5198255008)
- **Hamel Husain**, *Frequently Asked Questions (and Answers) About AI Evals*: the topics practitioners wrestle with. [hamel.dev/blog/posts/evals-faq](https://hamel.dev/blog/posts/evals-faq/)
- **Eugene Yan**, *Task-Specific LLM Evals that Do & Don't Work*. [eugeneyan.com/writing/evals](https://eugeneyan.com/writing/evals/)
- **Next chapter:** Chapter 14, the question bank.
