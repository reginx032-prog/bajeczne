"""Add intermediate responsive sizes without changing original images or layout."""
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
from html import escape
from pathlib import Path
from urllib.parse import unquote
import json
import re

from lxml import html
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT/'assets/optimized/manifest.json'


def set_attribute(tag, name, value):
    attribute = f'{name}="{escape(value, quote=True)}"'
    pattern = r'\b'+re.escape(name)+r'="[^"]*"'
    if re.search(pattern, tag):
        return re.sub(pattern, lambda _: attribute, tag)
    return re.sub(r'\s*/?>$', lambda m: ' '+attribute+m[0], tag)


def create_variant(job):
    src, width, lossless = job
    path = ROOT/unquote(src)
    digest = sha256(path.read_bytes()).hexdigest()[:12]
    stem = re.sub(r'[^a-z0-9-]+', '-', path.stem.lower())[:65].strip('-')
    target = ROOT/f'assets/optimized/{stem}-{digest}-{width}.webp'
    with Image.open(path) as original:
        image = ImageOps.exif_transpose(original)
        height = round(image.height*width/image.width)
        if not target.exists():
            image.resize((width, height), Image.Resampling.LANCZOS).save(target, 'WEBP', quality=90, lossless=lossless, method=5)
    return src, {'src': target.relative_to(ROOT).as_posix(), 'width': width, 'height': height, 'bytes': target.stat().st_size}


def optimize():
    manifest = json.loads(MANIFEST.read_bytes())
    pages = sorted(ROOT.glob('*.html'))
    sources = {i.get('src') for p in pages for i in html.fromstring(p.read_bytes().decode('utf8')).xpath('//img[@src]')}
    jobs = [(src, 600, False) for src in sorted(sources) if src in manifest
            and any(v['width'] > 600 for v in manifest[src]['variants'])
            and not any(v['width'] == 600 for v in manifest[src]['variants'])]
    for src in ('assets/logo-swkipr.png', 'assets/opinie/op-7.jpg', 'assets/opinie/op-3.jpg'):
        if src in sources and src not in manifest:
            with Image.open(ROOT/src) as image:
                jobs.append((src, image.width, src.endswith('.png')))
    created = 0
    with ThreadPoolExecutor(max_workers=4) as pool:
        for src, variant in pool.map(create_variant, jobs):
            entry = manifest.setdefault(src, {'originalBytes': (ROOT/src).stat().st_size, 'variants': []})
            entry['variants'].append(variant)
            entry['variants'].sort(key=lambda v: v['width'])
            created += 1
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
    for path in pages:
        original = path.read_bytes().decode('utf8')
        nodes = iter(html.fromstring(original).xpath('//img'))
        def update_image(match):
            node = next(nodes)
            entry = manifest.get(node.get('src'))
            if not entry:
                return match[0]
            tag = set_attribute(match[0], 'srcset', ', '.join(f'{v["src"]} {v["width"]}w' for v in entry['variants']))
            if not node.get('sizes'):
                tag = set_attribute(tag, 'sizes', f'{node.get("width")}px')
            return tag
        updated = re.sub(r'<img\b[^>]*>', update_image, original)
        def update_preload(match):
            node = html.fromstring(match[0])
            entry = manifest.get(node.get('href'))
            if not entry:
                return match[0]
            return set_attribute(match[0], 'imagesrcset', ', '.join(f'{v["src"]} {v["width"]}w' for v in entry['variants']))
        updated = re.sub(r'<link\b[^>]*rel="preload"[^>]*as="image"[^>]*>', update_preload, updated)
        if updated != original:
            path.write_bytes(updated.encode('utf8'))
    pairs = [(next(v['bytes'] for v in e['variants'] if v['width']==600), next(v['bytes'] for v in e['variants'] if v['width']==800))
             for e in manifest.values() if {600,800}.issubset({v['width'] for v in e['variants']})]
    total600, total800 = map(sum, zip(*pairs)) if pairs else (0,0)
    print(json.dumps({'newVariants': created, 'comparableImages': len(pairs), 'bytes600': total600, 'bytes800': total800,
                      'smallerTierSavingPercent': round(100*(1-total600/total800),1) if total800 else 0}, indent=2))


if __name__ == '__main__':
    optimize()
