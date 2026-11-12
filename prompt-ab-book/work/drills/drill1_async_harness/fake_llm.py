"""A fake, offline stand-in for a model API (Drill 1). Do not edit.

    llm = FakeLLM(latency_seed=0)
    text = await llm.call_model("fake-model-1", prompt)

Behaviour:
- The answer depends only on (model, prompt): same input, same text.
- Each call sleeps a small random time (seeded), so calls finish
  out of order.
- Prompts containing "FLAKY" raise RateLimitError (HTTP 429) on the
  first 2 attempts seen for that (model, prompt), then succeed.
- Prompts containing "BUSY" always raise RateLimitError.
- Prompts containing "POISON" always raise BadRequestError (400).
  Retrying a 400 never helps.

Counters for tests: llm.calls (total attempts), llm.attempts
(Counter of (model, prompt) -> attempts), llm.max_inflight,
llm.log (list of (time, model, prompt, outcome)).
"""
import asyncio
import hashlib
import random
import time
from collections import Counter

LABELS = ["refund", "delivery", "account", "other"]


class RateLimitError(Exception):
    """Simulated HTTP 429. Safe to retry after a pause."""
    status_code = 429


class BadRequestError(Exception):
    """Simulated HTTP 400. Retrying will not help."""
    status_code = 400


def _h(*parts):
    raw = "\x1f".join(parts).encode()
    return int(hashlib.sha256(raw).hexdigest(), 16)


def fake_answer(model, prompt):
    """Deterministic answer: usually the label word found in the
    prompt's last line (the customer message), sometimes a wrong one,
    sometimes with stray spaces or capitals."""
    h = _h(model, prompt)
    last = prompt.strip().splitlines()[-1].lower() if prompt.strip() else ""
    found = [lab for lab in LABELS if lab in last]
    if found and h % 10 < 7:
        ans = found[0]
    else:
        ans = LABELS[(h // 10) % 4]
    if (h // 100) % 3 == 0:
        ans = " " + ans.capitalize() + "\n"
    return ans


class FakeLLM:
    def __init__(self, latency_seed=0, min_latency=0.005,
                 max_latency=0.03):
        self._rng = random.Random(latency_seed)
        self.min_latency = min_latency
        self.max_latency = max_latency
        self.calls = 0
        self.attempts = Counter()
        self.inflight = 0
        self.max_inflight = 0
        self.log = []

    async def call_model(self, model, prompt):
        self.calls += 1
        key = (model, prompt)
        self.attempts[key] += 1
        n = self.attempts[key]
        self.inflight += 1
        self.max_inflight = max(self.max_inflight, self.inflight)
        try:
            await asyncio.sleep(
                self._rng.uniform(self.min_latency, self.max_latency))
            if "POISON" in prompt:
                self.log.append((time.monotonic(), model, prompt, 400))
                raise BadRequestError("400 invalid request")
            if "BUSY" in prompt or ("FLAKY" in prompt and n <= 2):
                self.log.append((time.monotonic(), model, prompt, 429))
                raise RateLimitError("429 rate limited")
            self.log.append((time.monotonic(), model, prompt, 200))
            return fake_answer(model, prompt)
        finally:
            self.inflight -= 1
