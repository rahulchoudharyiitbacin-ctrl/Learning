"""Run:  python test_graders.py   (plain asserts, no extra libraries)"""
from graders import (contains_all, contains_none, json_all_fields,
                     json_field_accuracy, max_words, normalized_match,
                     numeric_close, regex_match)

# normalized_match fixes the 'Refund.' vs 'refund' grader bug from Chapter 5
assert normalized_match({"expected": "refund"}, "Refund.") == 1
assert normalized_match({"expected": "refund"}, '  "refund"\n') == 1
assert normalized_match({"expected": "refund"}, "Label: refund") == 0
assert normalized_match({"expected": "refund"}, "delivery") == 0

assert contains_all({"must_include": ["order id", "refund"]}, "Your Refund for ORDER ID 12 is on its way") == 1
assert contains_all({"must_include": ["order id", "refund"]}, "Your refund is on its way") == 0
assert contains_none({"must_not_include": ["guarantee"]}, "We will look into it") == 1
assert contains_none({"must_not_include": ["guarantee"]}, "We GUARANTEE a refund") == 0

assert regex_match({"pattern": r"\b\d{4}-\d{2}-\d{2}\b"}, "Due on 2026-11-13.") == 1
assert regex_match({"pattern": r"\b\d{4}-\d{2}-\d{2}\b"}, "Due next Friday") == 0
assert max_words({"max_words": 5}, "one two three four five") == 1
assert max_words({"max_words": 5}, "one two three four five six") == 0

assert numeric_close({"expected": 42, "tolerance": 0.5}, "42.3") == 1
assert numeric_close({"expected": 42, "tolerance": 0.5}, "1,042") == 0
assert numeric_close({"expected": 42, "tolerance": 0.5}, "about 42") == 0   # not a bare number

case = {"expected": {"name": "Asha", "city": "Pune"}}
assert json_all_fields(case, '{"name": "Asha", "city": "Pune"}') == 1
assert json_all_fields(case, '```json\n{"name": "Asha", "city": "Pune"}\n```') == 1
assert json_all_fields(case, '{"name": "Asha", "city": "Delhi"}') == 0
assert json_all_fields(case, 'Here is the JSON: {"name": "Asha"}') == 0      # prose around JSON
assert json_all_fields(case, "[1, 2]") == 0                                  # not an object
assert json_field_accuracy(case, '{"name": "Asha", "city": "Delhi"}') == 0.5
assert json_field_accuracy(case, "not json") == 0

# Python trap: True == 1 and False == 0. A grader must not accept them as equal.
assert json_all_fields({"expected": {"n": 1}}, '{"n": true}') == 0
assert json_all_fields({"expected": {"ok": False}}, '{"ok": 0}') == 0
assert json_all_fields({"expected": {"ok": True}}, '{"ok": true}') == 1
assert json_all_fields({"expected": {"n": 1}}, '{"n": 1}') == 1
assert json_all_fields({"expected": {"n": 1.0}}, '{"n": 1}') == 1        # int vs float is fine
assert json_field_accuracy({"expected": {"a": 1, "ok": False}}, '{"a": 1, "ok": 0}') == 0.5
assert json_all_fields({"expected": {"x": None}}, '{}') == 0               # missing key is not None

print("all grader tests passed")
