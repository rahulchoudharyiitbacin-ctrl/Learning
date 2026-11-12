# Frameworks: the same experiment in promptfoo, in CI, and beyond

In Chapter 4 you built a harness by hand. It reads an experiment file, calls the model, grades each answer and prints a summary. You can explain every line.

Now imagine your team asks for three more things. A web page where they can see A and B side by side. A check that runs on every pull request. And a way to stop paying twice for answers you already have.

You could build all of that. Or you could use a framework that already has it.

In this chapter you'll run the **same** ticket-triage experiment (same prompts, same 20 cases, same grader idea) in promptfoo, put it in CI, and then look fairly at LangSmith, Langfuse and Braintrust.

<!-- page -->

## What a framework adds, and what it costs

| You get | The hand harness has |
|---|---|
| A results web view, side by side | A printed summary |
| A cache of model answers | A resume only |
| A library of ready-made checks | One grader |
| Exit codes built for CI | Nothing yet |
| Tracing, datasets, team review (hosted tools) | Files on your laptop |

What you give up: a framework is someone else's code. Its defaults decide things for you (you'll meet one surprise later). Its summary may not be the statistic you need. And a hosted tool means your prompts and data live on someone else's servers.

> **Teacher's note:** A framework is like a car's dashboard. Very useful, but you still need to know what the engine is doing. Chapter 4 was the engine.

<!-- page -->

## Where each tool sits

![Grid: rows are your harness, promptfoo, Claude Console, LangSmith, Langfuse and Braintrust; columns are dataset, run, score, compare and monitor. The first three cover dataset to compare. The three hosted platforms also cover monitoring.](images/framework-map.svg)

Every tool runs the same loop: a **dataset**, a **run**, a **score**, a **compare**. The big difference is the last column. The hosted platforms also watch production traffic, which Chapter 11 needs.

The filled cells only mean "the docs we checked describe this". Vendor docs are vendor claims.

<!-- page -->

## promptfoo: install and the config

promptfoo is an open-source command-line tool (MIT licence). You write one YAML file and it runs every prompt against every test. Its README says evals run locally, and that it is now part of OpenAI.

No global install. Use `npx` and pin the version:

```
npx promptfoo@0.125.1 --version
```

The first half of `work/promptfoo/promptfooconfig.yaml`:

```yaml
prompts:
  - id: file://prompts/triage-v1.json
    label: A-v1
  - id: file://prompts/triage-v2.json
    label: B-v2
providers:
  - id: anthropic:messages:claude-haiku-5-5
    config:
      max_tokens: 1024
      effort: low
```

Same model, effort and token budget as the harness. And no `temperature`, because current Claude models don't accept it.

<!-- page -->

## The config: tests and the grader

```yaml
tests: file://tests.csv
defaultTest:
  assert:
    - type: javascript
      metric: accuracy
      value: >-
        output.trim().toLowerCase() ===
        context.vars.expected.toLowerCase()
evaluateOptions:
  repeat: 3
  maxConcurrency: 4
```

`defaultTest` applies the check to every test. It is the harness's `exact_match`: trim, lowercase, compare. `repeat: 3` is your `runs_per_case`.

Each prompt file is a chat: the system message is your `v1.txt` or `v2.txt`, and the user message is `{{message}}`. Each CSV row fills in the variables:

```
__description,message,expected
t01,"I was charged twice ...",refund
```

`build_from_harness.py` writes both files from your Chapter 4 files, so nothing is copied by hand.

<!-- page -->

## Checks you can use

promptfoo calls checks **assertions**. A few that fit a labelling task:

| Type | What it checks |
|---|---|
| `equals` | Output is exactly the value |
| `icontains` | Contains the value, any case |
| `regex` | Matches a pattern |
| `is-json` | Output is valid JSON |
| `javascript` / `python` | Your own code returns pass or a score |
| `llm-rubric` | A model grades against your rubric |

Put `not-` in front of any type to flip it, for example `not-icontains`. Add `metric:` to name a score in the report.

A test passes only if all its assertions pass, unless you set a `threshold` on the test.

Why not plain `equals`? It's case-sensitive: in our test, `Refund` failed `equals: refund`. Our JavaScript line trims and lowercases first, like the harness did.

<!-- page -->

## A model-graded check

`work/promptfoo/judge-example.yaml` adds an LLM judge:

```yaml
defaultTest:
  options:
    provider:
      id: anthropic:messages:claude-sonnet-5-5
  assert:
    - type: llm-rubric
      value: >-
        The output is exactly one of: refund,
        delivery, account, other.
```

`options.provider` picks the grader. Without it, promptfoo picks a default based on which API key you have set. Choose it yourself, and use a different model from the one being tested.

For four labels a code check is enough. This file only shows the syntax. A judge must be validated before you trust it (Chapter 8).

> **Teacher's note:** In our offline test we fixed a bug in a grader, reran, and got the **old** grades back. Grades are cached too. After changing a grader, run with `--no-cache`.

<!-- page -->

## Run it

```
cd work/promptfoo
python build_from_harness.py
export ANTHROPIC_API_KEY="..."
npx promptfoo@0.125.1 eval -n 5 --repeat 1
npx promptfoo@0.125.1 eval -o results.json
npx promptfoo@0.125.1 view
```

`-n 5 --repeat 1` is your smoke test: the first 5 cases, once each, for both prompts. Then the full run: 20 cases x 2 prompts x 3 repeats = 120 calls. `view` opens the results in your browser, served from your machine.

Want a free dry run first, like `--mock`? Swap the model for a local stand-in:

```
npx promptfoo@0.125.1 eval \
  -r file://offline/fake_triage.mjs
```

It's a keyword rule, wrong on purpose sometimes. Its scores mean nothing. It only proves the config, checks and outputs work.

<!-- page -->

## Results, cache and exit codes

The terminal table and the CSV export have one row per test and one column per prompt. The web view adds filters for failures, errors and differences.

**Cache.** promptfoo stores successful answers in `~/.promptfoo/cache` for 14 days by default. Errors aren't cached. In our test against a fake local server, the first run sent 120 requests, the rerun sent **zero**, and `--no-cache` sent 120 again. Each repeat has its own cache slot, so three repeats really are three answers.

That means a plain rerun is **not** a new sample. To see how much outputs vary (Chapter 2), use `--no-cache`.

**Outputs.** `-o` writes csv, json, jsonl, yaml, html, xml or junit.xml.

**Exit codes.** 0 if every test passed, 100 if any failed, and 1 for other errors (per the docs). Set `PROMPTFOO_PASS_RATE_THRESHOLD=90` to exit 0 at 90% or more instead. We checked the 0, the 100 and the threshold.

<!-- page -->

## Running it in CI

`work/ci-example/eval.yml` runs the eval on every pull request that touches the prompts, cases or config. The key step:

```yaml
- name: Run eval
  env:
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
    PROMPTFOO_PASS_RATE_THRESHOLD: "90"
  run: >
    npx --yes promptfoo@${PROMPTFOO_VERSION} eval
    -c promptfooconfig.yaml --no-table
    -o results.json -o report.html
```

Below 90%, promptfoo exits 100, the step fails, and the pull request shows a red cross. The full file also rebuilds the inputs from the harness (and fails if they're out of date), restores the cache, fails on any error, and uploads the results.

promptfoo also has an official GitHub Action. We used plain `npx` so every flag is visible.

<!-- page -->

## CI traps we hit

**The threshold covers every prompt in the run.** With A and B together, a strong B can hide a weak A, or the other way round. Gate the prompt you're shipping: `--filter-prompts B-v2`, or `export_pairs.py --gate B-v2 --min 0.90`.

**Errors can slip through.** One test run had 6 errors out of 120 calls and still exited 0 under an 80% threshold. So the workflow checks `results.stats.errors` separately.

**Keep the key out of the repo.** Store it as a repository secret. GitHub doesn't pass secrets to workflows from forked repositories, so outside contributors' pull requests can't spend your key.

**`~` doesn't work in `PROMPTFOO_CACHE_PATH`.** promptfoo uses the path as written. Use an absolute path.

**A proxy changed the request.** Through a custom base URL, promptfoo 0.125.1 added `temperature: 0` to our Claude request. On the real endpoint it didn't. Check what a tool sends.

<!-- page -->

## Side by side with your harness

![Diagram: the loop dataset, task, scorer, run, compare, with an arrow back from compare to task labelled change one thing, run again. In promptfoo these are tests.csv, prompts, assert, eval and view. In the Chapter 4 harness they are cases.jsonl, prompts, graders.py, the job list and the summary.](images/framework-loop.svg)

| Chapter 4 harness | promptfoo |
|---|---|
| `variants: A, B` | `prompts` with labels |
| `model`, `effort`, `max_tokens` | `providers` + `config` |
| `cases-v1.jsonl` | `tests.csv` (built from it) |
| `grader: exact_match` | `javascript` assertion |
| `runs_per_case: 3` | `repeat: 3` |
| `workers: 4` | `maxConcurrency: 4` |
| `records.jsonl` + summary | `results.json` + `view` |
| resume after a crash | cache (plus `--resume`) |

<!-- page -->

## What the pass rate doesn't tell you

promptfoo prints a pass rate per prompt: passes divided by tests, with every repeat counted as a test. That's a fine dashboard number. It is not a verdict.

It doesn't pair A and B case by case. It doesn't average repeats per case first. It has no confidence interval. With 20 cases, one case is 5 points.

So export the raw results and do the Chapter 9 analysis yourself:

```
python export_pairs.py results.json \
  --a A-v1 --b B-v2 --out pairs.csv
```

It writes one row per case (A's mean, B's mean, the difference) and prints wins, losses and ties. It skips calls that errored and says how many. Feed `pairs.csv` to the paired bootstrap from Chapter 9.

> **Teacher's note:** Only claim what you computed. "B passed more tests" is a fact. "B is better" needs the interval.

<!-- page -->

## The hosted platforms

All three offer datasets, experiments, code and LLM-judge scorers, human review, tracing, and online evals on live traffic (vendor claims, from their docs).

- **LangSmith** (LangChain team). The compare view marks each case red or green against a baseline, with a text diff. Prompts are versioned with commits and tags. You test a plain function, so LangChain isn't required. Hosted; self-hosting is an Enterprise add-on.
- **Langfuse.** Open source (MIT, except its `ee` folders). Langfuse Cloud, or self-host with Docker Compose or Kubernetes. Prompts have versions and labels, linked to traces. It offers a GitHub Action that can fail a pull request on a score threshold.
- **Braintrust.** Experiments are immutable records compared against a baseline, with green and red rows and a diff mode. It has a playground and a GitHub Action that comments on pull requests. Hosted; running the data plane in your own cloud (BYOC) needs the Enterprise plan.

<!-- page -->

## Two more you'll hear about

**Claude Console's Evaluate tab.** Anthropic's July 2024 announcement says you can add test cases by hand, import a CSV or generate them, compare two or more prompt versions side by side, and grade outputs on a 5-point scale. It's handy for a quick look with no code. Its old docs page now redirects to Anthropic's general guide on building evals, so check what the Console offers today.

**OpenAI Evals: don't start here.** OpenAI's deprecations page says the Evals platform became read-only on 31 October 2026 and shuts down on 30 November 2026. It points users to a migration guide for promptfoo. Learn the loop, not a tool that's closing.

> **Teacher's note:** Tools come and go. That's one more reason to know the loop by heart: dataset, task, scorer, run, compare.

<!-- page -->

## How to choose

| Your situation | Worth a look | Why |
|---|---|---|
| Learning, solo | Your harness, promptfoo | Free, local, files in git |
| Gate every pull request | promptfoo; Langfuse or Braintrust Actions | Exit code or PR check |
| Small team, shared view | LangSmith, Langfuse, Braintrust | Shared experiments and review |
| Regulated data | promptfoo local, self-hosted Langfuse | Data stays with you |
| Already on LangChain | LangSmith | Same vendor's tracing |
| Self-hosting, no enterprise deal | Langfuse, promptfoo | Open source |
| Production monitoring | LangSmith, Langfuse, Braintrust | Online evals on traces |

<!-- page -->

## Before you choose

LangSmith and Braintrust can also keep data in your own infrastructure, on enterprise plans. There's no best tool here, only a fit. Check the current pricing and data terms yourself. They change faster than this book.

<!-- page -->

## Lab: your experiment in promptfoo

1. Point `build_from_harness.py` at your Chapter 4 prompts and cases, then run it.
2. Run the offline check: `eval -r file://offline/fake_triage.mjs`. Fix any config errors.
3. Smoke test for real: `-n 5 --repeat 1`. Open `view` and read every answer.
4. Run the full eval with `-o results.json`. Then run `export_pairs.py`.
5. Compare with your harness run. Write down each prompt's accuracy in both tools, and the cases where the tools disagree. They are different samples, so small gaps are normal (Chapter 2).
6. Rerun without `--no-cache`. How many new calls did it make?
7. Optional: push to a GitHub repo with the workflow and your key as a secret. Open a pull request that edits `v2.txt`.

<!-- page -->

## Checkpoint

**1.** You rerun a promptfoo eval to see how much outputs vary, and every answer is identical. Why?

**2.** Your CI gate is an 80% pass rate. The job went green, but 6 calls errored. How, and what's the fix?

**3.** The promptfoo view shows B passing more tests than A. Can you tell your manager B is better?

<details><summary>Show answers</summary>
1. The rerun was served from the cache, so no new answers were generated. Use `--no-cache` to draw new samples.
2. The threshold only looks at the pass rate, and errors were a small share of it. Also fail the job when `results.stats.errors` is above zero.
3. Not yet. The pass rate isn't paired by case and has no interval. Export per-case results and run the Chapter 9 analysis. Then report the difference with its interval.
</details>

<!-- page -->

## In an interview

*"Your team uses an eval framework. How would you test a prompt change with it, and what wouldn't you trust it for?"*

*"Whatever the tool, the loop is the same: a versioned dataset, the task (prompt plus model settings), scorers, a run with repeats, and a comparison. I'd use code checks where a rule can decide and a validated judge only where judgment is needed. I'd run a smoke test, then the full set, and gate pull requests in CI on the prompt being shipped, failing on errors as well as on the pass rate. I wouldn't treat the dashboard's pass rate as a verdict. I'd export per-case results and compute a paired difference with a confidence interval. And I'd check what the tool actually sends and caches, because a cached rerun isn't a new sample."*

<!-- page -->

## Read more

- **promptfoo**, configuration guide and assertions reference. [promptfoo.dev/docs/configuration/guide](https://www.promptfoo.dev/docs/configuration/guide/), [expected outputs](https://www.promptfoo.dev/docs/configuration/expected-outputs/)
- **promptfoo**, command line, caching and CI/CD. [command line](https://www.promptfoo.dev/docs/usage/command-line/), [caching](https://www.promptfoo.dev/docs/configuration/caching/), [CI/CD](https://www.promptfoo.dev/docs/integrations/ci-cd/)
- **promptfoo**, Anthropic provider (model IDs, `effort`). [promptfoo.dev/docs/providers/anthropic](https://www.promptfoo.dev/docs/providers/anthropic/)
- **LangSmith**, evaluation concepts. [docs.langchain.com/langsmith/evaluation-concepts](https://docs.langchain.com/langsmith/evaluation-concepts)
- **Langfuse**, evaluation overview. [langfuse.com/docs/evaluation/overview](https://langfuse.com/docs/evaluation/overview)
- **Braintrust**, evaluate. [docs.braintrust.dev/evaluate](https://docs.braintrust.dev/evaluate)
- **OpenAI**, deprecations (Evals platform timeline). [developers.openai.com/api/docs/deprecations](https://developers.openai.com/api/docs/deprecations)
- **Next chapter:** online A/B testing. You'll take a prompt that won offline and test it safely on real traffic: shadow, canary, split, and guardrail metrics.
