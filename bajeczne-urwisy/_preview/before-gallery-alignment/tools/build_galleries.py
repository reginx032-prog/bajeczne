"""Build both complete static galleries from the curated original-photo manifest.

No JavaScript fetch or pagination: every unique photograph is present in HTML.
Run optimize_images.py afterwards to refresh responsive image candidates.
"""
from pathlib import Path
from html import escape
from lxml import html
import json
import re

ROOT = Path(__file__).resolve().parent.parent
photos = json.loads((ROOT/'data/gallery-photos.json').read_text(encoding='utf8'))['photos']
leads = {
    'chihuahua': 'Poznaj nasze Chihuahua krótko- i długowłose. Szczenięta, wcześniejsze mioty i codzienne chwile, uchwycone na naszych zdjęciach.',
    'maltanczyki': 'Nasze Maltańczyki w domu i w ogrodzie. Małe odkrycia, wspólna zabawa i wspomnienia z wcześniejszych miotów.'
}
featured = {'chihuahua': [177,166,156,130,138,148,46,188], 'maltanczyki': [24,25,41,16,89,43,18,11]}
for breed in leads:
    selected = [p for p in photos if p['breed']==breed]
    selected.sort(key=lambda p: (featured[breed].index(p['id']) if p['id'] in featured[breed] else len(featured[breed]), photos.index(p)))
    path = ROOT/f'galeria-{breed}.html'
    source = path.read_text(encoding='utf8')
    # Replace just the static grid; preserve the rest of the page.
    start = source.index('<div class="gallery-mosaic')
    end = source.index('</div>', start)+6
    tiles=[]
    for p in selected:
        style=f'--photo-x:{p["x"]}%;--photo-y:{p["y"]}%;--photo-scale:{p["scale"]}'
        extra=' mosaic-tile--group' if p['fit']=='contain' else ''
        alt=escape(p['alt'],quote=True)
        tiles.append(f'      <button class="mosaic-tile{extra}" type="button" style="{style}" aria-label="Powiększ: {alt}" data-photo-id="{p["id"]}"><img src="{escape(p["src"],quote=True)}" alt="{alt}" width="{p["width"]}" height="{p["height"]}" loading="lazy" decoding="async" /><span class="mosaic-cap" aria-hidden="true">Zobacz całe zdjęcie</span></button>')
    mosaic_html='    <div class="gallery-mosaic gallery-mosaic--aligned" data-gallery-mosaic aria-label="Wszystkie fotografie '+('Chihuahua' if breed=='chihuahua' else 'Maltańczyków')+'">\n'+'\n'.join(tiles)+'\n    </div>'
    source=source[:start]+mosaic_html.strip()+source[end:]
    doc=html.fromstring(source)
    old_lead=doc.xpath('//main//p[contains(@class,"lead")]')[0]
    text=old_lead.text_content()
    source=source.replace(text,leads[breed],1)
    source=re.sub(r'\s*<!-- Gallery count -->.*?<!-- /Gallery count -->','',source,flags=re.S)
    marker=source.index('<div class="gallery-mosaic')
    count=f'<p class="gallery-count"><strong>{len(selected)} zdjęć</strong><span>Kliknij fotografię, aby zobaczyć pełny kadr. Zdjęcia przedstawiają również pieski, które znalazły już dom.</span></p>'
    source=source[:marker]+'<!-- Gallery count -->'+count+'<!-- /Gallery count -->\n    '+source[marker:]
    if 'breed-pages.css?' not in source:
        source=source.replace('</head>','  <link rel="stylesheet" href="breed-pages.css?v=20260918-photos1" />\n</head>')
    source=re.sub(r'<div class="lightbox-inner">.*?</div>', '<div class="lightbox-inner"></div>', source, flags=re.S)
    path.write_text(source,encoding='utf8')
    print(f'{path.name}: {len(selected)} photographs')
