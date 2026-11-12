#!/usr/bin/env bash
# Replays the steps of eval.yml on your machine, OFFLINE:
# the model is replaced by work/promptfoo/offline/*.mjs,
# so no API key and no API calls. Tests the gate logic only.
#
#   bash simulate_ci_locally.sh SCRATCH_DIR
#
# Needs: node/npx, python3, jq, git. Uses a copy of the
# project in SCRATCH_DIR; your files are not touched.
set -u
SCRATCH=${1:?usage: simulate_ci_locally.sh SCRATCH_DIR}
BOOK=$(cd "$(dirname "$0")/../.." && pwd)
PF="${PF:-npx --yes promptfoo@0.125.1}"
export PROMPTFOO_DISABLE_TELEMETRY=1 PROMPTFOO_DISABLE_UPDATE=1
export PROMPTFOO_CONFIG_DIR="$SCRATCH/pfhome"
export PROMPTFOO_CACHE_PATH="$SCRATCH/pfcache-ci"
unset ANTHROPIC_API_KEY ANTHROPIC_BASE_URL

fresh_repo() {
  rm -rf "$SCRATCH/repo" && mkdir -p "$SCRATCH/repo/work"
  cp -R "$BOOK/work/harness" "$BOOK/work/promptfoo" "$SCRATCH/repo/work/"
  (cd "$SCRATCH/repo" && git init -q && git add -A &&
   git -c user.email=ci@example.invalid -c user.name=ci commit -qm base)
}

# One CI job. $1 = provider file, $2 = threshold. Prints step results.
job() {
  cd "$SCRATCH/repo/work/promptfoo" || return 9
  python3 build_from_harness.py >/dev/null
  git diff --quiet -- . ; s1=$?
  PROMPTFOO_PASS_RATE_THRESHOLD=$2 $PF eval -c promptfooconfig.yaml \
    -r "file://offline/$1" --no-progress-bar --no-table \
    -o results.json -o report.html >eval.log 2>&1; s2=$?
  if [ -f results.json ]; then
    e=$(jq '.results.stats.errors' results.json); [ "$e" -eq 0 ]; s3=$?
  else s3=1; fi
  echo "  sync-check=$s1  eval-exit=$s2  errors-check=$s3  ($(grep -E 'passed \(' eval.log | tr -s ' '))"
}

echo "1) good change, threshold 90 (expect all 0):"
fresh_repo; job fake_triage.mjs 90
echo "2) same, threshold 95 (expect eval-exit 100):"
job fake_triage.mjs 95
echo "3) broken prompt output (expect eval-exit 100):"
sed 's#return { output: label };#return { output: "Label: " + label };#' \
  offline/fake_triage.mjs > offline/fake_bad.mjs
job fake_bad.mjs 90
echo "4) one case errors, threshold 80 (expect eval 0, errors-check 1):"
sed 's#async callApi(prompt) {#async callApi(prompt) { if (prompt.includes("vegan")) return { error: "simulated overload" };#' \
  offline/fake_triage.mjs > offline/fake_err.mjs
job fake_err.mjs 80
echo "5) harness prompt edited, promptfoo files not rebuilt (expect sync-check 1):"
fresh_repo
(cd "$SCRATCH/repo" && echo "Be brief." >> work/harness/prompts/triage/v2.txt &&
 git -c user.email=ci@example.invalid -c user.name=ci commit -qam edit)
job fake_triage.mjs 90
