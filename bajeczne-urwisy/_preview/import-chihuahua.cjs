const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const source = 'C:/Users/Admin/Desktop/nowy miot';
const photos = JSON.parse(fs.readFileSync(path.join(__dirname, 'chihuahua-import.json'), 'utf8'));
const destination = path.join(root, 'assets/photos/chihuahua-2026');
const htmlPath = path.join(root, 'galeria-chihuahua.html');
let html = fs.readFileSync(htmlPath, 'utf8');
if (html.includes('gallery-mosaic--aligned')) throw new Error('Photos have already been imported.');
fs.copyFileSync(htmlPath, path.join(__dirname, 'galeria-chihuahua-before-20260918.html'));
fs.mkdirSync(destination, { recursive: true });
const describe = (id) => {
  if (id <= 8) return ['Chihuahua krótkowłosa', 'Czarna Chihuahua w czerwonych szelkach'];
  if (id <= 14) return ['Chihuahua krótkowłosa', 'Czarna Chihuahua z białym podbródkiem'];
  if (id <= 23) return ['Czarna podpalana', 'Czarna podpalana Chihuahua na białym kocu'];
  if (id <= 31) return ['Niebieski podpalany', 'Niebieski podpalany szczeniak Chihuahua'];
  if (id <= 40) return ['Czekoladowa', 'Czekoladowa Chihuahua w czerwonych szelkach'];
  if (id <= 45) return ['Chihuahua długowłosa', 'Jasnobrązowy szczeniak Chihuahua w ogrodzie'];
  if (id <= 54) return ['Chihuahua długowłosa', 'Czekoladowy szczeniak Chihuahua na białym kocu'];
  if (id <= 61) return ['Chihuahua długowłosa', 'Szczeniak Chihuahua z jasnymi łapkami'];
  if (id <= 66) return ['Chihuahua długowłosa', 'Brązowy szczeniak Chihuahua w ogrodzie'];
  if (id === 67) return ['Chihuahua długowłosa', 'Długowłosa Chihuahua z białymi łapkami na drewnianej podłodze'];
  if (id === 68) return ['Chihuahua długowłosa', 'Długowłosa Chihuahua siedząca na kocu na kanapie'];
  if (id === 69) return ['Chihuahua długowłosa', 'Długowłosa Chihuahua odpoczywająca wśród poduszek'];
  return ['Chihuahua długowłosa', 'Długowłosa Chihuahua w czerwonych szelkach podczas podróży'];
};
const tiles = photos.map((photo, index) => {
  fs.copyFileSync(path.join(source, photo.source), path.join(destination, photo.file));
  const [caption, description] = describe(photo.id);
  const style = `--photo-x:${photo.positionX}%;--photo-y:${photo.positionY}%;--photo-scale:${photo.scale}`;
  return `      <button class="mosaic-tile" type="button" style="${style}" aria-label="Powiększ zdjęcie ${photo.id}: ${description}">\r\n` +
    `        <img class="ph-img" src="assets/photos/chihuahua-2026/${photo.file}" alt="${description}, zdjęcie ${photo.id}" width="${photo.width}" height="${photo.height}" loading="${index < 4 ? 'eager' : 'lazy'}" decoding="async" />\r\n` +
    `        <span class="mosaic-cap" aria-hidden="true">${caption}</span>\r\n` +
    '      </button>';
}).join('\r\n');
const opening = '<div class="gallery-mosaic reveal" data-gallery-mosaic aria-label="Zdjęcia Chihuahua z poprzednich miotów">';
if (!html.includes(opening)) throw new Error('Gallery insertion point is missing.');
html = html.replace(opening, '<div class="gallery-mosaic gallery-mosaic--aligned" data-gallery-mosaic aria-label="Galeria zdjęć Chihuahua z hodowli Bajeczne Urwisy">\r\n' + tiles);
html = html.replace('styles.css?v=20260716-wiedza1', 'styles.css?v=20260918-galeria-chihuahua');
html = html.replace('Zobacz umaszczenia czekoladowe, niebieskie i sable z naszych poprzednich miotów.', 'Poznaj nasze Chihuahua krótko- i długowłose, szczenięta z nowych i wcześniejszych miotów.');
html = html.replace('Umaszczenia czekoladowe, niebieskie i sable z naszych poprzednich miotów.', 'Chihuahua krótko- i długowłose. Zdjęcia szczeniąt z nowych i wcześniejszych miotów.');
html = html.replace('Odważne maluchy o wielkich serduszkach. Zobacz umaszczenia, które pojawiały się w naszej hodowli: czekoladowe, niebieskie i sable.', 'Poznaj nasze Chihuahua krótko- i długowłose. Zobacz szczenięta z nowych i wcześniejszych miotów oraz ich codzienne chwile.');
// Retain all 13 earlier photos, adapting their focal points to the same portrait frames.
const existingX = [54, 75, 29, 49, 53, 35, 55, 47, 58, 61, 48, 40, 10];
html = html.replace(/<button class="mosaic-tile(?: mosaic-tile--(?:sq|tall))?" type="button"><img class="ph-img" src="assets\/photos\/gallery-chihuahua-(\d+)\.png"([^]*?)<\/button>/g, (tile, number) => {
  const index = Number(number) - 1;
  return tile.replace(/class="mosaic-tile[^"]*" type="button"/, `class="mosaic-tile" type="button" style="--photo-x:${existingX[index]}%"`)
    .replace('loading="lazy"', 'loading="lazy" decoding="async"');
});
fs.writeFileSync(htmlPath, html);
console.log(`Added ${photos.length} new photos and retained 13 existing photos.`);
