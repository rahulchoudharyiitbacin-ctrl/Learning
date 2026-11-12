# Chapter 10 sources (fetched 2026-11-13)

Each entry: URL, what the page said (paraphrased; short quotes only), what the chapter uses it for. Vendor pages are vendor claims.

## promptfoo

- https://github.com/promptfoo/promptfoo (README). "Promptfoo remains open source and MIT licensed"; "LLM evals run 100% locally - your prompts never leave your machine"; "Promptfoo is now part of OpenAI". Used: licence, local, ownership note. npm latest on the day: 0.125.1 (`npm view promptfoo version`), which is the version tested.
- https://www.promptfoo.dev/docs/configuration/guide/ . `prompts` (incl. `file://`), `providers`, `tests` (inline, file, CSV, Google Sheets), `defaultTest` (shared asserts/vars/options), `assert` list of `type`/`value`; vars may load from files. Used: config structure.
- https://www.promptfoo.dev/docs/configuration/reference/ . `evaluateOptions.repeat` (default 1), `maxConcurrency` (default 4), `cache` (default true), `delay`, `timeoutMs`; `defaultTest.options.provider` for the grading provider. Used: repeat/concurrency mapping.
- https://www.promptfoo.dev/docs/configuration/prompts/ . Chat prompts as a JSON list of `{role, content}` with Nunjucks vars; `id` + `label` on file prompts. Used: prompts/triage-v*.json.
- https://www.promptfoo.dev/docs/configuration/test-cases/ . CSV headers become vars; special columns `__expected`, `__description`, `__metric`, `__threshold`, `__metadata:<key>`; JSONL needs `vars`/`assert` objects; in `defaultTest` use normal column names, not `__expected`. Used: tests.csv design (`expected` as a normal column).
- https://www.promptfoo.dev/docs/configuration/expected-outputs/ . Deterministic types incl. `equals`, `icontains`, `regex`, `is-json`, `javascript`, `python`; model-graded incl. `llm-rubric`; `not-` prefix; `weight`, `metric`, `threshold`; without a test threshold every non-zero-weight assertion must pass; inline JS single expression returns its value. Used: assertions page.
- https://www.promptfoo.dev/docs/configuration/expected-outputs/model-graded/llm-rubric/ . `value` is the rubric; default grader depends on available credentials (Anthropic key -> claude-sonnet-5); override via `--grader`, `defaultTest.options.provider`, test options or per-assertion `provider`; grader returns `{reason, pass, score}`; optional `threshold`. Used: judge page and judge-example.yaml.
- https://www.promptfoo.dev/docs/providers/anthropic/ . `anthropic:messages:<model>`; `ANTHROPIC_API_KEY`; options incl. `max_tokens`, `effort` (low/medium/high/xhigh/max, per model), `thinking`, `output_format`, `apiBaseUrl`, `extra_body`; lists `anthropic:messages:claude-haiku-5-5` (adaptive thinking by default); temperature/top_p/top_k omitted for several Claude 5-era models. Used: provider config. NOTE: tested 0.125.1 calls the model "unknown" and adds `temperature: 0` when the base URL is not api.anthropic.com (see work/promptfoo/README.md).
- https://www.promptfoo.dev/docs/usage/command-line/ . `eval` flags (`-c`, `-o` with csv/txt/json/jsonl/yaml/yml/html/xml/junit.xml, `--no-cache`, `--repeat`, `-j`, `--no-table`, `--no-write`, `--share`, `--filter-*`); exit code 100 on test failure or below threshold, 1 otherwise; `PROMPTFOO_PASS_RATE_THRESHOLD` (percent, default 100); `PROMPTFOO_FAILED_TEST_EXIT_CODE`; `promptfoo view`, `promptfoo cache clear`. Used: run page, exit codes. Cross-checked with `promptfoo eval --help` (0.125.1).
- https://www.promptfoo.dev/docs/configuration/caching/ . Successful responses cached on disk at `~/.promptfoo/cache`; errors and empty responses not cached; TTL 14 days; `PROMPTFOO_CACHE_ENABLED/PATH/TTL`; `--no-cache` or `evaluateOptions.cache: false`; each repeat index has its own cache namespace. Used: cache paragraph (also tested).
- https://www.promptfoo.dev/docs/providers/echo/ . `echo` returns the rendered prompt, no API calls, cost 0. Used: considered for offline tests; a custom provider was used instead.
- https://www.promptfoo.dev/docs/providers/custom-api/ . Custom provider = class with `id()` and `callApi(prompt, context, options)` returning `{output, ...}`; `file://` reference; ESM `.mjs` supported. Used: offline/fake_*.mjs.
- https://www.promptfoo.dev/docs/usage/web-ui/ . Viewer opened with `promptfoo view`; display modes All/Failures/Passes/Errors/Different/Highlights; ratings and comments; exports. Used: results page.
- https://www.promptfoo.dev/docs/integrations/ci-cd/ . GitHub Actions example with `npx promptfoo@latest eval -c ... -o results.json`, `actions/cache` on `~/.cache/promptfoo` with `PROMPTFOO_CACHE_PATH`, jq gate on `.results.stats.failures`, pass rate from `.results.stats.successes`/`failures`, `upload-artifact` with `if: always()`. Used: workflow design. Deviation: the example sets `PROMPTFOO_CACHE_PATH: ~/.cache/promptfoo`; 0.125.1 does not expand `~` (source), so our workflow uses an absolute path.
- https://www.promptfoo.dev/docs/integrations/github-action/ . Official `promptfoo/promptfoo-action@v1` (inputs `github-token`, `prompts`, `config`, `openai-api-key`, `cache-path`; posts PR comments; needs Node >=22.22.0 on the runner). No pass-rate-threshold input on the page. Used: one sentence ("also has an official GitHub Action").
- https://www.promptfoo.dev/docs/configuration/telemetry/ . Basic usage telemetry on by default; `PROMPTFOO_DISABLE_TELEMETRY=1`; telemetry excludes prompts, outputs, test cases, keys; `PROMPTFOO_DISABLE_UPDATE=1` stops the npm update check. Used: workflow env.

## Hosted platforms

- https://docs.langchain.com/langsmith/evaluation-concepts (redirect from docs.smith.langchain.com/evaluation). Datasets of examples (inputs, optional reference outputs); experiments; evaluators: code, LLM-as-judge, human (annotation queues incl. pairwise), pairwise; offline vs online evals; traces/threads. Used: LangSmith bullet.
- https://docs.langchain.com/langsmith/evaluate-llm-application . `Client().evaluate(target, data=, evaluators=, experiment_prefix=, max_concurrency=)`; target is a plain function. Used: "LangChain isn't required".
- https://docs.langchain.com/langsmith/compare-experiment-results . Select experiments -> Compare; source (baseline) experiment; regressions red, improvements green; Full and Diff views (diff for two experiments). Used: compare view.
- https://docs.langchain.com/langsmith/prompt-engineering-concepts . Prompt templates stored and versioned; each save is a commit; tags point to commits; Playground. Used: prompt versioning.
- https://docs.langchain.com/langsmith/self-hosted . Self-hosted LangSmith is "an add-on to the Enterprise plan", runs on Kubernetes (Helm), Terraform option. Used: hosting.
- https://langfuse.com/docs/evaluation/overview . Datasets, experiments (UI, SDK, OpenTelemetry), scores, LLM-as-judge, code evaluators, annotation queues, user feedback, online evaluation of production traces, a GitHub Action that can fail a PR on a score threshold; works with Cloud and self-hosted. Used: Langfuse bullet.
- https://github.com/langfuse/langfuse . "MIT licensed, except for the `ee` folders"; tracing on OpenTelemetry, prompt management, evaluations, datasets/experiments. Used: licence.
- https://langfuse.com/self-hosting . Open source, self-host with Docker Compose (testing, single VM) or Kubernetes/Helm (production); some features need a licence key. Used: hosting.
- https://langfuse.com/docs/prompt-management/overview . Versioned prompts, labels, link prompts to traces, client-side caching. Used: prompt management.
- https://langfuse.com/docs/evaluation/experiments/experiments-via-sdk . `langfuse.run_experiment(name, data, task, evaluators)`; runs comparable in the UI. Used: background only.
- https://docs.braintrust.dev/ (redirect from braintrust.dev/docs). "active observability platform"; stages Instrument, Observe, Annotate, Evaluate, Deploy. Used: background.
- https://docs.braintrust.dev/evaluate . Eval = data + task + scorers; experiments are an "immutable, comparable record"; playground; online scoring of production traces with LLM-as-judge scorers; CI/CD. Used: Braintrust bullet.
- https://docs.braintrust.dev/evaluate/compare-experiments . Baseline selection; green/red improvements and regressions; Diff toggle; trials grouped by input. Used: compare view.
- https://docs.braintrust.dev/evaluate/run-in-ci . `braintrustdata/eval-action@v2` posts a PR comment with scores. Used: CI mention.
- https://docs.braintrust.dev/admin/deployment . SaaS on Starter/Pro/Enterprise; "BYOC requires an Enterprise plan". Used: hosting.
- https://docs.braintrust.dev/admin/self-hosting . Control plane (UI, auth, metadata) hosted by Braintrust; data plane (experiments, logs, traces, datasets) run by the customer. Used: background (chapter mentions BYOC only).

## Anthropic Console Evaluate

- https://platform.claude.com/docs/en/test-and-evaluate/eval-tool (and the old docs.anthropic.com URL) now returns HTTP 307 to https://platform.claude.com/docs/en/test-and-evaluate/develop-tests , which is the general "define success criteria and build evals" guide and does not describe the Console tool (checked with curl and WebFetch).
- https://claude.com/resources/articles/evaluate-prompts (published 9 July 2024). Console Evaluate: add test cases manually, import CSV, or generate; run all; compare two or more prompts side by side; experts grade on a 5-point scale. Used: Console paragraph, dated as a 2024 announcement. UNVERIFIED: whether the tool exists unchanged today (chapter tells readers to check).

## OpenAI Evals

- https://developers.openai.com/api/docs/deprecations . 3 June 2026 deprecation announced for the Evals platform; 31 Oct 2026 existing evals become read-only; 30 Nov 2026 Evals dashboard and API scheduled to shut down; links a guide "Moving from OpenAI Evals to Promptfoo". Used: "don't start here" paragraph. Matches the earlier notes.

## GitHub

- https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets . "secrets are not passed to the runner when a workflow is triggered from a forked repository" (except GITHUB_TOKEN); reference as `${{ secrets.NAME }}`. Used: CI traps page.
- GitHub API releases (2026-11-13): actions/checkout v7.0.1, actions/setup-node v7.1.0, actions/cache v6.1.0, actions/upload-artifact v7.0.2. Used: action versions in eval.yml (promptfoo's own example still shows cache@v4 / upload-artifact@v4).
- https://json.schemastore.org/github-workflow.json (via schemastore.org). eval.yml validated against it with python jsonschema.

## Not used / UNVERIFIED (left out of the chapter)

- Pricing and free tiers of LangSmith, Langfuse Cloud, Braintrust: not checked.
- Whether LangSmith itself is open source: no page checked says so; chapter only says hosted + Enterprise self-host add-on.
- Braintrust `Eval()` code shape and autoevals licence: pages fetched did not show them.
- LangSmith CI integration (GitHub Action): not checked, so not listed in the "gate every PR" row.
- promptfoo web viewer layout beyond the documented display modes; promptfoo's monitoring/production features: not checked.
- promptfoo job ordering (does it interleave A and B like the harness's shuffle?): not checked.
