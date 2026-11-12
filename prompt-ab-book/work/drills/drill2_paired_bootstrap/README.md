# Drill 2: paired bootstrap, clustered by case

**Time budget:** 30 minutes. Start a timer before you read past this line.

## The task

You ran prompts A and B on the same test cases, several runs each. You have one record per call:

```json
{"case_id": "case-007", "variant": "B", "run": 2, "grade": 1}
```

Write two functions in your own copy of `starter.py`:

1. `case_diffs(records, a, b)` returns `({case_id: d}, dropped)`, where **d = mean grade of B minus mean grade of A for that case**. Average a case's runs first. Skip records with `grade` = `None` (API errors). A case with no graded run for A or for B is dropped and listed in `dropped` (sorted).
2. `paired_bootstrap(records, a, b, n_boot=5000, seed=0, alpha=0.05)` returns a dict with `mean_diff`, `ci_low`, `ci_high`, `n_cases`, `dropped_cases`.
   - `mean_diff` is the mean of the d values.
   - The interval is a **percentile bootstrap that resamples cases**: draw n d values with replacement, take the mean, repeat `n_boot` times with `random.Random(seed)`, sort, and read `means[int(alpha/2 * n_boot)]` and `means[ceil((1 - alpha/2) * n_boot) - 1]`.
   - Raise `ValueError` if fewer than 2 cases remain.

Sample data: `records.jsonl` (80 cases x 2 variants x 3 runs, shuffled, with two errors and one case missing B). It was written by `make_records.py`.

## Things a careful solution handles

- Cases can have **different numbers of runs**. Pooling all rows gives the wrong mean.
- Resampling **rows** instead of cases gives an interval that is too narrow.
- The **same seed** gives the **same answer** whatever order the records arrive in.
- A `None` grade is skipped, never counted as 0.

## Done means

```
python test_drill2.py my_drill2.py
```

prints `11/11 passed` (about 2 seconds; one test is a coverage simulation), and you can say in one sentence why you average runs per case first.

Running the reference on the sample: `python solution.py records.jsonl` prints `B - A: +0.036  95% CI [-0.057, +0.131]  n=79 cases, dropped 1`. The interval includes 0, so the verdict is "not proven".
