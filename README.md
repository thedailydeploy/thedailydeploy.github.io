# The Daily Deploy — Sources

Public source log for **The Daily Deploy by SAJ** (@dailydeploybysaj): every story's source links, sorted by day.

Live at **https://thedailydeploy.github.io** (linked from the Linktree "Sources" button).

## How it's organised

- `data/YYYY-MM.json` — the source data, one file per month. This is the only thing edited by hand.
- `build.py` — turns the data into the site. Run `python3 build.py` after any data change.
- Generated pages (don't edit by hand):
  - `/` — the last 7 days
  - `/YYYY/MM/DD/` — one page per day, shareable
  - `/YYYY/MM/` — one page per month
  - `/archive/` — years and months
  - `data/search.json`, `sitemap.xml`, `robots.txt`, `404.html`

## Adding a day

1. Open (or create) `data/YYYY-MM.json` for that month and add the day:

```json
{"date": "2026-10-29", "stories": [
  {"title": "Short story headline", "category": "Politics",
   "india": "The slide's 'Why it matters' line",
   "sources": [{"outlet": "Reuters", "title": "What the article covers", "url": "https://..."}]}
]}
```

2. Run `python3 build.py`.
3. Commit and push. GitHub Pages publishes within a minute or two.

Stories appear in the order they're listed, which matches the carousel slide order.
