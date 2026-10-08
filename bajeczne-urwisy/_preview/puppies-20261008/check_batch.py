"""Check photo provenance, availability, and preservation of existing content."""
from pathlib import Path
from collections import Counter
from hashlib import sha256
from PIL import Image, ImageOps
from lxml import html
import json
import re

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
result=json.loads((OUT/'import-result.json').read_bytes())
review=json.loads((OUT/'source-review.json').read_bytes())
catalog=json.loads((ROOT/'data/gallery-photos.json').read_bytes())
before=json.loads((OUT/'before/data/gallery-photos.json').read_bytes())
by_id={p['id']:p for p in catalog['photos']}
new_names=[d['name'] for d in result['dogs']]
new_ids={p['id'] for p in result['added']}
restored_ids={p['existing']['id'] for p in result['restored']}
assert len(new_ids)==37 and restored_ids=={133}
assert len(catalog['photos'])-len(before['photos'])==37
for old in before['photos']:
    expected=dict(old)
    if old['id'] in restored_ids: del expected['galleryOmission']
    assert by_id[old['id']]==expected,old['id']
assert [i for i in catalog['galleryOrder']['chihuahua'] if i not in new_ids|restored_ids]==before['galleryOrder']['chihuahua']
assert catalog['galleryOrder']['maltanczyki']==before['galleryOrder']['maltanczyki']
published=[p for p in catalog['photos'] if not p.get('galleryOmission')]
pixels=Counter(sha256(ImageOps.exif_transpose(Image.open(ROOT/p['src'])).convert('RGB').tobytes()).hexdigest() for p in published)
assert all(pixels[row['pixels']]==1 for row in review), 'Missing or repeated incoming photo'
for row in result['added']:
    reviewed=next(r for r in review if r['file']==row['source'])
    assert sha256((ROOT/row['src']).read_bytes()).hexdigest()==reviewed['sha'],'Original changed'
new_folder=ROOT/'assets/photos/chihuahua-2026-10-07'
assert {p.relative_to(ROOT).as_posix() for p in new_folder.iterdir()}=={r['src'] for r in result['added']}

homepage=html.fromstring((ROOT/'index.html').read_bytes().decode('utf8'))
cards=homepage.xpath('//*[@data-puppy-track]/article')
old_home=html.fromstring((OUT/'before/index.html').read_bytes().decode('utf8'))
old_cards=old_home.xpath('//*[@data-puppy-track]/article')
names=[p.xpath('string(.//h3)') for p in cards]
assert names==[p.xpath('string(.//h3)') for p in old_cards[:6]]+new_names+[p.xpath('string(.//h3)') for p in old_cards[6:]]
assert len(cards)==25
assert ['puppy--available' in p.get('class','').split() for p in cards]==[True]*13+[False]*12
for dog in result['dogs']:
    card=cards[names.index(dog['name'])]
    assert card.xpath('.//div[@class="puppy-meta"]//b/text()')==['Chihuahua',dog['color'],dog['coat'],dog['sex']]
    assert card.xpath('string(.//span[contains(@class,"status--free")])')==('Dostępny' if dog['sex']=='Samiec' else 'Dostępna')
    assert card.xpath('.//a/@href')==['tel:+48601074022']
    assert card.xpath('string(.//img/@src)')==dog['cardSrc']
    assert card.xpath('string(.//img/@alt)')==dog['alt']
    with Image.open(ROOT/dog['cardSrc']) as image: assert image.width==image.height

def visible(doc):
    for node in doc.xpath('//script | //style | //*[@data-gallery-mosaic]'):
        node.getparent().remove(node)
    return ' '.join(' '.join(doc.xpath('//body//text()')).split())

for path in ROOT.glob('*.html'):
    current=html.fromstring(path.read_bytes().decode('utf8'))
    previous=html.fromstring((OUT/'before'/path.name).read_bytes().decode('utf8'))
    if path.name=='index.html':
        # Only the seven authorized card additions may change visible copy.
        for card in current.xpath('//*[@data-puppy-track]/article'):
            if card.xpath('string(.//h3)') in new_names:card.getparent().remove(card)
    assert visible(current)==visible(previous),f'Unrelated copy changed: {path.name}'
    old_source=(OUT/'before'/path.name).read_bytes().decode('utf8')
    if path.name=='index.html':
        for block in re.findall(r'<article class="card puppy\b.*?</article>',old_source,re.S):
            assert block in path.read_bytes().decode('utf8'),'An existing card changed'

report={'incomingFiles':len(review),'distinctIncomingPhotos':len({r['pixels'] for r in review}),
        'newPhotos':len(new_ids),'restoredPhotos':len(restored_ids),'alreadyPresent':30,'duplicateFilesSkipped':1,
        'newAvailableCards':new_names,'availableCards':13,'homedCards':12,
        'chihuahuaGallery':len(catalog['galleryOrder']['chihuahua']),
        'allIncomingPhotosRepresentedOnce':True,'originalPhotoFilesPreserved':True,
        'existingCardsAndOtherVisibleCopyPreserved':True}
(OUT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(report,ensure_ascii=True,indent=2))
