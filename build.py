#!/usr/bin/env python3
"""Build the Daily Deploy sources site from data/YYYY-MM.json.

Each month file looks like:
  {"month": "2026-10", "days": [
     {"date": "2026-10-28", "stories": [
        {"title": "...", "category": "...", "india": "why it matters line",
         "sources": [{"outlet": "...", "title": "...", "url": "https://..."}]}]}]}

Run `python3 build.py` after editing any month file. It regenerates:
  index.html            last 7 days
  YYYY/MM/DD/index.html one page per day (shareable link)
  YYYY/MM/index.html    one page per month
  archive/index.html    years and months
  data/search.json      search index (loaded only when someone searches)
  sitemap.xml, robots.txt, 404.html
"""
import json, re, shutil, calendar
from datetime import date
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SITE = "https://thedailydeploy.github.io"
HOME_DAYS = 7
MONTHS = ["January","February","March","April","May","June","July","August","September","October","November","December"]


def e(s):
    return escape(str(s or ""), quote=True)


def load_days():
    days = []
    for f in sorted((ROOT / "data").glob("[0-9][0-9][0-9][0-9]-[0-9][0-9].json")):
        month = json.loads(f.read_text(encoding="utf-8"))
        for d in month["days"]:
            date.fromisoformat(d["date"])  # validates the date
            if d["date"][:7] != f.stem:
                raise SystemExit(f"{d['date']} is in the wrong file ({f.name})")
            days.append(d)
    days.sort(key=lambda d: d["date"], reverse=True)
    seen = set()
    for d in days:
        if d["date"] in seen:
            raise SystemExit(f"Duplicate day {d['date']}")
        seen.add(d["date"])
    return days


def dpath(iso):
    return "/" + iso.replace("-", "/") + "/"


def long_date(iso):
    d = date.fromisoformat(iso)
    return f"{d.strftime('%A')}, {d.day} {MONTHS[d.month-1]} {d.year}"


def short_date(iso):
    d = date.fromisoformat(iso)
    return f"{d.day} {MONTHS[d.month-1][:3]}"


def count_sources(day):
    return sum(len(s["sources"]) for s in day["stories"])


def og_for(p):
    """Use a share image only if it has been added to og/."""
    return p if (ROOT / p.lstrip("/")).exists() else "/assets/og-image.png"


def page(title, desc, path, body, search=True, chips=None, og="/assets/og-image.png"):
    canon = SITE + path
    bar = ""
    if search or chips:
        parts = []
        if search:
            parts.append('<div class="search"><input id="q" type="search" placeholder="Search every story, outlet or topic" aria-label="Search all sources" autocomplete="off"><div class="results" id="results" hidden></div></div>')
        if chips:
            parts.append(f'<nav class="dates" aria-label="Recent days">{chips}</nav>')
        bar = f'<div class="bar"><div class="wrap">{"".join(parts)}</div></div>'
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="The Daily Deploy by SAJ">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{canon}">
<meta name="theme-color" content="#0b0b0b">
<meta property="og:image" content="{SITE}{og}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32.png">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo+Black&family=Permanent+Marker&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="/assets/style.css">
</head>
<body>
<div class="wrap"><a class="mast" href="/"><img class="mark" src="/assets/logo.png" width="64" height="55" alt="The Daily Deploy logo"><div><h1>THE DAILY DEPLOY <small>by SAJ</small></h1><p>Every source behind every post, sorted by day and story.</p></div></a></div>
{bar}
<main class="wrap">
{body}
</main>
<div class="wrap"><footer><span>Sources are added each morning when the day's carousel goes live at <b>8:30 AM IST</b>.</span><span><a href="/">Latest</a> · <a href="/archive/">Archive</a> · <a href="https://www.instagram.com/dailydeploybysaj/">@dailydeploybysaj</a></span></footer></div>
<script>
(function(){{var t=new Date(Date.now()+19800000).toISOString().slice(0,10);document.querySelectorAll("[data-date='"+t+"'] .dayhead h2").forEach(function(h){{var s=document.createElement("span");s.className="today";s.textContent="today";h.appendChild(s)}});document.querySelectorAll(".chip[data-d='"+t+"']").forEach(function(c){{c.textContent="Today"}})}})();
(function(){{var chips=[].slice.call(document.querySelectorAll('.chip[href^="#d-"]'));if(!chips.length)return;
function mark(d){{chips.forEach(function(c){{var on=c.getAttribute("data-d")===d;c.classList.toggle("on",on);if(on)c.setAttribute("aria-current","true");else c.removeAttribute("aria-current")}})}}
function fromHash(){{var h=location.hash.slice(3);mark(h&&document.getElementById("d-"+h)?h:chips[0].getAttribute("data-d"))}}
chips.forEach(function(c){{c.addEventListener("click",function(){{mark(c.getAttribute("data-d"))}})}});
addEventListener("hashchange",fromHash);fromHash();
var lock=0;chips.forEach(function(c){{c.addEventListener("click",function(){{lock=Date.now()}})}});
if("IntersectionObserver"in window){{var io=new IntersectionObserver(function(es){{if(Date.now()-lock<900)return;es.forEach(function(x){{if(x.isIntersecting)mark(x.target.getAttribute("data-date"))}})}},{{rootMargin:"-45% 0px -50% 0px"}});document.querySelectorAll(".day[data-date]").forEach(function(d){{io.observe(d)}})}}}})();
</script>
{'<script src="/assets/search.js" defer></script>' if search else ''}{'<script src="/assets/share.js" defer></script>' if 'data-share' in body else ''}
</body>
</html>
"""


SHARE_ICON = '<svg aria-hidden="true" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12v7a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-7"/><path d="M12 3v13"/><path d="m7 8 5-5 5 5"/></svg>'


def render_day(day, link_heading=True):
    n_src = count_sources(day)
    n_st = len(day["stories"])
    head = e(long_date(day["date"]))
    if link_heading:
        head = f'<a href="{dpath(day["date"])}">{head}</a>'
    out = [f'<section class="day" id="d-{day["date"]}" data-date="{day["date"]}">',
           f'<div class="dayhead"><h2>{head}</h2><span>{n_st} {"story" if n_st == 1 else "stories"} · {n_src} sources</span><button type="button" class="share" data-share data-url="{SITE}{dpath(day["date"])}" data-title="{e("The Daily Deploy · " + long_date(day["date"]))}">{SHARE_ICON}Share day</button></div>']
    for i, s in enumerate(day["stories"], 1):
        out.append(story_html(day, i, s))
    out.append("</section>")
    return "".join(out)


def story_html(day, i, s):
        cat = f'<span class="cat">{e(s.get("category"))}</span>' if s.get("category") else ""
        why = f'<p class="why"><b>Why it matters:</b> {e(s["india"])}</p>' if s.get("india") else ""
        links = "".join(
            f'<li><a href="{e(x["url"])}" target="_blank" rel="noopener"><span class="o">{e(x["outlet"])}</span><span class="t">{e(x.get("title") or x["url"])}</span><span class="arr" aria-hidden="true">↗</span></a></li>'
            for x in s["sources"])
        return f'<article class="story" id="s-{i:02d}"><div class="top"><span class="num">STORY {i:02d}</span>{cat}<button type="button" class="share" data-share data-url="{SITE}{dpath(day["date"])}{i:02d}/" data-title="{e(s["title"])}">{SHARE_ICON}Share</button></div><h3>{e(s["title"])}</h3>{why}<ul class="srcs">{links}</ul></article>'


def chips_html(recent, current=None):
    c = "".join(f'<a class="chip{" on" if d["date"] == current else ""}"{" aria-current=\"page\"" if d["date"] == current else ""} data-d="{d["date"]}" href="{dpath(d["date"])}">{short_date(d["date"])}</a>' for d in recent)
    return c + '<a class="chip arch" href="/archive/">Archive</a>'


def write(rel, html):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(html, encoding="utf-8")


def main():
    days = load_days()
    recent = days[:HOME_DAYS]

    # clear previously generated folders
    for p in ROOT.iterdir():
        if p.is_dir() and (re.fullmatch(r"\d{4}", p.name) or p.name == "archive"):
            shutil.rmtree(p)

    urls = ["/", "/archive/"]

    # home
    if days:
        body = "".join(render_day(d) for d in recent)
        if len(days) > HOME_DAYS:
            body += '<a class="more" href="/archive/">Older days are in the archive →</a>'
        home_chips = "".join(f'<a class="chip" data-d="{d["date"]}" href="#d-{d["date"]}">{short_date(d["date"])}</a>' for d in recent) + '<a class="chip arch" href="/archive/">Archive</a>'
    else:
        body = '<section class="empty-state"><h2>No sources yet</h2><p>Each day\'s stories and their source links appear here after the carousel is posted at 8:30 AM IST.</p></section>'
        home_chips = '<a class="chip arch" href="/archive/">Archive</a>'
    write("index.html", page("Daily Deploy Sources", "Every source behind every post from The Daily Deploy by SAJ, sorted by day and story.", "/", body, chips=home_chips,
                             og=og_for(f'/og/{days[0]["date"]}.png') if days else "/assets/og-image.png"))

    # day pages
    for i, d in enumerate(days):
        newer = days[i - 1] if i > 0 else None
        older = days[i + 1] if i + 1 < len(days) else None
        pager = '<nav class="pager" aria-label="Other days">'
        pager += f'<a href="{dpath(older["date"])}">← {short_date(older["date"])}</a>' if older else "<span></span>"
        pager += f'<a href="{dpath(newer["date"])}">{short_date(newer["date"])} →</a>' if newer else '<a href="/">Latest</a>'
        pager += "</nav>"
        y, m, _ = d["date"].split("-")
        crumb = f'<p class="psub"><a href="/archive/">Archive</a> / <a href="/{y}/{m}/">{MONTHS[int(m)-1]} {y}</a></p>'
        titles = "; ".join(s["title"] for s in d["stories"][:4])
        write(f'{d["date"].replace("-", "/")}/index.html',
              page(f'Sources · {long_date(d["date"])} · The Daily Deploy', f'Sources for The Daily Deploy, {long_date(d["date"])}: {titles}.', dpath(d["date"]),
                   crumb + render_day(d, link_heading=False) + pager, chips=chips_html(recent, d["date"]), og=og_for(f'/og/{d["date"]}.png')))
        urls.append(dpath(d["date"]))

        # one page per story, so a shared story link previews that story
        dp, n = dpath(d["date"]), len(d["stories"])
        for k, s in enumerate(d["stories"], 1):
            prev_s = f'<a href="{dp}{k-1:02d}/">← Story {k-1:02d}</a>' if k > 1 else f'<a href="{dp}">← All stories</a>'
            next_s = f'<a href="{dp}{k+1:02d}/">Story {k+1:02d} →</a>' if k < n else f'<a href="{dp}">All stories →</a>'
            sbody = (f'<p class="psub"><a href="/archive/">Archive</a> / <a href="/{y}/{m}/">{MONTHS[int(m)-1]} {y}</a> / <a href="{dp}">{e(long_date(d["date"]))}</a></p>'
                     f'<section class="day" data-date="{d["date"]}">{story_html(d, k, s)}'
                     f'<a class="more" href="{dp}">See all {n} stories from {e(short_date(d["date"]))} →</a></section>'
                     f'<nav class="pager" aria-label="Other stories">{prev_s}{next_s}</nav>')
            desc = s.get("india") or f'Story {k:02d} from The Daily Deploy, {long_date(d["date"])}.'
            write(f'{d["date"].replace("-", "/")}/{k:02d}/index.html',
                  page(f'{s["title"]} · The Daily Deploy', desc, f"{dp}{k:02d}/", sbody, chips=chips_html(recent, d["date"]), og=og_for(f'/og/{d["date"]}-{k:02d}.png')))
            urls.append(f"{dp}{k:02d}/")

    # month pages
    by_month = {}
    for d in days:
        by_month.setdefault(d["date"][:7], []).append(d)
    for ym, mdays in by_month.items():
        y, m = ym.split("-")
        items = "".join(f'<li><a href="{dpath(d["date"])}"><b>{e(long_date(d["date"]).rsplit(" ", 1)[0])}</b><span>{len(d["stories"])} stories · {count_sources(d)} sources</span></a></li>' for d in mdays)
        body = f'<p class="psub"><a href="/archive/">Archive</a> / {y}</p><h2 class="ptitle">{MONTHS[int(m)-1]} {y}</h2><p class="psub">{len(mdays)} days · {sum(len(d["stories"]) for d in mdays)} stories</p><ul class="daylist">{items}</ul>'
        write(f"{y}/{m}/index.html", page(f"Sources · {MONTHS[int(m)-1]} {y} · The Daily Deploy", f"Every Daily Deploy story and source from {MONTHS[int(m)-1]} {y}.", f"/{y}/{m}/", body, chips=chips_html(recent)))
        urls.append(f"/{y}/{m}/")

    # archive
    years = sorted({ym[:4] for ym in by_month}, reverse=True)
    blocks = []
    for y in years:
        cells = []
        for mi in range(12, 0, -1):
            ym = f"{y}-{mi:02d}"
            if ym in by_month:
                md = by_month[ym]
                cells.append(f'<a class="mon" href="/{y}/{mi:02d}/"><b>{MONTHS[mi-1]}</b><span>{len(md)} days</span></a>')
        blocks.append(f'<section class="year"><h2>{y}</h2><div class="months">{"".join(cells)}</div></section>')
    total_days = len(days)
    body = f'<h2 class="ptitle">Archive</h2><p class="psub">{total_days} days · {sum(len(d["stories"]) for d in days)} stories · {sum(count_sources(d) for d in days)} sources</p>' + ("".join(blocks) or '<section class="empty-state"><h2>Nothing archived yet</h2><p>Past days will appear here, grouped by year and month.</p></section>')
    write("archive/index.html", page("Sources Archive · The Daily Deploy", "Browse every Daily Deploy source by year and month.", "/archive/", body, chips=chips_html(recent)))

    # 404
    write("404.html", page("Page not found · The Daily Deploy", "This page doesn't exist.", "/404.html",
          '<section class="empty-state"><h2>Page not found</h2><p>That day or page doesn\'t exist. Go to the <a href="/">latest sources</a> or browse the <a href="/archive/">archive</a>.</p></section>', chips=chips_html(recent)))

    # search index: [date, story number, title, category, outlets, extra text]
    rows = []
    for d in days:
        for i, s in enumerate(d["stories"], 1):
            outlets = " · ".join(dict.fromkeys(x["outlet"] for x in s["sources"]))
            extra = " ".join([s.get("india", "")] + [x.get("title", "") for x in s["sources"]])
            rows.append([d["date"], i, s["title"], s.get("category", ""), outlets, extra])
    write("data/search.json", json.dumps(rows, ensure_ascii=False, separators=(",", ":")))

    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"<url><loc>{SITE}{u}</loc></url>\n" for u in urls) + "</urlset>\n")
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
    write(".nojekyll", "")
    print(f"Built {len(days)} days, {len(by_month)} months, {len(rows)} stories.")


if __name__ == "__main__":
    main()
