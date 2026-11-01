// Generates missing share images in og/ for every day in data/YYYY-MM.json.
// Uses tools/sharegen.js (the approved design) in headless Chromium, with the fonts
// and logo served from this repo, so it needs no network access.
// Usage: node tools/make_og.mjs                      draw new or changed days
//        node tools/make_og.mjs --force YYYY-MM-DD   redraw a day
//        node tools/make_og.mjs --seed               record existing images as current
import { createRequire } from "node:module";
import fs from "node:fs";
import crypto from "node:crypto";
import path from "node:path";
import { fileURLToPath } from "node:url";

const { chromium } = createRequire(import.meta.url)("playwright");
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const OG = path.join(ROOT, "og");
const FONT_DIR = path.join(ROOT, "assets", "fonts");
const LOCAL = {
  "ArchivoBlack-Regular.ttf": path.join(FONT_DIR, "ArchivoBlack-Regular.ttf"),
  "PermanentMarker-Regular.ttf": path.join(FONT_DIR, "PermanentMarker-Regular.ttf"),
  "IBMPlexSans-Medium.ttf": path.join(FONT_DIR, "IBMPlexSans-Medium.ttf"),
  "IBMPlexSans-Bold.ttf": path.join(FONT_DIR, "IBMPlexSans-Bold.ttf"),
  "IBMPlexMono-Medium.ttf": path.join(FONT_DIR, "IBMPlexMono-Medium.ttf"),
  "logo.png": path.join(ROOT, "assets", "logo.png"),
};

const args = process.argv.slice(2);
const force = new Set(args[0] === "--force" ? args.slice(1) : []);

const days = fs.readdirSync(path.join(ROOT, "data"))
  .filter(f => /^\d{4}-\d{2}\.json$/.test(f))
  .flatMap(f => JSON.parse(fs.readFileSync(path.join(ROOT, "data", f), "utf8")).days);

// og/manifest.json remembers what each day's images were drawn from, so a day is
// redrawn when its stories change (a new headline, more sources) as well as when it is new.
const MANIFEST = path.join(OG, "manifest.json");
const manifest = fs.existsSync(MANIFEST) ? JSON.parse(fs.readFileSync(MANIFEST, "utf8")) : {};
const hash = d => crypto.createHash("sha1").update(JSON.stringify([d.date, d.stories.map(s => [s.title, s.category || "", s.india || "", s.sources.length])])).digest("hex").slice(0, 12);
const seed = args[0] === "--seed";

const missing = days.filter(d => {
  if (force.has(d.date)) return true;
  const names = [`${d.date}.png`, ...d.stories.map((_, i) => `${d.date}-${String(i + 1).padStart(2, "0")}.png`)];
  if (names.some(n => !fs.existsSync(path.join(OG, n)))) return true;
  if (seed && !manifest[d.date]) { manifest[d.date] = hash(d); return false; }
  return manifest[d.date] !== hash(d);
});
const saveManifest = () => fs.writeFileSync(MANIFEST, JSON.stringify(Object.fromEntries(Object.entries(manifest).sort()), null, 1) + "\n");

if (!missing.length) { if (seed) saveManifest(); console.log("Share images: up to date."); process.exit(0); }

fs.mkdirSync(OG, { recursive: true });
const browser = await chromium.launch();
const page = await browser.newPage();
await page.route("https://raw.githubusercontent.com/**", route => {
  const file = LOCAL[route.request().url().split("/").pop()];
  if (!file) return route.abort();
  route.fulfill({ body: fs.readFileSync(file), contentType: file.endsWith(".png") ? "image/png" : "font/ttf", headers: { "access-control-allow-origin": "*" } });
});
await page.setContent("<!doctype html><html><body></body></html>");
await page.addScriptTag({ content: fs.readFileSync(path.join(ROOT, "tools", "sharegen.js"), "utf8") });

let n = 0;
for (const day of missing) {
  const files = await page.evaluate(async d => {
    const out = await window.TDDShare.make(d);
    const b64 = blob => new Promise(r => { const fr = new FileReader(); fr.onload = () => r(fr.result.split(",")[1]); fr.readAsDataURL(blob); });
    return Promise.all(out.map(async o => ({ name: o.name, b64: await b64(o.blob) })));
  }, day);
  for (const f of files) { fs.writeFileSync(path.join(OG, f.name), Buffer.from(f.b64, "base64")); n++; }
  manifest[day.date] = hash(day);
  console.log(`Share images: ${day.date} (${files.length})`);
}
await browser.close();
saveManifest();
console.log(`Share images: wrote ${n}.`);
