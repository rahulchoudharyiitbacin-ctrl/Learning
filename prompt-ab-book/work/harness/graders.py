"""More code graders for run_experiment.py.

Each grader takes (case, output) and returns a score from 0 to 1.
Put the name in the experiment file, e.g.  grader: normalized_match
The case supplies what the grader needs (expected, must_include, ...).
"""
import json
import re


def _clean(text):
    text = text.strip().strip("\"'`*").strip()
    text = re.sub(r"[.!?,;:]+$", "", text)
    return re.sub(r"\s+", " ", text).lower()


def normalized_match(case, output):
    """Like exact match, but ignores case, spaces and end punctuation."""
    return int(_clean(output) == _clean(case["expected"]))


def contains_all(case, output):
    """Every phrase in case['must_include'] appears in the output."""
    low = output.lower()
    return int(all(p.lower() in low for p in case["must_include"]))


def contains_none(case, output):
    """No phrase in case['must_not_include'] appears in the output."""
    low = output.lower()
    return int(not any(p.lower() in low for p in case["must_not_include"]))


def regex_match(case, output):
    """case['pattern'] is found somewhere in the output."""
    return int(re.search(case["pattern"], output) is not None)


def max_words(case, output):
    """Output is no longer than case['max_words'] words."""
    return int(len(output.split()) <= case["max_words"])


def numeric_close(case, output):
    """Output is a number within case['tolerance'] of case['expected']."""
    try:
        value = float(output.strip().replace(",", ""))
    except ValueError:
        return 0
    return int(abs(value - float(case["expected"])) <= case.get("tolerance", 0))


def _same(a, b):
    """Equality that does not confuse True with 1 or False with 0."""
    if isinstance(a, bool) != isinstance(b, bool):
        return False
    return a == b


def parse_json(output):
    """Parse a JSON object, allowing a ```json fence. Returns None if invalid."""
    text = output.strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text)
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def json_all_fields(case, output):
    """Valid JSON object and every expected field has the expected value."""
    data = parse_json(output)
    if data is None:
        return 0
    return int(all(k in data and _same(data[k], v) for k, v in case["expected"].items()))


def json_field_accuracy(case, output):
    """Fraction of expected fields that are right (0 if the JSON is invalid)."""
    data = parse_json(output)
    if data is None:
        return 0
    fields = case["expected"]
    return sum(k in data and _same(data[k], v) for k, v in fields.items()) / len(fields)


EXTRA_GRADERS = {
    "normalized_match": normalized_match,
    "contains_all": contains_all,
    "contains_none": contains_none,
    "regex_match": regex_match,
    "max_words": max_words,
    "numeric_close": numeric_close,
    "json_all_fields": json_all_fields,
    "json_field_accuracy": json_field_accuracy,
}
