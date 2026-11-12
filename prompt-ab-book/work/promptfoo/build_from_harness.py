"""Build promptfoo inputs from the Chapter 4 harness files.

Same prompts, same 20 cases, no copy-paste:
  prompts/triage-v1.json, prompts/triage-v2.json  (system = harness v1/v2.txt,
                                                  user = the ticket text)
  tests.csv                                      (one row per case)

Run from anywhere:  python build_from_harness.py
"""
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
HARNESS = HERE.parent / "harness"

for v in ("v1", "v2"):
    system = (HARNESS / "prompts" / "triage" / f"{v}.txt").read_text()
    chat = [
        {"role": "system", "content": system},
        {"role": "user", "content": "{{message}}"},
    ]
    out = HERE / "prompts" / f"triage-{v}.json"
    out.write_text(json.dumps(chat, indent=2) + "\n")
    print("wrote", out.relative_to(HERE))

lines = (HARNESS / "data" / "cases-v1.jsonl").read_text().splitlines()
cases = [json.loads(x) for x in lines if x.strip()]
with open(HERE / "tests.csv", "w", newline="") as f:
    w = csv.writer(f, lineterminator="\n")
    w.writerow(["__description", "message", "expected"])
    for c in cases:
        w.writerow([c["id"], c["input"], c["expected"]])
print(f"wrote tests.csv ({len(cases)} cases)")
