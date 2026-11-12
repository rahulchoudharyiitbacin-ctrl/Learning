"""Write the sample labels.csv for Drill 3 (seeded).

Table (failure = positive): TP 12, FN 8, FP 6, TN 74, the same
illustrative numbers as Chapter 8, plus 3 rows the judge did not
label (blank, ERROR, N/A). Labels have mixed case and spaces, and
the file starts with a BOM, as Excel writes it.
"""
import csv
import random

rng = random.Random(3)
rows = ([("FAIL", "FAIL")] * 12 + [("FAIL", "PASS")] * 8
        + [("PASS", "FAIL")] * 6 + [("PASS", "PASS")] * 74
        + [("PASS", ""), ("FAIL", "ERROR"), ("PASS", "N/A")])
rng.shuffle(rows)
messy = {"PASS": ["PASS", "pass", " Pass"], "FAIL": ["FAIL", "fail ", "Fail"]}
with open("labels.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["id", "human_label", "judge_label"])
    for i, (h, j) in enumerate(rows):
        w.writerow([f"ex-{i:03d}", rng.choice(messy[h]),
                    rng.choice(messy[j]) if j in messy else j])
print(len(rows), "rows")
