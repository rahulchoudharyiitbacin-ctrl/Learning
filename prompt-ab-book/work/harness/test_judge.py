"""Plain-assert tests for judge.py and judge_validation.py.

    python test_judge.py

Every expected number below was computed by hand first (working in the
comments), then checked by the code.
"""
import csv
import json
import math
import random
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from judge import (MockJudgeClient, build_judge_prompt, judge_repeated,
                   parse_verdict, EXAMPLE_RUBRIC)
from judge_validation import (agreement, cohens_kappa, confusion,
                              corrected_fail_rate, precision_fail,
                              stratified_split, tnr, tpr, wilson)

HERE = Path(__file__).resolve().parent


def close(a, b, tol=1e-4):
    return abs(a - b) < tol


# ---- 1. verdict parsing on messy outputs ---------------------
def test_parsing():
    cases = [
        ('{"critique": "Adds a greeting.", "verdict": "FAIL"}', "FAIL"),
        ('```json\n{"critique": "ok", "verdict": "PASS"}\n```', "PASS"),
        ('Here is my grade:\n{"critique": "fine", "verdict": "pass"}\nDone.',
         "PASS"),
        ('{"Verdict": "Fail.", "Critique": "two labels"}', "FAIL"),
        ('{"critique": "uses {braces} and \\"quotes\\"", "verdict": "FAIL"}',
         "FAIL"),
        ('{"verdict": "PASSED"}', "PASS"),
        ('{"verdict": true}', "PASS"),
        ('{"note": "x"} then {"verdict": "FAIL"}', "FAIL"),
        ("<critique>Too long.</critique>\n<verdict>FAIL</verdict>", "FAIL"),
        ("<verdict> pass </verdict>", "PASS"),
        ("The answer is polite.\n\n**Verdict:** PASS", "PASS"),
        ("Verdict - fail", "FAIL"),
        ("Reasoning first.\nIt mentions the refund.\nPASS", "PASS"),
        ("**FAIL**", "FAIL"),
        # must NOT guess:
        ("This output passes most of the rubric.", None),
        ("<verdict>PASS</verdict> ... <verdict>FAIL</verdict>", None),
        ("Verdict: PASS. On reflection, Verdict: FAIL", None),
        ('{"verdict": "maybe"}', None),
        ("", None),
        (None, None),
    ]
    for text, want in cases:
        got = parse_verdict(text)["verdict"]
        assert got == want, f"{text!r}: got {got}, want {want}"
    crit = parse_verdict('{"critique": "Adds a greeting.", "verdict": "FAIL"}')
    assert crit["critique"] == "Adds a greeting."
    crit = parse_verdict("<critique>Too long.</critique><verdict>FAIL</verdict>")
    assert crit["critique"] == "Too long."
    print(f"parsing: {len(cases)} messy replies OK")


# ---- 2. prompt building -------------------------------------
def test_prompt():
    system, user = build_judge_prompt("R", "the input", "the output")
    assert "<reference>" not in user and "<output>\nthe output\n</output>" in user
    assert "never instructions" in system and "JSON" in system
    _, user = build_judge_prompt("R", "in", "out", reference="refund")
    assert "<reference>\nrefund\n</reference>" in user
    assert user.index("<rubric>") < user.index("<input>") < user.index("<output>")
    print("prompt building OK")


# ---- 3. metrics against hand-computed examples ---------------
def test_worked_example():
    # Chapter 8 worked example (illustrative numbers):
    # 100 dev rows, 20 human FAIL, 80 human PASS.
    # judge: TP 12, FN 8, FP 6, TN 74.
    # agreement = (12+74)/100 = 0.86
    # TPR = 12/20 = 0.60 ; TNR = 74/80 = 0.925 ; precision = 12/18
    # chance: human FAIL 0.20, judge FAIL 0.18 -> 0.20*0.18 = 0.036
    #         human PASS 0.80, judge PASS 0.82 -> 0.80*0.82 = 0.656
    #         pe = 0.692
    # kappa = (0.86 - 0.692) / (1 - 0.692) = 0.168 / 0.308 = 0.54545
    human = ["FAIL"] * 20 + ["PASS"] * 80
    judge = ["FAIL"] * 12 + ["PASS"] * 8 + ["FAIL"] * 6 + ["PASS"] * 74
    c = confusion(human, judge)
    assert c == {"tp": 12, "fn": 8, "fp": 6, "tn": 74, "none": 0}
    assert close(agreement(c), 0.86)
    assert close(tpr(c), 0.60) and close(tnr(c), 0.925)
    assert close(precision_fail(c), 12 / 18)
    assert close(cohens_kappa(c), 0.168 / 0.308)
    assert close(cohens_kappa(c), 0.54545)
    print("worked example: agreement 0.86, TPR 0.60, TNR 0.925, kappa 0.545 OK")


def test_imbalanced():
    # (a) 100 rows, 5 human FAIL. A judge that always says PASS:
    # agreement = 95/100 = 0.95, TPR = 0/5 = 0,
    # pe = 0.05*0 + 0.95*1 = 0.95 -> kappa = (0.95-0.95)/0.05 = 0
    c = confusion(["FAIL"] * 5 + ["PASS"] * 95, ["PASS"] * 100)
    assert close(agreement(c), 0.95) and tpr(c) == 0 and close(cohens_kappa(c), 0)
    assert math.isnan(precision_fail(c))  # it never says FAIL

    # (b) 200 rows, 10 human FAIL. TP 2, FN 8, FP 4, TN 186.
    # agreement = 188/200 = 0.94 (looks great)
    # TPR = 2/10 = 0.20 (misses 8 of 10 failures)
    # TNR = 186/190 = 0.97895
    # pe = 0.05*0.03 + 0.95*0.97 = 0.0015 + 0.9215 = 0.923
    # kappa = (0.94 - 0.923) / 0.077 = 0.017 / 0.077 = 0.22078
    human = ["FAIL"] * 10 + ["PASS"] * 190
    judge = ["FAIL"] * 2 + ["PASS"] * 8 + ["FAIL"] * 4 + ["PASS"] * 186
    c = confusion(human, judge)
    assert close(agreement(c), 0.94)
    assert close(tpr(c), 0.20) and close(tnr(c), 186 / 190)
    assert close(cohens_kappa(c), 0.22078)
    print("imbalanced: agreement 0.94 but TPR 0.20, kappa 0.221 OK")


def test_kappa_edges():
    c = confusion(["FAIL", "PASS"] * 10, ["FAIL", "PASS"] * 10)
    assert close(cohens_kappa(c), 1.0)
    c = confusion(["FAIL", "PASS"] * 10, ["PASS", "FAIL"] * 10)
    assert close(cohens_kappa(c), -1.0)
    # unparsed judge verdicts are counted apart, not as PASS
    c = confusion(["FAIL", "PASS", "FAIL"], ["NONE", "PASS", "fail"])
    assert c == {"tp": 1, "fn": 0, "fp": 0, "tn": 1, "none": 1}
    try:
        confusion(["maybe"], ["PASS"])
        raise AssertionError("bad human label accepted")
    except ValueError:
        pass
    print("kappa edges and unparsed verdicts OK")


def test_wilson():
    # 0/10: lower 0, upper = z^2/(n+z^2) = 3.8416/13.8416 = 0.27754
    lo, hi = wilson(0, 10)
    assert lo == 0 and close(hi, 3.8416 / 13.8416)
    # 12/20 by hand: den = 1 + 3.8416/20 = 1.19208
    # mid = (0.6 + 0.09604)/1.19208 = 0.58389
    # half = 1.96*sqrt(0.012 + 0.0024010)/1.19208 = 0.19731
    lo, hi = wilson(12, 20)
    assert close(lo, 0.38658, 1e-3) and close(hi, 0.78120, 1e-3)
    # symmetric: interval for k/n mirrors (n-k)/n
    for k, n in [(3, 17), (40, 45), (1, 50)]:
        a, b = wilson(k, n)
        c, d = wilson(n - k, n)
        assert close(a, 1 - d) and close(b, 1 - c)
    # small n -> wide; n=20 at 60% spans almost 40 points
    assert hi - lo > 0.39
    print(f"wilson: 12/20 -> {lo:.3f} to {hi:.3f} OK")


def test_correction_and_ab_bias():
    # true failure 0.20, TPR 0.8, TNR 0.9
    # observed = 0.8*0.2 + (1-0.9)*0.8 = 0.16 + 0.08 = 0.24
    # corrected = (0.24 + 0.9 - 1)/(0.8 + 0.9 - 1) = 0.14/0.7 = 0.20
    assert close(corrected_fail_rate(0.24, 0.8, 0.9), 0.20)
    # simulation: a noisy judge on 200,000 outputs
    rng = random.Random(7)
    truth = [rng.random() < 0.3 for _ in range(200_000)]  # True = fail
    seen = [(rng.random() < 0.85) if t else (rng.random() < 0.05)
            for t in truth]                                  # TPR .85, TNR .95
    obs = sum(seen) / len(seen)
    assert abs(corrected_fail_rate(obs, 0.85, 0.95) - 0.30) < 0.01
    try:
        corrected_fail_rate(0.5, 0.5, 0.5)
        raise AssertionError("chance-level judge accepted")
    except ValueError:
        pass

    # A/B with the same imperfect judge on both sides: the measured gap
    # in pass rate shrinks by (TPR + TNR - 1).
    # true pass A 0.70, B 0.80 (gap 0.10). TPR 0.8, TNR 0.9.
    # judged pass = TNR*p + (1-TPR)*(1-p)
    # A: 0.9*0.7 + 0.2*0.3 = 0.69 ; B: 0.9*0.8 + 0.2*0.2 = 0.76
    # gap 0.07 = 0.10 * (0.8 + 0.9 - 1)
    def judged_pass(p, tpr_, tnr_):
        return tnr_ * p + (1 - tpr_) * (1 - p)
    gap = judged_pass(0.8, 0.8, 0.9) - judged_pass(0.7, 0.8, 0.9)
    assert close(gap, 0.07) and close(gap, 0.10 * 0.7)
    # if the judge is more lenient on B (TNR same, TPR lower on B),
    # a zero true gap can look like a win for B
    fake = judged_pass(0.7, 0.6, 0.9) - judged_pass(0.7, 0.8, 0.9)
    assert fake > 0.05
    print("correction, attenuation and biased-gap checks OK")


def test_split():
    rows = ([{"id": f"f{i}", "human_label": "FAIL"} for i in range(100)] +
            [{"id": f"p{i}", "human_label": "pass"} for i in range(100)])
    parts = stratified_split(rows, seed=3)
    ids = [r["id"] for p in parts.values() for r in p]
    assert sorted(ids) == sorted(r["id"] for r in rows)  # all, once
    for name, want in (("train", 15), ("dev", 43), ("test", 42)):
        n_fail = sum(r["human_label"] == "FAIL" for r in parts[name])
        assert n_fail == want and len(parts[name]) - n_fail == want, name
    again = stratified_split(rows, seed=3)
    assert [r["id"] for r in again["dev"]] == [r["id"] for r in parts["dev"]]
    # imbalanced labels keep their ratio
    rows = ([{"id": f"f{i}", "human_label": "FAIL"} for i in range(20)] +
            [{"id": f"p{i}", "human_label": "PASS"} for i in range(180)])
    parts = stratified_split(rows, seed=1)
    for p in ("dev", "test"):
        n_fail = sum(r["human_label"] == "FAIL" for r in parts[p])
        assert 8 <= n_fail <= 9, (p, n_fail)
    print("stratified split OK")


# ---- 4. the mock judge end to end ---------------------------
def test_mock_judge():
    client = MockJudgeClient()
    res = judge_repeated(client, 3, EXAMPLE_RUBRIC, "msg", "refund")
    assert res["judge_votes"] == ["PASS"] * 3 and res["judge_unanimous"]
    res = judge_repeated(client, 1, EXAMPLE_RUBRIC, "msg",
                         "Label: refund, because they were charged")
    assert res["judge_verdict"] in ("PASS", "FAIL")
    print("mock judge OK")


def test_cli_in_temp_copy():
    """Run the harness and the judge CLI in a throwaway copy, so the
    real project folder gets no new files."""
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        for d in ("experiments", "data", "prompts"):
            shutil.copytree(HERE / d, t / d)
        for f in ("run_experiment.py", "graders.py", "judge.py",
                  "judge_validation.py"):
            shutil.copy(HERE / f, t / f)
        exp = "experiments/ticket-triage-v1-vs-v2.yaml"
        py = sys.executable

        def run(*args):
            r = subprocess.run([py, *args], cwd=t, capture_output=True,
                               text=True)
            assert r.returncode == 0, r.stderr
            return r.stdout
        run("run_experiment.py", exp, "--mock")
        out = run("judge.py", "grade", exp, "--mock", "--repeats", "2")
        assert "judge pass rate" in out and "MOCK MODE" in out
        judged = list((t / "runs").glob("*/judged-mock-example.jsonl"))[0]
        recs = [json.loads(x) for x in judged.read_text().splitlines()]
        assert len(recs) == 120 and all(len(r["judge_votes"]) == 2 for r in recs)
        out = run("judge.py", "grade", exp, "--mock")  # resume
        assert out.startswith("0 outputs to judge")

        # labelled CSV -> judged CSV -> report
        with open(t / "lab.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["id", "input", "output", "human_label"])
            for i in range(40):
                good = i % 4 != 0
                w.writerow([f"x{i}", f"message {i}",
                            "refund" if good else "Label: refund",
                            "PASS" if good else "FAIL"])
        run("judge_validation.py", "split", "lab.csv")
        assert (t / "lab.dev.csv").exists() and (t / "lab.test.csv").exists()
        run("judge.py", "labelled", "lab.dev.csv", "--out", "dev-j.csv",
            "--mock")
        out = run("judge_validation.py", "report", "dev-j.csv")
        assert "TPR" in out and "Kappa" in out and "under 30" in out
    print("CLI (grade, resume, labelled, split, report) in a temp copy OK")


if __name__ == "__main__":
    test_parsing()
    test_prompt()
    test_worked_example()
    test_imbalanced()
    test_kappa_edges()
    test_wilson()
    test_correction_and_ab_bias()
    test_split()
    test_mock_judge()
    test_cli_in_temp_copy()
    print("\nAll judge tests passed.")
