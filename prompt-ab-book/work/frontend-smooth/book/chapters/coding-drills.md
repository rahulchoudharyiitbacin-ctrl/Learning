# Coding drills

Reading about a bootstrap is not the same as writing one with a clock running and someone watching. This chapter gives you four timed drills, each 30 to 45 minutes, built from the code you met in Chapters 4, 7, 8 and 9:

1. An async eval harness with caching and retries.
2. A paired bootstrap, clustered by case.
3. Judge-agreement metrics from a labels CSV.
4. Structured-output validation with field-level accuracy.

Each drill has a task sheet, a starter file, tests and a reference solution in `work/drills/`. Everything runs offline with the Python standard library.

Prep sites and community repos describe two coding formats for these roles: a live exercise (often an eval harness with parallel calls and caching) and a take-home with an eval script. They report this rather than cite candidates, so treat it as a likely shape, not a promise. The drills cover both.

<!-- page -->

## The rules

Do the drills like an exam, not like a tutorial.

- **Set a timer** for the budget on the task sheet. When it rings, stop. Write down where you got to.
- **Read only the README** before you start. The hints in this chapter are hidden; open them only when stuck for 10 minutes.
- **No copy-paste** from this book, the solution file or Chapters 4 to 9. Python's own docs are fine. An AI assistant is not.
- **Talk out loud** while you work, as if an interviewer were listening. Say what you're about to do and why.
- **Run the tests** when you think you're done, not before. Then score yourself.

> **Teacher's note:** Stopping at the bell matters. A real interview ends on time, and a half-working solution you can explain beats a full one you can't. The timer trains that judgement.

<!-- page -->

## Running a drill

Each folder has the same files:

| File | What it is |
|---|---|
| `README.md` | The task, exactly as you get it |
| `starter.py` | Signatures, docstrings, TODOs |
| `test_drillN.py` | The tests |
| `solution.py` | Reference (don't open yet) |

Copy the starter and test your copy:

```
cd work/drills/drill2_paired_bootstrap
cp starter.py my_drill2.py
python test_drill2.py my_drill2.py
```

You can also write `DRILL_FILE=my_drill2.py python test_drill2.py`. With no argument the tests run against `solution.py`, which passes them all. The starter fails them all, which proves the tests check something real.

Each test prints PASS or FAIL with a short reason. Read the reasons. They name the edge case you missed.

<!-- page -->

## How to score yourself

After the timer, score each line 0, 1 or 2. Be strict.

| Criterion | 2 points means |
|---|---|
| Correctness | All tests pass |
| Edge cases | You handled them before a test told you |
| Clarity | Short functions, clear names, no dead code |
| Your own tests | You wrote at least two checks of your own |
| Narration | You explained each choice out loud |

That is 10 points per drill. **8 or more** is interview-ready. **5 to 7**: redo the drill from a blank file in three days. **Under 5**: reread the chapter it builds on, then redo it.

> **Teacher's note:** "Edge cases" counts only what you caught yourself. If the tests found it, you get 0 or 1 on that line, even after you fix it. That is the gap an interviewer sees.

<!-- page -->

## Drill 1: async eval harness (45 min)

**The task.** `fake_llm.py` gives you an async model client, `call_model(model, prompt)`. It is slow, it sometimes returns a 429, and some prompts always fail. Write `run_eval(...)` to run every case x variant x run and save one JSON line per job.

Requirements, in short:

- At most `concurrency` calls in flight.
- Retry a 429 with exponential backoff; don't retry other errors.
- An on-disk cache keyed by **model, prompt and run index**, so a rerun costs nothing.
- A JSONL file, overwritten each run, sorted by case, variant and run.
- Grade by exact match after trimming and lower-casing.

Hidden requirements the tests check: no duplicate calls, results that don't depend on which call finished first, and errors recorded, not hidden.

`work/drills/drill1_async_harness/README.md` has the full sheet. This is Chapter 4's harness, made async and made robust.

<!-- page -->

## Drill 1: hints

<details><summary>Hint 1: the idea</summary>
An `asyncio.Semaphore` caps calls in flight. A dict of in-flight tasks, keyed by the cache key, makes identical jobs share one call. The run index belongs in the key: without it, three runs of a prompt collapse into one cached answer and your repeated runs measure nothing.
</details>

<details><summary>Hint 2: the structure</summary>
Four small pieces. `call_with_retry` returns (output, error, attempts) and never raises. `fetch(key, prompt)` checks the cache, takes the semaphore, calls `call_with_retry`, and caches successes only. `job(case, variant, run)` builds the key, reuses or creates the in-flight task, and builds the record. `run_eval` gathers the jobs, sorts the records and writes the file.
</details>

> **Teacher's note:** The fake client has no temperature setting. Current Claude models don't accept temperature either, so repeated runs are how you sample the model's randomness. That is why the run index stays in the key.

<!-- page -->

## Drill 1: what interviewers look for

**Good signs:**

- You ask "what counts as the same call?" before writing the cache.
- You say why errors must not be cached: a rerun should try them again.
- You make a failed call visible. `output` and `grade` are `None`, `error` says what happened, and the run goes on.
- You mention that a real 429 may carry a `retry-after` header, and you'd wait that long.

**Common mistakes:**

- Checking the cache, then awaiting the call. Two identical jobs both miss the cache and both call. The tests count calls.
- Catching every exception and returning `""`. The case is graded 0, and a broken prompt looks like a bad one.
- Appending to the results file, so a rerun doubles the rows.
- Collecting results with `as_completed`, so the order changes every run.

<!-- page -->

## Drill 1: walk-through, part 1

The key is to claim the in-flight slot **before** the first `await`. asyncio only switches tasks at an `await`, so the check and the set happen together.

```python
async def job(case, variant, run):
    prompt = render(variants[variant], case)
    key = cache_key(model, prompt, run)
    owner = key not in inflight
    if owner:  # no await before this
        inflight[key] = asyncio.ensure_future(
            fetch(key, prompt))
    out, err, n, hit = await inflight[key]
    # build the record; a non-owner made
    # no call, so its attempts are 0
```

`fetch` checks the disk cache, then takes the semaphore, then calls. A duplicate job awaits the owner's task instead of making its own call. So the sum of `attempts` across records equals the number of real calls. That is a nice number to print at the end.

<!-- page -->

## Drill 1: walk-through, part 2

Retries live in one function that never raises. Simplified:

```python
while True:
    attempts += 1
    try:
        out = await call_model(model, prompt)
        return out, None, attempts
    except RateLimitError as e:
        if attempts > max_retries:
            return None, f"429: {e}", attempts
        await asyncio.sleep(
            base_delay * 2 ** (attempts - 1))
    except Exception as e:
        return None, repr(e), attempts
```

The waits grow: 1, 2, 4 times `base_delay`. A 400 returns at once, after one attempt. Back in `fetch`, only results with no error go into the cache.

The full version adds a little jitter and writes each cache file atomically: write to a temp file, then rename it. A crash halfway through never leaves a broken cache entry.

<!-- page -->

## Drill 2: paired bootstrap (30 min)

**The task.** You have one record per call: `case_id`, `variant`, `run`, `grade`. Write two functions.

- `case_diffs(records, a, b)` returns the per-case difference **d = mean grade of B minus mean grade of A**, averaging each case's runs first. Skip records whose grade is `None` (API errors). Drop cases without a graded run for both variants, and list them.
- `paired_bootstrap(...)` returns the mean of d and a 95% percentile bootstrap interval. It resamples **cases**, `n_boot` times, with `random.Random(seed)`. Fewer than 2 cases raises `ValueError`.

The README fixes the percentile positions, so your interval is comparable with the reference. Sample data: `records.jsonl`, 80 cases x 2 variants x 3 runs, shuffled. It has two errors and one case with no B runs.

This is Chapter 9's bootstrap. The trap is the same as there: runs of one case are not independent cases.

<!-- page -->

## Drill 2: hints

<details><summary>Hint 1: the idea</summary>
Reduce the data to one number per case before any statistics. After that, the bootstrap is four lines: draw n values of d with replacement, take the mean, repeat, sort, read two positions. Resampling the d values keeps each case's runs together and keeps A and B paired.
</details>

<details><summary>Hint 2: the structure</summary>
Group grades into a dict of case, then variant, then list of grades. Loop over the case ids in <b>sorted</b> order to build d and the dropped list. In <code>paired_bootstrap</code>, call <code>case_diffs</code>, check the case count, then resample. Sorting matters: if d follows record order, the same seed gives a different interval when the records arrive in a different order.
</details>

> **Teacher's note:** `rng.choices(d, k=n)` draws with replacement, which is what the bootstrap needs. `rng.sample` draws without replacement and would return the same mean every time.

<!-- page -->

## Drill 2: what interviewers look for

**Good signs:**

- You average runs per case **before** anything else, and say why: three runs of a case are not three new cases.
- You state what the interval means. If you repeated the experiment, about 95% of intervals built this way would contain the true gain. It is not "a 95% chance B is better".
- You know a p-value is **not** the probability that B is better.
- You report how many cases were dropped, and you note that dropping errors can bias the result if one prompt errors more.

**Common mistakes:**

- Pooling all rows: B's mean minus A's mean over rows. With unequal runs per case, that gives the wrong number.
- Resampling rows. The interval comes out too narrow and claims too much.
- Treating a `None` grade as 0, so an outage looks like a bad prompt.
- Using the global `random` without a seed, so nobody can reproduce your interval.

<!-- page -->

## Drill 2: walk-through

`case_diffs` has already turned the records into one d per case, averaging each case's runs first. The bootstrap is then short:

```python
d = [diffs[c] for c in sorted(diffs)]
n = len(d)
rng = random.Random(seed)
means = sorted(
    sum(rng.choices(d, k=n)) / n
    for _ in range(n_boot))
lo = means[int(alpha / 2 * n_boot)]
hi = means[math.ceil(
    (1 - alpha / 2) * n_boot) - 1]
```

The first line sorts the case ids, so the same seed gives the same interval whatever order the records arrive in. With 5,000 draws, `lo` is `means[125]` and `hi` is `means[4874]`, as in Chapter 9. On the sample file: a gain of +0.036, interval -0.057 to +0.131. It includes 0, so the verdict is **not proven**.

<!-- page -->

## Drill 2: how the tests check the maths

A statistics function can return a plausible number and still be wrong. The tests check yours four ways.

- **A hand-computed mean.** Three cases with 3, 1 and 2 runs give a case-level mean of 0.194. Pooling rows gives 0.111, which fails.
- **An exact small bootstrap.** With d = 0, 0, 0, 1, the number of 1s in 4 draws follows a binomial distribution. The chance the mean is 1 is 0.4%, under 2.5%. The chance it's at least 0.75 is 5.1%. So the upper bound must be exactly 0.75.
- **Clustering.** 60 cases with 5 identical runs each. Your width must be close to the case-level formula. Resampling rows gives about 45% of it.
- **Coverage.** 1,000 simulated experiments with a known true gain. The reference interval contains it 94.7% of the time. The test accepts 92% to 98%.

<!-- page -->

## Drill 3: judge agreement (30 min)

**The task.** An expert labelled 103 outputs PASS or FAIL. Your LLM judge labelled the same outputs. `labels.csv` has columns `id,human_label,judge_label`. Write:

- `load_labels(path)`, reading the CSV;
- `wilson(k, n)`, the Wilson score interval, or `None` when n is 0;
- `agreement_report(rows)`, returning the confusion counts, TPR, TNR, raw agreement, Cohen's kappa, and Wilson intervals for TPR and TNR.

**FAIL is the positive class**, as in Chapter 8. TPR is the share of real failures the judge caught. TNR is the share of real passes it passed.

The file is messy on purpose. Labels come as `fail `, `Pass` and `FAIL`. Three judge labels are blank, `ERROR` or `N/A`. And the file starts with a byte-order mark, the invisible character Excel adds to some CSV files.

When you're done, the sample gives Chapter 8's numbers: TPR 0.600 (0.387 to 0.781), TNR 0.925, kappa 0.545.

<!-- page -->

## Drill 3: hints

<details><summary>Hint 1: the idea</summary>
Everything comes from four counts: TP, FN, FP, TN. Normalise each label with strip and upper first. A judge label that is not PASS or FAIL is skipped and counted, never turned into PASS. A human label that is not PASS or FAIL is a data error, so raise. Any rate with a zero denominator is undefined: return <code>None</code>, not 0.
</details>

<details><summary>Hint 2: the structure</summary>
<code>confusion(rows)</code> returns the four counts plus <code>skipped</code>. <code>kappa(counts)</code> computes observed agreement, chance agreement from the two raters' FAIL rates, then the ratio, with a guard for chance agreement of 1. <code>wilson(k, n)</code> is one formula. <code>agreement_report</code> calls them and builds the dict. Open the CSV with <code>encoding="utf-8-sig"</code> to drop the byte-order mark.
</details>

<!-- page -->

## Drill 3: what interviewers look for

**Good signs:**

- You lead with TPR and TNR, not raw agreement, and say why: when failures are rare, agreement is mostly the big PASS row.
- You show kappa is low on an imbalanced table. TP 2, FN 8, FP 4, TN 186 has 94% agreement but kappa 0.22.
- You report n next to each rate and add intervals, because 20 failures is a small sample.
- You ask which label is "positive" before you code.

**Common mistakes:**

- Returning TPR = 0 when there are no human FAILs. Zero means "caught none of them"; here there were none to catch.
- Dropping unlabelled rows without counting them. If the judge errors on hard cases, the metrics look better than they are.
- Using `p ± 1.96·sqrt(p(1-p)/n)` (the Wald interval). At 0 failures caught, it has zero width.
- Returning kappa 1 when both raters said PASS to everything. That is 0/0, not perfect agreement.

<!-- page -->

## Drill 3: walk-through

Kappa, with the guard:

```python
po = (c["tp"] + c["tn"]) / n
h = (c["tp"] + c["fn"]) / n  # human FAIL
j = (c["tp"] + c["fp"]) / n  # judge FAIL
pe = h * j + (1 - h) * (1 - j)
if pe >= 1:
    return None  # 0/0: undefined
return (po - pe) / (1 - pe)
```

Chance agreement `pe` is the chance both say FAIL plus the chance both say PASS, from each rater's own FAIL rate. If both raters used one label only, `pe` is 1 and kappa is undefined.

Wilson is one formula (in the README). It stays inside 0 to 1 and keeps a sensible width at 0 out of 10: from 0 to 0.278. The tests check that bound against the closed form z² / (n + z²), and 12 of 20 against an independent brute-force search: 0.387 to 0.781.

<!-- page -->

## Drill 4: structured output (35 min)

**The task.** A triage prompt asks for JSON with five fields:

| Field | Type and rule |
|---|---|
| category | string, one of 4 labels |
| urgent | boolean |
| amount | number |
| items | integer |
| order_id | string, optional |

Write three functions:

- `parse_output(text)` accepts bare JSON, JSON in a code fence, or JSON with prose around it. Anything else fails, with a reason.
- `validate(obj, schema)` returns the errors (missing, wrong type, not in the enum) and lists extra keys separately. Extra keys are not errors.
- `evaluate(outputs, expected, schema)` returns parse rate, schema-valid rate, exact-match rate, per-field accuracy and per-case details.

`sample.jsonl` holds 10 raw outputs: fenced, chatty, single-quoted, a trailing comma, a list, and a few wrong types. It is Chapter 7's JSON grader, grown up.

<!-- page -->

## Drill 4: hints

<details><summary>Hint 1: the idea</summary>
Two Python facts are the whole drill. <code>isinstance(True, int)</code> is true, because bool is a subclass of int. And <code>0 == False</code> is true. So check booleans before integers, rule bool out of "integer" and "number", and compare a field only after its type is valid. Every rate divides by <b>all</b> outputs: one that didn't parse is wrong on every field.
</details>

<details><summary>Hint 2: the structure</summary>
<code>parse_output</code>: find a fenced block with a regex, else use the whole text; try <code>json.loads</code>; on failure, try the slice from the first <code>{</code> to the last <code>}</code>; reject anything that isn't a dict. <code>type_ok(value, kind)</code> and <code>validate</code> come next. <code>evaluate</code> loops once, filling a per-field counter and a per-case dict.
</details>

<!-- page -->

## Drill 4: what interviewers look for

**Good signs:**

- You ask what to do with extra keys and with optional fields before coding.
- You report the **parse rate** separately. A prompt that breaks JSON 10% of the time has a different problem from one that picks the wrong category.
- You score each field on its own, so one bad field doesn't hide four good ones.
- You say that even when an API can enforce a JSON shape, you still validate and score fields, because a valid shape can hold a wrong value.

**Common mistakes:**

- Computing accuracy over parsed outputs only. It flatters exactly the prompt that breaks JSON.
- `isinstance(v, int)` for integers, which lets `True` through.
- Plain `==` for comparison, so `"urgent": 0` counts as correct for `False`.
- Treating extra keys as fatal, or ignoring them silently. Report them.

<!-- page -->

## Drill 4: walk-through

The type check, with the bool trap:

```python
def type_ok(v, kind):
    if kind == "string":
        return isinstance(v, str)
    if kind == "boolean":
        return isinstance(v, bool)
    if isinstance(v, bool):  # True is an int
        return False
    if kind == "integer":
        return isinstance(v, int)
    return (isinstance(v, (int, float))
            and math.isfinite(v))
```

A field scores right only if the output parsed, has the field, the type is valid, and the value matches: numbers by value (3.0 equals 3), everything else exactly. An optional field missing on both sides is right.

On the sample: parsed 70%, schema-valid 30%, all fields right 30%. Those were also counted by hand.

<!-- page -->

## Did the tests earn your trust?

A test suite that passes everything proves nothing. So each one was checked against deliberately careless solutions. `work/drills/check_mutants.py` takes the reference, makes one typical mistake at a time, and runs the tests:

| Drill | Careless versions | Caught |
|---|---|---|
| 1 Harness | 9 | 9 |
| 2 Bootstrap | 5 | 5 |
| 3 Judge | 6 | 6 |
| 4 JSON | 6 | 6 |

The mistakes include the ones on the "common mistakes" pages: no in-flight dedup, a cache key without the run, rows resampled instead of cases, TPR 0 instead of undefined, and `True` accepted as an integer.

Run it yourself: `python check_mutants.py`, about 30 seconds. All four suites pass on Python 3.9, 3.11 and 3.14.

> **Teacher's note:** In a take-home, do the same in miniature. Break your own code on purpose and check that a test goes red.

<!-- page -->

## Narrate like this

Interviewers grade your thinking as much as your code. Here is drill 2's opening minute, said out loud:

*"Before any statistics I'll reduce this to one number per case, because the three runs of a case share its difficulty. If I treated them as separate cases, the interval would be too narrow. Some cases have different run counts, so I'll average within each variant first, then subtract. I'll skip null grades, since those are API errors, not failures, and I'll report how many cases I drop. For the interval I'll resample cases with a seeded generator and sort the case ids first, so the result doesn't depend on input order. Then I'll check it on a tiny case I can work out by hand."*

That is about 110 words, a minute of talking. It tells the interviewer you know the trap, the edge cases and how you'll test. Write a similar minute for each drill.

<!-- page -->

## Your drill schedule

The drills stick when you repeat them from a blank file.

| When | What |
|---|---|
| Day 1 | All four drills, timed, scored |
| Day 4 | Redo any drill under 8 |
| Day 14 | All four again, 10 minutes faster |
| Before an interview | One drill, cold, as a warm-up |

Keep a log: date, drill, minutes used, score, and the edge case you missed. Patterns show up quickly. Most people find they lose points on the same line, usually edge cases or narration, not correctness.

Then raise the bar. Add a feature the README didn't ask for: a `retry-after` value in drill 1, a t-interval next to the bootstrap in drill 2, a corrected failure rate in drill 3 (Chapter 8), nested objects in drill 4. Explaining an extension is a strong interview answer.

<!-- page -->

## Check yourself

**1.** Drill 1's cache is keyed by model and prompt only. You run 3 runs per case. What goes wrong, and would anyone notice?

**2.** Your judge report shows TPR = 0.0 on a dev set. What two very different things could that mean?

**3.** Your JSON eval reports category accuracy of 98%. Your colleague's script says 88% on the same outputs. Name a likely cause.

<details><summary>Show answers</summary>
1. Every run returns the first cached answer, so runs never vary. Nothing errors, so nobody notices. Put the run index in the key.
2. The judge caught none of the real failures, or there were no human failures at all. The second is undefined, not 0. Report n next to every rate.
3. One script divides by parsed outputs only. If 10% of outputs failed to parse, 98% of the parsed ones is about 88% of all of them.
</details>

<!-- page -->

## Read more

- **Python docs**, *asyncio synchronization primitives*: `Semaphore` and the `async with` form used in drill 1. [docs.python.org](https://docs.python.org/3/library/asyncio-sync.html)
- **Anthropic**, *Rate limits*: 429 errors and the `retry-after` header, which says how many seconds to wait. [platform.claude.com](https://platform.claude.com/docs/en/api/rate-limits)
- **Python docs**, `random.choices`: draws with replacement; seeded generators repeat their sequence. [docs.python.org](https://docs.python.org/3/library/random.html)
- **Miller 2024**, *Adding Error Bars to Evals*: the statistics behind drill 2. [arXiv 2411.00640](https://arxiv.org/abs/2411.00640)
- **Husain and Shankar**, *Evals FAQ*: measure a judge with TPR and TNR. [hamel.dev](https://hamel.dev/blog/posts/evals-faq/)
- **Wikipedia**, *Binomial proportion confidence interval* (Wilson) and *Cohen's kappa*. [Wilson](https://en.wikipedia.org/wiki/Binomial_proportion_confidence_interval), [kappa](https://en.wikipedia.org/wiki/Cohen%27s_kappa)
- **Python docs**, built-in `bool`: a subclass of `int`, the trap in drill 4. [docs.python.org](https://docs.python.org/3/library/functions.html#bool)
- **Next chapter:** none; return to Chapter 13 for the mock-interview plan.
