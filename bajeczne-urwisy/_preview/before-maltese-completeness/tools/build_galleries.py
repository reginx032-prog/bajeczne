"""Build both complete static galleries from the curated original-photo manifest.

No JavaScript fetch or pagination: every unique photograph is present in HTML.
Existing responsive derivatives are reused without rewriting unrelated pages.
"""
from pathlib import Path
from html import escape
from lxml import html
import json
import re

ROOT = Path(__file__).resolve().parent.parent
manifest = json.loads((ROOT/'data/gallery-photos.json').read_text(encoding='utf8'))
photos = manifest['photos']
optimized = json.loads((ROOT/'assets/optimized/manifest.json').read_text(encoding='utf8'))
leads = {
    'chihuahua': 'Poznaj nasze Chihuahua krótko- i długowłose. Szczenięta, wcześniejsze mioty i codzienne chwile, uchwycone na naszych zdjęciach.',
    'maltanczyki': 'Nasze Maltańczyki w domu i w ogrodzie. Małe odkrycia, wspólna zabawa i wspomnienia z wcześniejszych miotów.'
}
for breed in leads:
    selected = [p for p in photos if p['breed']==breed]
    order = manifest['galleryOrder'][breed]
    if len(order) != len(selected) or set(order) != {p['id'] for p in selected}:
        raise ValueError(f'Incomplete or repeated photo in {breed} gallery order')
    position = {photo_id: i for i, photo_id in enumerate(order)}
    selected.sort(key=lambda p: position[p['id']])
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
        responsive = ''
        if p['src'] in optimized:
            candidates = ', '.join(f'{v["src"]} {v["width"]}w' for v in optimized[p['src']]['variants'])
            responsive = f' srcset="{escape(candidates,quote=True)}" sizes="(max-width: 640px) 48vw, (max-width: 980px) 32vw, 300px"'
        tiles.append(f'      <button class="mosaic-tile{extra}" type="button" style="{style}" aria-label="Powiększ: {alt}" data-photo-id="{p["id"]}"><img src="{escape(p["src"],quote=True)}" alt="{alt}" width="{p["width"]}" height="{p["height"]}" loading="lazy" decoding="async"{responsive} /><span class="mosaic-cap" aria-hidden="true">Zobacz całe zdjęcie</span></button>')
    mosaic_html='    <div class="gallery-mosaic gallery-mosaic--aligned" data-gallery-mosaic aria-label="Wszystkie fotografie '+('Chihuahua' if breed=='chihuahua' else 'Maltańczyków')+'">\n'+'\n'.join(tiles)+'\n    </div>'
    source=source[:start]+mosaic_html.strip()+source[end:]
    doc=html.fromstring(source)
    old_lead=doc.xpath('//main//p[contains(@class,"lead")]')[0]
    text=old_lead.text_content()
    source=source.replace(text,leads[breed],1)
    source=re.sub(r'\s*<!-- Gallery count -->.*?<!-- /Gallery count -->','',source,flags=re.S)
    if 'breed-pages.css?' not in source:
        source=source.replace('</head>','  <link rel="stylesheet" href="breed-pages.css?v=20260918-gallery-fix" />\n</head>')
    source=re.sub(r'<div class="lightbox-inner">.*?</div>', '<div class="lightbox-inner"></div>', source, flags=re.S)
    path.write_text(source,encoding='utf8')
    print(f'{path.name}: {len(selected)} photographs')
