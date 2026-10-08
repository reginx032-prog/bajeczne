"""Build browser icons from the existing Bajeczne Urwisy logo mark.

The source logo remains unchanged. Run with Python and Pillow.
"""
from pathlib import Path
import re

from PIL import Image, ImageChops, ImageFilter, ImageOps


ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / 'assets'
PREFIX = 'favicon-bajeczne-urwisy'

# Preserve the original drawing and make its thin lines readable at tab sizes.
with Image.open(ASSETS / 'logo-dog-mark.png') as source:
    source = source.convert('RGBA')
    ink = ImageChops.multiply(source.getchannel('A'), ImageOps.invert(source.convert('L')))
    ink = ink.point(lambda value: 0 if value < 28 else min(255, round(value * 1.6)))
    ink = ink.crop(ink.getbbox()).filter(ImageFilter.MaxFilter(9))
    mark = Image.new('RGBA', ink.size, '#24231e')
    mark.putalpha(ink)


def icon(size):
    canvas = Image.new('RGBA', (size, size), 'white')
    fitted = ImageOps.contain(mark, (round(size * .86), round(size * .9)), Image.Resampling.LANCZOS)
    canvas.alpha_composite(fitted, ((size - fitted.width) // 2, (size - fitted.height) // 2))
    return canvas


icon(256).save(ASSETS / f'{PREFIX}.ico', sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])
icon(48).save(ASSETS / f'{PREFIX}-48.png', optimize=True)
icon(180).save(ASSETS / f'{PREFIX}-180.png', optimize=True)

links = (
    f'<link rel="icon" href="assets/{PREFIX}.ico" type="image/x-icon" sizes="16x16 32x32 48x48 64x64" />\n'
    f'  <link rel="icon" href="assets/{PREFIX}-48.png" type="image/png" sizes="48x48" />\n'
    f'  <link rel="apple-touch-icon" href="assets/{PREFIX}-180.png" sizes="180x180" />'
)
pages = 0
for page in sorted(ROOT.glob('*.html')):
    content = page.read_bytes().decode('utf8')
    # Idempotent: replace the existing icon declarations without touching other head tags.
    pattern = r'<link\b(?=[^>]*\brel="(?:icon|shortcut icon|apple-touch-icon)")[^>]*>\s*'
    matches = list(re.finditer(pattern, content))
    if not matches:
        raise ValueError(f'Missing icon declaration in {page.name}')
    newline = '\r\n' if '\r\n' in content else '\n'
    first = True

    def replace_icon(match):
        global first
        if not first:
            return ''
        first = False
        return links.replace('\n', newline) + newline + '  '

    updated = re.sub(pattern, replace_icon, content)
    if updated != content:
        page.write_bytes(updated.encode('utf8'))
    pages += 1

print(f'Brand logo icons configured on {pages} pages.')
