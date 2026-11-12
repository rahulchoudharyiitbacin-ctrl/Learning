"""Tests for Drill 1. Plain asserts, standard library only.

    python test_drill1.py               # tests solution.py
    python test_drill1.py my_drill1.py  # tests your file
    DRILL_FILE=my_drill1.py python test_drill1.py
"""
import asyncio
import importlib.util
import json
import os
import sys
import tempfile
import time
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from fake_llm import FakeLLM, fake_answer  # noqa: E402

MODEL = "fake-model-1"
VARIANTS = {"A": "Label this.\n{input}",
            "B": "Reply with one label only.\n{input}"}


def load_module():
    arg = (sys.argv[1] if len(sys.argv) > 1
           else os.environ.get("DRILL_FILE", "solution.py"))
    path = Path(arg)
    if not path.exists():
        path = HERE / arg
    sys.path.insert(0, str(path.resolve().parent))
    spec = importlib.util.spec_from_file_location("drill1_under_test",
                                                  path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    print(f"Testing {path}")
    return mod


M = None


def make_cases(texts, expected="refund"):
    return [{"id": f"c{i:02d}", "input": t, "expected": expected}
            for i, t in enumerate(texts)]


def run(cases, llm, tmp, *, runs=1, variants=VARIANTS, model=MODEL,
        concurrency=4, max_retries=3, base_delay=0.005, out="out.jsonl",
        cache="cache"):
    return asyncio.run(M.run_eval(
        cases, variants, llm.call_model, model=model, runs=runs,
        out_path=Path(tmp) / out, cache_dir=Path(tmp) / cache,
        concurrency=concurrency, max_retries=max_retries,
        base_delay=base_delay))


def strip_volatile(recs):
    return [{k: v for k, v in r.items() if k not in ("attempts", "cached")}
            for r in recs]


TEXTS = ["refund my kettle", "where is my delivery", "account locked",
         "gift cards?", "refund the charge", "late delivery again"]

# ------------------------------------------------------------------


def test_one_record_per_job_sorted_and_saved():
    with tempfile.TemporaryDirectory() as tmp:
        recs = run(make_cases(TEXTS[:4]), FakeLLM(), tmp, runs=2)
        assert len(recs) == 4 * 2 * 2, f"expected 16 records, got {len(recs)}"
        need = {"case_id", "variant", "run", "model", "output", "grade",
                "error", "attempts", "cached"}
        for r in recs:
            assert need <= set(r), f"missing fields: {need - set(r)}"
        keys = [(r["case_id"], r["variant"], r["run"]) for r in recs]
        assert keys == sorted(keys), "records must be sorted"
        assert len(set(keys)) == 16, "each (case, variant, run) once"
        lines = (Path(tmp) / "out.jsonl").read_text().splitlines()
        assert [json.loads(x) for x in lines] == recs, \
            "JSONL file must hold exactly the returned records, in order"


def test_grades_trim_and_ignore_case():
    with tempfile.TemporaryDirectory() as tmp:
        cases = make_cases(TEXTS)
        recs = run(cases, FakeLLM(), tmp)
        by_id = {c["id"]: c for c in cases}
        for r in recs:
            prompt = VARIANTS[r["variant"]].replace(
                "{input}", by_id[r["case_id"]]["input"])
            raw = fake_answer(MODEL, prompt)
            assert r["output"] == raw, "save the raw output, unmodified"
            want = int(raw.strip().lower() == "refund")
            assert r["grade"] == want, (r, want)
        assert any(r["output"] != r["output"].strip() for r in recs), \
            "test data should include padded outputs"


def test_no_duplicate_calls_for_identical_prompts():
    # Three cases share one message. Same prompt, same run -> one call.
    texts = ["refund my kettle"] * 3 + ["account locked"]
    llm = FakeLLM()
    with tempfile.TemporaryDirectory() as tmp:
        recs = run(make_cases(texts), llm, tmp, runs=2, concurrency=8)
        assert len(recs) == 4 * 2 * 2
        assert llm.calls == 2 * 2 * 2, (
            f"2 unique messages x 2 variants x 2 runs = 8 calls, "
            f"made {llm.calls} (duplicates in flight at the same time?)")
        assert sum(r["attempts"] for r in recs) == llm.calls, \
            "sum of attempts must equal real calls"


def test_repeated_runs_are_separate_samples():
    # Keying the cache on (model, prompt) only would make 1 call
    # per prompt and copy it to every run.
    llm = FakeLLM()
    with tempfile.TemporaryDirectory() as tmp:
        run(make_cases(TEXTS[:2]), llm, tmp, runs=3)
        for key, n in llm.attempts.items():
            assert n == 3, f"each prompt needs 3 calls for 3 runs, got {n}"


def test_rerun_costs_nothing():
    with tempfile.TemporaryDirectory() as tmp:
        cases = make_cases(TEXTS)
        first = run(cases, FakeLLM(), tmp, runs=2)
        llm2 = FakeLLM(latency_seed=9)
        second = run(cases, llm2, tmp, runs=2)
        assert llm2.calls == 0, f"rerun made {llm2.calls} calls"
        assert strip_volatile(first) == strip_volatile(second)
        assert all(r["cached"] for r in second)
        assert all(r["attempts"] == 0 for r in second)
        lines = (Path(tmp) / "out.jsonl").read_text().splitlines()
        assert len(lines) == len(second), "overwrite the file, don't append"


def test_model_is_part_of_cache_key():
    with tempfile.TemporaryDirectory() as tmp:
        cases = make_cases(TEXTS[:3])
        run(cases, FakeLLM(), tmp)
        llm2 = FakeLLM()
        recs = run(cases, llm2, tmp, model="fake-model-2")
        assert llm2.calls == 6, "a new model must not reuse old answers"
        assert all(r["model"] == "fake-model-2" for r in recs)


def test_concurrency_limit_respected_and_used():
    texts = [f"message {i} about delivery" for i in range(20)]
    llm = FakeLLM()
    with tempfile.TemporaryDirectory() as tmp:
        run(make_cases(texts), llm, tmp, concurrency=3)
    assert llm.max_inflight <= 3, f"{llm.max_inflight} calls in flight"
    assert llm.max_inflight >= 2, "calls must actually run concurrently"


def test_retries_429_with_growing_backoff():
    llm = FakeLLM(min_latency=0.001, max_latency=0.002)
    base = 0.02
    with tempfile.TemporaryDirectory() as tmp:
        recs = run(make_cases(["FLAKY refund please"]), llm, tmp,
                   variants={"A": "{input}"}, base_delay=base)
    r = recs[0]
    assert r["error"] is None and r["output"] is not None, r
    assert r["attempts"] == 3, f"2 x 429 then success = 3, got {r['attempts']}"
    times = [t for t, *_ in llm.log]
    gaps = [b - a for a, b in zip(times, times[1:])]
    assert gaps[0] >= base * 0.9, f"first wait {gaps[0]:.3f}s < {base}s"
    assert gaps[1] >= 2 * base * 0.9, \
        f"second wait {gaps[1]:.3f}s: backoff must grow"


def test_gives_up_and_records_the_error():
    llm = FakeLLM()
    with tempfile.TemporaryDirectory() as tmp:
        recs = run(make_cases(["BUSY account", "account ok"]), llm, tmp,
                   variants={"A": "{input}"}, max_retries=2)
    busy, ok = recs
    assert busy["output"] is None and busy["grade"] is None, \
        "a failed call must not be graded 0 or given empty output"
    assert busy["error"] and ("429" in busy["error"]
                              or "RateLimit" in busy["error"]), busy
    assert busy["attempts"] == 3, "1 try + 2 retries"
    assert ok["error"] is None and ok["output"] is not None


def test_non_retryable_error_not_retried():
    llm = FakeLLM()
    with tempfile.TemporaryDirectory() as tmp:
        recs = run(make_cases(["POISON {x}", "refund"]), llm, tmp,
                   variants={"A": "{input}"})
    bad = recs[0]
    err = bad["error"] or ""
    assert "400" in err or "BadRequest" in err, bad
    assert bad["attempts"] == 1 and llm.attempts[(MODEL, "POISON {x}")] == 1, \
        "a 400 must not be retried"
    assert bad["grade"] is None
    assert recs[1]["error"] is None, "one bad case must not stop the run"


def test_errors_are_not_cached():
    with tempfile.TemporaryDirectory() as tmp:
        cases = make_cases(["POISON", "BUSY", "refund now"])
        run(cases, FakeLLM(), tmp, variants={"A": "{input}"},
            max_retries=1)
        llm2 = FakeLLM()
        recs = run(cases, llm2, tmp, variants={"A": "{input}"},
                   max_retries=1)
        assert llm2.attempts[(MODEL, "POISON")] == 1, \
            "failed calls must be tried again on rerun"
        assert llm2.attempts[(MODEL, "BUSY")] == 2
        assert llm2.attempts[(MODEL, "refund now")] == 0
        assert recs[2]["cached"] is True


def test_results_do_not_depend_on_finish_order():
    cases = make_cases(TEXTS)
    with tempfile.TemporaryDirectory() as tmp:
        a = run(cases, FakeLLM(latency_seed=1), tmp, runs=2,
                cache="c1", out="a.jsonl")
        b = run(cases, FakeLLM(latency_seed=2), tmp, runs=2,
                cache="c2", out="b.jsonl")
        assert strip_volatile(a) == strip_volatile(b)
        fa = (Path(tmp) / "a.jsonl").read_text().splitlines()
        fb = (Path(tmp) / "b.jsonl").read_text().splitlines()
        assert [json.loads(x)["case_id"] for x in fa] == \
            [json.loads(x)["case_id"] for x in fb]


# ------------------------------------------------------------------
def main():
    global M
    M = load_module()
    tests = [(n, f) for n, f in globals().items()
             if n.startswith("test_") and callable(f)]
    failed = 0
    t0 = time.monotonic()
    for name, fn in tests:
        try:
            fn()
            print(f"PASS  {name}")
        except Exception as e:
            failed += 1
            msg = str(e) or type(e).__name__
            print(f"FAIL  {name}: {msg}")
            if os.environ.get("VERBOSE"):
                traceback.print_exc()
    print(f"\n{len(tests) - failed}/{len(tests)} passed "
          f"in {time.monotonic() - t0:.1f}s")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
