from pathlib import Path
import re,json
ROOT=Path(__file__).resolve().parent.parent
for page in ROOT.glob('galeria-*.html'):
    source=page.read_text(encoding='utf8')
    source=re.sub(r'<div class="lightbox-inner">.*?</div>','<div class="lightbox-inner"></div>',source,flags=re.S)
    page.write_text(source,encoding='utf8')
manifest=json.loads((ROOT/'assets/optimized/manifest.json').read_text(encoding='utf8'))
print(type(manifest).__name__, list(manifest)[:4])
readme=ROOT/'README.md'
source=readme.read_text(encoding='utf8')
source=source.replace('- `rasy.html`, `chihuahua.html`, `maltanczyk.html`: opisy ras.','- `rasy.html`, `chihuahua.html`, `maltanczyk.html`, `breed-pages.css`: podstrony ras z oryginalnymi fotografiami i kadrami.')
source=source.replace('- `galeria-chihuahua.html`, `galeria-maltanczyki.html`: galerie.','- `galeria-chihuahua.html`, `galeria-maltanczyki.html`: pełne galerie, 160 zdjęć Chihuahua i 28 Maltańczyków.\n- `data/gallery-photos.json`: lista 188 unikalnych fotografii, ich kadrów, opisów i rozpoznanych kopii.\n- `tools/build_galleries.py`: buduje obie statyczne galerie z tej listy, bez ukrywania fotografii i pobierania JSON w przeglądarce.')
source=source.replace('Wczytywany po pozostałych stylach.','Wczytywany po stylach bazowych; `breed-pages.css` uzupełnia go na stronach ras i galerii.')
source=source.replace('Po wymianie zdjęć uruchom', 'Galerię aktualizuj przez `data/gallery-photos.json`, a następnie `python tools/build_galleries.py`. Każde różne ujęcie ma jeden wpis. Pole `aliases` dokumentuje identyczne pliki i wcześniejsze wycinki; oryginalnych plików nie kasujemy. Portrety mają indywidualny kadr 3:4, a zdjęcia grupowe szersze miejsce w siatce z widocznym całym oryginałem.\n\nPo wymianie zdjęć uruchom')
source=source.replace('- `node --check script.js`:', '- `python _preview/check_gallery_coverage.py`: kompletność galerii, brak duplikatów, granice kadrów, właściwa rasa i zachowanie wcześniej widocznych zdjęć.\n- `node --check script.js`:')
source=source.replace('Foldery `_preview`, `tools`, `facebook-posts`,','Foldery `_preview`, `tools`, `data`, `facebook-posts`,')
readme.write_text(source,encoding='utf8')
