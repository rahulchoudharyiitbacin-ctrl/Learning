# The Chapter 4 experiment in promptfoo (Chapter 10)

Same prompts (`../harness/prompts/triage/v1.txt`, `v2.txt`), same 20 cases (`../harness/data/cases-v1.jsonl`), same grader idea (exact match after trim + lowercase), 3 repeats, model `claude-haiku-5-5`, `effort: low`, `max_tokens: 1024`, no temperature.

```
cd work/promptfoo
python3 build_from_harness.py                 # writes prompts/*.json and tests.csv from the harness files
export ANTHROPIC_API_KEY="..."                # never in a file
npx promptfoo@0.125.1 eval -n 5 --repeat 1    # smoke test: 5 cases x 2 prompts
npx promptfoo@0.125.1 eval -o results.json    # full run: 120 calls
npx promptfoo@0.125.1 view                    # local web viewer
python3 export_pairs.py results.json --a A-v1 --b B-v2 --out pairs.csv   # per-case pairs for Chapter 9
```

Files:
- `promptfooconfig.yaml`: the experiment. `judge-example.yaml`: the same plus an `llm-rubric` check (syntax demo; validate a judge before trusting it, Chapter 8).
- `build_from_harness.py`: builds `prompts/triage-v1.json`, `prompts/triage-v2.json` (system = the harness prompt, user = `{{message}}`) and `tests.csv` (`__description` = case id, `message`, `expected`).
- `export_pairs.py`: per-case means of A and B, paired differences, wins/losses/ties, error count; `--gate LABEL --min X` exits 1 below X.
- `offline/`: stand-ins for testing without a key: `fake_triage.mjs` (keyword-rule "model", scores meaningless), `fake_grader.mjs` (grader stand-in), `fake_anthropic_server.py` (fake Messages endpoint on 127.0.0.1 that logs requests), `request_check.cjs` (shows the request promptfoo would send to the real endpoint, with network disabled and the SDK call stubbed), `run_offline_checks.sh` (runs all of it).
- CI: `../ci-example/eval.yml` (GitHub Actions) and `../ci-example/simulate_ci_locally.sh` (replays its steps offline).

## How it was tested (2026-11-13, promptfoo 0.125.1, Node 26.3, macOS; no API key, no real model calls)

- Offline stand-in model: config parses, 120 results (20 x 2 x 3), assertions run, exit code 100 when any test fails. `PROMPTFOO_PASS_RATE_THRESHOLD`: 90 -> exit 0 at 92.5%; 95 and 99 -> exit 100 with "Pass rate 92.50% is below the threshold". `--filter-prompts B-v2` -> 60 results; `--repeat 1` overrides the config's 3; `-n 5` -> 10 results. Output files csv/json/jsonl/html/xml/junit.xml all written.
- `export_pairs.py` matched an independent hand computation of the keyword rule (A 0.90, B 0.95, one case differs) and its gate exits 1/0 as expected; errored calls are skipped and counted.
- Errors: a stand-in that errors on one case gave 6 errors of 120; with threshold 80 the eval still **exited 0**. Hence the separate errors check in CI.
- Real promptfoo Anthropic provider against a fake local server: run 1 = 120 requests, rerun = 0 new requests (cache hits 60 + 60), `--no-cache` = 120 new requests. Request body: `model`, `system`, `messages`, `max_tokens: 1024`, `output_config.effort: low`, `stream: false`, **plus `temperature: 0`**.
- Same provider with the default endpoint (`https://api.anthropic.com`), fetch disabled and `messages.create` stubbed: **no temperature** sent. promptfoo 0.125.1 only applies its "Claude 5+ rejects sampling params" rule by model-name pattern when the base URL is api.anthropic.com (read in its source). With a proxy or `ANTHROPIC_BASE_URL`, check your requests. It also logs "Using unknown Anthropic model: claude-haiku-5-5" (its catalog lacks that ID).
- `llm-rubric` with the stand-in grader: passes/fails as expected. Grades are cached: after fixing the grader, a rerun without `--no-cache` returned the old grades.
- `PROMPTFOO_CACHE_PATH` is used as written (no `~` expansion; read in source).
- `promptfoo view` served on localhost (HTTP 200).
- **Not tested:** a real API call; the GitHub workflow on GitHub itself (it was validated against the schemastore GitHub-workflow JSON schema and its steps were replayed locally by `simulate_ci_locally.sh`); `actions/cache` restore behaviour; the official promptfoo GitHub Action.
