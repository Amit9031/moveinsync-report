"""Makes data/check_sample.csv: 50 random 1-2 star reviews for a hand accuracy check of the theme tags."""
import csv, random
rows = [r for r in csv.DictReader(open("data/tagged.csv", encoding="utf-8")) if int(r["score"]) <= 2]
random.seed(1)
sample = random.sample(rows, min(50, len(rows)))
with open("data/check_sample.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["content", "themes", "correct (type 1 or 0)"])
    for r in sample:
        w.writerow([r["content"], r["themes"], ""])
print(f"wrote data/check_sample.csv with {len(sample)} reviews")
