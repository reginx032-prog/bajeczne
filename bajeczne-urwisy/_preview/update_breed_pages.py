from pathlib import Path
from html import escape
from lxml import html
import json,re,shutil
ROOT=Path(__file__).resolve().parent.parent
backup=ROOT/'_preview/before-original-galleries';backup.mkdir(exist_ok=True)
for name in ['chihuahua.html','maltanczyk.html','rasy.html','galeria-chihuahua.html','galeria-maltanczyki.html']:
    if not (backup/name).exists(): shutil.copy2(ROOT/name,backup/name)
photos={p['id']:p for p in json.loads((ROOT/'data/gallery-photos.json').read_text(encoding='utf8'))['photos']}
doc=html.fromstring((ROOT/'chihuahua.html').read_text(encoding='utf8'))
phone=html.tostring(doc.xpath('//a[starts-with(@href,"tel:")]//svg')[0],encoding='unicode',with_tail=False)
arrow='<svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M5 12h14m-6-6 6 6-6 6"/></svg>'
def photo(n,caption='',priority=False):
    p=photos[n];style=f'--photo-x:{p["x"]}%;--photo-y:{p["y"]}%;--photo-scale:{p["scale"]}'
    loading='loading="eager" fetchpriority="high"' if priority else 'loading="lazy"'
    return f'<figure class="breed-photo"><div class="breed-photo-frame" style="{style}"><img src="{escape(p["src"])}" alt="{escape(p["alt"])}" width="{p["width"]}" height="{p["height"]}" {loading} decoding="async" /></div>'+ (f'<figcaption>{caption}</figcaption>' if caption else '')+'</figure>'
def call(label): return f'<a class="btn" href="tel:+48601074022">{phone} {label}</a>'
def section_links(items):return '<div class="breed-read-links">'+''.join(f'<a href="{url}">{label}{arrow}</a>' for url,label in items)+'</div>'
configs={
'chihuahua.html':dict(name='Chihuahua',eyebrow='Rasa Chihuahua',heading='Chihuahua.<span>Mały piesek,<br>wielki charakter.</span>',lead='Blisko człowieka, z ciekawością świata i własnym charakterem. Poznaj nasze Chihuahua i opowiedz nam, jakiego towarzysza szukasz.',hero=177,gallery='galeria-chihuahua.html',facts=[('Szata','Krótka lub długa'),('Codzienność','Blisko opiekuna'),('Hodowla','Dom i ogród')],
copy=[('Charakter','Czy Chihuahua pasuje do Twojego domu?','Mały rozmiar to tylko część tej opowieści. Chihuahua potrzebuje codziennego kontaktu, spacerów i spokojnego poznawania świata. Wspólne chwile budują relację z opiekunem.','Podczas rozmowy zapytamy o Twój rytm dnia i oczekiwania. Opowiemy o konkretnych maluszkach, bo każdy ma swój temperament.','wiedza-chihuahua.html','Więcej o charakterze Chihuahua'),('Szata i umaszczenie','Każdy maluszek jest inny','W naszej galerii zobaczysz Chihuahua krótko- i długowłose, w różnych umaszczeniach. Zdjęcia pokazują zarówno obecne maluszki, jak i pieski z wcześniejszych miotów.','Jeśli szukasz konkretnego typu szaty, zadzwoń. Pomożemy poznać różnice w pielęgnacji i sprawdzimy aktualną dostępność.','wiedza-siersc-chihuahua.html','Krótka i długa szata Chihuahua')],
shots=[(130,'Czarna szata i biała łatka pod brodą.'),(156,'Czekoladowy maluszek w naszym ogrodzie.'),(188,'Chihuahua długowłosy, także po okresie szczenięcym.')],
reading=[('wiedza-kolory-chihuahua.html','Umaszczenia Chihuahua'),('wiedza-pierwsze-dni.html','Pierwsze dni w nowym domu'),('wiedza-wyprawka.html','Wyprawka dla maluszka')],cta='Porozmawiajmy o Twoim przyszłym towarzyszu.',ctatext='Zapytaj o nasze Chihuahua, charakter konkretnego maluszka i możliwość poznania go osobiście. Chętnie pomożemy Ci w wyborze.'),
'maltanczyk.html':dict(name='Maltańczyki',eyebrow='Rasa Maltańczyk',heading='Maltańczyk.<span>Czuły towarzysz<br>Twojej rodziny.</span>',lead='Biała szata, uważne spojrzenie i radość ze wspólnego czasu. Poznaj nasze Maltańczyki oraz codzienność, z której wyruszają do nowych domów.',hero=25,gallery='galeria-maltanczyki.html',facts=[('Szata','Biała'),('Codzienność','Kontakt i zabawa'),('Pielęgnacja','Regularne czesanie')],
copy=[('Codzienność','Bliskość, zabawa i spokojny rytm','Maltańczyk może być czułym towarzyszem codziennych chwil. Ważne są wspólny czas, zabawa i stopniowe poznawanie nowych sytuacji. Charakter warto poznawać u konkretnego pieska.','Nasze fotografie pokazują maluszki w domu i ogrodzie. Podczas rozmowy opowiemy o ich zachowaniu, zwyczajach i przygotowaniu do nowego domu.','wiedza-maltanczyk.html','Poznaj bliżej Maltańczyka'),('Pielęgnacja','O białą szatę dbamy od początku','Regularne czesanie i przyzwyczajanie do dotyku są częścią codzienności Maltańczyka. Krótkie, spokojne sesje pomagają maluszkowi oswoić zabiegi pielęgnacyjne.','Chętnie podpowiemy, jak zacząć pielęgnację po odbiorze pieska i jakie akcesoria przygotować. Wskazówki dobieramy do potrzeb maluszka.','wiedza-pielegnacja.html','Przewodnik po pielęgnacji')],
shots=[(24,'Spokojna chwila w domu.'),(41,'Mały odkrywca w naszym ogrodzie.'),(89,'Pierwsze przygody na trawie.')],
reading=[('wiedza-maltanczyk.html','Charakter i potrzeby Maltańczyka'),('wiedza-pielegnacja.html','Codzienna pielęgnacja'),('wiedza-wyprawka.html','Co przygotować przed odbiorem')],cta='Chcesz poznać nasze Maltańczyki?',ctatext='Zadzwoń i opowiedz nam o swoim domu. Porozmawiamy o maluszkach, ich pielęgnacji i aktualnych lub planowanych miotach.')
}
for filename,c in configs.items():
    facts=''.join(f'<div><dt>{a}</dt><dd>{b}</dd></div>' for a,b in c['facts'])
    copy=''.join(f'<article><span class="breed-kicker">{k}</span><h2>{title}</h2><p>{p1}</p><p>{p2}</p><a class="breed-inline-link" href="{url}">{label} {arrow}</a></article>' for k,title,p1,p2,url,label in c['copy'])
    main=f'''<main class="subpage-main" id="main-content" tabindex="-1">
  <section class="breed-hero"><div class="container breed-hero-grid">
    <div class="breed-hero-copy"><span class="subpage-eyebrow">{c['eyebrow']}</span><h1>{c['heading']}</h1><p>{c['lead']}</p>
      <div class="breed-actions">{call('Porozmawiajmy o maluszku')}<a class="btn btn--ghost" href="{c['gallery']}">Zobacz naszą galerię {arrow}</a></div>
      <dl class="breed-facts">{facts}</dl>
    </div>{photo(c['hero'],'Maluszek z naszej hodowli Bajeczne Urwisy.',True)}
  </div></section>
  <section class="breed-section breed-section--cream"><div class="container breed-copy-grid">{copy}</div></section>
  <section class="breed-section"><div class="container">
    <div class="breed-section-heading"><span class="breed-kicker">Nasze pieski z bliska</span><h2>Małe chwile, piękne wspomnienia.</h2><p>Zdjęcia z naszego domu i ogrodu. Każde z nich to część historii Bajecznych Urwisów.</p></div>
    <div class="breed-photo-row">{''.join(photo(n,caption) for n,caption in c['shots'])}</div>
    <div class="breed-gallery-link"><a class="btn btn--ghost" href="{c['gallery']}">Cała galeria: {c['name']} {arrow}</a></div>
  </div></section>
  <section class="breed-section breed-section--cream"><div class="container"><div class="breed-section-heading"><span class="breed-kicker">Przed powitaniem maluszka</span><h2>Warto wiedzieć wcześniej.</h2></div>{section_links(c['reading'])}</div></section>
  <section class="subpage-cta-section"><div class="container"><div class="subpage-cta-box"><div><span class="subpage-eyebrow">Jesteśmy do rozmowy</span><h2>{c['cta']}</h2><p>{c['ctatext']}</p></div>{call('601 074 022')}</div></div></section>
</main>'''
    source=(ROOT/filename).read_text(encoding='utf8')
    source=re.sub(r'<main\b.*?</main>',lambda _:main,source,count=1,flags=re.S)
    source=re.sub(r'<body class="([^"]*)"',lambda m:'<body class="'+m[1]+(' breed-page' if 'breed-page' not in m[1].split() else '')+'"',source,count=1)
    if 'breed-pages.css?' not in source: source=source.replace('</head>','  <link rel="stylesheet" href="breed-pages.css?v=20260918-photos1" />\n</head>')
    (ROOT/filename).write_text(source,encoding='utf8')

cards=''
for name,n,filename,desc in [('Chihuahua',166,'chihuahua.html','Mały piesek o wyrazistym charakterze. Poznaj nasze Chihuahua krótko- i długowłose, ich codzienność i potrzeby.'),('Maltańczyk',24,'maltanczyk.html','Biała szata i radość ze wspólnego czasu. Zobacz nasze Maltańczyki i dowiedz się więcej o ich pielęgnacji.')]:
    cards+=f'<article>{photo(n)}<h2>{name}</h2><p>{desc}</p><a class="breed-inline-link" href="{filename}">Poznaj rasę {name} {arrow}</a></article>'
main=f'''<main class="subpage-main" id="main-content" tabindex="-1">
  <section class="breed-hero"><div class="container breed-hero-grid"><div class="breed-hero-copy"><span class="subpage-eyebrow">Nasze rasy</span><h1>Małe pieski.<span>Wielkie miejsce<br>w Twoim domu.</span></h1><p>Chihuahua i Maltańczyki z rodzinnej hodowli Bajeczne Urwisy. Poznaj obie rasy i wybierz towarzysza, którego potrzeby pasują do Twojej codzienności.</p><div class="breed-actions"><a class="btn" href="chihuahua.html">Poznaj Chihuahua {arrow}</a><a class="btn btn--ghost" href="maltanczyk.html">Poznaj Maltańczyki {arrow}</a></div></div><div class="breed-overview-pair">{photo(177,'Nasze Chihuahua.',True)}{photo(25,'Nasze Maltańczyki.')}</div></div></section>
  <section class="breed-section breed-section--cream"><div class="container breed-overview-cards">{cards}</div></section>
  <section class="breed-section"><div class="container"><div class="breed-section-heading"><span class="breed-kicker">Dobry początek</span><h2>Wybór zaczyna się od poznania potrzeb.</h2><p>Porozmawiajmy o czasie na wspólne spacery, pielęgnację i zabawę. Pomożemy Ci poznać różnice między rasami oraz temperament konkretnego maluszka.</p></div>{section_links([('wiedza-chihuahua-czy-maltanczyk.html','Chihuahua czy Maltańczyk?'),('galeria-chihuahua.html','Galeria naszych Chihuahua'),('galeria-maltanczyki.html','Galeria naszych Maltańczyków')])}</div></section>
  <section class="subpage-cta-section"><div class="container"><div class="subpage-cta-box"><div><span class="subpage-eyebrow">Poznajmy się</span><h2>Pomożemy Ci wybrać maluszka.</h2><p>Opowiedz nam o swoim domu. Zapytaj o szczenięta, ich charakter i możliwość spotkania w naszej hodowli.</p></div>{call('601 074 022')}</div></div></section>
</main>'''
path=ROOT/'rasy.html';source=path.read_text(encoding='utf8');source=re.sub(r'<main\b.*?</main>',lambda _:main,source,count=1,flags=re.S);source=source.replace('class="subpage"','class="subpage breed-page"')
if 'breed-pages.css?' not in source: source=source.replace('</head>','  <link rel="stylesheet" href="breed-pages.css?v=20260918-photos1" />\n</head>')
path.write_text(source,encoding='utf8')
print('Updated three breed pages with original photographs.')
