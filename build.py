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
import json, re, shutil, calendar, os
from datetime import date
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SITE = "https://thedailydeploy.github.io"
HOME_DAYS = 7
# Visitor stats: your GoatCounter site code ("dailydeploy" -> https://dailydeploy.goatcounter.com). Empty = no tracking.
GOATCOUNTER = ""
# Daily email: your Buttondown username. Empty = the subscribe box offers RSS and Instagram only.
BUTTONDOWN = ""
# Fonts for the per-day share images (the GitHub Action downloads them; no fonts = shared default image).
FONT_DIR = Path(os.environ.get("TDD_FONT_DIR", ROOT / ".fonts"))
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


def page(title, desc, path, body, search=True, chips=None, og=None, filt=False):
    canon = SITE + path
    og = og or "/assets/og-image.png"
    bar = ""
    if search or chips:
        parts = []
        if search:
            parts.append('<div class="search"><input id="q" type="search" placeholder="Search every story, outlet or topic" aria-label="Search all sources" autocomplete="off"><div class="results" id="results" hidden></div></div>')
        if chips:
            parts.append(f'<nav class="dates" aria-label="Recent days">{chips}</nav>')
        if filt:
            parts.append('<div class="filter" role="group" aria-label="Filter stories"><span>Show</span><button type="button" class="fbtn on" data-f="all" aria-pressed="true">All stories</button><button type="button" class="fbtn" data-f="india" aria-pressed="false">India angle</button></div>')
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
<link rel="alternate" type="application/rss+xml" title="The Daily Deploy · Sources" href="/feed.xml">
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
<div class="wrap"><footer><span>Sources are added each morning when the day's carousel goes live at <b>8:30 AM IST</b>.</span><span><a href="/">Latest</a> · <a href="/archive/">Archive</a> · <a href="/corrections/">Corrections</a> · <a href="/feed.xml">RSS</a> · <a href="https://www.instagram.com/dailydeploybysaj/">@dailydeploybysaj</a></span>{'<span class="priv">Visitor counts are anonymous: no cookies, no tracking across sites.</span>' if GOATCOUNTER else ''}</footer></div>
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
{'<script src="/assets/search.js" defer></script>' if search else ''}
{FILTER_JS if filt else ''}
{f'<script data-goatcounter="https://{GOATCOUNTER}.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>' if GOATCOUNTER else ''}
</body>
</html>
"""


FILTER_JS = """<script>
(function(){var bs=[].slice.call(document.querySelectorAll(".fbtn"));if(!bs.length)return;
function set(f){bs.forEach(function(b){var on=b.getAttribute("data-f")===f;b.classList.toggle("on",on);b.setAttribute("aria-pressed",on?"true":"false")});
document.querySelectorAll(".story").forEach(function(s){s.hidden=f==="india"&&!s.hasAttribute("data-angle")});
document.querySelectorAll(".day").forEach(function(d){var n=d.querySelectorAll(".story:not([hidden])").length,c=d.querySelector(".fcount");if(c)c.textContent=f==="india"?n+" with an India angle":""});
try{localStorage.setItem("tdd_f",f)}catch(e){}}
bs.forEach(function(b){b.addEventListener("click",function(){set(b.getAttribute("data-f"))})});
try{if(localStorage.getItem("tdd_f")==="india")set("india")}catch(e){}})();
</script>"""


def fixes_html(fixes, iso):
    items = [f for f in fixes if f["date"] == iso]
    if not items:
        return ""
    lis = "".join(f'<li><b>{e(short_date(f["date"]))}{", " + e(f["time"]) if f.get("time") else ""}:</b> {e(f["text"])}</li>' for f in items)
    return f'<aside class="fix" aria-label="Updates and corrections"><h3>Updates &amp; corrections</h3><ul>{lis}</ul><a href="/corrections/">All corrections →</a></aside>'


def render_day(day, link_heading=True, fixes=()):
    n_src = count_sources(day)
    n_st = len(day["stories"])
    head = e(long_date(day["date"]))
    if link_heading:
        head = f'<a href="{dpath(day["date"])}">{head}</a>'
    out = [f'<section class="day" id="d-{day["date"]}" data-date="{day["date"]}">',
           f'<div class="dayhead"><h2>{head}</h2><span>{n_st} {"story" if n_st == 1 else "stories"} · {n_src} sources<b class="fcount"></b></span></div>',
           fixes_html(fixes, day["date"])]
    for i, s in enumerate(day["stories"], 1):
        cat = f'<span class="cat">{e(s.get("category"))}</span>' if s.get("category") else ""
        why = f'<p class="why"><b>Why it matters:</b> {e(s["india"])}</p>' if s.get("india") else ""
        summ = f'<p class="sum">{e(s["summary"])}</p>' if s.get("summary") else ""
        ang = s.get("angle")
        tag = '<span class="angle">India angle</span>' if ang else ""
        links = "".join(
            f'<li><a href="{e(x["url"])}" target="_blank" rel="noopener" data-goatcounter-click="src/{day["date"]}/{i:02d}/{e(x["outlet"])}" data-goatcounter-title="{e(s["title"])} · {e(x["outlet"])}"><span class="o">{e(x["outlet"])}</span><span class="t">{e(x.get("title") or x["url"])}</span><span class="arr" aria-hidden="true">↗</span></a></li>'
            for x in s["sources"])
        out.append(f'<article class="story" id="s-{i:02d}"{" data-angle" if ang else ""}><div class="top"><span class="num">STORY {i:02d}</span>{cat}{tag}</div><h3>{e(s["title"])}</h3>{summ}{why}<ul class="srcs">{links}</ul></article>')
    out.append("</section>")
    return "".join(out)


def chips_html(recent, current=None):
    c = "".join(f'<a class="chip{" on" if d["date"] == current else ""}"{" aria-current=\"page\"" if d["date"] == current else ""} data-d="{d["date"]}" href="{dpath(d["date"])}">{short_date(d["date"])}</a>' for d in recent)
    return c + '<a class="chip arch" href="/archive/">Archive</a>'


def subscribe_html():
    if BUTTONDOWN:
        form = (f'<form action="https://buttondown.com/api/emails/embed-subscribe/{e(BUTTONDOWN)}" method="post" target="_blank" class="subf">'
                '<label for="bd-email">Email</label><div><input type="email" name="email" id="bd-email" placeholder="you@example.com" required>'
                '<button type="submit">Subscribe</button></div></form>')
        lead = "The world in the last 24 hours, with every source, in your inbox each morning. No algorithm in the way."
    else:
        form = '<p class="subl"><a href="https://www.instagram.com/dailydeploybysaj/">Follow @dailydeploybysaj</a> for the carousel every morning at 8:30 AM IST.</p>'
        lead = "Get every day's sources without waiting for the algorithm."
    return f'<section class="sub" aria-label="Subscribe"><h2>Get it every morning</h2><p>{lead}</p>{form}<a class="rss" href="/feed.xml">Follow the RSS feed →</a></section>'


def share_image(d):
    """Render og/YYYY-MM-DD.png (1200x630). Returns its site path, or None when fonts or Pillow are missing."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return None
    fd = FONT_DIR
    need = {"d": fd / "Anton-Regular.ttf", "m": fd / "PermanentMarker-Regular.ttf", "b": fd / "IBMPlexSans-Bold.ttf", "r": fd / "IBMPlexSans-Medium.ttf"}
    if not all(p.exists() for p in need.values()):
        return None
    F = lambda k, s: ImageFont.truetype(str(need[k]), s)
    W, H = 1200, 630
    ink, cream, lime, muted, paper = (11, 11, 11), (241, 234, 216), (200, 255, 46), (172, 167, 150), (241, 234, 216)
    im = Image.new("RGB", (W, H), ink)
    dr = ImageDraw.Draw(im)
    logo = ROOT / "assets" / "logo.png"
    x0 = 64
    if logo.exists():
        L = Image.open(logo).convert("RGBA")
        L = L.resize((84, int(84 * L.height / L.width)))
        im.paste(L, (x0, 52), L)
    dr.text((x0 + 100, 62), "THE DAILY DEPLOY", font=F("d", 34), fill=cream)
    dr.text((x0 + 100 + dr.textlength("THE DAILY DEPLOY ", font=F("d", 34)), 70), "by SAJ", font=F("m", 22), fill=lime)
    dd = date.fromisoformat(d["date"])
    label = f"SOURCES · {dd.strftime('%a').upper()} {dd.day} {MONTHS[dd.month-1][:3].upper()} {dd.year}"
    lw = dr.textlength(label, font=F("b", 20))
    dr.rectangle((x0, 160, x0 + lw + 28, 196), fill=lime)
    dr.text((x0 + 14, 165), label, font=F("b", 20), fill=ink)
    y = 222
    for t, c in (("WHAT HAPPENED", cream), ("IN THE LAST", cream), ("24 HOURS?", lime)):
        dr.text((x0, y), t, font=F("d", 76), fill=c)
        y += 92
    dr.text((x0, 548), f"{len(d['stories'])} stories · {count_sources(d)} sources · thedailydeploy.github.io", font=F("r", 22), fill=muted)
    cx, cy, cw = 700, 120, 436
    for k, s in enumerate(d["stories"][:3]):
        title = s["title"]
        f = F("d", 30)
        words, lines, cur = title.split(), [], ""
        for w in words:
            tt = (cur + " " + w).strip()
            if dr.textlength(tt, font=f) > cw - 36 and cur:
                lines.append(cur); cur = w
            else:
                cur = tt
        lines.append(cur)
        lines = lines[:2]
        h = 46 + 36 * len(lines)
        dr.rectangle((cx, cy, cx + cw, cy + h), fill=paper)
        dr.text((cx + 18, cy + 12), f"STORY {k+1:02d} · {(s.get('category') or '').upper()}", font=F("b", 15), fill=ink)
        for j, ln in enumerate(lines):
            dr.text((cx + 18, cy + 36 + 36 * j), ln, font=f, fill=ink)
        cy += h + 18
    if len(d["stories"]) > 3:
        dr.text((cx, cy + 4), f"+ {len(d['stories']) - 3} more stories", font=F("m", 26), fill=lime)
    dr.rectangle((0, H - 8, W, H), fill=lime)
    out = ROOT / "og" / f"{d['date']}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    im.save(out, optimize=True)
    return f"/og/{d['date']}.png"


def feed_xml(days):
    from email.utils import format_datetime
    from datetime import datetime, timezone, timedelta
    items = []
    for d in days[:30]:
        dt = datetime.fromisoformat(d["date"] + "T08:30:00").replace(tzinfo=timezone(timedelta(hours=5, minutes=30)))
        desc = "".join(f"<p><b>{e(s['title'])}</b>{' — ' + e(s['summary']) if s.get('summary') else ''}</p>" for s in d["stories"])
        items.append(f"<item><title>{e(long_date(d['date']))}: {len(d['stories'])} stories</title><link>{SITE}{dpath(d['date'])}</link>"
                     f"<guid>{SITE}{dpath(d['date'])}</guid><pubDate>{format_datetime(dt)}</pubDate><description>{e(desc)}</description></item>")
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel><title>The Daily Deploy · Sources</title>'
            f'<link>{SITE}/</link><description>Every source behind every post from The Daily Deploy by SAJ.</description><language>en-in</language>'
            + "".join(items) + "</channel></rss>\n")


def write(rel, html):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(html, encoding="utf-8")


def main():
    days = load_days()
    recent = days[:HOME_DAYS]
    fp = ROOT / "data" / "corrections.json"
    fixes = json.loads(fp.read_text(encoding="utf-8")) if fp.exists() else []

    # clear previously generated folders
    for p in ROOT.iterdir():
        if p.is_dir() and (re.fullmatch(r"\d{4}", p.name) or p.name in ("archive", "corrections", "og")):
            shutil.rmtree(p)

    urls = ["/", "/archive/", "/corrections/"]
    ogs = {d["date"]: share_image(d) for d in days}

    # home
    if days:
        body = "".join(render_day(d, fixes=fixes) for d in recent)
        if len(days) > HOME_DAYS:
            body += '<a class="more" href="/archive/">Older days are in the archive →</a>'
        home_chips = "".join(f'<a class="chip" data-d="{d["date"]}" href="#d-{d["date"]}">{short_date(d["date"])}</a>' for d in recent) + '<a class="chip arch" href="/archive/">Archive</a>'
    else:
        body = '<section class="empty-state"><h2>No sources yet</h2><p>Each day\'s stories and their source links appear here after the carousel is posted at 8:30 AM IST.</p></section>'
        home_chips = '<a class="chip arch" href="/archive/">Archive</a>'
    if days:
        body += subscribe_html()
    write("index.html", page("Daily Deploy Sources", "Every source behind every post from The Daily Deploy by SAJ, sorted by day and story.", "/", body, chips=home_chips,
                             og=ogs.get(days[0]["date"]) if days else None, filt=True))

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
                   crumb + render_day(d, link_heading=False, fixes=fixes) + subscribe_html() + pager, chips=chips_html(recent, d["date"]),
                   og=ogs.get(d["date"]), filt=True))
        urls.append(dpath(d["date"]))

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

    # corrections
    if fixes:
        lis = "".join(f'<li><a href="{dpath(f["date"])}"><b>{e(long_date(f["date"]))}{", " + e(f["time"]) if f.get("time") else ""}</b><span>{e(f["text"])}</span></a></li>'
                      for f in sorted(fixes, key=lambda f: f["date"], reverse=True))
        cbody = f'<h2 class="ptitle">Updates &amp; corrections</h2><p class="psub">When we fix or update a story after it is posted, it is logged here.</p><ul class="fixlist">{lis}</ul>'
    else:
        cbody = '<h2 class="ptitle">Updates &amp; corrections</h2><section class="empty-state"><h2>Nothing to correct yet</h2><p>When we fix or update a story after it is posted, it is logged here.</p></section>'
    write("corrections/index.html", page("Updates & corrections · The Daily Deploy", "Every fix and update to a Daily Deploy story after it was posted.", "/corrections/", cbody, chips=chips_html(recent)))

    write("feed.xml", feed_xml(days))

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
