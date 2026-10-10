"""Tag each review with one or more complaint themes.
Default: free keyword rules (works offline). Better: --llm uses Claude (set ANTHROPIC_API_KEY).
Usage: python tag.py [--llm] [--in data/reviews.csv] [--out data/tagged.csv]"""
import argparse, csv, json, os, re

THEMES = {  # key: (label, regex of keywords)
 "tracking_eta": ("Live tracking / ETA wrong", r"gps|track|location|\beta\b|live|map|wrong place|pickup time|pick.?up time"),
 "notifications": ("Late or missing notifications", r"notif|alert|remind|\bsms\b|message not"),
 "no_show": ("Unfair No-Show / penalty", r"no.?show|marked absent|penalt|deduct|salary|charged"),
 "booking": ("Booking / roster bugs", r"book|cancel|roster|shift|schedul|wrong date|slot|reschedul"),
 "ux_changes": ("Confusing UI change / banners", r"\bui\b|redesign|new version|banner|pop.?up|\bsteps?\b|confus|complicat|interface|layout|used to|difficult to use|earlier|previous|recent update|latest update"),
 "driver_contact": ("Cannot reach the driver", r"contact (the )?driver|call (the )?driver|driver.{0,25}(not|no).{0,12}(respon|pick|answer|call)|auto.?reply|chat|phone number|masked"),
 "login_otp": ("Login / OTP / registration", r"login|log in|sign in|\botp\b|register|password|verification|logged out"),
 "app_bugs": ("Crashes, bugs, slow loading", r"crash|\bhang(s|ing|ed)?\b|freez|stuck|\bbug|not working|error|glitch|\bslow|\blag|loading|not opening|force close"),
 "cab_ops": ("Cab late / driver / route", r"running late|always late|very late|comes? late|arrives? late|reach(es|ed)? late|\blate (by|pick|arriv)|delay|driver|cab (did|not)|not come|not arriv|waiting|route|rude|\bac\b|rash"),
 "safety": ("Safety concern", r"safe|\bsos\b|night|women|female|harass|panic"),
 "support": ("No support response", r"support|no response|customer care|helpdesk|ticket|complaint|no reply|unresponsive"),
}
POSITIVE = r"\b(good|great|nice|best|excellent|awesome|easy|useful|helpful)\b"

def keyword_tags(text):
    t = text.lower()
    tags = [k for k, (_, rx) in THEMES.items() if re.search(rx, t)]
    return tags or (["positive_or_other"] if re.search(POSITIVE, t) or not t.strip() else ["other"])

def llm_tags(rows, model):
    import anthropic
    client = anthropic.Anthropic()
    keys = list(THEMES) + ["other"]
    for i in range(0, len(rows), 25):
        chunk = rows[i:i+25]
        prompt = ("Tag each employee-commute app review with 1-3 themes from: " + ", ".join(keys) +
                  ". Themes: " + "; ".join(f"{k}={v[0]}" for k, v in THEMES.items()) +
                  '\nReturn ONLY JSON: {"<id>": ["theme", ...]}.\n\n' +
                  "\n".join(f"{j}: {r['content'][:400]}" for j, r in enumerate(chunk)))
        msg = client.messages.create(model=model, max_tokens=1500, messages=[{"role": "user", "content": prompt}])
        try:
            res = json.loads(re.search(r"\{.*\}", msg.content[0].text, re.S).group())
        except Exception:
            res = {}
        for j, r in enumerate(chunk):
            r["themes"] = "|".join(t for t in res.get(str(j), []) if t in keys) or "|".join(keyword_tags(r["content"]))
        print(f"tagged {min(i+25, len(rows))}/{len(rows)}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--llm", action="store_true"); ap.add_argument("--model", default="claude-haiku-5-5")
    ap.add_argument("--in", dest="inp", default="data/reviews.csv"); ap.add_argument("--out", default="data/tagged.csv")
    a = ap.parse_args()
    rows = list(csv.DictReader(open(a.inp, encoding="utf-8")))
    if a.llm: llm_tags(rows, a.model)
    else:
        for r in rows: r["themes"] = "|".join(keyword_tags(r["content"]))
    with open(a.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    low = [r for r in rows if int(r["score"]) <= 2]
    untagged = sum(1 for r in low if r["themes"] == "other")
    print(f"{len(rows)} reviews tagged -> {a.out}")
    print(f"1-2 star reviews with no theme (check these by hand): {untagged}/{len(low)}")

if __name__ == "__main__": main()
