"""Offline site-wide integrity audit. No external requests or browser navigation."""
from collections import Counter
from pathlib import Path
from urllib.parse import unquote, urlsplit
import json
import re
import sys
from lxml import html, etree
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
PAGES = sorted(ROOT.glob('*.html'))
DOCS = {p.name: html.fromstring(p.read_text(encoding='utf-8-sig')) for p in PAGES}
issues = []
stats = Counter()
image_sizes = {}

def size_of(path):
    if path not in image_sizes:
        with Image.open(path) as image:
            image_sizes[path] = image.size
    return image_sizes[path]
def issue(page, kind, detail):
    issues.append(dict(page=page, kind=kind, detail=detail))
def has_class(node, name):
    return name in node.get('class', '').split()

for page in PAGES:
    doc = DOCS[page.name]
    stats['pages'] += 1
    for ident, count in Counter(doc.xpath('//@id')).items():
        if count > 1: issue(page.name, 'duplicate-id', ident)
    for selector, wanted in [('//h1', 1), ('//main', 1), ('//title', 1), ('//meta[@name="description"]', 1)]:
        if len(doc.xpath(selector)) != wanted: issue(page.name, 'page-structure', selector)
    if not doc.xpath('//a[contains(@class,"skip")]'): issue(page.name, 'skip-link', 'Missing main-content shortcut')
    for el in doc.xpath('//*[@href or @src]'):
        value = el.get('href') or el.get('src')
        parsed = urlsplit(value)
        if parsed.scheme or parsed.netloc or value.startswith('//'): continue
        target = ROOT/unquote(parsed.path) if parsed.path else page
        stats['localReferences'] += 1
        if not target.is_file():
            issue(page.name, 'missing-file', value)
            continue
        if parsed.fragment and target.suffix in ['.html', '.svg']:
            targetdoc = DOCS.get(target.name) if target.suffix == '.html' else etree.parse(str(target))
            if targetdoc is not None and parsed.fragment not in targetdoc.xpath('//@id'):
                issue(page.name, 'missing-fragment', value)
        if el.tag == 'use':
            stats['svgUses'] += 1
            if parsed.path: issue(page.name, 'external-svg-use', value)
    for img in doc.xpath('//img'):
        stats['images'] += 1
        if img.get('alt') is None: issue(page.name, 'image-alt', img.get('src'))
        if not img.get('width') or not img.get('height'): issue(page.name, 'image-dimensions', img.get('src'))
        target = ROOT/unquote(urlsplit(img.get('src','')).path)
        if target.is_file() and target.suffix.lower() in ('.png','.jpg','.jpeg','.webp'):
            if (img.get('width'),img.get('height')) != tuple(map(str,size_of(target))):
                issue(page.name, 'wrong-image-dimensions', img.get('src'))
        for candidate in img.get('srcset','').split(','):
            if not candidate.strip(): continue
            src, width = candidate.strip().rsplit(' ',1)
            target = ROOT/unquote(urlsplit(src).path)
            stats['responsiveCandidates'] += 1
            if not target.is_file(): issue(page.name, 'missing-responsive-image', src)
            elif width != str(size_of(target)[0])+'w': issue(page.name, 'wrong-responsive-width', src)
        if img.get('srcset') and not img.get('sizes'): issue(page.name, 'missing-image-sizes', img.get('src'))
    for control in doc.xpath('//button | //*[@role="button"] | //a'):
        name = control.get('aria-label') or control.get('aria-labelledby') or ''.join(control.itertext()).strip()
        if not name: name = ' '.join(control.xpath('.//img/@alt'))
        if not name: issue(page.name, 'unnamed-control', etree.tostring(control, encoding='unicode')[:180])
    for toggle in doc.xpath('//button[contains(@class,"nav-sub-toggle")]'):
        if not toggle.get('aria-controls'): issue(page.name, 'submenu-controls', toggle.text_content().strip())
    for el in doc.xpath('//*[@target="_blank"]'):
        if 'noopener' not in el.get('rel',''): issue(page.name, 'new-tab-rel', el.get('href'))
    for svg in doc.xpath('//svg[contains(@class,"ico")]'):
        if not svg.get('aria-hidden') and not svg.get('aria-label'): issue(page.name, 'decorative-svg', 'Icon is exposed to assistive technology')
        stats['icons'] += 1
        if not svg.get('viewbox') or not len(svg): issue(page.name, 'empty-icon', str(svg.sourceline))
        if svg.get('fill') == 'none' and not svg.get('stroke') and not svg.xpath('.//*[@fill or @stroke]'):
            issue(page.name, 'invisible-icon', str(svg.sourceline))
    phones = doc.xpath('//footer//a[starts-with(@href,"tel:")]')
    if len(phones) != 1: issue(page.name, 'footer-phone', 'Expected one telephone link in the footer')
    for phone in phones + doc.xpath('//a[starts-with(@href,"tel:") and contains(concat(" ", normalize-space(@class), " "), " btn ")]'):
        if not phone.xpath('.//svg'): issue(page.name, 'missing-phone-icon', str(phone.sourceline))
    for el in doc.xpath('//*[@aria-controls or @aria-labelledby]'):
        for ident in (el.get('aria-controls','')+' '+el.get('aria-labelledby','')).split():
            if ident not in doc.xpath('//@id'): issue(page.name, 'missing-aria-target', ident)
    for name in ['og:title', 'og:description', 'og:type', 'og:locale', 'og:site_name']:
        if len(doc.xpath('//meta[@property=$name]', name=name)) != 1: issue(page.name, 'social-metadata', name)
    structured = doc.xpath('//script[@type="application/ld+json"]')
    if len(structured) != 1: issue(page.name, 'structured-data', 'Expected one JSON-LD graph')
    for item in structured:
        try: json.loads(item.text)
        except (TypeError, ValueError): issue(page.name, 'invalid-json-ld', 'JSON parse error')
    if not doc.xpath('//link[@rel="canonical"]'): stats['pagesWithoutCanonical'] += 1
    if not doc.xpath('//meta[@property="og:image"]'): stats['pagesWithoutSocialImage'] += 1
    for node in doc.xpath('//iframe'):
        if not node.get('title'): issue(page.name, 'iframe-title', node.get('src'))
    for node in doc.xpath('//input[not(@type="hidden")] | //select | //textarea'):
        if not node.get('aria-label') and not node.get('aria-labelledby') and not doc.xpath('//label[@for=$id]', id=node.get('id','')):
            issue(page.name, 'input-label', node.get('name'))

css='\n'.join(p.read_text(encoding='utf8') for p in ROOT.glob('*.css'))
for xpath, label in [('//title/text()', 'duplicate-title'), ('//meta[@name="description"]/@content', 'duplicate-description')]:
    values = Counter(d.xpath(xpath)[0] for d in DOCS.values())
    for value, count in values.items():
        if count > 1: issue('pages', label, value)
for url in re.findall(r'url\(\s*[\"\']?([^\)\"\']+)',css):
    if url.startswith(('data:', 'http:', 'https:', '#')): continue
    if not (ROOT/unquote(urlsplit(url).path)).is_file(): issue('stylesheets','missing-file',url)
report = dict(stats=dict(stats), counts=dict(Counter(i['kind'] for i in issues)), issues=issues)
suffix=sys.argv[1] if len(sys.argv)>1 else 'latest'
destination=ROOT/'_preview'/('site-audit-'+suffix+'.json')
destination.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(dict(stats=report['stats'], counts=report['counts'], examples=issues[:8]),ensure_ascii=True,indent=2))
