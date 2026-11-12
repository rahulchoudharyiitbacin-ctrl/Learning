# Beyond single prompts: a short brief

Everything so far tested one prompt that turns one input into one answer. Real products add more: documents fetched from a knowledge base, tools that take actions, conversations that last many turns.

Evaluating those systems is a big topic that deserves its own book. This chapter is only a **map**: what changes, what stays the same, and the handful of ideas an interviewer expects you to know.

The good news: the loop is the same one you already know. Read outputs, find failures, grade, compare. What changes is **what you treat as the unit** and **where you look**.

<!-- page -->

## The map

![Diagram: three columns. RAG: split into retrieval and answer; grade with Recall@k, MRR and faithfulness to the context. Agents: split into outcome and steps; grade the final state, not the words, over repeated trials with pass^k. Multi-turn: split into whole chat and one turn; grade pass/fail first, then find the first failure.](images/beyond-single-prompts.svg)

The common move: **split the system into parts**, so a failure points at one part.

<!-- page -->

## RAG: grade retrieval first

A RAG system has two parts. Husain's evals FAQ says they need different evaluation: retrieval and generation.

**Retrieval is a search problem.** Use search metrics:
- **Recall@k:** of all relevant documents, how many are in the top k?
- **Precision@k:** of the top k, how many are relevant?
- **MRR:** how high is the first relevant document?

Example (ranked d1 to d5, relevant d1, d3, d9): Recall@5 = 2/3, Precision@5 = 2/5, reciprocal rank = 1. A second query whose first hit is at rank 3 scores 1/3, so MRR over both = 2/3.

`rag_metrics.py` computes these, with tests.

<!-- page -->

## RAG: then grade the answer

Once retrieval works, ask how the model *uses* what it retrieved. The FAQ points to relationships between question, context and answer:

- Is the context **relevant** to the question?
- Is the answer **faithful to the context**, with nothing made up?
- Does the answer actually **address the question**?

Use error analysis to find failure modes, then judges validated against human labels (Chapters 5 and 8). Husain credits Jason Liu's "There Are Only 6 RAG Evals" for this framing.

The Ragas paper proposes reference-free metrics for the retrieval and generation parts of RAG.

<!-- page -->

## Agents: check the outcome

An agent calls tools and changes things. Anthropic's article on agent evals makes a sharp distinction:

- The **transcript** is everything the agent said and did.
- The **outcome** is the final state of the world.

A flight-booking agent may say "Your flight has been booked", but the outcome is whether a reservation exists in the database. **Grade the outcome**, not the words.

They also describe three grader types, which are the ones you know: code, model and human. Husain's advice is to evaluate **end to end** first, then run step-level diagnostics on the workflows that fail most.

<!-- page -->

## Agents: repeat and isolate

Agents vary from run to run, so you run several **trials** per task. Two ways to summarise them:

- **pass@k:** at least one of k trials succeeds.
- **pass^k:** *all* k trials succeed.

If an agent succeeds 75% of the time per trial, pass^3 is 0.75³ ≈ **42%**, while pass@3 is about 98%. By k = 10, pass@k is near 100% and pass^k is about 6%. Anthropic suggests pass^k where users need reliability every time.

Also: start every trial from a **clean environment**. Shared state between runs causes correlated failures that aren't the agent's fault.

<!-- page -->

## Multi-turn conversations

Don't start by scoring every turn. Husain's FAQ suggests:

1. Check whether the **whole conversation** met the user's goal: pass or fail.
2. Find the **first upstream failure**. Later problems often cascade from it.
3. Reproduce it with the **simplest test** you can, often a single turn.

To build test cases, simulate users with another model, or use **N-1 testing**: feed in the first N−1 turns of a real conversation and see what happens next.

Log a **trace ID** on every message so you can rebuild the whole path.

<!-- page -->

## What stays the same

| You already know | What changes here |
|---|---|
| Error analysis (Ch 5) | Read whole traces, find the first failure |
| Dataset (Ch 6) | Cases become tasks or conversations |
| Graders (Ch 7) | Add outcome checks and retrieval metrics |
| Judges (Ch 8) | Validate them just the same |
| Statistics (Ch 9) | Trials of one task aren't independent: cluster by task |
| Online (Ch 11) | Same ladder: shadow, canary, split |

Anthropic also separates **capability evals** ("can it do this at all?") from **regression evals** ("does it still do what it did?"), which should pass nearly always.

<!-- page -->

## Lab: one trace, one retrieval check

Pick one of these, using your own project or a small invented one:

- **RAG:** write 5 questions, each with its relevant document. Run your retriever and compute Recall@3 and MRR with `rag_metrics.py`.
- **Agent or chat:** take 5 conversations or traces. For each, mark pass or fail, then write down the **first** upstream failure.

Write one sentence: which part of the system would you fix first?

<!-- page -->

## Checkpoint

**1.** A RAG bot gives wrong answers. Why measure retrieval separately?

**2.** An agent says "Refund issued" but no refund exists. What did you grade wrong?

**3.** 75% success per trial. What is the chance of passing 3 trials in a row?

<details><summary>Show answers</summary>
1. Wrong answers can come from retrieval (the right document wasn't found) or generation (it was found but misused). Splitting tells you which to fix.
2. You graded the transcript, not the outcome. Check the final state, here whether a refund exists.
3. 0.75 × 0.75 × 0.75 ≈ 42%.
</details>

<!-- page -->

## In an interview

*"How would you evaluate a RAG chatbot?"*

*"I'd split it. For retrieval I'd build queries paired with their relevant documents and track Recall@k and MRR. For generation I'd do error analysis on real answers, then build judges for things like faithfulness to the context and validate them against human labels. Finally I'd track whole-conversation success and read traces, starting with the first failure in each."*

<!-- page -->

## Read more

- **Hamel Husain**, *Frequently Asked Questions About AI Evals*: evaluating RAG, multi-turn traces and agentic workflows. [hamel.dev/blog/posts/evals-faq](https://hamel.dev/blog/posts/evals-faq/)
- **Anthropic**, *Demystifying evals for AI agents*: transcript vs outcome, graders, pass@k and pass^k, isolated trials. [anthropic.com/engineering/demystifying-evals-for-ai-agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- **Es et al. 2023**, *Ragas: Automated Evaluation of Retrieval Augmented Generation*. [arXiv 2309.15217](https://arxiv.org/abs/2309.15217)
- **Husain and Shankar**, free evals course, with an e-book on advanced RAG optimisation and evals. [ai.hamel.dev/eval-course](https://ai.hamel.dev/eval-course)
- **Next chapter:** a practice system for interviews: questions, rubrics and drills.
