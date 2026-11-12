"""Prove the drill tests are meaningful.

For each drill: the reference solution must pass, the starter must
fail, and each "careless" variant of the solution (one typical
mistake each, made by a text substitution) must fail at least one
test. Run from anywhere:

    python check_mutants.py
"""
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent

MUTANTS = {
    "drill1_async_harness": [
        ("no in-flight dedup (duplicate calls)",
         "owner = key not in inflight", "owner = True"),
        ("cache key without run index",
         "json.dumps([model, prompt, run])", "json.dumps([model, prompt])"),
        ("error hidden as empty output",
         'return None, f"{type(e).__name__}: {e}", attempts',
         'return "", None, attempts'),
        ("retries every exception",
         "except RateLimitError as e:", "except Exception as e:"),
        ("no concurrency limit",
         "async with sem:", "if True:"),
        ("constant backoff",
         "delay = base_delay * 2 ** (attempts - 1)", "delay = base_delay"),
        ("appends to results file",
         'out_path.open("w")', 'out_path.open("a")'),
        ("results in finish order",
         "records = list(await asyncio.gather(*jobs))\n\n    records.sort(",
         "records = [await f for f in asyncio.as_completed(jobs)]\n\n"
         "    (lambda **k: None)("),
        ("errors cached",
         "        if err is None:\n            cache.put(key, out)",
         "        cache.put(key, out or '')"),
    ],
    "drill2_paired_bootstrap": [
        ("pools rows (no per-case mean)",
         "diffs[cid] = sum(gb) / len(gb) - sum(ga) / len(ga)",
         "diffs[cid] = (sum(gb) - sum(ga)) / max(len(ga), len(gb))"),
        ("record order leaks into the seed",
         "d = [diffs[c] for c in sorted(diffs)]",
         "d = [diffs[c] for c in dict.fromkeys("
         "str(r['case_id']) for r in records) if c in diffs]"),
        ("None grade counted as 0",
         'if r["variant"] in (a, b) and r.get("grade") is not None:\n'
         '            grades[cid][r["variant"]].append(float(r["grade"]))',
         'if r["variant"] in (a, b):\n'
         '            grades[cid][r["variant"]].append('
         'float(r["grade"] or 0))'),
        ("resamples runs, not cases (via expanded rows)",
         "means = sorted(sum(rng.choices(d, k=n)) / n for _ in range(n_boot))",
         "rows = [g for c in sorted(diffs) for g in [diffs[c]] * 5]\n"
         "    means = sorted(sum(rng.choices(rows, k=len(rows))) / len(rows)"
         " for _ in range(n_boot))"),
        ("no guard for < 2 cases",
         "if len(diffs) < 2:", "if len(diffs) < 1:"),
    ],
    "drill3_judge_agreement": [
        ("0 instead of undefined",
         "return a / b if b else None", "return a / b if b else 0"),
        ("kappa 1 when pe == 1",
         "return None if pe >= 1 else", "return 1.0 if pe >= 1 else"),
        ("no label normalising",
         'h = (r["human"] or "").strip().upper()', 'h = r["human"] or ""'),
        ("judge blanks counted as PASS",
         'if j not in LABELS:\n            c["skipped"] += 1\n        elif',
         'if j not in LABELS:\n            j = "PASS"\n        if'),
        ("Wald interval instead of Wilson",
         "den = 1 + z * z / n", "den = 1; z2 = 0"),
        ("BOM not handled",
         'encoding="utf-8-sig"', 'encoding="utf-8"'),
    ],
    "drill4_structured_output": [
        ("bool accepted as int",
         "    if isinstance(value, bool):\n        return False\n", ""),
        ("plain == comparison, no type check",
         "    if not field_ok(got, spec):\n        return False\n"
         "    if spec[\"type\"] == \"number\":\n"
         "        return abs(got - want) <= 1e-6\n"
         "    return type(got) is type(want) and got == want",
         "    return got == want"),
        ("rates over parsed outputs only",
         "rate = (lambda k: k / n) if n else (lambda k: None)",
         "rate = (lambda k: k / max(parsed, 1))"),
        ("no prose fallback",
         'i, j = body.find("{"), body.rfind("}")', "i, j = -1, -1"),
        ("extra keys are errors",
         "    extra = sorted(k for k in obj if k not in schema)\n",
         "    extra = sorted(k for k in obj if k not in schema)\n"
         "    errors += [f'extra: {k}' for k in extra]\n"),
        ("list accepted as object",
         "if not isinstance(obj, dict):", "if obj is None:"),
    ],
}


def run_tests(drill, file):
    test = next((HERE / drill).glob("test_drill*.py"))
    p = subprocess.run([sys.executable, str(test), str(file)],
                       capture_output=True, text=True, cwd=HERE / drill,
                       timeout=300)
    last = p.stdout.strip().splitlines()[-1] if p.stdout.strip() else "?"
    fails = [ln.split(":")[0][6:] for ln in p.stdout.splitlines()
             if ln.startswith("FAIL")]
    return p.returncode, last, fails


def main():
    bad = 0
    t0 = time.monotonic()
    for drill, muts in MUTANTS.items():
        print(f"== {drill}")
        rc, last, _ = run_tests(drill, HERE / drill / "solution.py")
        print(f"   solution: {last}")
        bad += rc != 0
        rc, last, _ = run_tests(drill, HERE / drill / "starter.py")
        print(f"   starter:  {last}")
        bad += rc == 0
        src = (HERE / drill / "solution.py").read_text()
        with tempfile.TemporaryDirectory() as tmp:
            for i, (name, old, new) in enumerate(muts):
                if old not in src:
                    print(f"   MUTANT NOT APPLIED: {name}")
                    bad += 1
                    continue
                f = Path(tmp) / f"mutant{i}.py"
                f.write_text(src.replace(old, new, 1))
                rc, last, fails = run_tests(drill, f)
                status = "caught" if rc != 0 else "MISSED"
                bad += rc == 0
                print(f"   {status:7} {name}: {', '.join(fails)[:90]}")
    print(f"\n{'OK' if not bad else f'{bad} PROBLEMS'} "
          f"in {time.monotonic() - t0:.0f}s")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
