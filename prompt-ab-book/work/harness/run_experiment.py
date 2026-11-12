"""Minimal A/B harness for prompts.

Usage:
    python run_experiment.py experiments/ticket-triage-v1-vs-v2.yaml --mock
    python run_experiment.py experiments/ticket-triage-v1-vs-v2.yaml
"""
import argparse
import hashlib
import json
import random
import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import yaml


# ---- Step 1: read the inputs -------------------------------
def read_jsonl(path):
    lines = Path(path).read_text().splitlines()
    return [json.loads(x) for x in lines if x.strip()]


# ---- Step 3: grading (code checks first) -------------------
def exact_match(case, output):
    return int(output.strip().lower() == case["expected"].lower())


GRADERS = {"exact_match": exact_match}

try:  # more graders live in graders.py (Chapter 7)
    from graders import EXTRA_GRADERS
    GRADERS.update(EXTRA_GRADERS)
except ImportError:
    pass


# ---- Step 2: call the model --------------------------------
def call_model(client, cfg, system, text):
    t0 = time.time()
    extra = {}
    if cfg.get("effort"):
        extra["output_config"] = {"effort": cfg["effort"]}
    resp = client.messages.create(
        model=cfg["model"],
        max_tokens=cfg["max_tokens"],
        system=system,
        messages=[{"role": "user", "content": text}],
        **extra,
    )
    out = "".join(b.text for b in resp.content if b.type == "text")
    return {
        "output": out,
        "stop_reason": resp.stop_reason,
        "tokens_in": resp.usage.input_tokens,
        "tokens_out": resp.usage.output_tokens,
        "latency_ms": int((time.time() - t0) * 1000),
    }


def run_job(client, cfg, prompts, grader, job):
    case, variant, run = job
    rec = {"case_id": case["id"], "variant": variant, "run": run}
    try:
        rec.update(call_model(client, cfg, prompts[variant], case["input"]))
        rec["grade"] = grader(case, rec["output"])
    except Exception as e:  # keep errors as data, never hide them
        rec["error"] = f"{type(e).__name__}: {e}"[:200]
    return rec


# ---- Free dry run: a fake model, no API key needed ---------
class MockClient:
    class _Msgs:
        def create(self, **kw):
            text = kw["messages"][0]["content"].lower()
            keys = {"refund": ("money back", "refund", "charged", "reimburs"),
                    "delivery": ("late", "driver", "deliver", "arrive"),
                    "account": ("password", "log in", "account", "phone")}
            label = "other"
            for name, words in keys.items():
                if any(w in text for w in words):
                    label = name
                    break
            noise = 0.15 if "Examples" in kw["system"] else 0.25
            if random.random() < noise:
                label = random.choice(["refund", "delivery", "account", "other"])
            return _Resp(label, len(kw["system"]) // 4 + 20)

    messages = _Msgs()


class _Block:
    type = "text"

    def __init__(self, text):
        self.text = text


class _Usage:
    def __init__(self, n_in, n_out):
        self.input_tokens, self.output_tokens = n_in, n_out


class _Resp:
    stop_reason = "end_turn"

    def __init__(self, label, n_in):
        self.content = [_Block(label)]
        self.usage = _Usage(n_in, 3)


# ---- Step 5: summarize -------------------------------------
def summarize(records, cfg):
    good = [r for r in records if "error" not in r]
    print(f"\n{len(records)} calls, {len(records) - len(good)} errors")
    per = {}
    for r in good:
        per.setdefault((r["variant"], r["case_id"]), []).append(r["grade"])
    case_mean = {k: sum(v) / len(v) for k, v in per.items()}
    a, b = list(cfg["variants"])[:2]
    for v in (a, b):
        rows = [r for r in good if r["variant"] == v]
        scores = [m for (vv, _), m in case_mean.items() if vv == v]
        if not scores:
            continue
        print(f"{v}: accuracy {statistics.mean(scores):.3f}  "
              f"tokens in/out {sum(r['tokens_in'] for r in rows)}/"
              f"{sum(r['tokens_out'] for r in rows)}  "
              f"median latency {statistics.median(r['latency_ms'] for r in rows)} ms")
    cases = {c for (_, c) in case_mean}
    diffs = [case_mean[(b, c)] - case_mean[(a, c)]
             for c in cases if (a, c) in case_mean and (b, c) in case_mean]
    if diffs:
        print(f"{b} - {a} = {statistics.mean(diffs):+.3f} over {len(diffs)} cases "
              f"({b} better on {sum(d > 0 for d in diffs)}, "
              f"{a} better on {sum(d < 0 for d in diffs)})")
        print("This is a difference, not a verdict. Chapter 9 adds the interval.")


# ---- Step 4: run everything --------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("--mock", action="store_true")
    args = ap.parse_args()

    cfg_path = Path(args.config).resolve()
    root = cfg_path.parent.parent
    cfg = yaml.safe_load(cfg_path.read_text())
    cases = read_jsonl(root / cfg["dataset"])
    prompts = {v: (root / p).read_text() for v, p in cfg["variants"].items()}
    grader = GRADERS[cfg["grader"]]

    blob = cfg_path.read_text() + "".join(prompts.values())
    chash = hashlib.sha256(blob.encode()).hexdigest()[:6]

    out_dir = root / "runs" / cfg["name"]
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / ("records-mock.jsonl" if args.mock else "records.jsonl")
    old = read_jsonl(path) if path.exists() else []
    done = {(r["case_id"], r["variant"], r["run"]) for r in old if "error" not in r}

    jobs = [(c, v, i) for c in cases for v in prompts
            for i in range(cfg["runs_per_case"])]
    random.Random(0).shuffle(jobs)
    jobs = [j for j in jobs if (j[0]["id"], j[1], j[2]) not in done]
    print(f"{cfg['name']}: {len(jobs)} calls to make ({len(done)} already done)")

    if args.mock:
        client = MockClient()
    else:
        import anthropic
        client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY

    with ThreadPoolExecutor(max_workers=cfg.get("workers", 4)) as pool, \
            open(path, "a") as f:
        futures = [pool.submit(run_job, client, cfg, prompts, grader, j) for j in jobs]
        for n, fut in enumerate(as_completed(futures), 1):
            rec = fut.result()
            rec["config_hash"] = chash
            f.write(json.dumps(rec) + "\n")
            f.flush()
            if n % 20 == 0:
                print(f"  {n}/{len(jobs)} done")

    if args.mock:
        print("\n*** MOCK MODE: these numbers are fake, only the code is tested ***")
    summarize(read_jsonl(path), cfg)


if __name__ == "__main__":
    main()
