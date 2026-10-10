"""Collect public Play Store reviews + a dated rating snapshot.
Usage: python scrape.py [--max 20000] [--apps employee,field]
Output: data/reviews.csv (merged, de-duplicated), data/ratings_log.csv (one row per app per run).
Reviewer names are NOT stored (privacy)."""
import argparse, csv, os, time
from datetime import date
from google_play_scraper import app as gp_app, reviews, Sort

APPS = {"employee": "com.moveinsync.ets", "field": "field.moveinsync.ets",
        "driver_onboarding": "com.moveinsync.driver.dco", "workplace": "com.workinsync.meeting"}
FIELDS = ["app", "reviewId", "at", "score", "thumbsUp", "version", "content", "reply", "repliedAt"]

def fetch(pkg, limit):
    out, token = [], None
    while len(out) < limit:
        batch, token = reviews(pkg, lang="en", country="in", sort=Sort.NEWEST, count=200, continuation_token=token)
        out += batch
        if not token or not batch: break
        time.sleep(1)  # be polite
    return out[:limit]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max", type=int, default=20000)
    ap.add_argument("--apps", default="employee")
    a = ap.parse_args()
    os.makedirs("data", exist_ok=True)
    path = "data/reviews.csv"
    seen = {}
    if os.path.exists(path):
        for r in csv.DictReader(open(path, encoding="utf-8")): seen[r["reviewId"]] = r
    snap_new = not os.path.exists("data/ratings_log.csv")
    with open("data/ratings_log.csv", "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if snap_new: w.writerow(["date", "app", "score", "ratings", "histogram_1_to_5"])
        for name in a.apps.split(","):
            pkg = APPS[name]
            info = gp_app(pkg, lang="en", country="in")
            w.writerow([date.today().isoformat(), name, info["score"], info["ratings"], info["histogram"]])
            print(f"{name}: rating {info['score']:.2f} from {info['ratings']} ratings")
            for r in fetch(pkg, a.max):
                seen[r["reviewId"]] = {"app": name, "reviewId": r["reviewId"], "at": r["at"].isoformat(),
                    "score": r["score"], "thumbsUp": r["thumbsUpCount"], "version": r["reviewCreatedVersion"] or "",
                    "content": (r["content"] or "").replace("\n", " "), "reply": r["replyContent"] or "",
                    "repliedAt": r["repliedAt"].isoformat() if r["repliedAt"] else ""}
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, FIELDS); w.writeheader(); w.writerows(seen.values())
    print(f"{len(seen)} reviews saved to {path}")

if __name__ == "__main__": main()
