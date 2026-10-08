"""Import the six supplied puppy photos and prepend their available cards."""
from pathlib import Path
from hashlib import sha256
import json
import re
import shutil

from PIL import Image, ImageOps, ImageDraw
from lxml import html

ROOT = Path(__file__).resolve().parent.parent
TEMP = Path('C:/Users/Admin/AppData/Local/Temp')
DOGS = [
    ('Elf', 'Elfa', 'czarny', 'Czarny', 'Samiec', 'f21fb676-9c95-4b37-b0dd-0feb222899f1', 50),
    ('Gabi', 'Gabi', 'czekoladowa', 'Czekoladowy', 'Samica', '5c90874d-2ef6-4b33-bf74-90cc802216ee', 0),
    ('Gacek', 'Gacka', 'czekoladowy-podpalany', 'Czekoladowy podpalany', 'Samiec', '5bb453ad-8c5a-4b25-a916-5570d2fbdcbc', 40),
    ('Fibi', 'Fibi', 'niebieska', 'Niebieski', 'Samica', '3b1b425e-7549-40db-a54c-ccf5a780c033', 0),
    ('Fifi', 'Fifi', 'niebieska', 'Niebieski', 'Samica', '336ab640-7eff-413d-9e7c-0536e3904bb9', 25),
    ('Fionka', 'Fionkę', 'bezowa', 'Beżowy', 'Samica', 'c699df45-e4f9-48ce-8c21-927173ffbc5c', 0),
]

page = ROOT / 'index.html'
source = page.read_bytes().decode('utf8')
newline = '\r\n' if '\r\n' in source else '\n'
assert '<h3>Elf</h3>' not in source, 'Cards already imported'
doc = html.fromstring(source)
original_cards = doc.xpath('//*[@data-puppy-track]/article')
assert len(original_cards) == 12
phone_icon = re.search(r'<svg\b.*?</svg>', html.tostring(original_cards[0].xpath('.//a')[0], encoding='unicode')).group()
manifest_path = ROOT / 'assets/optimized/manifest.json'
manifest_bytes = manifest_path.read_bytes()
manifest = json.loads(manifest_bytes)
backup = ROOT / '_preview/before-new-puppies-20261007'
backup.mkdir(exist_ok=True)
for path in (page, manifest_path):
    target = backup / path.name
    if not target.exists():
        shutil.copy2(path, target)

cards = []
sheet = Image.new('RGB', (960, 710), '#faf7f2')
draw = ImageDraw.Draw(sheet)
for index, (name, accusative, slug, color, sex, attachment, position) in enumerate(DOGS):
    original = TEMP / f'codex-clipboard-{attachment}.jpg'
    src = f'assets/photos/puppy-{name.lower()}-{slug}.jpg'
    destination = ROOT / src
    assert not destination.exists(), destination
    shutil.copy2(original, destination)
    digest = sha256(destination.read_bytes()).hexdigest()[:12]
    variants = []
    with Image.open(destination) as photo:
        im = ImageOps.exif_transpose(photo)
        width, height = im.size
        for target_width in sorted({min(w, width) for w in (400, 800, 1200, 1600)}):
            target_height = round(height * target_width / width)
            target_src = f'assets/optimized/{destination.stem}-{digest}-{target_width}.webp'
            target = ROOT / target_src
            im.resize((target_width, target_height), Image.Resampling.LANCZOS).save(target, 'WEBP', quality=86, method=5)
            variants.append({'src': target_src, 'width': target_width, 'height': target_height, 'bytes': target.stat().st_size})
        # Offline contact sheet mirrors the square CSS frame and object-position.
        top = round((height - width) * position / 100)
        tile = im.crop((0, top, width, top + width)).resize((300, 300), Image.Resampling.LANCZOS)
        x, y = 10 + (index % 3) * 320, 10 + (index // 3) * 350
        sheet.paste(tile, (x, y))
        draw.text((x + 6, y + 312), name, fill='#222222')
    manifest[src] = {'originalBytes': destination.stat().st_size, 'variants': variants}
    srcset = ', '.join(f'{v["src"]} {v["width"]}w' for v in variants)
    status = 'Dostępny' if sex == 'Samiec' else 'Dostępna'
    descriptor = ('czarny piesek' if name == 'Elf' else
                  'czekoladowy podpalany piesek' if name == 'Gacek' else
                  'czekoladowa suczka' if name == 'Gabi' else
                  'beżowa suczka' if name == 'Fionka' else 'niebieska suczka')
    cards.append(f'''      <article class="card puppy puppy--available reveal">
        <div class="puppy-media">
          <span class="status status--free">{status}</span>
          <img class="ph-img" src="{src}" alt="{name}, {descriptor} Chihuahua krótkowłosego z hodowli Bajeczne Urwisy" width="{width}" height="{height}" loading="lazy" decoding="async" style="object-position: 50% {position}%;" srcset="{srcset}" sizes="(max-width: 760px) 90vw, 420px" />
        </div>
        <div class="puppy-body">
          <h3>{name}</h3>
          <div class="puppy-meta">
            <span><span class="meta-label">Rasa</span><b>Chihuahua</b></span>
            <span><span class="meta-label">Kolor</span><b>{color}</b></span>
            <span><span class="meta-label">Włos</span><b>Krótkowłosy</b></span>
            <span><span class="meta-label">Płeć</span><b>{sex}</b></span>
          </div>
          <a href="tel:+48601074022" class="btn btn--ghost">{phone_icon} Zapytaj o {accusative}</a>
        </div>
      </article>''')

anchor = '      <div class="puppy-grid" data-puppy-track tabindex="0" aria-label="Karty szczeniąt Chihuahua">' + newline
assert source.count(anchor) == 1
source = source.replace(anchor, anchor + ('\n\n'.join(cards) + '\n\n').replace('\n', newline), 1)
old_note = 'Wszystkie pokazane maluszki znalazły już swoje domy. Przewiń, aby poznać pieski z naszej hodowli.'
assert source.count(old_note) == 1
source = source.replace(old_note, 'Na początku znajdziesz maluszki, które czekają na swoje rodziny. Dalej pokazujemy pieski, które znalazły już dom.', 1)
page.write_bytes(source.encode('utf8'))
manifest_newline = '\r\n' if b'\r\n' in manifest_bytes else '\n'
manifest_text = json.dumps(manifest, ensure_ascii=False, indent=2).replace('\n', manifest_newline)
if manifest_bytes.endswith(b'\n'):
    manifest_text += manifest_newline
manifest_path.write_bytes(manifest_text.encode('utf8'))
sheet.save(ROOT / '_preview/new-puppies-20261007-crops.jpg', quality=92)
print('Added 6 available puppy cards, 6 original photos and 18 responsive WebP variants.')
