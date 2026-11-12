"""Write the sample records.jsonl for Drill 2 (seeded, reproducible).

80 cases x 2 variants x 3 runs. B fixes some cases and breaks a few.
Two API errors (grade null) and one case with no B runs at all.
"""
import json
import random

rng = random.Random(7)
rows = []
for i in range(80):
    cid = f"case-{i:03d}"
    p_a = rng.uniform(0.2, 0.9)
    u = rng.random()
    p_b = min(1, p_a + 0.4) if u < 0.3 else max(0, p_a - 0.4) if u < 0.4 else p_a
    for variant, p in (("A", p_a), ("B", p_b)):
        if cid == "case-042" and variant == "B":
            continue
        for run in range(3):
            g = int(rng.random() < p)
            rows.append({"case_id": cid, "variant": variant,
                         "run": run, "grade": g})
rows[5]["grade"] = None
rows[100]["grade"] = None
rng.shuffle(rows)                      # finish order, not case order
with open("records.jsonl", "w") as f:
    for r in rows:
        f.write(json.dumps(r) + "\n")
print(len(rows), "rows")
