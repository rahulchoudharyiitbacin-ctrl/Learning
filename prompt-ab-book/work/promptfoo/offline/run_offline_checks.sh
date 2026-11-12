#!/usr/bin/env bash
# Offline checks for the Chapter 10 promptfoo config. No API key,
# no real model calls. Run:  bash offline/run_offline_checks.sh SCRATCH
# Needs a local promptfoo:  (cd SCRATCH && npm i promptfoo@0.125.1)
set -u
SCRATCH=${1:?usage: run_offline_checks.sh SCRATCH_DIR}
HERE=$(cd "$(dirname "$0")/.." && pwd)
PF="$SCRATCH/node_modules/.bin/promptfoo"
export PROMPTFOO_DISABLE_TELEMETRY=1 PROMPTFOO_DISABLE_UPDATE=1
export PROMPTFOO_CONFIG_DIR="$SCRATCH/pfhome" PROMPTFOO_CACHE_PATH="$SCRATCH/pfcache-chk"
unset ANTHROPIC_API_KEY ANTHROPIC_BASE_URL OPENAI_API_KEY
W="$SCRATCH/chk"; rm -rf "$W" "$PROMPTFOO_CACHE_PATH"; cp -R "$HERE" "$W"; cd "$W"

echo "== A. config + assertions with the offline stand-in model"
$PF eval -r file://offline/fake_triage.mjs --no-progress-bar --no-table -o results.json >a.log 2>&1
echo "exit=$? (100 = some test failed)"; grep -E "passed \(|failed \(" a.log
python3 export_pairs.py results.json --a A-v1 --b B-v2 --out pairs.csv

echo "== B. real Anthropic provider code against a fake LOCAL server: caching"
PORT=$(python3 -c "import socket;s=socket.socket();s.bind(('127.0.0.1',0));print(s.getsockname()[1])")
python3 - "$PORT" <<'PY'
import sys, yaml
c = yaml.safe_load(open("promptfooconfig.yaml"))
c["providers"][0]["config"]["apiBaseUrl"] = f"http://127.0.0.1:{sys.argv[1]}"
yaml.safe_dump(c, open("local.yaml", "w"), sort_keys=False)
PY
python3 offline/fake_anthropic_server.py "$PORT" "$W/req.jsonl" & SP=$!; sleep 1
export ANTHROPIC_BASE_URL="http://127.0.0.1:$PORT" ANTHROPIC_API_KEY=fake-local-test-key
$PF eval -c local.yaml --no-progress-bar --no-table -o r1.json >/dev/null 2>&1
echo "run 1: requests so far $(wc -l <req.jsonl)"
$PF eval -c local.yaml --no-progress-bar --no-table -o r2.json >/dev/null 2>&1
echo "run 2 (cache): requests so far $(wc -l <req.jsonl)"
$PF eval -c local.yaml --no-cache --no-progress-bar --no-table -o r3.json >/dev/null 2>&1
echo "run 3 (--no-cache): requests so far $(wc -l <req.jsonl)"
kill $SP; unset ANTHROPIC_BASE_URL
head -1 req.jsonl | python3 -c "import json,sys;b=json.load(sys.stdin)['body'];print('sent keys:',sorted(b))"

echo "== C. request the real endpoint WOULD get (network disabled, call stubbed)"
NODE_PATH="$SCRATCH/node_modules" node offline/request_check.cjs 2>&1 | grep -E "baseURL|sent"
