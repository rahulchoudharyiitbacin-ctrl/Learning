# Minimal A/B harness (Chapter 4)

```
cd work/harness
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY="..."        # never put the key in a file

python run_experiment.py experiments/ticket-triage-v1-vs-v2.yaml --mock   # free dry run
python run_experiment.py experiments/ticket-triage-v1-vs-v2.yaml          # real calls (120)
```

- Config paths are relative to the project folder (the parent of `experiments/`).
- Records go to `runs/<name>/records.jsonl` (mock runs: `records-mock.jsonl`). Finished calls are skipped on rerun; use a new `name` or delete the file for a fresh run.
- Start with ~5 cases for a smoke test before the full set.
- No `temperature`: current Claude models don't accept it. Lock `model`, `effort` and `max_tokens` instead.

## How it was tested

- `--mock`: runs end to end, saves records, resumes (second run makes 0 calls).
- Real SDK (`anthropic` 2.8.0, isolated virtualenv) against a fake local server: sent `model`, `max_tokens`, `system`, `messages`, `output_config.effort` and nothing else, parsed the replies, wrote 120 records.
- **Not tested:** a live call to the real API (no key was used). The first real run is the learner's lab.

## Error analysis helper (Chapter 5)

```
python error_analysis.py show experiments/ticket-triage-v1-vs-v2.yaml [--mock] [--disagree] [--sample-pass 5]
python error_analysis.py template experiments/ticket-triage-v1-vs-v2.yaml [--mock]   # writes runs/<name>/notes.csv
python error_analysis.py tally experiments/ticket-triage-v1-vs-v2.yaml               # counts the categories you filled in
```

Tested on mock records (show, show --disagree, show --sample-pass, template with overwrite protection, tally with blank rows).

## Dataset helper (Chapter 6)

```
python dataset_tools.py check data/cases-v1.jsonl --labels refund,delivery,account,other
python dataset_tools.py summary data/cases-v1.jsonl
python dataset_tools.py split data/cases-v1.jsonl --dev 0.5 --seed 1      # writes .dev.jsonl and .test.jsonl
python dataset_tools.py leak experiments/ticket-triage-v1-vs-v2.yaml      # case text found inside a prompt?
```

Tested on the sample set and on deliberately bad data (duplicate id, duplicate input, bad label, empty input, a prompt containing a test case). Two bugs found and fixed by those tests: empty inputs falsely reported as leaks; split rounded half down.

## More graders and a classification report (Chapter 7)

```
python test_graders.py                                   # plain asserts for every grader in graders.py
python classification_report.py experiments/ticket-triage-v1-vs-v2.yaml [--mock]   # precision/recall/F1 + confusion matrix
```

`graders.py` is picked up automatically by `run_experiment.py` (set `grader: normalized_match`, `json_all_fields`, etc.). Tested: grader asserts (incl. traps like prose around JSON), harness wiring with a different grader, and the report's math against hand-computed examples (a 95/5 imbalance and an 8/10 recall, 8/12 precision case).

## LLM judge (Chapter 8)

```
python judge.py grade experiments/EXP.yaml --rubric RUBRIC [--mock]     # judge saved records
python judge.py labelled labels.csv --out judged.csv [--mock]           # judge human-labelled examples
python judge_validation.py report judged.csv                            # confusion matrix, TPR/TNR + Wilson CIs, kappa
python judge_validation.py split labels.csv                             # stratified train/dev/test
python test_judge.py                                                    # hand-computed checks
```

Never sends temperature/top_p/top_k. Real-SDK request path tested against a fake local server only (no live call).

## Statistics (Chapter 9)

```
python compare_runs.py experiments/EXP.yaml [--mock]    # per-case means, paired CI (t and case bootstrap), McNemar, verdict
python sample_size.py --help                            # paired sample size, with the single-accuracy formula for contrast
python test_stats.py                                    # hand-computed checks + coverage/power/peeking simulations (~13 s)
```

Coverage simulation (1,000 repeats, 100 cases x 3 runs, B fixes some cases and breaks others): t-interval 94.3%, case bootstrap 93.7%, naive all-rows 80.2%.

## Frameworks (Chapter 10)

The same experiment as a promptfoo config lives in `work/promptfoo/` (README there), with a CI workflow and a local replay of its gate logic in `work/ci-example/`. Tested offline only (promptfoo 0.125.1 with fake providers). Findings from testing: a pass-rate threshold does not catch API errors (check `stats.errors` separately); `~` does not work in `PROMPTFOO_CACHE_PATH`; promptfoo caches grades too, so a rerun is not a new sample unless you use `--no-cache`; behind a custom base URL, promptfoo 0.125.1 sent `temperature: 0` to a Claude 5 model.

## Online A/B tools (Chapter 11)

```
python online_tools.py assign  --experiment NAME [--rollout 0.05] USER_ID...   # stable, stateless user bucketing
python online_tools.py srm     --counts A=5000,B=5200                            # sample ratio mismatch (chi-square)
python online_tools.py plan    --baseline 0.10 --mde 0.01 --daily-users 4000     # users per arm and weeks
python online_tools.py compare --a 100/1000 --b 130/1000                         # two-proportion z-test and CI
python test_online.py                                                            # checks incl. 100k-user balance, power ~0.80, false positives ~5%
```

Standard library only. Tested values: planner 14,751 users per arm for 10% baseline and +1 point; SRM 5,000 vs 5,200 gives p = 0.0477; chi-square tails match table values; simulated power 0.801; false-positive rate 0.046.

## RAG and trial metrics (Chapter 12)

```
python test_rag_metrics.py     # recall@k, precision@k, MRR, pass@k, pass^k: hand-computed examples + a simulation
```

`rag_metrics.py` is a library (import `recall_at_k`, `precision_at_k`, `mrr`, `pass_at_k`, `pass_pow_k`).

## Mock interviewer (Chapter 13)

```
python mock_interview.py --question "..." --rubric "Weak: ... OK: ... Strong: ..." [--mock] [--answers FILE]
```

An LLM plays the interviewer: asks the question, up to 3 probes, then scores you against the rubric. `--mock` = fake interviewer, no API. Tested in mock mode and through the real SDK against a fake local server (request fields: model, max_tokens, system, messages, output_config.effort; rubric kept in the private system prompt). A bug found by testing (the 3rd probe was never answered) is fixed. No live API call made.

## Interview practice material (Chapters 14-16)

Question bank and system-design prompts are chapters only. The coding drills live in `../drills/` (README there): `python test_drillN.py my_solution.py` tests your own file; with no argument it tests the reference solution. `python check_mutants.py` runs 26 deliberately careless solution variants through the tests.

Also fixed (found via a drill's trap list): `graders.py` JSON graders treated `True` as equal to `1` and `False` as `0`; they now compare types (tests added to `test_graders.py`).
