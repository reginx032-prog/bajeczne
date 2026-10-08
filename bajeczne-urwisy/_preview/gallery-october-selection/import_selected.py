"""Import a visually reviewed selection; preserve original photos and old tiles."""
from pathlib import Path
from hashlib import sha256
import json
import shutil

from PIL import Image, ImageOps, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
REVIEW = Path(__file__).resolve().parent
SELECTION = [
    ('ELF 01', 'Elf', 'elf-portret', [216, 280, 840, 1120], 'Elf, czarny krótkowłosy Chihuahua na dłoni opiekuna'),
    ('GABI 02', 'Gabi', 'gabi-na-kocu', [180, 60, 840, 1120], 'Gabi, czekoladowa krótkowłosa suczka Chihuahua z przechyloną główką'),
    ('GACEK 01', 'Gacek', 'gacek-na-kocu', [180, 190, 840, 1120], 'Gacek, czekoladowy podpalany Chihuahua na białym kocu'),
    ('FIBI 05', 'Fibi', 'fibi-w-sloncu', [210, 100, 960, 1280], 'Fibi, niebieska krótkowłosa suczka Chihuahua w słońcu'),
    ('FIFI 02', 'Fifi', 'fifi-portret', [160, 180, 960, 1280], 'Fifi, niebieska krótkowłosa suczka Chihuahua na dłoni opiekuna'),
    ('FIONA 01', 'Fionka', 'fionka-portret', [80, 70, 960, 1280], 'Fionka, beżowa krótkowłosa suczka Chihuahua'),
    ('GABI 03', 'Gabi', 'gabi-na-rekach', [0, 0, 1200, 1600], 'Gabi, czekoladowa suczka Chihuahua z białymi znaczeniami na łapkach'),
    ('GACEK 03', 'Gacek', 'gacek-na-rekach', [0, 30, 1140, 1520], 'Gacek, czekoladowy podpalany piesek Chihuahua na rękach opiekuna'),
    ('FIBI 01', 'Fibi', 'fibi-portret', [180, 180, 840, 1120], 'Fibi, niebieska suczka Chihuahua na białym kocu'),
    ('FIONA 02', 'Fionka', 'fionka-na-kocu', [240, 80, 960, 1280], 'Fionka, beżowa suczka Chihuahua stojąca na białym kocu'),
]


def write_json(path, data):
    old = path.read_bytes() if path.exists() else b''
    newline = '\r\n' if b'\r\n' in old else '\n'
    text = json.dumps(data, ensure_ascii=False, indent=2)
    if not old or old.endswith(b'\n'):
        text += '\n'
    path.write_bytes(text.replace('\n', newline).encode('utf8'))


records = {r['label']: r for r in json.loads((REVIEW / 'source-review.json').read_text(encoding='utf8'))}
catalog_path = ROOT / 'data/gallery-photos.json'
optimized_path = ROOT / 'assets/optimized/manifest.json'
inventory_path = ROOT / '_preview/originals-inventory.json'
catalog = json.loads(catalog_path.read_bytes())
optimized = json.loads(optimized_path.read_bytes())
inventory = json.loads(inventory_path.read_bytes())
assert len(catalog['photos']) == 197, 'Selection already imported or catalog changed'
backup = REVIEW / 'before'
backup.mkdir(exist_ok=True)
for rel in ('data/gallery-photos.json', 'assets/optimized/manifest.json', '_preview/originals-inventory.json', 'galeria-chihuahua.html', 'galeria-maltanczyki.html', 'index.html', 'README.md'):
    target = backup / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        shutil.copy2(ROOT / rel, target)

dest = ROOT / 'assets/photos/chihuahua-2026-10'
dest.mkdir(exist_ok=True)
next_id = max(r['id'] for r in inventory) + 1
new_ids = []
selected_records = []
seen = set()
font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 20)
sheet = Image.new('RGB', (1550, 900), '#f6f3ed')
draw = ImageDraw.Draw(sheet)
for index, (label, name, slug, crop, alt) in enumerate(SELECTION):
    record = records[label]
    assert not any('id' in r for r in record['existing']), f'Already catalogued: {label}'
    assert record['pixelHash'] not in seen
    seen.add(record['pixelHash'])
    # Reuse card originals when this exact photo is already in the site.
    if record['existing']:
        src = record['existing'][0]['src']
        target = ROOT / src
    else:
        target = dest / f'{slug}.jpg'
        assert not target.exists()
        shutil.copy2(record['source'], target)
        src = target.relative_to(ROOT).as_posix()
    with Image.open(target) as original:
        photo = ImageOps.exif_transpose(original).convert('RGB')
        width, height = photo.size
        digest = sha256(target.read_bytes()).hexdigest()
        pixels = sha256(photo.tobytes()).hexdigest()
        assert pixels == record['pixelHash']
        left, top, cw, ch = crop
        assert 0 <= left <= width - cw and 0 <= top <= height - ch
        assert abs(cw / ch - .75) < .00001
        entry = {
            'id': next_id, 'breed': 'chihuahua', 'src': src, 'alt': alt,
            'width': width, 'height': height, 'crop': crop,
            'x': round(left / (width - cw) * 100, 3) if width > cw else 50,
            'y': round(top / (height - ch) * 100, 3) if height > ch else 50,
            'scale': round(min(width, height * .75) / cw, 5), 'fit': 'cover', 'aliases': []
        }
        catalog['photos'].append(entry)
        gray = list(photo.convert('L').resize((9, 8), Image.Resampling.LANCZOS).getdata())
        dhash = 0
        for y in range(8):
            for x in range(8):
                dhash = (dhash << 1) | (gray[y * 9 + x] > gray[y * 9 + x + 1])
        inventory.append({'id': next_id, 'src': src, 'size': [width, height], 'sha': digest, 'pixels': pixels, 'dhash': hex(dhash)})
        new_ids.append(next_id)
        selected_records.append({'label': label, 'name': name, 'source': record['source'], 'src': src, 'id': next_id})
        next_id += 1
        if src not in optimized:
            variants = []
            for w in sorted({min(w, width) for w in (400, 800, 1200, 1600)}):
                h = round(height * w / width)
                path = ROOT / f'assets/optimized/{target.stem}-{digest[:12]}-{w}.webp'
                photo.resize((w, h), Image.Resampling.LANCZOS).save(path, 'WEBP', quality=86, method=5)
                variants.append({'src': path.relative_to(ROOT).as_posix(), 'width': w, 'height': h, 'bytes': path.stat().st_size})
            optimized[src] = {'originalBytes': target.stat().st_size, 'variants': variants}
        tile = photo.crop((left, top, left + cw, top + ch)).resize((288, 384), Image.Resampling.LANCZOS)
        x, y = 10 + (index % 5) * 310, 10 + (index // 5) * 450
        sheet.paste(tile, (x, y))
        draw.text((x + 6, y + 398), f'{name} | {label}', fill='#222222', font=font)

catalog['galleryOrder']['chihuahua'] = new_ids + catalog['galleryOrder']['chihuahua']
write_json(catalog_path, catalog)
write_json(optimized_path, optimized)
write_json(inventory_path, inventory)
write_json(REVIEW / 'selected.json', selected_records)
sheet.save(REVIEW / 'selected-crops.jpg', quality=94)
readme = ROOT / 'README.md'
content = readme.read_bytes().decode('utf8')
content = content.replace('149 zdjęć Chihuahua', '159 zdjęć Chihuahua').replace('katalog 197 fotografii', 'katalog 207 fotografii').replace('Galerie pokazują 181 zdjęć', 'Galerie pokazują 191 zdjęć')
readme.write_bytes(content.encode('utf8'))
print('Added 10 selected photographs: reused 5 originals, imported 5 new originals. New IDs:', new_ids)
