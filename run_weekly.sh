#!/usr/bin/env bash
# Weekly refresh: scrape -> tag -> dashboard. Schedule with cron, e.g.  0 9 * * MON /path/run_weekly.sh
set -e
python scrape.py --apps employee,field,driver_onboarding,workplace
python tag.py            # add --llm for Claude tagging (needs ANTHROPIC_API_KEY)
python dashboard.py --app employee
