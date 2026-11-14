# cues.py
import csv, json
from collections import defaultdict

acc = defaultdict(lambda: defaultdict(list))
for row in csv.DictReader(open("eval_results.csv")):
    cues = json.loads(row["cues"])
    for k, v in cues.items():
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            acc[row["label"]][k].append(v)
for label, d in acc.items():
    print(label, {k: round(sum(v) / len(v), 3) for k, v in d.items()})
