const fs = require('node:fs');
const path = require('node:path');
const file = path.join(__dirname, 'chihuahua-import.json');
const photos = JSON.parse(fs.readFileSync(file, 'utf8').replace(/^\uFEFF/, ''));
// Center x/y and crop width, as percentages of each original. The gallery uses 3:4 frames.
const crops = [
  [52,46,62], [50,47,72], [50,48,72], [54,40,57],
  [53,44,66], [60,43,65], [46,46,68], [62,45,68],
  [44,52,78], [55,50,76], [54,52,76], [47,48,60],
  [51,46,66], [50,48,66], [55,41,60], [49,41,60],
  [44,44,62], [47,43,62], [44,44,62], [48,49,76],
  [44,45,64], [56,53,78], [48,47,78], [59,58,76],
  [40,62,58], [40,61,65], [38,60,69], [39,51,70],
  [37,51,70], [46,51,66], [44,46,58], [49,52,72],
  [52,47,94], [41,59,71], [44,58,76], [58,42,83],
  [59,39,66], [56,37,70], [65,39,70], [54,43,62],
  [44,53,70], [51,48,70], [55,53,64], [49,52,57],
  [44,53,64], [53,53,76], [58,47,76], [55,53,63],
  [49,54,66], [52,52,65], [50,50,100], [38,51,63],
  [58,55,62], [58,48,64], [55,48,76], [54,47,68],
  [54,50,66], [51,43,78], [54,52,88], [52,50,91],
  [46,42,76], [44,48,72], [45,45,58], [42,49,56],
  [52,43,68], [42,56,72], [50,54,100], [50,55,90],
  [50,42,100], [50,54,100]
];
if (photos.length !== crops.length) throw new Error('Crop count must match photo count.');
const clamp = (n, min, max) => Math.max(min, Math.min(max, n));
photos.forEach((photo, index) => {
  const [cx, cy, widthPercent] = crops[index];
  const w = photo.width * widthPercent / 100;
  const h = w / .75;
  const left = clamp(photo.width * cx / 100 - w / 2, 0, photo.width - w);
  const top = clamp(photo.height * cy / 100 - h / 2, 0, photo.height - h);
  photo.crop = [cx, cy, widthPercent];
  photo.rect = [left, top, w, h];
  photo.positionX = photo.width === w ? 50 : +(left / (photo.width - w) * 100).toFixed(3);
  photo.positionY = photo.height === h ? 50 : +(top / (photo.height - h) * 100).toFixed(3);
  photo.scale = +(photo.width / w).toFixed(5);
});
fs.writeFileSync(file, JSON.stringify(photos, null, 2) + '\n');
console.log(`Prepared ${photos.length} individual crops.`);
