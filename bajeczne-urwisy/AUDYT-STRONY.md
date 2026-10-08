> Raport archiwalny. Aktualny stan domeny, galerii i optymalizacji opisuje [audyt z 7 października 2026](AUDYT-SEO-2026-10-07.md).

# Audyt i poprawki strony Bajeczne Urwisy

18 września 2026 r. Zakres: wszystkie 28 publicznych stron HTML, wspólne CSS i JavaScript, kontakt, baza wiedzy, galerie, ikony, mobilna nawigacja i przygotowanie SEO.

## Najnowsza aktualizacja: podstrony ras i pełne galerie

Przebudowano podstrony Chihuahua, Maltańczyka i przegląd ras. Zdjęcia AI w tych podstronach zastąpiły oryginalne fotografie hodowli. Uporządkowano skalę nagłówków, proporcje fotografii, sekcje o charakterze i pielęgnacji, odsyłacze do poradników oraz przyciski kontaktu. Osobny `breed-pages.css` zachowuje dotychczasową identyfikację i dostosowuje układ do telefonu.

Galerie zawierają 188 unikalnych fotografii: 160 Chihuahua i 28 Maltańczyków. Wcześniej było 94 kafelków przedstawiających 90 różnych zdjęć. Przywrócono 98 pominiętych fotografii i usunięto cztery powtarzające się kafelki. Zidentyfikowano również 73 kopie plików lub wcześniej wycięte wersje tych samych zdjęć. Oryginalnych plików nie usuwano. Różne ujęcia tego samego pieska pozostają osobnymi fotografiami.

Każdemu portretowi przypisano indywidualny kadr. Fotografie grupowe zajmują dwa pola i pokazują całe ujęcie. Pełny oryginał otwiera się po kliknięciu. Wszystkie zdjęcia są zapisane w statycznym HTML, widoczne bez filtrów i bez JavaScript; pobierane są stopniowo przez `loading="lazy"`. Usunięto automatyczne kasowanie kafelków przez `onerror` oraz nieużywaną zapowiedź nowych zdjęć w podglądzie.

Źródłem galerii jest `data/gallery-photos.json`; generator to `tools/build_galleries.py`. Lista obejmuje wszystkie przejrzane pliki oryginalnych fotografii i ich aliasy. Logo nie jest częścią galerii psów. Kadry sprawdzono na lokalnych planszach kontaktowych; nie jest to kontrola renderu przeglądarki.

Wyniki najnowszych kontroli:

- 28 stron, 1443 lokalne odwołania, 487 wystąpień obrazów, 1082 warianty `srcset`, 472 ikony z klasą `ico`: bez błędów w zakresie audytu statycznego.
- Kontrola galerii potwierdza 188 różnych fotografii, zgodność z manifestem, brak powtórzonych obrazów, prawidłowe granice kadrów i zachowanie wszystkich wcześniej pokazywanych ujęć.
- 11 testów logiki menu, podglądu, fokusu i animacji przeszło. Składnia JavaScript jest prawidłowa.
- Test generatora SEO na izolowanej kopii przeszedł. Zdjęcia udostępniania stron ras wskazują nowe oryginalne fotografie.
- Optymalizacja obejmuje teraz 211 źródeł w 319 miejscach serwisu. Oryginały tych źródeł zajmują 43 376 878 B, największe kopie WebP 39 277 188 B. Przeglądarka dobiera mniejsze warianty według rozmiaru ekranu. To rozmiary plików, nie pomiar wydajności strony.

Wyniki zapisano w `_preview/site-audit-breed-galleries.json` i `_preview/gallery-coverage-result.json`. Kopia pięciu podstron sprzed zmian znajduje się w `_preview/before-original-galleries`. Opis poniżej dokumentuje wcześniejszą serię poprawek; ograniczenie dostępu do przeglądarki nadal obowiązuje.

## Poprawki po zgłoszeniu brakującej ikony telefonu

| Obszar | Wykryty problem | Stan po zmianach |
| --- | --- | --- |
| Telefon w stopce | 18 pełnych stopek zawierało numer bez ikony. W 10 poradnikach była tylko krótka stopka bez kontaktu. | Wszystkie 28 stron ma pełną stopkę z ikoną SVG i klikalnym telefonem. |
| Przyciski telefonu | 20 przycisków kontaktowych nie miało ikony. | Uzupełniono SVG bez zależności od zewnętrznych bibliotek i sprite'ów. |
| Pozostałe znaki | Strzałki w podmenu były przezroczyste do najechania. Znaki organizacji miały niską widoczność. | Strzałki są stale widoczne. Wzmocniono widoczność znaków w stopce. |
| Mobilny nagłówek | Telefon był ukrywany przez reguły mobilne. Kontakt dodatkowo ukrywał go na części tabletów. | Każda strona ma kompaktowy przycisk telefonu 46 × 46 px obok menu. Na komputerze pozostaje numer. |
| Mobilna stopka | Podwójny dolny odstęp powodował nadmierną pustą przestrzeń. | Miejsce na przyklejony przycisk rezerwują tylko strony, które go posiadają. Uwzględniono bezpieczną strefę telefonu. |
| Galerie | Kafelki były przezroczyste do uruchomienia animacji. Bez JS lub przy niekorzystnych proporcjach okna mogły pozostać niewidoczne. | Bazowy stan zdjęć jest widoczny. Animacje wejścia wykonują się raz. Mobilna galeria maltańczyków ma siatkę dwóch kolumn. |
| Opinie | Strzałki karuzeli były ukrywane na telefonie. | Przywrócono przyciski 44 × 44 px pod kartami. Pozostaje przesuwanie palcem. |
| Proporcje mobilne | Duże nagłówki i przesuwanie sekcji przez szerokość ekranu mogły utrudniać czytanie. | Ograniczono nagłówki, poprawiono minima siatek i łamanie przycisków. Sekcje pozostają na miejscu na małych ekranach. |
| Tabele | Przewijanie poziome nie miało własnego miejsca w kolejności klawiatury. | Trzy kontenery tabel mają fokus i nazwę. Nagłówki kolumn mają scope. |
| Zdjęcia | Telefon pobierał te same duże pliki co komputer. | Warianty WebP dla 121 fotografii zastosowano w 221 miejscach. Oryginały i kadry zachowane. |
| Metadane | Część stron nie miała podstawowych metadanych udostępniania; brakowało danych strukturalnych. | Spójne Open Graph, Twitter, opisy i JSON-LD na 28 stronach. Poradniki mają dane Article, kontakt ContactPage, hodowla Organization. |

Największe warianty WebP zajmują łącznie 15 160 852 B wobec 29 574 917 B oryginałów objętych optymalizacją, czyli o 48,7% mniej. Warianty najbliższe 800 px zajmują 8 759 622 B, czyli o 70,4% mniej. To porównanie plików, nie wynik pomiaru czasu ładowania ani Core Web Vitals.

Wcześniejsze poprawki pozostają: właściwe logo i profile społecznościowe, SVG osadzone w HTML, obsługa menu klawiaturą, skip linki, fokus i nieaktywne tło w podglądzie, pauza animacji, oryginalne zdjęcie w kontakcie i fotografie galerii dobrane do poradników.

## SEO i domena

Plik site-config.json zawiera rzeczywisty telefon, miejscowość i profile społecznościowe. baseUrl pozostaje pusty, ponieważ właściciel nie podał docelowej domeny. Przygotowany robots.txt pozwala na przeglądanie strony, zdjęć, CSS i JS. Foldery robocze należy pominąć podczas publikacji, niezależnie od wpisów robots.

Po wpisaniu adresu HTTPS i uruchomieniu tools/prepare_seo.py powstaną bezwzględne canonical i og:url dla 28 stron, adresy oryginalnych zdjęć do udostępniania, BreadcrumbList, WebSite oraz sitemap.xml. Publiczne pliki nie zawierają domeny przykładowej. Nie dodano wymyślonych dat publikacji, ocen, ulicy ani adresu e-mail.

Google wymaga pełnych adresów w mapie witryny. Dlatego ostateczna mapa czeka na domenę. [Dokumentacja map witryn Google](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap).

Komputer i telefon korzystają z tych samych treści, zdjęć i metadanych, a układ dostosowuje się do szerokości. Jest to podejście responsywne zalecane przez Google. [Dokumentacja wersji mobilnej Google](https://developers.google.com/search/docs/crawling-indexing/mobile/mobile-sites-mobile-first-indexing).

Dobór metadanych oparto na dokumentacji [Organization](https://developers.google.com/search/docs/appearance/structured-data/organization) i [Article](https://developers.google.com/search/docs/appearance/structured-data/article). Dodane oznaczenia nie gwarantują pozycji ani rozszerzonych wyników wyszukiwania.

## Weryfikacja

- Audyt 28 stron: 1322 lokalne odwołania, 386 wystąpień obrazów, 696 wariantów srcset, 463 ikony z klasą ico. Łącznie dokumenty zawierają 636 SVG, wliczając dekoracje i znaki. Brak błędów w sprawdzonych odsyłaczach, identyfikatorach, strukturze ikon, wymiarach zdjęć, nazwach kontrolek i metadanych.
- Każda stopka ma dokładnie jeden telefon z ikoną. Przyciski typu btn prowadzące do telefonu również mają ikonę.
- Składnia JavaScript oraz 11 testów interakcji przeszły. Obejmują menu, Escape, fokus, podgląd, opinie, pauzę, kotwice i brak IntersectionObserver.
- Generator SEO sprawdzono na izolowanej kopii: 28 adresów canonical, 28 zdjęć udostępniania, 20 artykułów, 27 ścieżek nawigacji, mapa, robots i ponowne uruchomienie bez duplikowania metadanych. Testowa domena była używana tylko w tymczasowym katalogu.
- Wyniki: _preview/site-audit-mobile-seo.json, _preview/check-interactions.cjs, _preview/check_seo.py. Kopia sprzed tej serii zmian: _preview/before-mobile-seo.

## Ograniczenia i pozostałe dane

Automatyczna kontrola dostępu odrzuciła otwarcie lokalnego adresu file:/// w przeglądarce i zabroniła obejścia przez localhost lub inne sterowanie przeglądarką. Nie wykonano rzeczywistego renderowania po zmianach, testów dotykowych, Lighthouse ani produkcyjnego Google Rich Results. Kontrole kodu i model DOM nie zastępują tych testów. Nie deklarujemy pełnego braku błędów ani potwierdzonej zgodności WCAG.

Po umożliwieniu dozwolonego podglądu pozostaje kontrola typów stron przy 320, 390, 768, 1024, 1280 i 1440 px, pozioma orientacja telefonu, powiększenie tekstu, menu, galerie i przyciski telefonu. Lokalny plik nie jest publiczną stroną, którą Google może zaindeksować. Potrzebna jest publikacja pod docelowym adresem i weryfikacja w Search Console.

Statusy szczeniąt są aktualizowane ręcznie. E-mail i formularz nie zostały dodane, bo nie podano danych ani obsługi wysyłki. Informacja o prywatności wymaga danych właściciela i konfiguracji publikacji. Obecnie wykorzystywane są zewnętrzne fonty i mapa Google.

Przegląd interfejsu uwzględnił [Web Interface Guidelines](https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md). Ustalenia dotyczą konkretnych plików tego projektu.

