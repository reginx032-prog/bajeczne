"""Apply the site audit's markup repairs without reformatting page content."""
from pathlib import Path
from html import escape
from urllib.parse import unquote
import re
import shutil
from lxml import etree, html
from PIL import Image

ROOT=Path(__file__).resolve().parent.parent
BACKUP=ROOT/'_preview/site-before-audit'
BACKUP.mkdir(exist_ok=True)
pages=sorted(ROOT.glob('*.html'))
for path in [*pages,ROOT/'script.js',ROOT/'styles.css']:
    if not (BACKUP/path.name).exists(): shutil.copy2(path,BACKUP/path.name)

symbols={}
def collect_symbols(source):
    found={}
    for match in re.finditer(r'<symbol\b[^>]*>.*?</symbol>',source,re.S):
        symbol=etree.fromstring(match.group().encode())
        found[symbol.get('id')]=symbol
    return found
for page in pages: symbols.update(collect_symbols(page.read_text(encoding='utf8')))
external=collect_symbols((ROOT/'assets/icons.svg').read_text(encoding='utf8'))
symbols.update(external)
footer=re.search(r'<footer\b.*?</footer>',(ROOT/'baza-wiedzy.html').read_text(encoding='utf8'),re.S).group()
counts={'inlinedIcons':0,'imageDimensions':0,'repairedFooters':0}

for path in pages:
    source=path.read_text(encoding='utf8')
    local=collect_symbols(source)
    if path.name in ['chihuahua.html','maltanczyk.html','rasy.html']:
        source=re.sub(r'<footer\b.*?</footer>',lambda _:footer,source,flags=re.S)
        counts['repairedFooters']+=1
    def inline_icon(match):
        attrs,reference=match.group(1),match.group(2)
        ident=reference.split('#')[-1]
        symbol=(external if reference.startswith('assets/') else local).get(ident)
        if symbol is None: symbol=symbols[ident]
        for key,value in symbol.attrib.items():
            if key=='id': continue
            if not re.search(r'\b'+re.escape(key)+r'\s*=',attrs): attrs+=' '+key+'="'+escape(value,quote=True)+'"'
        if 'aria-hidden=' not in attrs: attrs+=' aria-hidden="true"'
        if 'focusable=' not in attrs: attrs+=' focusable="false"'
        children=''.join(etree.tostring(c,encoding='unicode',with_tail=False) for c in symbol)
        if ident=='i-heart':
            children='<path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78L12 21.23l8.84-8.84a5.5 5.5 0 0 0 0-7.78Z"/>'
        counts['inlinedIcons']+=1
        return '<svg'+attrs+'>'+children+'</svg>'
    source=re.sub(r'<svg\b([^>]*)>\s*<use\b[^>]*\bhref="([^"]+)"[^>]*/>\s*</svg>',inline_icon,source)
    assert '<use ' not in source,path.name
    # Every icon is decorative; its button/link already supplies the name.
    def hide_icon(match):
        tag=match.group()
        if 'aria-label=' not in tag and 'aria-hidden=' not in tag: tag=tag[:-1]+' aria-hidden="true">'
        if 'focusable=' not in tag: tag=tag[:-1]+' focusable="false">'
        return tag
    source=re.sub(r'<svg\b[^>]*\bclass="[^"]*\bico\b[^"]*"[^>]*>',hide_icon,source)
    source=re.sub(r'<svg\b[^>]*>\s*(?:<symbol\b.*?</symbol>\s*)+</svg>\s*','',source,flags=re.S)

    def dimensions(match):
        tag=match.group()
        element=html.fromstring(tag)
        if element.get('width') and element.get('height'): return tag
        src=element.get('src','')
        if src.startswith(('http:','https:','data:')): return tag
        with Image.open(ROOT/unquote(src)) as image: width,height=image.size
        additions=''
        if not element.get('width'): additions+=' width="'+str(width)+'"'
        if not element.get('height'): additions+=' height="'+str(height)+'"'
        if not element.get('decoding'): additions+=' decoding="async"'
        counts['imageDimensions']+=1
        return re.sub(r'\s*/?>$',lambda m:additions+m.group(),tag)
    source=re.sub(r'<img\b[^>]*>',dimensions,source)

    if not re.search(r'<a[^>]+class="[^"]*skip',source):
        main=re.search(r'<main\b([^>]*)>',source)
        attrs=main.group(1)
        existing_id=re.search(r'\bid="([^"]+)"',attrs)
        ident=existing_id.group(1) if existing_id else 'main-content'
        if not existing_id: attrs+=' id="'+ident+'"'
        if 'tabindex=' not in attrs: attrs+=' tabindex="-1"'
        source=source[:main.start()]+'<main'+attrs+'>'+source[main.end():]
        source=re.sub(r'(<body\b[^>]*>)',lambda m:m.group()+'\n<a class="skip-link" href="#'+ident+'">Przejdź do treści</a>',source,count=1)
    source=source.replace('aria-controls="nav"','aria-controls="main-navigation"')
    source=re.sub(r'<ul class="nav-links"[^>]*>', '<ul class="nav-links" id="main-navigation">',source,count=1)
    # Gallery is a disclosure, matching the existing breeds disclosure.
    source=re.sub(r'<a\b[^>]*>Galeria (.*?)</a>\s*(<div class="nav-sub")',
                  r'<button class="nav-sub-toggle" type="button" aria-expanded="false">Galeria \1</button>\2',source,flags=re.S)
    counter=[0]
    def disclosure(match):
        attrs,content=match.group(1),match.group(2)
        counter[0]+=1
        ident='nav-submenu-'+str(counter[0])
        attrs=re.sub(r'\saria-haspopup="[^"]*"','',attrs)
        attrs=re.sub(r'\saria-controls="[^"]*"','',attrs)
        return '<button'+attrs+' aria-controls="'+ident+'">'+content+'</button><div class="nav-sub" id="'+ident+'"'
    source=re.sub(r'<button\b([^>]*class="nav-sub-toggle"[^>]*)>(.*?)</button>\s*<div class="nav-sub"',disclosure,source,flags=re.S)
    source=source.replace('href="https://www.facebook.com/"','href="https://www.facebook.com/BajeczneUrwisy"')
    source=source.replace('href="https://www.instagram.com/"','href="https://www.instagram.com/bajeczneurwisy/"')
    source=re.sub(r'(href="styles\.css)(?:\?[^\"]*)?"',r'\1?v=20260918-audit1"',source)
    source=re.sub(r'(src="script\.js)(?:\?[^\"]*)?"',r'\1?v=20260918-audit1"',source)
    if 'site-audit.css' not in source:
        source=source.replace('</head>','  <link rel="stylesheet" href="site-audit.css?v=20260918-audit1" />\n</head>')
    if path.name=='index.html':
        source=source.replace('<p class="review-note reveal">','<button class="motion-toggle" type="button" data-motion-toggle aria-pressed="false">Wstrzymaj animacje</button>\n    <p class="review-note reveal">')
    path.write_text(source,encoding='utf8',newline='\n')
print(counts)
