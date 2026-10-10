"""Build a self-contained dashboard.html from data/tagged.csv (+ data/ratings_log.csv).
Usage: python dashboard.py [--app employee] [--days 180]"""
import argparse, csv, html, os
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from tag import THEMES

def avg(xs): return sum(xs) / len(xs) if xs else 0.0

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--app", default="employee"); ap.add_argument("--days", type=int, default=180)
    ap.add_argument("--out", default="dashboard.html")
    a = ap.parse_args()
    rows = [r for r in csv.DictReader(open("data/tagged.csv", encoding="utf-8")) if r["app"] == a.app]
    for r in rows: r["score"] = int(r["score"]); r["dt"] = datetime.fromisoformat(r["at"]); r["th"] = [t for t in r["themes"].split("|") if t]
    latest = max(r["dt"] for r in rows)
    recent = [r for r in rows if r["dt"] >= latest - timedelta(days=a.days)]
    low = [r for r in recent if r["score"] <= 2]
    synthetic = os.path.exists("data/SYNTHETIC")

    snap = None
    if os.path.exists("data/ratings_log.csv"):
        s = [x for x in csv.DictReader(open("data/ratings_log.csv")) if x["app"] == a.app]
        snap = s[-1] if s else None

    # monthly trend
    m = defaultdict(list)
    for r in recent: m[r["dt"].strftime("%Y-%m")].append(r["score"])
    months = sorted(m); pts = [avg(m[k]) for k in months]
    W, H, P = 640, 200, 30
    xy = [(P + i * (W - 2 * P) / max(1, len(pts) - 1), H - P - (v - 1) / 4 * (H - 2 * P)) for i, v in enumerate(pts)]
    line = " ".join(f"{x:.1f},{y:.1f}" for x, y in xy)
    labels = "".join(f'<text x="{x:.1f}" y="{H-8}" text-anchor="middle">{months[i][2:]}</text>' for i, (x, _) in enumerate(xy) if i % max(1, len(xy)//8) == 0)
    dots = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3"><title>{months[i]}: {pts[i]:.2f} ({len(m[months[i]])} reviews)</title></circle>' for i, (x, y) in enumerate(xy))
    grid = "".join(f'<line x1="{P}" x2="{W-P}" y1="{H-P-(g-1)/4*(H-2*P):.1f}" y2="{H-P-(g-1)/4*(H-2*P):.1f}"/><text x="4" y="{H-P-(g-1)/4*(H-2*P)+4:.1f}">{g}</text>' for g in (1, 2, 3, 4, 5))

    # themes among 1-2 star reviews, with simulated lift if those reviews were 4 stars
    base = avg([r["score"] for r in recent])
    trows = []
    for k, (label, _) in THEMES.items():
        hit = [r for r in low if k in r["th"]]
        fixed = avg([4 if (r["score"] <= 2 and k in r["th"]) else r["score"] for r in recent])
        trows.append((k, label, len(hit), fixed - base, sorted(hit, key=lambda r: -int(r["thumbsUp"] or 0))[:2]))
    trows.sort(key=lambda t: -t[2]); top = max([t[2] for t in trows] + [1])
    bars = "".join(f'<div class="row"><span class="lab">{html.escape(l)}</span><span class="bar"><i style="width:{n/top*100:.0f}%"></i></span><b>{n}</b><em>+{lift:.3f}</em></div>' for _, l, n, lift, _ in trows)
    quotes = "".join(f'<h3>{html.escape(l)}</h3>' + "".join(f'<blockquote>{html.escape(r["content"][:280])}<small>{r["score"]}★ · v{html.escape(r["version"] or "?")} · {r["dt"]:%d %b %Y} · {r["thumbsUp"]} found helpful</small></blockquote>' for r in ex) for _, l, n, _, ex in trows[:4] if ex)

    # versions
    v = defaultdict(list)
    for r in recent: v[r["version"] or "unknown"].append(r)
    vers = sorted([(k, x) for k, x in v.items() if len(x) >= 20], key=lambda kv: max(r["dt"] for r in kv[1]), reverse=True)[:8]
    vtab = "".join(f'<tr><td>{html.escape(k)}</td><td>{len(x)}</td><td>{avg([r["score"] for r in x]):.2f}</td><td>{sum(r["score"]<=2 for r in x)/len(x)*100:.0f}%</td></tr>' for k, x in vers)

    unanswered = sum(1 for r in low if not r["reply"])
    reply_rate = 100 * (1 - unanswered / len(low)) if low else 100
    dist = Counter(r["score"] for r in recent)
    banner = '<p class="warn">Demo data: these reviews are synthetic and only show how the dashboard works. Run scrape.py for real numbers.</p>' if synthetic else ""
    snap_html = f'<div><b>{float(snap["score"]):.2f}</b><span>Play Store rating on {snap["date"]}<br>{int(snap["ratings"]):,} ratings</span></div>' if snap else ""

    page = f"""<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>MoveInSync Play Store ratings</title><style>
:root{{--ink:#17252e;--mute:#5d6b73;--bg:#f7f8f6;--line:#d9ded9;--acc:#0b6e6e;--bad:#b3392f}}
@media(prefers-color-scheme:dark){{:root{{--ink:#e8ecea;--mute:#9aa7ad;--bg:#12191d;--line:#2a363c;--acc:#4fc3bd;--bad:#ef8a7e}}}}
body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}}
main{{max-width:760px;margin:0 auto;padding:28px 18px 60px}}h1{{font-size:26px;margin:0 0 4px}}h2{{font-size:18px;margin:36px 0 8px}}h3{{font-size:15px;margin:18px 0 4px}}
.sub,small,.hint{{color:var(--mute)}}.sub{{margin:0 0 18px}}.hint{{font-size:14px;margin:0 0 10px}}
.kpis{{display:flex;flex-wrap:wrap;gap:12px 28px;border-top:1px solid var(--line);border-bottom:1px solid var(--line);padding:14px 0}}
.kpis div{{min-width:130px}}.kpis b{{display:block;font-size:30px;line-height:1.1}}.kpis span{{font-size:13px;color:var(--mute)}}
svg{{width:100%;height:auto}}svg line{{stroke:var(--line)}}svg text{{fill:var(--mute);font-size:10px}}svg polyline{{fill:none;stroke:var(--acc);stroke-width:2.5}}svg circle{{fill:var(--acc)}}
.row{{display:grid;grid-template-columns:190px 1fr 40px 62px;gap:8px;align-items:center;margin:6px 0;font-size:14px}}.bar{{background:var(--line);height:10px;border-radius:2px}}.bar i{{display:block;height:100%;background:var(--bad);border-radius:2px}}.row b{{text-align:right}}.row em{{color:var(--acc);font-style:normal;text-align:right}}
blockquote{{margin:6px 0;padding-left:12px;border-left:3px solid var(--line)}}blockquote small{{display:block}}
table{{border-collapse:collapse;width:100%;font-size:14px}}td,th{{padding:6px 8px;border-bottom:1px solid var(--line);text-align:left}}
.warn{{background:#fff3cd;color:#5c4400;padding:8px 12px;border-radius:4px}}@media(max-width:560px){{.row{{grid-template-columns:1fr 70px 34px 54px}}.lab{{grid-column:1/-1}}}}
</style><main>
<h1>How are our Play Store ratings?</h1><p class="sub">App: {html.escape(a.app)} · {len(recent):,} reviews in the last {a.days} days · latest review {latest:%d %b %Y}</p>{banner}
<div class="kpis">{snap_html}<div><b>{base:.2f}</b><span>Average of recent reviews</span></div><div><b>{len(low)/len(recent)*100:.0f}%</b><span>1-2★ reviews ({len(low)})</span></div><div><b>{reply_rate:.0f}%</b><span>1-2★ reviews with a reply</span></div></div>
<h2>Average rating by month</h2><svg viewBox="0 0 {W} {H}" role="img" aria-label="Monthly average rating">{grid}<polyline points="{line}"/>{dots}{labels}</svg>
<h2>What 1-2★ reviews complain about</h2><p class="hint">Count of low-star reviews mentioning each theme; the right column estimates how much the average would rise if those reviews became 4★. A review can have several themes, so the lifts overlap.</p>{bars}
<h2>Most helpful complaints</h2>{quotes}
<h2>Rating by app version</h2><p class="hint">Versions with at least 20 reviews. A version with a sudden dip points to a release regression.</p><table><tr><th>Version</th><th>Reviews</th><th>Avg ★</th><th>1-2★</th></tr>{vtab}</table>
<h2>Star distribution</h2><p>{" · ".join(f"{s}★ {dist.get(s,0)}" for s in (5,4,3,2,1))}</p>
</main></html>"""
    open(a.out, "w", encoding="utf-8").write(page)
    print(f"wrote {a.out}")

if __name__ == "__main__": main()
