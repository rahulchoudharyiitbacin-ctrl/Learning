# Hands-on: a minimal A/B harness in Python

In Chapter 3 you wrote an experiment file. A file is a plan, not a result. Now you'll build the machine that runs it: about 100 lines of Python that call a real model, grade every answer, save everything, and print a summary.

This is the same loop that tools like promptfoo run for you (Chapter 10). Build it once by hand, and those tools stop being magic.

The tested code is in `work/harness/run_experiment.py`, with a sample experiment, prompts and 20 test cases beside it. The pages ahead walk through it piece by piece.

<!-- page -->

## The plan

![Diagram: five steps. 1 read the experiment file. 2 make the job list of cases times variants times runs, shuffled. 3 call the model and grade each answer, a few calls in parallel. 4 save one line per call. 5 print the summary.](images/harness-pipeline.svg)

The sample task is sorting customer messages into four labels: refund, delivery, account, other. Prompt A is plain instructions. Prompt B adds three worked examples.

<!-- page -->

## Setup

```
cd work/harness
python3 -m venv .venv
source .venv/bin/activate
pip install anthropic pyyaml
export ANTHROPIC_API_KEY="..."
```

The SDK reads the key from that environment variable. **Never paste a key into a file** you might commit or share.

Your folder should match Chapter 3: `prompts/`, `data/`, `experiments/`. The harness writes to a new `runs/` folder.

<!-- page -->

## Step 1: read the inputs

```python
def read_jsonl(path):
    lines = Path(path).read_text().splitlines()
    return [json.loads(x) for x in lines
            if x.strip()]

cfg = yaml.safe_load(cfg_path.read_text())
cases = read_jsonl(root / cfg["dataset"])
prompts = {v: (root / p).read_text()
           for v, p in cfg["variants"].items()}
```

Everything the run depends on comes from the files, so you can rerun it next month and get the same setup.

<!-- page -->

## Step 2: call the model

```python
resp = client.messages.create(
    model=cfg["model"],
    max_tokens=cfg["max_tokens"],
    system=system,
    messages=[{"role": "user",
               "content": text}],
    **extra,   # effort, if the config sets it
)
out = "".join(b.text for b in resp.content
              if b.type == "text")
```

We also save `resp.stop_reason`, the token counts from `resp.usage`, and the time taken.

> **Teacher's note:** There is no `temperature` here. Newer Claude models don't accept it. And current models can think before answering, which uses `max_tokens`, so we give them 1024 instead of 20.

<!-- page -->

## Step 3: grade

```python
def exact_match(case, output):
    return int(output.strip().lower()
               == case["expected"].lower())

GRADERS = {"exact_match": exact_match}
```

The experiment file says `grader: exact_match`, and the harness looks that name up. Adding a new grader means adding one function and one dictionary entry.

Use code checks wherever the answer can be checked exactly. They're free, fast and never in a bad mood (Chapter 7 covers when you need more, and Chapter 8 the LLM judge).

<!-- page -->

## Step 4a: the job list

```python
jobs = [(c, v, i) for c in cases
        for v in prompts
        for i in range(cfg["runs_per_case"])]
random.Random(0).shuffle(jobs)
jobs = [j for j in jobs
        if (j[0]["id"], j[1], j[2]) not in done]
```

20 cases x 2 variants x 3 runs = **120 calls**. We shuffle them, so A and B are spread over the whole run (Chapter 3's "run them together"). The fixed seed makes the order repeatable.

The last line is a **resume**: calls already saved are skipped, so a crash at call 90 doesn't cost you the first 89.

<!-- page -->

## Step 4b: run and save

```python
with ThreadPoolExecutor(max_workers=4) as pool, \
        open(path, "a") as f:
    futures = [pool.submit(run_job, client, cfg,
               prompts, grader, j) for j in jobs]
    for fut in as_completed(futures):
        rec = fut.result()
        rec["config_hash"] = chash
        f.write(json.dumps(rec) + "\n")
        f.flush()
```

Four calls run at once. Each finished call is written to disk right away, one JSON line each (the run record from Chapter 3).

If a call fails, `run_job` stores the error text in the record instead of crashing, so you can count failures rather than lose them.

<!-- page -->

## Step 5: the summary

```python
case_mean[(variant, case_id)] = mean grade
# accuracy = average of the per-case means
# diff = B - A, case by case
```

(Shortened; see the file for the full version.)

The harness averages the 3 runs **per case first**, then compares A and B on the same cases. That is the paired comparison from Chapter 2, and it's why three runs aren't counted as three independent cases.

It prints accuracy per variant, total tokens, median latency, and how many cases B won, lost or tied. It deliberately stops short of a verdict. Chapter 9 adds the confidence interval.

<!-- page -->

## First, a free dry run

```
python run_experiment.py \
  experiments/ticket-triage-v1-vs-v2.yaml --mock
```

`--mock` swaps in a fake model, so there are no API calls and no cost. It tests the file reading, job list, saving and summary.

```
120 calls, 0 errors
A: accuracy 0.833 ...
B: accuracy 0.750 ...
B - A = -0.083 over 20 cases
```

Those numbers are **random and meaningless**. Mock results go to a separate file so they never mix with real ones.

<!-- page -->

## Your first real run

Start small. Copy 5 lines of `cases-v1.jsonl` into `cases-small.jsonl`, point the config at it, and run without `--mock`:

```
python run_experiment.py \
  experiments/ticket-triage-v1-vs-v2.yaml
```

That's 30 calls. Check the records before scaling to the full 120. Then ask:

- Are there any errors?
- Is any `output` empty?
- What does `stop_reason` say?
- Do the token counts look sensible?

This habit, **smoke test, then scale**, saves money and time in every eval you'll ever run.

<!-- page -->

## When something goes wrong

| You see | Likely cause | Fix |
|---|---|---|
| Error mentioning `temperature` | Model doesn't accept it | Remove it from your call |
| Empty `output`, `stop_reason: max_tokens` | Thinking used up the budget | Raise `max_tokens` |
| 401 error | Key missing or wrong | Check the environment variable |
| 429 errors | Too many calls at once | Lower `workers` |
| Rerun gives different accuracy | Outputs vary (Chapter 2) | Expected, not a bug |
| Nothing new runs | Resume skipped saved calls | New experiment `name`, or delete the records file |

<!-- page -->

## What this harness leaves out

It is deliberately small. Not included:

- **Statistics.** A difference without an interval is not a verdict (Chapter 9).
- **LLM judges.** Only exact match, for now (Chapter 8).
- **Smarter retries.** The SDK retries failures a couple of times; nothing more.
- **Caching, cost reports, dashboards.** Frameworks add these (Chapter 10).

Small is a feature: every line is something you can explain in an interview.

<!-- page -->

## Lab: run your own experiment

1. Take your Chapter 3 experiment file and prompts.
2. Replace the sample cases with at least 20 of your own, each with an `expected` answer.
3. Run `--mock`, then 5 cases for real, then the full set.
4. Write down: accuracy of A and B, errors, empty outputs, tokens, and total cost.
5. Open 5 records where A and B disagree. Which prompt looks right?

Keep the `runs/` folder. Chapter 5 starts by reading those outputs.

<!-- page -->

## Checkpoint

**1.** Why save one line per call instead of just the final accuracy?

**2.** Why store errors in the record instead of letting the run crash?

**3.** You rerun the full experiment and accuracy changes slightly. Is the harness broken?

<details><summary>Show answers</summary>
1. The raw lines let you find out *why* a prompt lost, regrade later, and recompute any statistic without paying for the calls again.
2. A crash loses the progress, and silently skipping errors hides a problem. Saved errors can be counted and investigated.
3. Not necessarily. Model outputs vary between runs (Chapter 2), which is why the harness runs each case several times and why differences need an interval (Chapter 9).
</details>

<!-- page -->

## In an interview

*"Walk me through how you'd build a small eval harness."*

*"I'd read an experiment file with the prompts, dataset, model settings and grader. I'd build the job list of cases times variants times runs, shuffle it so both variants face the same conditions, and run the calls in parallel with a resume so a crash doesn't lose work. Each call writes one record with the output, grade, tokens, latency and a config hash. The summary averages repeated runs per case, then compares variants case by case. I always start with a mock run and a small smoke test."*

<!-- page -->

## Read more

- **Anthropic**, Messages API and Python SDK documentation. [platform.claude.com/docs](https://platform.claude.com/docs)
- **Anthropic**, *Define success criteria and build evaluations*, for grading approaches. [platform.claude.com](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)
- **Chip Huyen**, *AI Engineering* (O'Reilly, 2025), Ch 4, "Design Your Evaluation Pipeline".
- **Hamel Husain**, *Your AI Product Needs Evals*, on writing your own eval tooling. [hamel.dev/blog/posts/evals](https://hamel.dev/blog/posts/evals/)
- **Next chapter:** error analysis. You'll read the outputs this harness saved.
