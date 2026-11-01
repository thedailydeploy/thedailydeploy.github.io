// The Daily Deploy — share-image generator (1200x630). Runs in a browser page (github.com or the site).
// TDDShare.make(dayObj) -> [{name:"2026-10-29.png", blob}, {name:"2026-10-29-01.png", blob}, ...]
window.TDDShare = (function () {
  const RAW = "https://raw.githubusercontent.com/";
  const FONTS = [
    ["TDDDisplay", "google/fonts/main/ofl/archivoblack/ArchivoBlack-Regular.ttf"],
    ["TDDMarker", "google/fonts/main/apache/permanentmarker/PermanentMarker-Regular.ttf"],
    ["TDDSans", "IBM/plex/master/packages/plex-sans/fonts/complete/ttf/IBMPlexSans-Medium.ttf"],
    ["TDDSansB", "IBM/plex/master/packages/plex-sans/fonts/complete/ttf/IBMPlexSans-Bold.ttf"],
    ["TDDMono", "IBM/plex/master/packages/plex-mono/fonts/complete/ttf/IBMPlexMono-Medium.ttf"]
  ];
  const C = { ink: "#0b0b0b", paper: "#f1ead8", pink: "#151513", lime: "#c8ff2e", muted: "#aca796", line: "#3e3c35" };
  const MON = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"];
  const DAYS = ["SUNDAY","MONDAY","TUESDAY","WEDNESDAY","THURSDAY","FRIDAY","SATURDAY"];
  let ready = null, logo = null;
  async function init() {
    if (ready) return ready;
    ready = (async () => {
      for (const [fam, path] of FONTS) {
        const buf = await fetch(RAW + path).then(r => { if (!r.ok) throw new Error("font " + path); return r.arrayBuffer(); });
        const f = new FontFace(fam, buf); await f.load(); document.fonts.add(f);
      }
      const lb = await fetch(RAW + "thedailydeploy/thedailydeploy.github.io/main/assets/logo.png").then(r => r.blob());
      logo = await createImageBitmap(lb);
    })();
    return ready;
  }
  function wrap(ctx, text, maxW) {
    const words = text.split(/\s+/), lines = []; let cur = "";
    for (const w of words) { const t = cur ? cur + " " + w : w; if (ctx.measureText(t).width > maxW && cur) { lines.push(cur); cur = w; } else cur = t; }
    if (cur) lines.push(cur); return lines;
  }
  function torn(ctx, x, y, w, h) {
    const T = [[0,6],[4,0],[11,5],[19,1],[28,6],[37,0],[46,4],[55,0],[64,5],[73,1],[82,6],[91,0],[100,5]];
    const B = [[100,-4],[93,0],[84,-5],[75,0],[66,-4],[57,0],[48,-6],[39,0],[30,-3],[21,0],[12,-5],[3,0],[0,-3]];
    ctx.beginPath(); T.forEach(([px, dy], i) => { const X = x + w * px / 100, Y = y + dy * 2; i ? ctx.lineTo(X, Y) : ctx.moveTo(X, Y); });
    B.forEach(([px, dy]) => ctx.lineTo(x + w * px / 100, y + h + dy * 2)); ctx.closePath();
  }
  function brand(ctx, iso) {
    ctx.fillStyle = C.ink; ctx.fillRect(0, 0, 1200, 630);
    const lw = 76, lh = lw * logo.height / logo.width; ctx.drawImage(logo, 60, 40, lw, lh);
    ctx.fillStyle = C.paper; ctx.font = "30px TDDDisplay"; ctx.textBaseline = "alphabetic";
    ctx.fillText("THE DAILY DEPLOY", 152, 86);
    const tw = ctx.measureText("THE DAILY DEPLOY ").width;
    ctx.fillStyle = C.lime; ctx.font = "20px TDDMarker"; ctx.fillText("by SAJ", 152 + tw, 86);
    const d = new Date(iso + "T12:00:00Z");
    ctx.fillStyle = C.muted; ctx.font = "20px TDDMono"; ctx.textAlign = "right";
    ctx.fillText(`${DAYS[d.getUTCDay()]} · ${d.getUTCDate()} ${MON[d.getUTCMonth()]} ${d.getUTCFullYear()}`, 1140, 82);
    ctx.textAlign = "left";
    ctx.fillStyle = C.lime; ctx.fillRect(0, 620, 1200, 10);
  }
  function fit(ctx, text, fam, maxW, maxLines, big, small) {
    for (let s = big; s >= small; s -= 2) { ctx.font = `${s}px ${fam}`; const l = wrap(ctx, text, maxW); if (l.length <= maxLines) return [s, l]; }
    ctx.font = `${small}px ${fam}`; const l = wrap(ctx, text, maxW); return [small, l.slice(0, maxLines)];
  }
  function storyCard(day, i, s, n) {
    const cv = document.createElement("canvas"); cv.width = 1200; cv.height = 630; const ctx = cv.getContext("2d");
    brand(ctx, day.date);
    const x = 60, y = 128, w = 1080, h = 420;
    ctx.save(); ctx.shadowColor = "rgba(0,0,0,.6)"; ctx.shadowBlur = 24; ctx.shadowOffsetY = 8; torn(ctx, x, y, w, h); ctx.fillStyle = C.paper; ctx.fill(); ctx.restore();
    const px = x + 44; let py = y + 62;
    ctx.fillStyle = C.pink; ctx.font = "22px TDDMono"; const num = `STORY ${String(i).padStart(2, "0")} OF ${n}`; ctx.fillText(num, px, py);
    if (s.category) {
      const nx = px + ctx.measureText(num).width + 22; ctx.font = "24px TDDMarker"; const cw = ctx.measureText(s.category).width + 24;
      ctx.save(); ctx.translate(nx, py - 26); ctx.rotate(-0.025); ctx.fillStyle = C.ink; ctx.fillRect(0, 0, cw, 36); ctx.fillStyle = C.lime; ctx.fillText(s.category, 12, 27); ctx.restore();
    }
    py += 28;
    const [hs, hl] = fit(ctx, s.title, "TDDDisplay", w - 88, 3, 60, 38);
    ctx.fillStyle = C.pink; ctx.font = `${hs}px TDDDisplay`;
    hl.forEach((l, k) => ctx.fillText(l, px, py + hs * 1.0 + k * hs * 1.12));
    py += hs * 1.0 + (hl.length - 1) * hs * 1.12 + 24;
    if (s.india) {
      ctx.fillStyle = "rgba(21,21,19,.25)"; ctx.fillRect(px, py, 140, 3); py += 40;
      ctx.font = "26px TDDSansB"; const lab = "Why it matters: "; const lw2 = ctx.measureText(lab).width;
      ctx.font = "26px TDDSans"; let lines = wrap(ctx, lab + s.india, w - 88).slice(0, 3);
      const room = Math.floor((y + h - 30 - py) / 36) + 1; lines = lines.slice(0, Math.max(1, room));
      lines.forEach((l, k) => {
        if (k === 0) { ctx.font = "26px TDDSansB"; ctx.fillStyle = C.pink; ctx.fillText(lab, px, py); ctx.font = "26px TDDSans"; ctx.fillStyle = "#2b2a27"; ctx.fillText(l.slice(lab.length), px + lw2, py); }
        else { ctx.fillStyle = "#2b2a27"; ctx.fillText(l, px, py + k * 36); }
      });
    }
    ctx.fillStyle = C.paper; ctx.font = "20px TDDMono"; ctx.fillText("EVERY SOURCE BEHIND THIS STORY →", 60, 594);
    ctx.fillStyle = C.lime; ctx.textAlign = "right"; ctx.fillText("thedailydeploy.github.io", 1140, 594); ctx.textAlign = "left";
    return cv;
  }
  function dayCard(day) {
    const cv = document.createElement("canvas"); cv.width = 1200; cv.height = 630; const ctx = cv.getContext("2d");
    brand(ctx, day.date);
    ctx.fillStyle = C.paper; ctx.font = "52px TDDDisplay";
    ["WHAT HAPPENED", "IN THE LAST"].forEach((t, k) => ctx.fillText(t, 60, 220 + k * 66));
    ctx.fillStyle = C.lime; ctx.fillText("24 HOURS?", 60, 352);
    const src = day.stories.reduce((a, s) => a + s.sources.length, 0);
    ctx.fillStyle = C.muted; ctx.font = "22px TDDMono"; ctx.fillText(`${day.stories.length} STORIES · ${src} SOURCES`, 60, 420);
    ctx.fillStyle = C.paper; ctx.font = "20px TDDMono"; ctx.fillText("EVERY SOURCE, STORY BY STORY →", 60, 594);
    ctx.fillStyle = C.lime; ctx.textAlign = "right"; ctx.fillText("thedailydeploy.github.io", 1140, 594); ctx.textAlign = "left";
    let cy = 128; const cx = 660, cw = 480;
    day.stories.slice(0, 3).forEach((s, k) => {
      ctx.font = "28px TDDDisplay"; const lines = wrap(ctx, s.title, cw - 40).slice(0, 2); const hh = 52 + lines.length * 34;
      ctx.save(); ctx.translate(cx + cw / 2, cy + hh / 2); ctx.rotate([-0.012, 0.01, -0.008][k]); ctx.translate(-cw / 2, -hh / 2);
      ctx.shadowColor = "rgba(0,0,0,.5)"; ctx.shadowBlur = 14; ctx.shadowOffsetY = 5; ctx.fillStyle = C.paper; ctx.fillRect(0, 0, cw, hh); ctx.shadowColor = "transparent";
      ctx.fillStyle = C.pink; ctx.font = "16px TDDMono"; ctx.fillText(`STORY ${String(k + 1).padStart(2, "0")} · ${(s.category || "").toUpperCase()}`, 20, 30);
      ctx.font = "28px TDDDisplay"; lines.forEach((l, j) => ctx.fillText(l, 20, 66 + j * 34)); ctx.restore();
      cy += hh + 18;
    });
    if (day.stories.length > 3) { ctx.fillStyle = C.lime; ctx.font = "26px TDDMarker"; ctx.fillText(`+ ${day.stories.length - 3} more stories`, cx, cy + 22); }
    return cv;
  }
  const toBlob = cv => new Promise(r => cv.toBlob(r, "image/png"));
  async function make(day) {
    await init();
    const out = [{ name: `${day.date}.png`, blob: await toBlob(dayCard(day)) }];
    for (let i = 0; i < day.stories.length; i++)
      out.push({ name: `${day.date}-${String(i + 1).padStart(2, "0")}.png`, blob: await toBlob(storyCard(day, i + 1, day.stories[i], day.stories.length)) });
    return out;
  }
  return { init, make, storyCard, dayCard };
})();
