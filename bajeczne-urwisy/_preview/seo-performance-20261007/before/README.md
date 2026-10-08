# Bajeczne Urwisy

Statyczna strona hodowli z 28 podstronami. Bieżący stan po audycie opisuje `AUDYT-STRONY.md`.

## Otwieranie

Otwórz `index.html` w przeglądarce. Podstrony można otwierać bezpośrednio. Ikony są osadzone w HTML i nie wymagają pobierania zewnętrznego sprite'a. Po zmianach odśwież stronę przez Ctrl+F5. Fonty Google, mapa i profile społecznościowe wymagają połączenia z internetem.

## Pliki

- `index.html`: strona główna, dostępność szczeniąt, opinie i skrócony kontakt.
- `kontakt.html` i `contact.css`: pełny kontakt, oryginalne zdjęcie, mapa i pytania.
- `rasy.html`, `chihuahua.html`, `maltanczyk.html`, `breed-pages.css`: podstrony ras z oryginalnymi fotografiami i kadrami.
- `galeria-chihuahua.html`, `galeria-maltanczyki.html`: galerie, 159 zdjęć Chihuahua i 32 Maltańczyków.
- `data/gallery-photos.json`: katalog 207 fotografii, ich kadrów, opisów i rozpoznanych kopii. Galerie pokazują 191 zdjęć; pominięto pięć podobnych ujęć oraz 11 fotografii wskazanych przez właściciela do usunięcia z galerii.
- `tools/build_galleries.py`: buduje obie statyczne galerie z tej listy, uwzględniając udokumentowane pominięcia, bez pobierania JSON w przeglądarce.
- `baza-wiedzy.html`, `wiedza-*.html`, `knowledge-photos.css`: 20 poradników i kadrowanie fotografii.
- `styles.css`: wspólne style i kolory marki.
- `site-audit.css`: wspólne poprawki dostępności, nawigacji, stopki i podglądu zdjęć. Wczytywany po stylach bazowych; `breed-pages.css` uzupełnia go na stronach ras i galerii.
- `script.js`: menu, galerie, opinie, animacje i obsługa poradników.
- `assets`: fotografie, logo i pozostałe zasoby.
- `assets/optimized`: responsywne kopie WebP. Oryginały zdjęć pozostają w `assets/photos`.
- `site-config.json`: potwierdzone dane hodowli i docelowy adres strony, obecnie nieustalony.
- `tools/prepare_seo.py`: powtarzalne generowanie metadanych i danych strukturalnych, a po ustaleniu domeny również mapy strony, canonical i adresów udostępniania.
- `tools/optimize_images.py`: powtarzalne przygotowanie mniejszych kopii zdjęć i atrybutów `srcset` / `sizes`.
- `_preview`: materiały robocze, kopie zapasowe i kontrole. Nie publikować.

## Aktualizacja treści

Zdjęcia są wskazane bezpośrednio przez atrybuty `src` w HTML. Samo dodanie dowolnego pliku do folderu nie umieszcza go na stronie. Przy zmianie fotografii zaktualizuj również jej opis `alt`, wymiary `width` i `height` oraz kadr.

Galerię aktualizuj przez `data/gallery-photos.json`, a następnie `python tools/build_galleries.py`. Każde różne ujęcie ma jeden wpis. Pole `aliases` dokumentuje identyczne pliki i wcześniejsze wycinki; oryginalnych plików nie kasujemy. `galleryOrder` ustala kolejność opublikowanych zdjęć. Pole `galleryOmission` zawiera powód pominięcia zdjęcia. Przy podobnych ujęciach `representedBy` wskazuje pozostawioną fotografię; przy usunięciu wskazanym przez właściciela zapisujemy `requestedRemoval: true`. Takie ujęcie pozostaje w katalogu, lecz nie wraca do galerii po jej przebudowaniu. Dziewięć dodatkowych zdjęć Maltańczyków pochodzi z `assets/opinie`; ich kopie są zapisane w `aliases`. Wszystkie ramki mają proporcje 3:4 i zajmują jedną komórkę siatki. Portrety mają indywidualne kadry, a zdjęcia grupowe pokazują cały oryginał wewnątrz takiej samej ramki. Generator zachowuje istniejące warianty WebP z `assets/optimized/manifest.json`.

Po wymianie zdjęć uruchom `python tools/optimize_images.py`, a następnie `python tools/prepare_seo.py`. Przeglądarka dobiera lżejszą kopię do szerokości ekranu. Podgląd po kliknięciu w galerii nadal otwiera oryginał.

W bazie wiedzy kadr ustalają `--photo-x`, `--photo-y` i `--photo-scale` na elemencie `kb-photo-frame`. Fotografie należy sprawdzić na liście tematów, w artykule i w odsyłaczach do powiązanych poradników.

Dane i statusy szczeniąt znajdują się w sekcji `id="szczenieta"` w `index.html`. Aktualizuje się je ręcznie. Kontakt, numer telefonu i profile społecznościowe występują na wielu podstronach, więc ich zmianę trzeba zastosować we wszystkich plikach HTML.

Strona nie ma formularza wysyłającego wiadomości ani automatycznego pobierania dostępności z Facebooka. Kontakt odbywa się telefonicznie oraz przez profile społecznościowe.

## Kontrole

- `python _preview/audit_site.py latest`: lokalne pliki, kotwice, podstawowa struktura i dostępność HTML.
- `python _preview/check_gallery_coverage.py`: kompletność galerii, brak duplikatów, granice kadrów, właściwa rasa i zachowanie wcześniej widocznych zdjęć.
- `node --check script.js`: składnia JavaScript.
- `node _preview/check-interactions.cjs`: testy logiki interakcji bez renderowania strony.
- `python _preview/check_seo.py`: test konfiguracji domeny, mapy strony, danych strukturalnych i udostępniania na tymczasowej kopii. Nie zmienia domeny publicznych plików.

Skrypty Pythona wymagają Pillow i lxml. Jednorazowe skrypty zmian w `_preview` nie są systemem budowania strony; nie uruchamiaj ich ponownie na aktualnym serwisie, ponieważ mogą odtwarzać wcześniejsze wersje plików.

## Przed publikacją

Wpisz rzeczywisty adres HTTPS w `baseUrl` w pliku `site-config.json` i uruchom `python tools/prepare_seo.py`. Alternatywnie podaj go jako argument `--base-url`. Skrypt wygeneruje statyczne adresy kanoniczne, pełne adresy zdjęć udostępniania, dane nawigacji oraz `sitemap.xml` i wpis mapy w `robots.txt`. Nie podstawia domeny z adresu lokalnego ani nie wpisuje fikcyjnego adresu do publicznych plików.

Przenieś publiczne pliki HTML, CSS, JavaScript, `robots.txt`, wygenerowany `sitemap.xml` i wymagane zasoby `assets`. Foldery `_preview`, `tools`, `data`, `facebook-posts`, kopie zapasowe i dokumentację pozostaw lokalnie. `robots.txt` umieść w głównym katalogu domeny. Strona wymaga publicznego hostingu HTTPS, aby Google mógł ją odwiedzić.

Po publikacji zgłoś mapę w Google Search Console i sprawdź adresy narzędziem kontroli URL. Uzupełnij informacje o prywatności zgodnie z faktycznymi danymi właściciela i konfiguracją strony. Podgląd lokalny nie pozwala zmierzyć produkcyjnych Core Web Vitals ani potwierdzić indeksowania.
