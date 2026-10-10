# MoveInSync Play Store ratings: analysis and weekly dashboard

Answers "How are our Play Store ratings?" on demand: collects public reviews, groups complaints into themes, and shows what to fix first.

**Result (10 Oct 2026):** the employee app's listing rating is 4.64 from 114,843 ratings, but the 1,538 reviews from the last 180 days average 3.82, and 28% are 1-2 star. Only 1% of 1-2 star reviews received a reply. The complaints cluster around trip reliability (tracking, ETA, late cabs, notifications), app quality (crashes, slowness, login) and booking clarity (booking bugs, confusing UI changes). The full ranked recommendation is in the memo submitted with this project.

## Run it
```bash
python3 -m venv venv && source venv/bin/activate    # macOS/Linux
pip install -r requirements.txt
python scrape.py --max 20000       # reviews + dated rating snapshot -> data/
python tag.py                      # keyword themes (offline, free)
python dashboard.py                # writes dashboard.html
open dashboard.html
```
Optional, more accurate tagging with Claude: `export ANTHROPIC_API_KEY=...` then `python tag.py --llm`.
Try it without scraping: `python make_sample.py && python tag.py && python dashboard.py` (synthetic demo data, flagged on the page).
Weekly refresh for all four MoveInSync apps: `./run_weekly.sh`.

## Files
| File | Job |
|---|---|
| scrape.py | Pulls reviews, merges new ones into data/reviews.csv, logs the rating each run. Reviewer names are not stored. |
| tag.py | Labels each review with complaint themes (keyword rules or Claude). Prints how many low-star reviews matched no theme. |
| dashboard.py | Builds a single-file dashboard: rating trend, top complaint themes with estimated rating lift, most helpful complaints, rating by app version, reply rate. |
| run_weekly.sh | One command for the weekly refresh. |
| make_sample.py | Generates synthetic demo data. Not real. |
| make_memo_pdf.py | Optional helper that turns a Markdown memo into a PDF. |

## Method notes and limits
- The listing rating is a lifetime average; the dashboard also reports the recent-review average, which reacts faster to releases. Written reviews skew negative, so the two are not directly comparable.
- "Estimated lift" assumes every 1-2 star review with that theme became 4 stars. It ranks fixes, is not a forecast, and the lifts overlap.
- Keyword tagging is a baseline and was corrected after sample quotes showed false matches. Check a hand-labelled sample before trusting the counts.
- Reviews are public Play Store data. Only English reviews from India are fetched by default; change `lang` and `country` in scrape.py to widen this.
