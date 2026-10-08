"""Curated gallery photo placements and offline crop review for the knowledge base.

Run without arguments to review crops. --apply updates only knowledge-base pages.
Original gallery images are referenced directly and are never rewritten.
"""
from pathlib import Path
from html import escape
import hashlib
import json
import re
import sys

from PIL import Image, ImageDraw, ImageFont, ImageOps
from lxml import html

ROOT = Path(__file__).resolve().parent.parent
PREVIEW = ROOT / '_preview'
BACKUP = PREVIEW / 'knowledge-before-gallery-photos'
INVENTORY = {p['id']: p for p in json.loads((PREVIEW / 'knowledge-gallery-inventory.json').read_text(encoding='utf8'))}


def photo(key, x, y, scale, alt, label=None):
    item = INVENTORY[key]
    return dict(id=key, src=item['src'], width=item['size'][0], height=item['size'][1],
                x=x, y=y, scale=scale, alt=alt, label=label)


def topic(slug, title, *photos):
    return dict(page='wiedza-' + slug + '.html', title=title, photos=list(photos))


TOPICS = [
    topic('jak-wybrac-hodowle', 'Jak wybrać dobrą hodowlę',
          photo('M04', 53, 51, 1, 'Trzy szczenięta Maltańczyka z hodowli Bajeczne Urwisy na miękkim posłaniu')),
    topic('chihuahua', 'Chihuahua, mały pies z dużym charakterem',
          photo('C36', 53, 7, 1, 'Krótkowłosy Chihuahua z dużymi, stojącymi uszami na jasnym kocu')),
    topic('maltanczyk', 'Maltańczyk w rodzinie',
          photo('M01', 51, 25, 1, 'Biały szczeniak Maltańczyka odpoczywający na podłodze w domu')),
    topic('chihuahua-czy-maltanczyk', 'Chihuahua czy Maltańczyk',
          photo('C06', 60, 44, 1.4, 'Czarny, krótkowłosy szczeniak Chihuahua', 'Chihuahua'),
          photo('M01', 52, 46, 1, 'Biały szczeniak Maltańczyka z puszystą szatą', 'Maltańczyk')),
    topic('wyprawka', 'Wyprawka dla szczeniaka',
          photo('C69', 55, 28, 1, 'Chihuahua na miękkim kocu z materiałową zabawką w kształcie gwiazdy')),
    topic('pierwsze-dni', 'Pierwsze dni w nowym domu',
          photo('C68', 56, 52, 1, 'Chihuahua siedzący na dzianinowym kocu w domowym otoczeniu')),
    topic('zywienie', 'Żywienie psa miniaturowego',
          photo('C55', 56, 52, 1.08, 'Szczeniak Chihuahua z jasnymi łapkami stojący na puszystym kocu')),
    topic('pielegnacja', 'Pielęgnacja bez stresu',
          photo('M10', 51, 25, 1.02, 'Maltańczyk podtrzymywany dłonią opiekuna, widoczna puszysta szata i łapki')),
    topic('zdrowie', 'Zdrowie i kontrola rozwoju',
          photo('C42', 53, 49, 1, 'Mały szczeniak Chihuahua bezpiecznie podtrzymywany dłonią opiekuna')),
    topic('socjalizacja', 'Socjalizacja małego psa',
          photo('M09', 50, 73, 1, 'Dwa szczenięta Maltańczyka z pomarańczową piłeczką w domu')),
    topic('kolory-chihuahua', 'Kolory Chihuahua i zmiany umaszczenia',
          photo('C19', 51, 41, 1.6, 'Chihuahua o czarnej sierści z jasnymi znaczeniami na pyszczku'),
          photo('C34', 47, 50, 1.6, 'Chihuahua o brązowej sierści na białym kocu')),
    topic('siersc-chihuahua', 'Chihuahua krótkowłosa i długowłosa',
          photo('C06', 60, 44, 1.4, 'Chihuahua o krótkiej, gładkiej sierści', 'Krótka szata'),
          photo('C67', 52, 43, 1, 'Chihuahua z dłuższą sierścią na uszach i klatce piersiowej', 'Długa szata')),
    topic('dzieci-i-pies', 'Dzieci i pies miniaturowy',
          photo('C58', 52, 35, 1, 'Maleńki Chihuahua spokojnie podtrzymywany dłonią opiekuna')),
    topic('bezpieczny-dom', 'Bezpieczny dom dla miniaturki',
          photo('M11', 48, 37, 1.5, 'Szczeniak Maltańczyka leżący na podłodze obok wiklinowego fotela')),
    topic('podroz-i-odbior', 'Podróż i odbiór maluszka',
          photo('C70', 50, 25, 1, 'Długowłosy Chihuahua w czerwonych szelkach we wnętrzu samochodu')),
    topic('plan-dnia-szczeniaka', 'Plan dnia szczeniaka',
          photo('M07', 51, 30, 1.08, 'Biały szczeniak Maltańczyka wśród ogrodowej zieleni')),
    topic('nauka-czystosci', 'Nauka czystości bez nerwów',
          photo('M02', 37, 70, 1.3, 'Maltańczyk na podłodze w domowym otoczeniu')),
    topic('szelki-spacer-miniaturka', 'Szelki, obroża i bezpieczne wyjścia',
          photo('C08', 65, 32, 1.12, 'Czarny szczeniak Chihuahua w czerwonych szelkach z przypiętą smyczą')),
    topic('pielegnacja-oczu-maltanczyka', 'Oczy i pyszczek Maltańczyka',
          photo('M10', 52, 22, 1.27, 'Zbliżenie oczu i pyszczka białego szczeniaka Maltańczyka')),
    topic('jezyk-ciala-szczeniaka', 'Jak czytać sygnały szczeniaka',
          photo('C65', 52, 42, 1, 'Chihuahua z przymkniętymi oczami odpoczywający na dłoni opiekuna')),
]
HUB = dict(title='Baza wiedzy: zdjęcie główne', photos=[
    photo('M09', 50, 73, 1, 'Dwa Maltańczyki z hodowli Bajeczne Urwisy obok swojej piłeczki')])
BODY = {
    'wiedza-chihuahua.html': [photo('C67', 51, 29, 1, 'Długowłosy Chihuahua stojący na podłodze w domu')],
    'wiedza-maltanczyk.html': [photo('M07', 51, 29, 1.08, 'Maltańczyk z naszej hodowli w ogrodzie')],
    'wiedza-pielegnacja.html': [photo('M01', 51, 12, 1, 'Maltańczyk z miękką, białą szatą')],
    'wiedza-pierwsze-dni.html': [photo('C69', 55, 25, 1, 'Chihuahua odpoczywający przy miękkiej zabawce na kocu')],
    'wiedza-socjalizacja.html': [photo('M04', 53, 51, 1, 'Szczenięta Maltańczyka przebywające razem na posłaniu')],
    'wiedza-wyprawka.html': [photo('C68', 56, 45, 1, 'Chihuahua na miękkim dzianinowym kocu')],
    'wiedza-zdrowie.html': [photo('C56', 56, 32, 1.15, 'Szczeniak Chihuahua z hodowli Bajeczne Urwisy')],
    'wiedza-zywienie.html': [photo('M01', 51, 12, 1, 'Szczeniak Maltańczyka z hodowli Bajeczne Urwisy')],
}
BY_PAGE = {t['page']: t for t in TOPICS}


def frame(item, eager=False):
    """Focal point applies to both object-position and transform-origin."""
    crop = f'--photo-x:{item["x"]}%;--photo-y:{item["y"]}%;--photo-scale:{item["scale"]}'
    priority = ' fetchpriority="high"' if eager else ''
    label = f'<span class="kb-photo-label">{escape(item["label"])}</span>' if item['label'] else ''
    return (f'<span class="kb-photo-frame" style="{crop}">'
            f'<img src="{escape(item["src"], quote=True)}" alt="{escape(item["alt"], quote=True)}" '
            f'width="{item["width"]}" height="{item["height"]}" '
            f'loading="{"eager" if eager else "lazy"}" decoding="async"{priority} />'
            f'{label}</span>')


def image_markup(items, eager=False):
    frames = ''.join(frame(p, eager) for p in items)
    return f'<span class="kb-photo-pair">{frames}</span>' if len(items) > 1 else frames


def apply_pages():
    BACKUP.mkdir(exist_ok=True)
    for name in ['baza-wiedzy.html', *BY_PAGE]:
        destination = ROOT / name
        backup = BACKUP / name
        if not backup.exists():
            backup.write_bytes(destination.read_bytes())
        page = backup.read_text(encoding='utf8')
        page = re.sub(r'(<body class=")([^"]+)(")', r'\1\2 kb-gallery-photos\3', page, count=1)
        page = re.sub(r'(<link rel="stylesheet" href="styles\.css[^>]+>)',
                      r'\1\n  <link rel="stylesheet" href="knowledge-photos.css?v=20260918-1" />', page, count=1)

        # Match the destination article, so covers and recommended cards use the same photographs.
        def replace_card(match):
            opening, href, inside = match.group(1), match.group(2), match.group(3)
            if href not in BY_PAGE:
                raise ValueError('Unknown article: ' + href)
            inside, count = re.subn(r'(<span class="(?:kb-topic-visual|kb-card-visual)">)\s*<img\b[^>]*?/?>\s*</span>',
                                   lambda m: m.group(1) + image_markup(BY_PAGE[href]['photos']) + '</span>', inside, count=1)
            if count != 1:
                raise ValueError('Missing cover in ' + name + ': ' + href)
            opening = opening.replace(' kb-topic-card--wide', '').replace(' kb-topic-card--tall', '')
            return opening + inside + '</a>'

        page = re.sub(r'(<a\b[^>]*class="(?:kb-topic-card|kb-card)(?:\s[^"]*)?"[^>]*href="([^"]+)"[^>]*>)([\s\S]*?)</a>', replace_card, page)
        hero_class = 'kb-hub-visual' if name == 'baza-wiedzy.html' else 'article-visual'
        selected = HUB if name == 'baza-wiedzy.html' else BY_PAGE[name]
        page, count = re.subn(r'(<figure class="' + hero_class + r'[^>]+>)\s*<img\b[^>]*?/?>',
                             lambda m: m.group(1) + '\n          ' + image_markup(selected['photos'], True), page, count=1)
        if count != 1:
            raise ValueError('Missing hero in ' + name)

        if name in BODY:
            page, count = re.subn(r'(<figure class="article-figure">)\s*<img\b[^>]*?/?>',
                                 lambda m: m.group(1) + '\n          ' + image_markup(BODY[name]), page, count=1)
            if count != 1:
                raise ValueError('Missing body image in ' + name)
            if name == 'wiedza-socjalizacja.html':
                page = page.replace('Socjalizacja zaczyna się u nas, w domu, wśród ludzi i codziennego życia.',
                                    'Wspólny odpoczynek naszych Maltańczyków w domowym otoczeniu.')
        if 'assets/wiedza/' in page:
            raise ValueError('An AI image reference remains in ' + name)
        destination.write_text(page, encoding='utf8', newline='\n')
    print('Updated knowledge hub and 20 article pages.')


def crop_preview(item, size):
    """Reproduce CSS object-fit: cover plus its focal point and scale, for QA only."""
    with Image.open(ROOT / item['src']) as original:
        image = ImageOps.exif_transpose(original).convert('RGB')
        ratio = size[0] / size[1]
        crop_w = min(image.width, image.height * ratio) / item['scale']
        crop_h = crop_w / ratio
        left = (image.width - crop_w) * item['x'] / 100
        top = (image.height - crop_h) * item['y'] / 100
        return image.resize(size, Image.Resampling.LANCZOS, box=(left, top, left + crop_w, top + crop_h))


def composition_preview(items, size):
    image = Image.new('RGB', size, '#fbf8f2')
    gap = 3
    width = (size[0] - gap * (len(items) - 1)) // len(items)
    for i, item in enumerate(items):
        image.paste(crop_preview(item, (width, size[1])), (i * (width + gap), 0))
        if item['label']:
            draw = ImageDraw.Draw(image)
            font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 12)
            x, y = i * (width + gap) + 8, size[1] - 32
            text_width = draw.textlength(item['label'], font=font)
            draw.rounded_rectangle((x,y,x+text_width+16,y+24), radius=5, fill='#fbf8f2')
            draw.text((x+8,y+5),item['label'],font=font,fill='#262520')
    return image


def review_sheets():
    font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 17)
    small_font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 14)
    for batch in range(3):
        rows = TOPICS[batch * 8:(batch + 1) * 8]
        sheet = Image.new('RGB', (1200, 730), '#f3eee5')
        draw = ImageDraw.Draw(sheet)
        for i, row in enumerate(rows):
            x, y = (i % 4) * 300 + 10, (i // 4) * 360 + 10
            sheet.paste(composition_preview(row['photos'], (280,210)), (x,y))
            number = batch * 8 + i + 1
            words = row['title'].split(); lines = ['']
            for word in words:
                test = (lines[-1] + ' ' + word).strip()
                if draw.textlength(test,font=font) > 278: lines.append(word)
                else: lines[-1] = test
            draw.multiline_text((x,y+221),f'{number:02d}. '+('\n'.join(lines)),font=font,fill='#262520',spacing=3)
            ids = ', '.join(p['id'] for p in row['photos'])
            draw.text((x,y+315),ids,font=small_font,fill='#686257')
        sheet.save(PREVIEW / f'knowledge-selected-crops-{batch+1}.jpg',quality=92)
    secondary = [HUB] + [dict(title=name.replace('wiedza-','').replace('.html',''),photos=items) for name,items in BODY.items()]
    sheet=Image.new('RGB',(1200,3*285),'#f3eee5'); draw=ImageDraw.Draw(sheet)
    for i,row in enumerate(secondary):
        x,y=i%4*300+10,i//4*285+10
        size=(280,210) if i==0 else (280,175)
        sheet.paste(composition_preview(row['photos'],size),(x,y))
        draw.text((x,y+220),row['title'],font=small_font,fill='#262520')
    sheet.save(PREVIEW/'knowledge-secondary-crops.jpg',quality=92)


def save_plan():
    assets = {p['src'] for t in TOPICS+[HUB] for p in t['photos']}
    assets |= {p['src'] for photos in BODY.values() for p in photos}
    hashes = {src:hashlib.sha256((ROOT/src).read_bytes()).hexdigest() for src in sorted(assets)}
    (PREVIEW / 'knowledge-photo-plan.json').write_text(json.dumps(dict(topics=TOPICS,hub=HUB,body=BODY,sourceHashes=hashes),ensure_ascii=False,indent=2),encoding='utf8')


if __name__ == '__main__':
    save_plan()
    review_sheets()
    if '--apply' in sys.argv:
        apply_pages()
    print('Created four offline crop-review sheets; gallery originals unchanged.')
