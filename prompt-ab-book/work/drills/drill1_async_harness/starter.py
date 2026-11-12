"""Drill 1 starter: async eval harness with caching.

Copy this file to my_drill1.py, fill in the TODOs, then run
    python test_drill1.py my_drill1.py

Read README.md for the full task. Standard library only.
"""
import asyncio
import hashlib
import json
import random
from pathlib import Path

from fake_llm import RateLimitError, BadRequestError  # noqa: F401


def render(template, case):
    """Return the prompt: template with "{input}" replaced by
    case["input"]."""
    # TODO
    raise NotImplementedError


def grade(output, expected):
    """1 if output matches expected after strip() and lower(), else 0."""
    # TODO
    raise NotImplementedError


async def run_eval(cases, variants, call_model, *, model, runs,
                   out_path, cache_dir, concurrency=4, max_retries=3,
                   base_delay=0.01):
    """Run every case x variant x run and return the records.

    cases:     list of {"id", "input", "expected"}
    variants:  dict variant name -> template containing "{input}"
    call_model: async function (model, prompt) -> str. It may raise
               RateLimitError (retry) or other errors (don't retry).
    runs:      repeated runs per case and variant (run = 0..runs-1)
    out_path:  JSONL file to write (overwrite), one record per line
    cache_dir: folder for the on-disk cache (create it if missing)

    Each record: case_id, variant, run, model, output, grade, error,
    attempts, cached. Sorted by (case_id, variant, run).
    """
    # TODO 1: build the job list (case, variant, run)
    # TODO 2: cache lookup keyed by (model, prompt, run)
    # TODO 3: no two calls for the same key, even at the same time
    # TODO 4: at most `concurrency` calls in flight
    # TODO 5: retry RateLimitError with exponential backoff
    # TODO 6: record errors (output None, grade None); don't cache them
    # TODO 7: sort, write JSONL, return the records
    raise NotImplementedError


if __name__ == "__main__":
    from fake_llm import FakeLLM
    here = Path(__file__).parent
    cases = [json.loads(x) for x in
             (here / "cases.jsonl").read_text().splitlines() if x]
    variants = json.loads((here / "variants.json").read_text())
    llm = FakeLLM()
    recs = asyncio.run(run_eval(
        cases, variants, llm.call_model, model="fake-model-1", runs=3,
        out_path=here / "runs" / "results.jsonl",
        cache_dir=here / "runs" / "cache"))
    print(f"{len(recs)} records, {llm.calls} API calls")
