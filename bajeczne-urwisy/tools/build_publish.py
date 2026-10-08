"""Build a clean static deployment containing only public pages and used assets.

Keeps readable source files in the project. Updates CSS/JS URL fingerprints to
share cached assets across pages, then copies a dependency-checked public set.
"""
from hashlib import sha256
from pathlib import Path
from urllib.parse import urlsplit, unquote
from lxml import html
import gzip
import json
import re
import shutil

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT/'_publish'
REPORT = ROOT/'_preview/deployment-manifest.json'


def refresh_asset_versions():
    for page in ROOT.glob('*.html'):
        original = page.read_bytes().decode('utf8')
        def replace(match):
            attribute, asset = match.groups()
            fingerprint = sha256((ROOT/asset).read_bytes()).hexdigest()[:12]
            return f'{attribute}="{asset}?v={fingerprint}"'
        updated = re.sub(r'(href|src)="([a-z-]+\.(?:css|js))(?:\?[^"\s]*)?"', replace, original)
        updated = re.sub(r'<script (?![^>]*\bdefer\b)(src="script\.js[^>]+)>', r'<script defer \1>', updated)
        if updated != original:
            page.write_bytes(updated.encode('utf8'))


def collect_files():
    base = json.loads((ROOT/'site-config.json').read_bytes())['baseUrl']
    if not base:
        raise ValueError('Set the production HTTPS domain with prepare_seo.py first.')
    files = {p.name for p in ROOT.glob('*.html')} | {'robots.txt','sitemap.xml','.htaccess'}
    queue = list(files)
    def add(value, parent=''):
        if not value:
            return
        if value.startswith(base):
            value = value[len(base):]
        parsed = urlsplit(value)
        if parsed.scheme or parsed.netloc or not parsed.path:
            return
        path = (ROOT/parent/unquote(parsed.path)).resolve()
        if not path.is_relative_to(ROOT.resolve()):
            raise ValueError(f'Asset outside project: {value}')
        relative = path.relative_to(ROOT.resolve()).as_posix()
        if relative.startswith(('_preview/', '_publish/', 'tools/', 'data/', 'facebook-posts/')):
            raise ValueError(f'Private dependency in public page: {relative}')
        if not path.is_file():
            raise FileNotFoundError(path)
        if relative not in files:
            files.add(relative)
            queue.append(relative)
    while queue:
        relative = queue.pop()
        path = ROOT/relative
        if path.suffix == '.html':
            text = path.read_text(encoding='utf8')
            doc = html.fromstring(text)
            for node in doc.xpath('//*[@src or @href]'):
                for attribute in ('src','href'):
                    add(node.get(attribute))
            for value in doc.xpath('//@srcset | //@imagesrcset'):
                for candidate in value.split(','):
                    add(candidate.strip().rsplit(' ',1)[0])
            for value in doc.xpath('//meta[@property="og:image"]/@content | //meta[@name="twitter:image"]/@content'):
                add(value)
            for value in re.findall(r"this\.src=['\"]([^'\"]+)",text):
                add(value)
        elif path.suffix == '.css':
            for value in re.findall(r'url\(\s*[\'\"]?([^\)\'\"]+)',path.read_text(encoding='utf8')):
                add(value, path.parent.relative_to(ROOT).as_posix())
    return files


def build():
    refresh_asset_versions()
    files = collect_files()
    OUTPUT.mkdir(exist_ok=True)
    for relative in sorted(files):
        source = ROOT/relative
        target = OUTPUT/relative
        target.parent.mkdir(parents=True,exist_ok=True)
        if source.suffix == '.html':
            text = re.sub(r'<!--.*?-->', '', source.read_bytes().decode('utf8'), flags=re.S)
            target.write_bytes(text.encode('utf8'))
        else:
            shutil.copy2(source,target)
    # Remove only files owned by the previous deployment build.
    if REPORT.exists():
        for relative in set(json.loads(REPORT.read_bytes())['files'])-files:
            target = (OUTPUT/relative).resolve()
            if not target.is_relative_to(OUTPUT.resolve()):
                raise ValueError('Deployment cleanup path escaped the output directory.')
            if target.is_file():
                target.unlink()
    text_files = [ROOT/p for p in files if Path(p).suffix in ('.html','.css','.js','.xml','.txt','.svg')]
    report = {'files':sorted(files),'fileCount':len(files),'bytes':sum((OUTPUT/p).stat().st_size for p in files),
              'textBytes':sum(p.stat().st_size for p in text_files),
              'textGzipBytes':sum(len(gzip.compress(p.read_bytes())) for p in text_files)}
    REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:v for k,v in report.items() if k!='files'},indent=2))


if __name__ == '__main__':
    build()
