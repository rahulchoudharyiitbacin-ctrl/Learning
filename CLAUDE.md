# Research lab: coordinator instructions

In this folder you are the **coordinator**. Run this session on Claude Fable 5.2. Your job is planning, judgment, verification and synthesis. Hand the bulk of the work to the worker subagents.

## Your team

| Subagent | Model | Hand it |
|---|---|---|
| `research-worker` | Opus 5.5 | One sub-problem that needs real reasoning or experiments: deriving, coding, simulating, searching for counterexamples |
| `reader` | Sonnet 5.5 (cheaper) | Reading and extraction: web searches, papers, docs, pulling facts out of files |

## How to delegate

1. **Plan first.** Break the problem into independent sub-problems and write the plan to `<project>/notes/plan.md`.
2. **Brief completely.** Workers see none of this conversation. Each task must include the goal, the relevant file paths, the constraints, and the report format you want.
3. **Run in parallel.** Start independent tasks together, usually 2 to 4 at once.
4. **Pick the cheapest worker that fits.** Use `reader` for reading and `research-worker` for reasoning or experiments.
5. **Don't delegate small things.** If a task takes a few tool calls, do it yourself; a handoff costs a briefing and a round trip.
6. **Verify before trusting.** Check key claims in each report yourself, for example by re-running a script or spot-checking a source. Send back work that fails.
7. **Keep the synthesis.** You write the final conclusions in `<project>/notes/findings.md`: what's established, what's uncertain, and what to try next.

## Folder layout

Each project lives in its own folder at the top level. Inside a project folder:

- `notes/`: plan, findings, reading notes
- `work/<task>/`: scripts and data from each worker task

Shared setup stays at the top level: `CLAUDE.md`, `README.md`, `.claude/agents/` (worker definitions), `.claude/launch.json` (local servers).

## Projects

| Project | Where | What |
|---|---|---|
| Prompt A/B testing book | `prompt-ab-book/` | A page-turning book that teaches Rahul prompt A/B testing, one Markdown chapter at a time |
| Voice-controlled switchboard | `PROJECT.md`, `docs/`, `sim/` (top level, not yet moved into a folder) | Hardware project; see `PROJECT.md` |

## Prompt A/B testing book (`prompt-ab-book/`)

```
prompt-ab-book/
  book/index.html          The book front end (reads the chapters, turns pages)
  book/chapters/contents.md  Order of the book + one-line description per chapter
  book/chapters/*.md       One file per chapter
  notes/                   Plan, findings, research notes, older visual notes
  work/ab-prompt-test/     Simulated A/B demo (demo.py) and its output
```

**Chapter structure:** hook story, core idea, mechanics (tables, diagram, code), worked example, traps, **Lab** (from Chapter 3 on: something the learner does, such as running the harness or reading outputs), checkpoint, interview page, Read more. Statistics wording must be exact: a p-value is not the probability B is better; online A/B is randomised between users while offline eval is paired by case; repeated runs per case must be averaged or clustered by case before computing an interval. Don't present a sample or a maximum as typical (say "up to ... on some tasks"). Chapters 1-3 were corrected against `prompt-ab-book/notes/review-opus.md`; re-read its accuracy section (E) before writing similar claims.

**Scope decisions:** RAG, agent and multi-turn evals get only a short brief (they belong in a future separate book). The portfolio project is deferred until the book is done; then it gets assembled from the labs and the book is updated with its real numbers.

**Claude API facts for code in chapters:** don't send `temperature`, `top_p` or `top_k` to current Claude models (they return 400, and the newest API version rejects them on every model); lock `model`, `effort` and `max_tokens` instead. Current models think before answering, which uses `max_tokens`, so don't set it tiny. Check the `claude-api` skill before writing API code. Test chapter code without the user's key: a `--mock` mode plus the real SDK against a fake local server (isolated venv in the scratchpad). Say plainly what wasn't tested live. Tools between you and the API can change requests: promptfoo 0.125.1 behind a custom base URL sent `temperature: 0` to a Claude 5 model (this machine has `ANTHROPIC_BASE_URL` set to the default host); check what actually goes on the wire.

**Current state (2026-11-13):** all 16 chapters are written and published (1-12 the A/B-testing course, 13 practice system, 14 question bank, 15 system-design prompts, 16 coding drills). Next planned work: the portfolio project (assembled from the chapter labs with real API numbers, then update the book with those numbers), and the SHOULD/NICE items in `review-opus.md` that the user hasn't decided on. Code in `prompt-ab-book/work/` (harness, promptfoo, ci-example, drills, system-design-prompts) was tested offline only; no live API call has been made yet.

**Plan and status:** the agreed 12-chapter outline and what's written is in `prompt-ab-book/notes/outline.md`; sources by chapter are in `prompt-ab-book/notes/references.md`. Chapters name their sources in the text and end with a "Read more" page. Only cite what's marked Verified there.

**Adding a chapter**
1. Write `book/chapters/<topic-slug>.md`. No number prefix in the filename.
2. Split it into pages with a line containing only `<!-- page -->`. Keep each page to about 120–170 words so it fits without scrolling.
3. Read the descriptions in `contents.md` and insert the new entry **right after the chapter it builds on**, not at the end by default. Format:
   ```
   4. [Chapter name](topic-slug.md)
      One-line description of what the chapter teaches.
   ```
   The order of the lines is the order of the book. Numbers are only for reading.
4. Republish (see below) and check the page turns and that no page overflows.

**Writing style for chapters:** plain language for a learner, not dense notes. Use everyday analogies (cricket, chai, exams), a yellow `> **Teacher's note:**` where useful, and checkpoint questions with answers in `<details><summary>…</summary>…</details>`. Only state facts you can source; cite papers by name.

**Images and diagrams:** add them where a picture teaches faster than words (flows, comparisons, charts of real numbers). Save as SVG in `prompt-ab-book/book/images/<name>.svg` and reference with `![descriptive alt text](images/<name>.svg)` on its own line. Rules: pages are light paper in both themes, so use fixed light-friendly colors (ink #1d262d, teal #13857a, orange #b8661a); SVG loaded as an image can't use the page's fonts or CSS variables, so use Helvetica/Arial and large text (about 20px in a 600-wide viewBox) so it stays readable on a phone; keep labels short. Never draw invented data: any chart must use real numbers from our demo or a cited source. After adding, check overflow at desktop and ~400px width, and publish the images in `files` (`"images/<name>.svg": "images/<name>.svg"`).

**Publishing:** the book is the Artifact at https://claude.ai/artifact/HMaqRGpPkRebAvmnZgz9mK. Republish `prompt-ab-book/book/index.html` with `url` set to that link (so it updates the same book) and `root` set to `prompt-ab-book/book`. Pass every chapter file in `files` (`"chapters/<file>.md": "chapters/<file>.md"`), including `contents.md`, and `null` for any removed or renamed chapter.

**Local preview:** the book needs a web server, because opening `index.html` directly can't load the chapters. Run `python3 -m http.server 8765 --bind 127.0.0.1` from `prompt-ab-book/book/` in a shell and open http://127.0.0.1:8765. The `book` entry in `.claude/launch.json` can't start the server, because macOS blocks it from reading the Desktop folder.

**Models:** use `reader` (Sonnet) for fact-finding and source checks, and `research-worker` (Opus) only for real experiments or hard reasoning. Write the chapters yourself, so the voice stays consistent.
