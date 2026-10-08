"""Create responsive WebP copies. Original photographs remain unchanged.

Run with Python, Pillow and lxml. Re-running reuses unchanged derivatives.
"""
from pathlib import Path
from urllib.parse import unquote, urlsplit
from hashlib import sha256
from html import escape
import json
import re
from PIL import Image, ImageOps
from lxml import html

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / 'assets' / 'optimized'
DEST.mkdir(exist_ok=True)
PAGES = sorted(ROOT.glob('*.html'))
SOURCES = sorted({img.get('src') for p in PAGES for img in html.fromstring(p.read_text(encoding='utf8')).xpath('//img[@src]')})
manifest = {}

for src in SOURCES:
    if urlsplit(src).scheme:
        continue
    source = ROOT / unquote(urlsplit(src).path)
    if source.suffix.lower() not in {'.jpg', '.jpeg', '.png'} or source.stat().st_size < 65000:
        continue
    with Image.open(source) as original:
        im = ImageOps.exif_transpose(original)
        if im.width < 500 or im.height < 350:
            continue
        # Logos and credentials keep their existing lossless assets.
        if any(token in source.name.lower() for token in ('logo', 'ppk', 'wku', 'swk', 'badge', 'rodowod')):
            continue
        digest = sha256(source.read_bytes()).hexdigest()[:12]
        stem = re.sub(r'[^a-z0-9-]+', '-', source.stem.lower())[:65].strip('-')
        variants = []
        widths = sorted({min(w, im.width) for w in (400, 600, 800, 1200, 1600)})
        for width in widths:
            height = round(im.height * width / im.width)
            name = f'{stem}-{digest}-{width}.webp'
            target = DEST / name
            if not target.exists():
                resized = im.resize((width, height), Image.Resampling.LANCZOS)
                if resized.mode not in ('RGB', 'RGBA'):
                    resized = resized.convert('RGB')
                resized.save(target, 'WEBP', quality=86, method=5)
            variants.append({'src': target.relative_to(ROOT).as_posix(), 'width': width, 'height': height, 'bytes': target.stat().st_size})
        manifest[src] = {'originalBytes': source.stat().st_size, 'variants': variants}

def sizes_for(img):
    ancestors = ' '.join(n.get('class', '') for n in img.iterancestors())
    if 'breed-overview-pair' in ancestors:
        return '(max-width: 760px) 46vw, 280px'
    if 'breed-hero' in ancestors:
        return '(max-width: 760px) 92vw, 390px'
    if 'breed-photo-row' in ancestors:
        return '(max-width: 760px) 92vw, 400px'
    if 'hw-tile' in ancestors:
        return '(max-width: 760px) 55vw, 540px'
    if 'gallery-mosaic--aligned' in ancestors:
        return '(max-width: 640px) 48vw, (max-width: 980px) 32vw, 300px'
    if 'mosaic-tile' in ancestors:
        return '(max-width: 760px) 48vw, (max-width: 980px) 32vw, 400px'
    if any(token in ancestors for token in ('kb-topic-card', 'kb-card')):
        return '(max-width: 760px) 100vw, (max-width: 1020px) 50vw, 400px'
    if 'puppy-media' in ancestors or 'rs-photo' in ancestors:
        return '(max-width: 760px) 90vw, 420px'
    if 'article-figure' in ancestors:
        return '(max-width: 1020px) 100vw, 840px'
    return '(max-width: 800px) 100vw, 720px'

def set_attr(tag, name, value):
    attr = f'{name}="{escape(value, quote=True)}"'
    pattern = r'\b' + re.escape(name) + r'="[^"]*"'
    if re.search(pattern, tag):
        return re.sub(pattern, lambda _: attr, tag)
    return re.sub(r'\s*/?>$', lambda m: ' ' + attr + m[0], tag)

placements = 0
for page in PAGES:
    source = page.read_text(encoding='utf8')
    doc = html.fromstring(source)
    images = iter(doc.xpath('//img'))
    def image_tag(match):
        global placements
        img = next(images)
        entry = manifest.get(img.get('src'))
        if not entry:
            return match[0]
        tag = set_attr(match[0], 'srcset', ', '.join(f'{v["src"]} {v["width"]}w' for v in entry['variants']))
        tag = set_attr(tag, 'sizes', sizes_for(img))
        tag = set_attr(tag, 'decoding', 'async')
        placements += 1
        return tag
    source = re.sub(r'<img\b[^>]*>', image_tag, source)
    # Avoid downloading the original as well as the responsive contact image.
    def preload(match):
        tag = match[0]
        node = html.fromstring(tag)
        entry = manifest.get(node.get('href'))
        if not entry:
            return tag
        tag = set_attr(tag, 'imagesrcset', ', '.join(f'{v["src"]} {v["width"]}w' for v in entry['variants']))
        return set_attr(tag, 'imagesizes', '(max-width: 800px) 100vw, 720px')
    source = re.sub(r'<link\b[^>]*rel="preload"[^>]*as="image"[^>]*>', preload, source)
    page.write_text(source, encoding='utf8')

(DEST/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf8')
original_bytes = sum(v['originalBytes'] for v in manifest.values())
large_bytes = sum(v['variants'][-1]['bytes'] for v in manifest.values())
print(json.dumps({'photos': len(manifest), 'placements': placements, 'originalBytes': original_bytes, 'largestWebpBytes': large_bytes, 'reductionPercent': round(100*(1-large_bytes/original_bytes),1)}, indent=2))
