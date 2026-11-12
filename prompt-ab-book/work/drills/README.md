# Coding drills (Chapter 16)

Four timed drills. Standard library only, Python 3.9+, offline, no API key.

| Folder | Drill | Budget | Tests |
|---|---|---|---|
| `drill1_async_harness/` | async eval harness: concurrency, retries, disk cache, JSONL | 45 min | 12 |
| `drill2_paired_bootstrap/` | paired bootstrap clustered by case | 30 min | 11 |
| `drill3_judge_agreement/` | confusion matrix, TPR/TNR, kappa, Wilson | 30 min | 12 |
| `drill4_structured_output/` | JSON parsing, schema validation, field accuracy | 35 min | 14 |

Each folder: `README.md` (the task), `starter.py`, `solution.py`, `test_drillN.py`, sample data.

```
cd drill2_paired_bootstrap
cp starter.py my_drill2.py
python test_drill2.py my_drill2.py      # or DRILL_FILE=my_drill2.py python test_drill2.py
python test_drill2.py                   # default: tests solution.py (all pass)
```

`python check_mutants.py` (about 30 s) proves the tests are meaningful: every solution passes, every starter fails, and 26 careless variants of the solutions (one typical mistake each) are all caught.

Tested on Python 3.9.6, 3.11.9 and 3.14 (macOS). Test runtimes: drill 1 about 1.3 s, drill 2 about 2 s (includes a 1,000-experiment coverage simulation), drills 3 and 4 under 0.1 s.

Note on drill 1: the cache key includes the run index. Keying on (model, prompt) only would turn repeated runs into copies of one cached answer.
