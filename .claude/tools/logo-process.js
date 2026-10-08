// Usuwanie białego tła z logotypów (flood-fill od krawędzi) + autocrop.
// Wymaga: jimp@0.22
const Jimp = require("jimp");
const path = require("path");

const ASSETS = path.join(__dirname, "..", "..", "bajeczne-urwisy", "assets");
const A = (f) => path.join(ASSETS, f);

async function process(inFile, outFile, opts = {}) {
  const { threshold = 236, recolor = null, autocrop = true } = opts;
  const img = await Jimp.read(A(inFile));
  const w = img.bitmap.width, h = img.bitmap.height, d = img.bitmap.data;

  const isWhite = (idx) =>
    d[idx] >= threshold && d[idx + 1] >= threshold && d[idx + 2] >= threshold;

  // Flood-fill białego tła zaczynając od krawędzi (zachowuje białe WEWNĄTRZ logo)
  const visited = new Uint8Array(w * h);
  const stack = [];
  const tryPush = (x, y) => {
    if (x < 0 || y < 0 || x >= w || y >= h) return;
    const p = y * w + x;
    if (visited[p]) return;
    visited[p] = 1;
    const idx = p * 4;
    if (!isWhite(idx)) return;
    d[idx + 3] = 0;       // przezroczystość
    stack.push(p);
  };
  for (let x = 0; x < w; x++) { tryPush(x, 0); tryPush(x, h - 1); }
  for (let y = 0; y < h; y++) { tryPush(0, y); tryPush(w - 1, y); }
  while (stack.length) {
    const p = stack.pop();
    const x = p % w, y = (p - x) / w;
    tryPush(x + 1, y); tryPush(x - 1, y); tryPush(x, y + 1); tryPush(x, y - 1);
  }

  // Zmiękczenie półprzezroczystych krawędzi (anty-aliasing białych pikseli)
  img.scan(0, 0, w, h, (x, y, idx) => {
    if (d[idx + 3] !== 0 && isWhite(idx)) {
      const near = (d[idx] + d[idx + 1] + d[idx + 2]) / 3;
      if (near >= threshold - 8) d[idx + 3] = Math.max(0, d[idx + 3] - 120);
    }
  });

  if (recolor) {
    img.scan(0, 0, w, h, (x, y, idx) => {
      if (d[idx + 3] > 24) { d[idx] = recolor[0]; d[idx + 1] = recolor[1]; d[idx + 2] = recolor[2]; }
    });
  }

  if (autocrop) {
    try { img.autocrop({ tolerance: 0.002, cropOnlyFrames: false }); } catch (e) {}
  }

  await img.writeAsync(A(outFile));
  console.log("OK ->", outFile, img.bitmap.width + "x" + img.bitmap.height);
}

(async () => {
  const MAIN = "354776148_653068083362503_1002884658195686127_n.png";
  await process(MAIN, "logo.png", { threshold: 234 });
  await process(MAIN, "logo-white.png", { threshold: 234, recolor: [251, 247, 241] });
  await process("logo_swkipr.jpg", "logo-swkipr.png", { threshold: 226 });
  await process("logo_ppk.png", "logo-ppk.png", { threshold: 240 });
  await process("logo_wku.gif", "logo-wku.png", { threshold: 242 });
  console.log("Gotowe.");
})().catch((e) => { console.error(e); process.exitCode = 1; });
