"""Generate SYNTHETIC reviews so you can test the pipeline without scraping. Not real data."""
import csv, os, random
from datetime import datetime, timedelta
random.seed(7); os.makedirs("data", exist_ok=True); open("data/SYNTHETIC", "w").write("demo")
BAD = ["GPS shows driver at wrong location, ETA never correct", "Notifications come late, missed my cab", "Marked no show even though I booked, salary deduction",
       "Booking created for wrong date", "App crashes on login, OTP not coming", "Cab always late and driver rude", "Support gives no response to my complaint", "Feels unsafe at night, SOS slow"]
GOOD = ["Good app, easy to book", "Very useful and helpful", "Great service", "Nice app"]
rows, now = [], datetime(2026, 10, 1)
for i in range(1500):
    d = now - timedelta(days=random.randint(0, 200)); ver = "9.%d.0" % (9 - (now - d).days // 40)
    bad = random.random() < 0.32
    rows.append({"app": "employee", "reviewId": f"s{i}", "at": d.isoformat(), "score": random.choice([1, 1, 2, 2, 3]) if bad else random.choice([4, 5, 5, 5]),
                 "thumbsUp": random.randint(0, 12), "version": ver, "content": random.choice(BAD) if bad else random.choice(GOOD),
                 "reply": "Sorry, please write to us." if random.random() < 0.15 else "", "repliedAt": ""})
with open("data/reviews.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, list(rows[0])); w.writeheader(); w.writerows(rows)
print("synthetic data written")
