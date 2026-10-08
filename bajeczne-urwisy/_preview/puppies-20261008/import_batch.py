"""Import only the reviewed photo batch and add the seven available puppy cards."""
from pathlib import Path
from hashlib import sha256
from collections import Counter
from html import escape
from PIL import Image, ImageOps
import json
import re
import shutil
import sys

sys.stdout.reconfigure(encoding='utf8')
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
SOURCE = Path('C:/Users/Admin/Desktop/psy')
plan = json.loads((OUT/'batch-plan.json').read_bytes())
review = json.loads((OUT/'source-review.json').read_bytes())
catalog_path = ROOT/'data/gallery-photos.json'
inventory_path = ROOT/'_preview/originals-inventory.json'
optimized_path = ROOT/'assets/optimized/manifest.json'
catalog = json.loads(catalog_path.read_bytes())
inventory = json.loads(inventory_path.read_bytes())
optimized = json.loads(optimized_path.read_bytes())
dogs = {d['name']: d for d in plan['dogs']}
next_id = max(p['id'] for p in inventory)+1
seen_pixels = {p['pixels'] for p in inventory}
destination = ROOT/'assets/photos/chihuahua-2026-10-07'
destination.mkdir(exist_ok=True)
assert all(p['pixels'] not in seen_pixels for p in plan['photos']), 'Batch already imported'
index_path = ROOT/'index.html'
homepage = index_path.read_bytes().decode('utf8')
assert all(f'<h3>{d["name"]}</h3>' not in homepage for d in plan['dogs']), 'Cards already exist'


def save_json(path,value):
    previous = path.read_bytes() if path.exists() else b''
    newline = '\r\n' if b'\r\n' in previous else '\n'
    path.write_bytes((json.dumps(value,ensure_ascii=False,indent=2)+'\n').replace('\n',newline).encode('utf8'))


def optimize(src,photo):
    target = ROOT/src
    digest = sha256(target.read_bytes()).hexdigest()
    variants = []
    for width in sorted({min(photo.width,x) for x in (400,600,800,1200)}):
        height = round(photo.height*width/photo.width)
        variant = ROOT/f'assets/optimized/{target.stem}-{digest[:12]}-{width}.webp'
        photo.resize((width,height),Image.Resampling.LANCZOS).save(variant,'WEBP',quality=86,method=5)
        variants.append({'src':variant.relative_to(ROOT).as_posix(),'width':width,'height':height,'bytes':variant.stat().st_size})
    optimized[src] = {'originalBytes':target.stat().st_size,'variants':variants}


added = []
counts = Counter()
for row in plan['photos']:
    counts[row['dog']] += 1
    dog = dogs[row['dog']]
    src = f'assets/photos/chihuahua-2026-10-07/{dog["slug"]}-{counts[row["dog"]]:02d}.jpg'
    target = ROOT/src
    assert not target.exists(),src
    shutil.copy2(SOURCE/row['file'],target)
    photo = ImageOps.exif_transpose(Image.open(target)).convert('RGB')
    assert sha256(photo.tobytes()).hexdigest() == row['pixels']
    assert sha256(target.read_bytes()).hexdigest() == row['sha']
    left,top,cw,ch = row['crop']
    w,h = photo.size
    entry = {'id':next_id,'breed':'chihuahua','src':src,'alt':dog['alt'],
             'width':w,'height':h,'crop':row['crop'],
             'x':round(left/(w-cw)*100,3) if w>cw else 50,
             'y':round(top/(h-ch)*100,3) if h>ch else 50,
             'scale':round(min(w,h*.75)/cw,5),'fit':'cover','aliases':[]}
    catalog['photos'].append(entry)
    inventory.append({'id':next_id,'src':src,'size':[w,h],'sha':row['sha'],'pixels':row['pixels']})
    optimize(src,photo)
    added.append({'id':next_id,'dog':row['dog'],'source':row['file'],'src':src,'pixels':row['pixels']})
    next_id += 1
    print(f'Prepared {dog["name"]}: {counts[row["dog"]]}',flush=True)

# The owner has explicitly supplied this photo again as part of the new full batch.
restored = [r for r in review if r['status']=='omitted']
assert len(restored)==1 and restored[0]['existing']['id']==133
restored_id = restored[0]['existing']['id']
restored_photo = next(p for p in catalog['photos'] if p['id']==restored_id)
assert restored_photo['galleryOmission']['requestedRemoval']
del restored_photo['galleryOmission']

# Start with one portrait of each new puppy, then show the other supplied views.
covers = [next(p['id'] for p in added if p['source']==d['file']) for d in plan['dogs']]
other_ids = [p['id'] for p in added if p['id'] not in covers]
catalog['galleryOrder']['chihuahua'] = covers+other_ids+catalog['galleryOrder']['chihuahua']
elf_ids = {r['existing']['id'] for r in review if r['dog']=='Elf' and r.get('existing')}
order = catalog['galleryOrder']['chihuahua']
order.insert(max(i for i,pid in enumerate(order) if pid in elf_ids)+1,restored_id)

template = re.search(r'      <article class="card puppy puppy--available reveal">.*?</article>',homepage,re.S).group(0)
card_blocks = []
for dog in plan['dogs']:
    original = ImageOps.exif_transpose(Image.open(SOURCE/dog['file'])).convert('RGB')
    x,y,w,h = dog['crop']
    portrait = original.crop((x,y,x+w,y+h))
    src = f'assets/photos/puppy-{dog["slug"]}-20261007.jpg'
    target = ROOT/src
    assert not target.exists(),src
    portrait.save(target,'JPEG',quality=94,subsampling=0,optimize=True)
    optimize(src,portrait)
    srcset = ', '.join(f'{v["src"]} {v["width"]}w' for v in optimized[src]['variants'])
    image = (f'<img class="ph-img" src="{src}" alt="{escape(dog["alt"],quote=True)}" '
             f'width="{w}" height="{h}" loading="lazy" decoding="async" '
             f'style="object-position: 50% 50%;" srcset="{srcset}" sizes="(max-width: 760px) 90vw, 420px" />')
    card = re.sub(r'<img\b[^>]+>',lambda m:image,template,count=1)
    card = card.replace('<h3>Elf</h3>',f'<h3>{dog["name"]}</h3>')
    for old,new in [('Czarny',dog['color']),('Krótkowłosy',dog['coat']),('Samiec',dog['sex'])]:
        card = card.replace(f'<b>{old}</b>',f'<b>{new}</b>')
    if dog['sex']=='Samica':
        card = card.replace('status--free">Dostępny','status--free">Dostępna')
    card = card.replace('Zapytaj o Elfa',f'Zapytaj o {dog["ask"]}')
    card_blocks.append(card)
    dog['cardSrc'] = src
    dog['galleryPhotoId'] = next(p['id'] for p in added if p['source']==dog['file'])

newline = '\r\n' if '\r\n' in homepage else '\n'
insertion = (newline*2).join(card_blocks)+newline*2
marker = '      <article class="card puppy reveal">'
assert marker in homepage
homepage = homepage.replace(marker,insertion+marker,1)
index_path.write_bytes(homepage.encode('utf8'))
for path,value in [(catalog_path,catalog),(inventory_path,inventory),(optimized_path,optimized)]:
    save_json(path,value)
save_json(OUT/'import-result.json',{'added':added,'restored':restored,'dogs':plan['dogs']})
print(json.dumps({'newOriginalPhotos':len(added),'restoredPhotos':len(restored),'newCards':len(card_blocks),'galleryChihuahua':len(order)},ensure_ascii=False))
