// Kopiuje wybrane zdjęcia (po numerze z arkusza) do czytelnych nazw używanych na stronie.
const fs = require("fs");
const path = require("path");

const PHOTOS = path.join(__dirname, "..", "..", "bajeczne-urwisy", "assets", "photos");
const idx = require("./photo-index.json"); // [{n,file}]
const map = {};
idx.forEach((o) => (map[o.n] = o.file));

// HERO: 1 rząd maltańczyków + 3 rzędy chihuahua (po 5)
const hero = [
  24, 42, 19, 40, 11,      // maltańczyki
  25, 81, 82, 84, 80,      // chihuahua
  64, 70, 54, 53, 35,      // chihuahua
  47, 51, 60, 90, 31,      // chihuahua
];

// GALERIA (mix)
const gallery = [23, 44, 76, 9, 15, 34, 26, 27, 28, 83, 85, 94, 1, 49, 67, 72];

// Pojedyncze sloty
const named = {
  "maltanczyk.jpg": 23,
  "chihuahua.jpg": 82,
  "o-hodowli.jpg": 9,
  "szczeniak-1.jpg": 17,
  "szczeniak-2.jpg": 28,
  "szczeniak-3.jpg": 47,
};

let ok = 0, miss = 0;
function copy(n, target) {
  const src = map[n];
  if (!src) { console.warn("BRAK numeru", n, "->", target); miss++; return; }
  fs.copyFileSync(path.join(PHOTOS, src), path.join(PHOTOS, target));
  ok++;
}

hero.forEach((n, i) => copy(n, `hero-${i + 1}.jpg`));
gallery.forEach((n, i) => copy(n, `g${i + 1}.jpg`));
Object.entries(named).forEach(([target, n]) => copy(n, target));

console.log(`Skopiowano: ${ok}, brakujące: ${miss}`);
