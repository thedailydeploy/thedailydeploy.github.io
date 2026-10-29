# The Daily Deploy — Sources

Public source log for **The Daily Deploy by SAJ** (@dailydeploybysaj): every story's source links, sorted by day.

Live at **https://thedailydeploy.github.io** (linked from the Linktree "Sources" button).

## How it's organised

- `data/YYYY-MM.json` — the source data, one file per month. Edited by hand.
- `data/corrections.json` — updates and corrections, shown on the day they apply to and at `/corrections/`.
- `build.py` — turns the data into the site. A GitHub Action (`.github/workflows/build.yml`) runs it on every push that changes `data/`, `assets/` or `build.py`, and commits the generated pages, so you only edit the data.
- Settings at the top of `build.py`: `GOATCOUNTER` (visitor stats site code) and `BUTTONDOWN` (newsletter username). Leave empty to switch off.
- Generated pages (don't edit by hand):
  - `/` — the last 7 days
  - `/YYYY/MM/DD/` — one page per day, shareable
  - `/YYYY/MM/` — one page per month
  - `/archive/` — years and months
  - `/corrections/` — every update and correction
  - `/og/YYYY-MM-DD.png` — each day's share image
  - `data/search.json`, `feed.xml` (RSS), `sitemap.xml`, `robots.txt`, `404.html`

## Adding a day

1. Open (or create) `data/YYYY-MM.json` for that month and add the day:

```json
{"date": "2026-10-29", "stories": [
  {"title": "Short story headline", "category": "Politics",
   "india": "The slide's 'Why it matters' line",
   "summary": "One line on what happened",
   "angle": true,
   "sources": [{"outlet": "Reuters", "title": "What the article covers", "url": "https://..."}]}
]}
```

`angle: true` marks a story with a genuine India angle (it gets the tag and shows under the "India angle" filter).

2. Commit and push (or upload the file on github.com). The Action rebuilds the site and GitHub Pages publishes within a few minutes. To build locally instead, run `python3 build.py`.

To log a fix, add `{"date": "2026-10-29", "time": "1:40 PM IST", "text": "What changed and why"}` to `data/corrections.json` (`time` is optional).

Stories appear in the order they're listed, which matches the carousel slide order.
