"""Check complete original-photo coverage and generated gallery integrity."""
from pathlib import Path
from PIL import Image,ImageOps
from hashlib import sha256
from collections import Counter
from lxml import html
import json, re
ROOT=Path(__file__).resolve().parent.parent
manifest=json.loads((ROOT/'data/gallery-photos.json').read_text(encoding='utf8'))
photos=manifest['photos']
canonical={p['src']:p['src'] for p in photos}
for p in photos:
    canonical.update({alias:p['src'] for alias in p['aliases']})
inventory=json.loads((ROOT/'_preview/originals-inventory.json').read_text(encoding='utf8'))
excluded={p['src'] for p in manifest['excluded']}
assert {p['src'] for p in inventory}==set(canonical)|excluded, 'Unaccounted source files'
fingerprints=[]
for p in photos:
    im=ImageOps.exif_transpose(Image.open(ROOT/p['src'])).convert('RGB')
    fingerprints.append(sha256(im.tobytes()).hexdigest())
    assert list(im.size)==[p['width'],p['height']]
    x,y,w,h=p['crop']
    assert x>=0 and y>=0 and x+w<=im.width+.01 and y+h<=im.height+.01
    assert abs(w/h-.75)<.0001
    assert 0<=p['x']<=100 and 0<=p['y']<=100 and p['scale']>=1
assert len(set(fingerprints))==len(photos), 'Duplicate decoded photograph'
before=[]
report={}
for breed in ['chihuahua','maltanczyki']:
    file=f'galeria-{breed}.html';doc=html.fromstring((ROOT/file).read_text(encoding='utf8'))
    tiles=doc.xpath('//*[@data-gallery-mosaic]/*')
    assert [int(n.get('data-photo-id')) for n in tiles] == manifest['galleryOrder'][breed], 'Gallery session order changed'
    notice_icons=doc.xpath('//div[contains(concat(" ",normalize-space(@class)," ")," notice ")]/svg')
    assert len(notice_icons)==1
    assert notice_icons[0].get('width')=='26' and notice_icons[0].get('height')=='26', 'Unbounded gallery notice icon'
    expected={p['src'] for p in photos if p['breed']==breed}
    actual=[n.xpath('.//img/@src')[0] for n in tiles]
    assert Counter(actual)==Counter(expected), 'Missing or repeated gallery photograph'
    assert all(n.tag=='button' and n.get('type')=='button' and n.get('aria-label') for n in tiles)
    assert not doc.xpath('//*[@data-gallery-mosaic]//*[@onerror or @hidden]')
    assert not doc.xpath('//*[@data-gallery-mosaic]/*[contains(@class,"is-hidden")]')
    for n in tiles:
        img=n.xpath('.//img')[0]
        assert img.get('loading')=='lazy'
        if (ROOT/img.get('src')).stat().st_size>=65000 and int(img.get('width'))>=500 and int(img.get('height'))>=350:
            assert img.get('srcset'), 'Large photograph missing responsive candidates'
        if img.get('srcset'):
            assert img.get('sizes')=='(max-width: 640px) 48vw, (max-width: 980px) 32vw, 300px', 'Image download size does not match uniform gallery tiles'
    old=html.fromstring((ROOT/'_preview/before-original-galleries'/file).read_text(encoding='utf8'))
    old_src=old.xpath('//*[@data-gallery-mosaic]//img/@src')
    assert all(s in canonical for s in old_src),'Previously displayed photograph missing'
    before.extend(canonical[s] for s in old_src)
    report[file]=len(actual)
for file in ['chihuahua.html','maltanczyk.html','rasy.html']:
    doc=html.fromstring((ROOT/file).read_text(encoding='utf8'))
    assert 'breed-page' in doc.xpath('//body/@class')[0].split()
    assert len(doc.xpath('//h1'))==1
    assert all(i.get('src') in canonical for i in doc.xpath('//main//img'))
    assert doc.xpath('//main//img[@fetchpriority="high"]')
    assert doc.xpath('//link[contains(@href,"breed-pages.css")]')
assert not any('page-'+x+'-hero' in (ROOT/p).read_text(encoding='utf8') for x in ['chihuahua','maltanczyk','rasy'] for p in ['chihuahua.html','maltanczyk.html','rasy.html'])
report.update(total=len(photos),previousTiles=len(before),previousUnique=len(set(before)),restored=len(set(p['src'] for p in photos)-set(before)),removedRepeatedTiles=len(before)-len(set(before)),duplicateAssetCopies=sum(len(p['aliases']) for p in photos))
(ROOT/'_preview/gallery-coverage-result.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(report,ensure_ascii=False,indent=2))
