"""Drill 4 starter: structured-output validation and field accuracy.

Copy this file to my_drill4.py, fill in the TODOs, then run
    python test_drill4.py my_drill4.py

Read README.md for the full task. Standard library only.
"""
import json
import math
import re
import sys

SCHEMA = {
    "category": {"type": "string",
                 "enum": ["refund", "delivery", "account", "other"]},
    "urgent": {"type": "boolean"},
    "amount": {"type": "number"},
    "items": {"type": "integer"},
    "order_id": {"type": "string", "required": False},
}


def parse_output(text):
    """Return (obj, None) if text holds one JSON object (code fences
    and prose around it are OK), else (None, reason)."""
    # TODO
    raise NotImplementedError


def validate(obj, schema):
    """Return (errors, extra_keys).
    errors: list of strings naming the field (missing, wrong type,
            not in enum). extra_keys: sorted keys not in the schema."""
    # TODO
    raise NotImplementedError


def evaluate(outputs, expected, schema=SCHEMA):
    """outputs: list of raw model texts. expected: list of dicts.
    Return {"n", "parsed_rate", "schema_valid_rate",
    "exact_match_rate", "field_accuracy": {field: rate},
    "cases": [{"index", "parse_error", "errors", "extra_keys",
               "fields": {field: bool}}]}.
    Every rate divides by n, the number of outputs."""
    # TODO
    raise NotImplementedError


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "sample.jsonl"
    with open(path) as fh:
        rows = [json.loads(x) for x in fh if x.strip()]
    rep = evaluate([r["output"] for r in rows],
                   [r["expected"] for r in rows])
    print(json.dumps({k: v for k, v in rep.items() if k != "cases"},
                     indent=2))
