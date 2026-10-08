"""Offline integrity, crawlability and deployment checks; no browser simulation."""
from collections import Counter, deque
from pathlib import Path
from urllib.parse import urlsplit, unquote
from urllib.robotparser import RobotFileParser
import argparse
import json
import re
import xml.etree.ElementTree as ET

from lxml import html

ROOT = Path(__file__).resolve().parent.parent
BASE = json.loads((ROOT/'site-config.json').read_bytes())['baseUrl']
PAGES = sorted(ROOT.glob('*.html'))
DOCS = {p.name: html.fromstring(p.read_bytes().decode('utf8')) for p in PAGES}
SITEMAP_NS = {'s':'http://www.sitemaps.org/schemas/sitemap/0.9', 'i':'http://www.google.com/schemas/sitemap-image/1.1'}


def public_url(name):
    return BASE+('' if name=='index.html' else name)


def visible_text(doc):
    clone = html.fromstring(html.tostring(doc, encoding='unicode'))
    for node in clone.xpath('//script | //style | //*[@data-gallery-mosaic]'):
        node.getparent().remove(node)
    return ' '.join(' '.join(clone.xpath('//body//text()')).split())


def check(copy_baseline=None):
    titles=[];descriptions=[];links={};image_count=0
    robots=RobotFileParser()
    robots.parse((ROOT/'robots.txt').read_text(encoding='utf8').splitlines())
    for name,doc in DOCS.items():
        assert doc.get('lang')=='pl',name
        assert len(doc.xpath('//h1'))==1,name
        assert doc.xpath('//meta[@name="viewport" and contains(@content,"width=device-width")]'),name
        assert doc.xpath('//link[@rel="canonical"]/@href')==[public_url(name)],name
        assert doc.xpath('//meta[@property="og:url"]/@content')==[public_url(name)],name
        assert 'noindex' not in doc.xpath('string(//meta[@name="robots"]/@content)'),name
        assert robots.can_fetch('Googlebot',public_url(name)),name
        title=doc.xpath('string(//title)').strip();description=doc.xpath('string(//meta[@name="description"]/@content)').strip()
        assert title and description,name
        titles.append(title);descriptions.append(description)
        for script in doc.xpath('//script[@src]'):
            assert script.get('defer') is not None,name
        payloads=doc.xpath('//script[@type="application/ld+json"]/text()')
        assert len(payloads)==1,name
        graph=json.loads(payloads[0])['@graph']
        ids=[n['@id'] for n in graph if '@id' in n]
        assert len(ids)==len(set(ids)),name
        for node in graph:
            if node['@type']=='ImageObject':
                assert (ROOT/unquote(node['contentUrl'].removeprefix(BASE))).is_file(),name
        assert {'Organization','WebSite','ImageObject'}.issubset({n['@type'] for n in graph}),name
        links[name]=set()
        for a in doc.xpath('//a[@href]'):
            url=urlsplit(a.get('href'))
            if not url.scheme and not url.netloc and url.path.endswith('.html'):
                links[name].add(unquote(url.path))
        for image in doc.xpath('//main//img'):
            assert image.get('alt') is not None and image.get('width') and image.get('height'),name
            image_count+=1
        deployed=ROOT/'_publish'/name
        assert deployed.is_file(),name
        assert visible_text(doc)==visible_text(html.fromstring(deployed.read_bytes().decode('utf8'))),name
        if copy_baseline is not None:
            baseline=copy_baseline/name
            assert baseline.is_file(),f'Missing copy baseline: {name}'
            assert visible_text(doc)==visible_text(html.fromstring(baseline.read_bytes().decode('utf8'))),f'Visible copy changed: {name}'
    assert all(n==1 for n in Counter(titles).values()),'Repeated titles'
    assert all(n==1 for n in Counter(descriptions).values()),'Repeated descriptions'
    visited=set();queue=deque(['index.html'])
    while queue:
        name=queue.popleft()
        if name in visited:continue
        assert name in links,name
        visited.add(name);queue.extend(links[name]-visited)
    assert visited==set(DOCS),'Unreachable public page'
    sitemap=ET.parse(ROOT/'sitemap.xml')
    urls=sitemap.findall('s:url',SITEMAP_NS)
    assert {n.find('s:loc',SITEMAP_NS).text for n in urls}=={public_url(p.name) for p in PAGES}
    image_urls=sitemap.findall('.//i:loc',SITEMAP_NS)
    for node in image_urls:
        assert node.text.startswith(BASE)
        assert (ROOT/unquote(node.text.removeprefix(BASE))).is_file(),node.text
        assert robots.can_fetch('Googlebot-Image',node.text),node.text
    for doc in DOCS.values():
        for image in doc.xpath('//*[@data-gallery-mosaic]//img'):
            assert any(unquote(n.text.removeprefix(BASE))==image.get('src') for n in image_urls),image.get('src')
    manifest=json.loads((ROOT/'_preview/deployment-manifest.json').read_bytes())
    actual={p.relative_to(ROOT/'_publish').as_posix() for p in (ROOT/'_publish').rglob('*') if p.is_file()}
    assert actual==set(manifest['files']),'Unexpected file in publication folder'
    assert not any(p.startswith(('_preview/','tools/','data/','facebook-posts/')) or p.endswith(('.py','.md','.json')) for p in actual)
    for path in (ROOT/'_publish').glob('*.html'):
        source=path.read_text(encoding='utf8')
        assert '<!--' not in source
        assert not re.search(r'codex|chatgpt|request_user_input|send_user_message|<INSTRUCTIONS>',source,re.I),path.name
    print(json.dumps({'pages':len(DOCS),'reachablePages':len(visited),'sitemapPages':len(urls),
                      'imageSitemapEntries':len(image_urls),'mainImages':image_count,
                      'uniqueTitles':len(set(titles)),'uniqueDescriptions':len(set(descriptions)),
                      'publishedCopyMatchesSource':True,'copyBaselineChecked':copy_baseline is not None,
                      'cleanDeploymentFiles':len(actual)},indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--copy-baseline',type=Path,help='Optional approved HTML snapshot to compare visible copy against')
    args=parser.parse_args()
    check(args.copy_baseline.resolve() if args.copy_baseline else None)
