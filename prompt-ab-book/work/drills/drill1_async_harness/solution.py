"""Drill 1 reference solution: async eval harness with caching."""
import asyncio
import hashlib
import json
import random
from pathlib import Path

from fake_llm import RateLimitError


def render(template, case):
    """Fill the prompt template. Plain replace, so braces in the
    customer text cannot break str.format."""
    return template.replace("{input}", case["input"])


def grade(output, expected):
    """Exact match after trimming spaces and ignoring case."""
    return int(output.strip().lower() == expected.strip().lower())


def cache_key(model, prompt, run):
    """Run index is in the key: three runs stay three samples."""
    raw = json.dumps([model, prompt, run]).encode()
    return hashlib.sha256(raw).hexdigest()


class DiskCache:
    """One small JSON file per key. Only successes are stored."""

    def __init__(self, folder):
        self.folder = Path(folder)
        self.folder.mkdir(parents=True, exist_ok=True)

    def get(self, key):
        path = self.folder / f"{key}.json"
        if not path.exists():
            return None
        return json.loads(path.read_text())["output"]

    def put(self, key, output):
        path = self.folder / f"{key}.json"
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps({"output": output}))
        tmp.replace(path)          # atomic: no half-written files


async def call_with_retry(call_model, model, prompt, max_retries,
                          base_delay):
    """Return (output, error, attempts). Retries 429 only."""
    attempts = 0
    while True:
        attempts += 1
        try:
            return await call_model(model, prompt), None, attempts
        except RateLimitError as e:
            if attempts > max_retries:
                return None, f"RateLimitError: {e}", attempts
            delay = base_delay * 2 ** (attempts - 1)
            await asyncio.sleep(delay + random.uniform(0, base_delay / 4))
        except Exception as e:     # not retryable: record it
            return None, f"{type(e).__name__}: {e}", attempts


async def run_eval(cases, variants, call_model, *, model, runs,
                   out_path, cache_dir, concurrency=4, max_retries=3,
                   base_delay=0.01):
    cache = DiskCache(cache_dir)
    sem = asyncio.Semaphore(concurrency)
    inflight = {}                  # key -> Task, shared by duplicates

    async def fetch(key, prompt):
        cached = cache.get(key)
        if cached is not None:
            return cached, None, 0, True
        async with sem:
            out, err, n = await call_with_retry(
                call_model, model, prompt, max_retries, base_delay)
        if err is None:
            cache.put(key, out)
        return out, err, n, False

    async def job(case, variant, run):
        prompt = render(variants[variant], case)
        key = cache_key(model, prompt, run)
        owner = key not in inflight
        if owner:                  # no await between check and set
            inflight[key] = asyncio.ensure_future(fetch(key, prompt))
        out, err, n, hit = await inflight[key]
        # A duplicate shares the owner's call: it cost nothing.
        return {"case_id": str(case["id"]), "variant": variant,
                "run": run, "model": model, "output": out,
                "grade": None if err else grade(out, case["expected"]),
                "error": err, "attempts": n if owner else 0,
                "cached": hit if owner else True}

    jobs = [job(c, v, r) for c in cases for v in variants
            for r in range(runs)]
    records = list(await asyncio.gather(*jobs))

    records.sort(key=lambda d: (d["case_id"], d["variant"], d["run"]))
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w") as f:  # overwrite, never append
        for rec in records:
            f.write(json.dumps(rec) + "\n")
    return records


if __name__ == "__main__":
    import sys
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
    errors = sum(r["error"] is not None for r in recs)
    print(f"{len(recs)} records, {llm.calls} API calls, "
          f"{errors} errors", file=sys.stderr)
