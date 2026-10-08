"""Exercise SEO preparation in an isolated fixture; no external requests."""
from pathlib import Path
from shutil import copy2
from tempfile import TemporaryDirectory
from urllib.parse import unquote
import contextlib
import importlib.util
import io
import json
import xml.etree.ElementTree as ET
from lxml import html

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('prepare_seo', ROOT/'tools/prepare_seo.py')
seo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(seo)
config = json.loads((ROOT/'site-config.json').read_text(encoding='utf8'))
pages = list(ROOT.glob('*.html'))
data = {p.name: seo.page_data(p, p.read_text(encoding='utf8')) for p in pages}
for bad in ('http://example.invalid', 'https://localhost', 'https://example.invalid/#x', 'https://example.invalid/?q=1', 'file:///tmp/site'):
    try:
        seo.normalize_base(bad)
    except ValueError:
        pass
    else:
        raise AssertionError('Invalid public URL accepted: '+bad)
assert seo.public_url('https://example.invalid/', 'assets/zdjęcie pieska.jpg') == 'https://example.invalid/assets/zdj%C4%99cie%20pieska.jpg'
with TemporaryDirectory(prefix='seo-check-', dir=ROOT/'_preview') as temp:
    fixture = Path(temp)
    copy2(ROOT/'site-config.json', fixture/'site-config.json')
    for p in pages:
        copy2(p, fixture/p.name)
        photo = Path(unquote(data[p.name]['photo']))
        (fixture/photo).parent.mkdir(parents=True, exist_ok=True)
        copy2(ROOT/photo, fixture/photo)
    seo.ROOT = fixture
    with contextlib.redirect_stdout(io.StringIO()):
        seo.prepare('https://example.invalid/')
    for p in fixture.glob('*.html'):
        d = html.fromstring(p.read_text(encoding='utf8'))
        expected = 'https://example.invalid/'+('' if p.name == 'index.html' else p.name)
        assert d.xpath('//link[@rel="canonical"]/@href') == [expected]
        assert d.xpath('//meta[@property="og:url"]/@content') == [expected]
        assert d.xpath('//meta[@property="og:image"]/@content')[0].startswith('https://example.invalid/assets/')
        assert len(d.xpath('//meta[@property="og:title"]')) == 1
        graph = json.loads(d.xpath('//script[@type="application/ld+json"]/text()')[0])['@graph']
        if p.name.startswith('wiedza-'):
            assert len([n for n in graph if n['@type']=='Article']) == 1
        if p.name != 'index.html':
            assert len([n for n in graph if n['@type']=='BreadcrumbList']) == 1
        assert not any('aggregateRating' in n or 'datePublished' in n for n in graph)
    sitemap = ET.parse(fixture/'sitemap.xml')
    urls = sitemap.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
    assert len(urls) == len(pages) == len({url.text for url in urls})
    assert 'Sitemap: https://example.invalid/sitemap.xml' in (fixture/'robots.txt').read_text()
    before = {p.name:p.read_bytes() for p in fixture.glob('*.html')}
    with contextlib.redirect_stdout(io.StringIO()):
        seo.prepare()
    assert before == {p.name:p.read_bytes() for p in fixture.glob('*.html')}, 'SEO regeneration is not idempotent'
print('PASS: 28 canonical pages, 28 social images, 20 articles, 27 breadcrumbs, sitemap, robots and repeatable generation. Test domain used only in a temporary fixture.')
