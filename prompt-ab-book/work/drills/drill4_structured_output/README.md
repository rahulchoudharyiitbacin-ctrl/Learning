# Drill 4: structured-output validation and field-level accuracy

**Time budget:** 35 minutes. Start a timer before you read past this line.

## The task

A support-triage prompt asks the model for JSON like this:

```json
{"category": "refund", "urgent": false, "amount": 24.5, "items": 1, "order_id": "A-1001"}
```

The schema (in `starter.py`):

| field | type | rule |
|---|---|---|
| category | string | one of refund, delivery, account, other |
| urgent | boolean | |
| amount | number | int or float |
| items | integer | |
| order_id | string | optional |

Write, in your own copy of `starter.py`:

1. `parse_output(text)` returns `(obj, None)` or `(None, reason)`. Accept a bare JSON object, one inside a code fence (` ```json ` or plain ` ``` `), or one with prose before or after it. Anything else (invalid JSON, a list, a number, empty text) is a parse failure.
2. `validate(obj, schema)` returns `(errors, extra_keys)`. Errors: a required field missing, a wrong type, a value outside the enum. Extra keys are **reported but are not errors**.
3. `evaluate(outputs, expected, schema)` returns a report (see the docstring) with the parse rate, the schema-valid rate, the exact-match rate (every field right), per-field accuracy, and per-case details.

A field is right when the output has it, its value has the right type (and enum), and it equals the expected value. Numbers compare by value (3.0 equals 3). An optional field missing from both output and expected is right.

Sample data: `sample.jsonl`, 10 raw outputs with expected values.

## Things a careful solution handles

- `isinstance(True, int)` is `True` in Python. `True` is not a valid integer here, and `0` is not a valid boolean.
- `0 == False` is `True` in Python. An output of `"urgent": 0` is still wrong.
- **Every rate divides by all outputs.** An output that didn't parse is wrong on every field. Dividing by parsed outputs only flatters a prompt that breaks JSON.
- One bad field doesn't make the other fields wrong.
- `outputs` and `expected` of different lengths: raise `ValueError`.

## Done means

```
python test_drill4.py my_drill4.py
```

prints `14/14 passed`. On the sample you get: parsed 0.70, schema-valid 0.30, all fields right 0.30; category 0.60, urgent 0.50, amount 0.50, items 0.60, order_id 0.70. (These were also counted by hand, row by row.)
