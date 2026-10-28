// Search across every day. The index loads only when someone uses the search box.
(function () {
  const q = document.getElementById("q");
  const box = document.getElementById("results");
  if (!q || !box) return;
  let index = null, loading = null;
  const esc = s => String(s).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  const fmt = d => new Date(d + "T12:00:00Z").toLocaleDateString("en-IN", {timeZone: "UTC", day: "numeric", month: "short", year: "numeric"});

  function load() {
    if (index) return Promise.resolve(index);
    if (!loading) loading = fetch("/data/search.json").then(r => r.json()).then(rows => {
      index = rows.map(r => ({date: r[0], n: r[1], title: r[2], cat: r[3], outlets: r[4], hay: (r[2] + " " + r[3] + " " + r[4] + " " + r[5]).toLowerCase()}));
      return index;
    }).catch(() => { loading = null; return null; });
    return loading;
  }

  async function run() {
    const term = q.value.trim().toLowerCase();
    if (!term) { box.hidden = true; box.innerHTML = ""; return; }
    const rows = await load();
    if (term !== q.value.trim().toLowerCase()) return;
    if (!rows) { box.innerHTML = '<div class="none">Search isn’t available right now. Check your connection and try again.</div>'; box.hidden = false; return; }
    const words = term.split(/\s+/);
    const hits = rows.filter(r => words.every(w => r.hay.includes(w))).slice(0, 40);
    box.innerHTML = hits.length
      ? hits.map(h => `<a href="/${h.date.replace(/-/g, "/")}/#s-${String(h.n).padStart(2, "0")}"><span class="rd">${fmt(h.date)} · ${esc(h.cat)}</span><span class="rt">${esc(h.title)}</span><span class="ro">${esc(h.outlets)}</span></a>`).join("")
      : `<div class="none">No stories match “${esc(q.value.trim())}”. Try one keyword, like an outlet or a place.</div>`;
    box.hidden = false;
  }

  let t;
  q.addEventListener("focus", load, {once: true});
  q.addEventListener("input", () => { clearTimeout(t); t = setTimeout(run, 120); });
  q.addEventListener("keydown", e => { if (e.key === "Escape") { q.value = ""; run(); } });
  document.addEventListener("click", e => { if (!e.target.closest(".search")) box.hidden = true; });
  q.addEventListener("focus", () => { if (q.value.trim()) box.hidden = false; });
})();
