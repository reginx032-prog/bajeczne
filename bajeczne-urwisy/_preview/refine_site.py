"""One-time markup corrections, preserving the existing document formatting."""
from pathlib import Path
from shutil import copy2
import re
from lxml import html

ROOT = Path(__file__).resolve().parent.parent
BACKUP = ROOT / '_preview' / 'before-mobile-seo'
BACKUP.mkdir(exist_ok=True)
PHONE = '<svg class="ico" aria-hidden="true" focusable="false" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3 19.5 19.5 0 0 1-6-6 19.8 19.8 0 0 1-3-8.6A2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/></svg>'

def add_class(tag, name):
    match = re.search(r'class="([^"]*)"', tag)
    if match:
        if name in match[1].split():
            return tag
        return tag[:match.start(1)] + match[1] + ' ' + name + tag[match.end(1):]
    return tag[:-1] + ' class="' + name + '">'

stats = {'footerPhones': 0, 'newButtonIcons': 0, 'scrollableTables': 0}
for path in [*ROOT.glob('*.html'), ROOT/'styles.css', ROOT/'script.js', ROOT/'site-audit.css']:
    if not (BACKUP/path.name).exists():
        copy2(path, BACKUP/path.name)

for path in ROOT.glob('*.html'):
    source = path.read_text(encoding='utf-8-sig')
    def footer(match):
        block = match[0]
        def phone(m):
            opening, content = m[1], m[2]
            opening = add_class(opening, 'footer-phone')
            if '<svg' not in content:
                content = PHONE + ' ' + content.strip()
            stats['footerPhones'] += 1
            return opening + content + '</a>'
        return re.sub(r'(<a\b[^>]*href="tel:[^"]*"[^>]*>)(.*?)</a>', phone, block, flags=re.S)
    source = re.sub(r'<footer\b.*?</footer>', footer, source, flags=re.S)
    def button_phone(match):
        opening, content = match[1], match[2]
        classes = re.search(r'class="([^"]*)"', opening)
        if classes and 'btn' in classes[1].split() and '<svg' not in content:
            content = PHONE + ' ' + content.strip()
            stats['newButtonIcons'] += 1
        return opening + content + '</a>'
    source = re.sub(r'(<a\b[^>]*href="tel:[^"]*"[^>]*>)(.*?)</a>', button_phone, source, flags=re.S)
    def header(match):
        def phone(m):
            opening, content = m[1], m[2]
            opening = add_class(opening, 'nav-phone')
            if 'aria-label=' not in opening:
                opening = opening[:-1] + ' aria-label="Zadzwoń: 601 074 022">'
            if 'nav-phone__label' not in content:
                content = re.sub(r'601\s+074\s+022', '<span class="nav-phone__label">601 074 022</span>', content)
            return opening + content + '</a>'
        block = re.sub(r'(<a\b[^>]*href="tel:[^"]*"[^>]*>)(.*?)</a>', phone, match[0], flags=re.S)
        block = re.sub(r'<nav class="nav" id="nav">', '<nav class="nav" id="nav" aria-label="Nawigacja główna">', block)
        return block
    source = re.sub(r'<header\b.*?</header>', header, source, flags=re.S)
    if 'class="mobile-call' in source or re.search(r'class="[^"]*\bmobile-call\b', source):
        source = re.sub(r'<body\b[^>]*>', lambda m: add_class(m[0], 'has-mobile-call'), source, count=1)
    source = source.replace('href="kontakt.html#kontakt-tresc"', 'href="#kontakt-tresc"')
    # Tables keep their header relationship and can be scrolled with a keyboard.
    def table(match):
        tag = match[0]
        if 'tabindex=' not in tag:
            tag = tag[:-1] + ' tabindex="0" role="region" aria-label="Tabela porównawcza, przewiń w poziomie">'
            stats['scrollableTables'] += 1
        return tag
    source = re.sub(r'<div\b[^>]*class="article-table-wrap"[^>]*>', table, source)
    source = re.sub(r'<th(\s[^>]*)?>', lambda m: m[0] if 'scope=' in m[0] else m[0][:-1] + ' scope="col">', source)
    source = re.sub(r'(?<=[?&])v=20260918-(?:audit1|mobile2)', 'v=20260918-mobile2', source)
    path.write_text(source, encoding='utf-8')
print(stats)
