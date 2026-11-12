"""Drill 4 reference solution: structured-output validation and
field-level accuracy.

    python solution.py sample.jsonl
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

FENCE = re.compile(r"```[a-zA-Z]*\s*\n?(.*?)```", re.DOTALL)


def parse_output(text):
    """Return (obj, None) or (None, error). Tolerates a code fence
    and prose around one JSON object."""
    if not isinstance(text, str) or not text.strip():
        return None, "empty output"
    m = FENCE.search(text)
    body = (m.group(1) if m else text).strip()
    try:
        obj = json.loads(body)
    except json.JSONDecodeError:
        i, j = body.find("{"), body.rfind("}")
        if i < 0 or j <= i:
            return None, "invalid JSON"
        try:
            obj = json.loads(body[i:j + 1])
        except json.JSONDecodeError:
            return None, "invalid JSON"
    if not isinstance(obj, dict):
        return None, f"JSON is a {type(obj).__name__}, not an object"
    return obj, None


def type_ok(value, kind):
    """bool is a subclass of int in Python: rule it out explicitly."""
    if kind == "string":
        return isinstance(value, str)
    if kind == "boolean":
        return isinstance(value, bool)
    if isinstance(value, bool):
        return False
    if kind == "integer":
        return isinstance(value, int)
    if kind == "number":
        return isinstance(value, (int, float)) and math.isfinite(value)
    raise ValueError(f"unknown type {kind!r}")


def field_ok(value, spec):
    """Is one present value valid for its field spec?"""
    if not type_ok(value, spec["type"]):
        return False
    return "enum" not in spec or value in spec["enum"]


def validate(obj, schema):
    """Return (errors, extra_keys). Extra keys are not errors."""
    errors = []
    for name, spec in schema.items():
        if name not in obj:
            if spec.get("required", True):
                errors.append(f"missing: {name}")
        elif not type_ok(obj[name], spec["type"]):
            errors.append(f"type: {name} should be {spec['type']}")
        elif "enum" in spec and obj[name] not in spec["enum"]:
            errors.append(f"enum: {name}={obj[name]!r}")
    extra = sorted(k for k in obj if k not in schema)
    return errors, extra


def same(got, want, spec):
    """Right value AND valid type: 0 must not equal False."""
    if not field_ok(got, spec):
        return False
    if spec["type"] == "number":
        return abs(got - want) <= 1e-6
    return type(got) is type(want) and got == want


def evaluate(outputs, expected, schema=SCHEMA):
    """Field-level accuracy over ALL outputs (unparseable ones count
    as wrong on every field)."""
    if len(outputs) != len(expected):
        raise ValueError("outputs and expected differ in length")
    n = len(outputs)
    right = {f: 0 for f in schema}
    parsed = valid = exact = 0
    cases = []
    for i, (text, exp) in enumerate(zip(outputs, expected)):
        obj, perr = parse_output(text)
        errors, extra, fields = [], [], {}
        if obj is not None:
            parsed += 1
            errors, extra = validate(obj, schema)
            valid += not errors
        for f, spec in schema.items():
            if obj is None:
                ok = False
            elif f not in exp:
                ok = f not in obj      # absent on both sides
            else:
                ok = f in obj and same(obj[f], exp[f], spec)
            fields[f] = ok
            right[f] += ok
        exact += all(fields.values())
        cases.append({"index": i, "parse_error": perr, "errors": errors,
                      "extra_keys": extra, "fields": fields})
    rate = (lambda k: k / n) if n else (lambda k: None)
    return {"n": n, "parsed_rate": rate(parsed),
            "schema_valid_rate": rate(valid),
            "exact_match_rate": rate(exact),
            "field_accuracy": {f: rate(k) for f, k in right.items()},
            "cases": cases}


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "sample.jsonl"
    with open(path) as fh:
        rows = [json.loads(x) for x in fh if x.strip()]
    rep = evaluate([r["output"] for r in rows],
                   [r["expected"] for r in rows])
    print(f"n={rep['n']}  parsed {rep['parsed_rate']:.2f}  "
          f"schema-valid {rep['schema_valid_rate']:.2f}  "
          f"all fields right {rep['exact_match_rate']:.2f}")
    for f, acc in rep["field_accuracy"].items():
        print(f"  {f:<9} {acc:.2f}")
    for c in rep["cases"]:
        if c["parse_error"] or c["errors"] or c["extra_keys"]:
            print(f"  #{c['index']}: {c['parse_error'] or ''} "
                  f"{c['errors']} extra={c['extra_keys']}")
