// Tworzy arkusze kontaktowe (montaż miniatur) z numerami, do szybkiego przeglądu.
const Jimp = require("jimp");
const fs = require("fs");
const path = require("path");

const PHOTOS = path.join(__dirname, "..", "..", "bajeczne-urwisy", "assets", "photos");
const OUT = path.join(__dirname, "sheets");
fs.mkdirSync(OUT, { recursive: true });

const THUMB = 168, PAD = 8, COLS = 6, ROWS = 8, PERSHEET = COLS * ROWS;
const CELL = THUMB + PAD;

(async () => {
  let files = fs.readdirSync(PHOTOS)
    .filter((f) => /\.(jpe?g)$/i.test(f))
    .sort();

  // mapowanie indeks -> plik
  const index = files.map((f, i) => ({ n: i + 1, file: f }));
  fs.writeFileSync(path.join(__dirname, "photo-index.json"), JSON.stringify(index, null, 2));
  console.log("Zdjęć:", files.length);

  const font = await Jimp.loadFont(Jimp.FONT_SANS_32_WHITE);

  let sheetNo = 0;
  for (let start = 0; start < files.length; start += PERSHEET) {
    sheetNo++;
    const chunk = files.slice(start, start + PERSHEET);
    const rows = Math.ceil(chunk.length / COLS);
    const sheet = new Jimp(COLS * CELL + PAD, rows * CELL + PAD, 0xf3ece0ff);

    for (let i = 0; i < chunk.length; i++) {
      const col = i % COLS, row = Math.floor(i / COLS);
      const x = PAD + col * CELL, y = PAD + row * CELL;
      try {
        const img = await Jimp.read(path.join(PHOTOS, chunk[i]));
        img.cover(THUMB, THUMB);
        sheet.composite(img, x, y);
      } catch (e) {
        // pomiń uszkodzone
      }
      // numer w ciemnym prostokącie
      const label = new Jimp(54, 36, 0x000000cc);
      sheet.composite(label, x, y);
      sheet.print(font, x + 6, y - 1, String(start + i + 1));
    }
    const outPath = path.join(OUT, `sheet-${sheetNo}.png`);
    await sheet.writeAsync(outPath);
    console.log("OK ->", outPath, sheet.bitmap.width + "x" + sheet.bitmap.height, "(" + chunk.length + " zdjęć)");
  }
  console.log("Gotowe. Arkuszy:", sheetNo);
})().catch((e) => { console.error(e); process.exitCode = 1; });
