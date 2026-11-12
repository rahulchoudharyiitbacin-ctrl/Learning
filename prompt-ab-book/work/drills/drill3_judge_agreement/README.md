# Drill 3: judge-agreement metrics from a labels CSV

**Time budget:** 30 minutes. Start a timer before you read past this line.

## The task

A domain expert labelled 103 outputs PASS or FAIL. Your LLM judge labelled the same outputs. The file `labels.csv` has columns `id,human_label,judge_label`.

Write, in your own copy of `starter.py`:

1. `load_labels(path)`: read the CSV into a list of `{"id", "human", "judge"}`.
2. `wilson(k, n, z=1.96)`: the Wilson score interval for k successes out of n, as `(lo, hi)` clipped to [0, 1]; `None` if n is 0.
3. `agreement_report(rows, positive="FAIL")`: a dict with
   - the confusion counts `tp`, `fn`, `fp`, `tn` (rows = human, columns = judge, **FAIL is the positive class**), plus `n`, `n_pos`, `n_neg`, `skipped`;
   - `tpr` = TP / (TP + FN), `tnr` = TN / (TN + FP), raw `agreement`;
   - Cohen's `kappa` = (po - pe) / (1 - pe);
   - `tpr_ci` and `tnr_ci`: Wilson intervals.

Wilson interval, with p = k/n:

```
centre = (p + z^2/(2n)) / (1 + z^2/n)
half   = z * sqrt(p(1-p)/n + z^2/(4n^2)) / (1 + z^2/n)
```

## Things a careful solution handles

- Labels arrive as ` fail`, `Pass`, `FAIL `. Normalise them.
- The judge sometimes gave no verdict (blank, `ERROR`, `N/A`). Skip those rows and **count** them.
- A human label that is not PASS or FAIL is a data error: raise `ValueError`.
- **No positives** (no human FAILs): TPR is undefined. Return `None`, not 0, and don't crash.
- Kappa when both raters used one label only: chance agreement is 1, so kappa is 0/0. Return `None`.
- The CSV may start with a byte-order mark (Excel does this).

## Done means

```
python test_drill3.py my_drill3.py
```

prints `12/12 passed`, and on the sample file you get TP 12, FN 8, FP 6, TN 74, 3 skipped, TPR 0.600 (95% CI 0.387-0.781), TNR 0.925 (0.846-0.965), kappa 0.545. These are the Chapter 8 numbers. `make_labels.py` wrote the file.
