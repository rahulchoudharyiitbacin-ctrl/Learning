# Drill 1: async eval harness with caching

**Time budget:** 45 minutes. Start a timer before you read past this line.

## The task

You have a model client, `call_model(model, prompt) -> str`, in `fake_llm.py`. It is async, slow, and sometimes rate-limited. Write `run_eval(...)` in your own copy of `starter.py`. It runs every **case x variant x run**, calls the model concurrently, grades each answer, and saves one JSON line per job.

Requirements:

1. **Concurrency limit.** At most `concurrency` model calls in flight at once.
2. **Retries.** On `RateLimitError` (HTTP 429), wait and retry with exponential backoff: wait about `base_delay * 2**k` before retry k+1 (k = 0, 1, ...), plus optional jitter of at most `base_delay / 4`. Give up after `max_retries` retries. Do **not** retry other errors.
3. **On-disk cache** in `cache_dir`, keyed by **(model, prompt, run index)**. Running the same eval again makes **zero** calls for jobs that succeeded before.
4. **Results file:** JSONL at `out_path`, overwritten each run, one record per job, sorted by `(case_id, variant, run)`. Return the same list.
5. **Grading:** `grade = 1` if `output.strip().lower() == expected.strip().lower()`, else 0.

Record fields: `case_id` (str), `variant`, `run` (int), `model`, `output`, `grade`, `error`, `attempts`, `cached`.

- `attempts`: real calls made for this record (0 if served from the cache or shared with an identical job).
- `cached`: true if no call was made for this record.

## Inputs

- `cases`: list of `{"id", "input", "expected"}`. Sample: `cases.jsonl`.
- `variants`: dict of name -> template with `{input}`. Sample: `variants.json`.
- The prompt is the template with `{input}` replaced by the case input.

## Things a careful solution handles (the hidden requirements)

The tests check all of these. Some are not spelled out above on purpose; they are what an interviewer probes.

- Two jobs with the **same key** must not both call the model, even if they start at the same moment.
- Repeated runs must stay **separate samples**.
- **Errors are recorded, not hidden**: `output` and `grade` are `None`, `error` says what happened. One bad case never stops the run. Errors are **not cached**, so a rerun tries them again.
- Results must not depend on which call **finished first**.

## Done means

```
python test_drill1.py my_drill1.py
```

prints `12/12 passed`, and you can explain each design choice out loud in two minutes. Then compare with `solution.py`.
