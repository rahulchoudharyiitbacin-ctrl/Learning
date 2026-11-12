# References verified for Chapter 16 (Coding drills)

All opened on 2026-11-13.

| URL | What it says | Used for |
|---|---|---|
| https://docs.python.org/3/library/asyncio-sync.html | `asyncio.Semaphore` keeps a counter; `acquire()` blocks at zero; `async with sem:` is the preferred form | Drill 1 concurrency limit; Read more |
| https://platform.claude.com/docs/en/api/rate-limits (redirect from docs.claude.com/en/api/rate-limits) | Exceeding a rate limit returns a 429; "When the response has a `retry-after` header, wait that many seconds before retrying." Not every 429 carries it (spend-cap 429s never do) | Drill 1 "what interviewers look for"; Read more |
| https://docs.python.org/3/library/random.html | `choices` returns a k-sized list chosen with replacement; reusing a seed reproduces the sequence (algorithms may change across Python versions) | Drill 2 hint and teacher's note; Read more |
| https://arxiv.org/abs/2411.00640 | Miller, "Adding Error Bars to Evals: A Statistical Approach to Language Model Evaluations" (abstract does not itself say "clustered"; Chapter 9 already cites the body) | Read more |
| https://hamel.dev/blog/posts/evals-faq/ | Focus on high TPR and TNR on a held-out labelled set when aligning a judge | Drill 3 framing; Read more |
| https://en.wikipedia.org/wiki/Binomial_proportion_confidence_interval | Wilson interval improves on the normal-approximation (Wald) interval; usable with small samples and skewed observations | Drill 3 common mistakes (Wald zero width); Read more |
| https://en.wikipedia.org/wiki/Cohen%27s_kappa | kappa = (po - pe)/(1 - pe); can be undefined (zero denominator); prevalence/imbalance affects kappa | Drill 3 kappa guard; Read more |
| https://docs.python.org/3/library/functions.html#bool | "The bool class is a subclass of int" | Drill 4 bool trap; Read more |

Interview-format evidence (live harness exercise, take-home with eval script) comes from notes/review-opus.md section A.3, whose sources are prep sites and community repos (medium-low credibility). The chapter says so.

Numbers in the chapter that come from code, not sources: Wilson 12/20 = 0.387-0.781 and 74/80 = 0.846-0.965 (checked by an independent brute-force inversion of the score test), kappa 0.545 and 0.221, the exact bootstrap bound 0.75 for d = 0,0,0,1, coverage 94.7% (1,000 reps), sample outputs of drills 2-4. All are asserted in work/drills/*/test_drill*.py.
