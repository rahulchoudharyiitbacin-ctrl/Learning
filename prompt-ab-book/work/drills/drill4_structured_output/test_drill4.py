"""Tests for Drill 4. Plain asserts, standard library only.

    python test_drill4.py               # tests solution.py
    python test_drill4.py my_drill4.py  # tests your file
    DRILL_FILE=my_drill4.py python test_drill4.py
"""
import importlib.util
import json
import os
import sys
import time
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load_module():
    arg = (sys.argv[1] if len(sys.argv) > 1
           else os.environ.get("DRILL_FILE", "solution.py"))
    path = Path(arg)
    if not path.exists():
        path = HERE / arg
    sys.path.insert(0, str(path.resolve().parent))
    spec = importlib.util.spec_from_file_location("drill4_under_test",
                                                  path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    print(f"Testing {path}")
    return mod


M = None

SCHEMA = {
    "category": {"type": "string",
                 "enum": ["refund", "delivery", "account", "other"]},
    "urgent": {"type": "boolean"},
    "amount": {"type": "number"},
    "items": {"type": "integer"},
    "order_id": {"type": "string", "required": False},
}
GOOD = {"category": "refund", "urgent": False, "amount": 24.5, "items": 1}


def parses(text):
    obj, err = M.parse_output(text)
    return obj


# ---- parsing ------------------------------------------------------
def test_parse_plain_and_fenced():
    raw = json.dumps(GOOD)
    assert parses(raw) == GOOD
    assert parses(f"```json\n{raw}\n```") == GOOD
    assert parses(f"```\n{raw}\n```") == GOOD
    assert parses(f"```JSON\n{raw}\n```") == GOOD


def test_parse_with_prose_around():
    raw = json.dumps(GOOD)
    assert parses(f"Here you go:\n```json\n{raw}\n```\nAnything else?") == GOOD
    assert parses(f"Sure! {raw} Hope that helps.") == GOOD
    tricky = '{"note": "a {brace} inside", "x": 1}'
    assert parses(tricky) == {"note": "a {brace} inside", "x": 1}


def test_parse_rejects_invalid_and_non_objects():
    bad = ["", "   ", "{'category': 'refund'}", '{"a": 1,}',
           "not json at all", '{"a": ', "[1, 2]", "null", "42", '"text"']
    for text in bad:
        obj, err = M.parse_output(text)
        assert obj is None, f"{text!r} should not parse to an object"
        assert err, f"{text!r}: give a reason"


# ---- validation ---------------------------------------------------
def test_validate_ok_and_extra_keys():
    errs, extra = M.validate({**GOOD, "confidence": 0.9, "a": 1}, SCHEMA)
    assert errs == [], errs
    assert sorted(extra) == ["a", "confidence"], \
        "extra keys are reported, not treated as errors"


def test_validate_missing_type_enum():
    errs, _ = M.validate({"category": "Refund", "urgent": "no",
                          "items": 1}, SCHEMA)
    joined = " ".join(errs)
    assert len(errs) == 3, errs   # enum, type, missing amount
    assert "amount" in joined and "urgent" in joined \
        and "category" in joined
    errs, _ = M.validate(GOOD, SCHEMA)
    assert errs == [], "order_id is optional"


def test_bool_is_not_a_number_and_int_is_not_bool():
    # In Python, isinstance(True, int) is True. A careful check isn't.
    errs, _ = M.validate({**GOOD, "items": True}, SCHEMA)
    assert any("items" in e for e in errs), "True is not an integer"
    errs, _ = M.validate({**GOOD, "amount": False}, SCHEMA)
    assert any("amount" in e for e in errs), "False is not a number"
    errs, _ = M.validate({**GOOD, "urgent": 0}, SCHEMA)
    assert any("urgent" in e for e in errs), "0 is not a boolean"
    errs, _ = M.validate({**GOOD, "items": 1.5}, SCHEMA)
    assert any("items" in e for e in errs), "1.5 is not an integer"
    errs, _ = M.validate({**GOOD, "amount": 3}, SCHEMA)
    assert errs == [], "an int is a valid number"
    errs, _ = M.validate({**GOOD, "category": None}, SCHEMA)
    assert errs, "null is not a string"


# ---- field-level accuracy -----------------------------------------
def test_field_accuracy_counts_invalid_json_as_wrong():
    outs = [json.dumps(GOOD), json.dumps(GOOD), json.dumps(GOOD),
            "{'category': 'refund'}"]
    rep = M.evaluate(outs, [GOOD] * 4, SCHEMA)
    assert rep["n"] == 4
    assert rep["field_accuracy"]["category"] == 0.75, \
        "denominator is all outputs, not only the ones that parsed"
    assert rep["parsed_rate"] == 0.75
    assert rep["exact_match_rate"] == 0.75
    assert rep["cases"][3]["parse_error"]


def test_one_bad_field_does_not_zero_the_others():
    out = json.dumps({**GOOD, "category": "Refund"})
    rep = M.evaluate([out], [GOOD], SCHEMA)
    fa = rep["field_accuracy"]
    assert fa["category"] == 0 and fa["urgent"] == 1 and fa["amount"] == 1
    assert rep["schema_valid_rate"] == 0 and rep["exact_match_rate"] == 0


def test_wrong_type_with_equal_value_is_wrong():
    # 0 == False and 1 == True and "1" != 1. All must count as wrong.
    exp = {**GOOD, "urgent": False, "items": 1, "amount": 24.5}
    outs = [json.dumps({**exp, "urgent": 0}),
            json.dumps({**exp, "items": True}),
            json.dumps({**exp, "amount": "24.5"})]
    rep = M.evaluate(outs, [exp] * 3, SCHEMA)
    fa = rep["field_accuracy"]
    assert abs(fa["urgent"] - 2 / 3) < 1e-9, fa
    assert abs(fa["items"] - 2 / 3) < 1e-9, fa
    assert abs(fa["amount"] - 2 / 3) < 1e-9, fa


def test_numbers_compare_by_value():
    exp = {**GOOD, "amount": 3}
    rep = M.evaluate([json.dumps({**exp, "amount": 3.0})], [exp], SCHEMA)
    assert rep["field_accuracy"]["amount"] == 1, "3.0 equals 3"


def test_optional_field_absent_on_both_sides_is_right():
    with_id = {**GOOD, "order_id": "A-1"}
    outs = [json.dumps(GOOD), json.dumps(GOOD), json.dumps(with_id)]
    rep = M.evaluate(outs, [GOOD, with_id, GOOD], SCHEMA)
    assert abs(rep["field_accuracy"]["order_id"] - 1 / 3) < 1e-9, \
        rep["field_accuracy"]
    assert rep["cases"][0]["fields"]["order_id"] is True


def test_extra_keys_reported_per_case():
    rep = M.evaluate([json.dumps({**GOOD, "confidence": 0.9})], [GOOD],
                     SCHEMA)
    assert rep["cases"][0]["extra_keys"] == ["confidence"]
    assert rep["schema_valid_rate"] == 1 and rep["exact_match_rate"] == 1


def test_length_mismatch_raises():
    try:
        M.evaluate([json.dumps(GOOD)], [GOOD, GOOD], SCHEMA)
    except ValueError:
        return
    raise AssertionError("outputs and expected must line up")


def test_sample_file_hand_counted():
    rows = [json.loads(x) for x in
            (HERE / "sample.jsonl").read_text().splitlines() if x]
    rep = M.evaluate([r["output"] for r in rows],
                     [r["expected"] for r in rows], SCHEMA)
    # Hand count (see README): 7 parse, 3 schema-valid, 3 all right.
    assert abs(rep["parsed_rate"] - 0.7) < 1e-9, rep["parsed_rate"]
    assert abs(rep["schema_valid_rate"] - 0.3) < 1e-9
    assert abs(rep["exact_match_rate"] - 0.3) < 1e-9
    want = {"category": 0.6, "urgent": 0.5, "amount": 0.5,
            "items": 0.6, "order_id": 0.7}
    for f, v in want.items():
        assert abs(rep["field_accuracy"][f] - v) < 1e-9, (f, rep[
            "field_accuracy"][f], v)


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
