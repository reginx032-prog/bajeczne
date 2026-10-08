# Bajeczne Urwisy — strona internetowa (landing page)

Nowoczesna, jasna i responsywna strona wizytówka dla hodowli psów rasowych
**Bajeczne Urwisy** (Chihuahua i Maltańczyki, Kowalewo Pomorskie).

## 🚀 Jak uruchomić

Wystarczy **dwukrotnie kliknąć plik `index.html`** — strona otworzy się w przeglądarce.
Nie trzeba niczego instalować.

## 📁 Co jest w folderze

```
bajeczne-urwisy/
├── index.html        ← treść strony (wszystkie sekcje)
├── styles.css        ← wygląd / kolory / układ
├── script.js         ← animacje, menu, formularz
├── README.md         ← ten plik
└── assets/
    ├── favicon.svg       ← ikonka na karcie przeglądarki
    ├── logo-swkipr.svg   ← znaczek organizacji (do podmiany)
    ├── logo-wku.svg      ← znaczek organizacji (do podmiany)
    └── logo-ppk.svg      ← znaczek organizacji (do podmiany)
```

---

## 🖼️ Jak dodać własne ZDJĘCIA — wystarczy wrzucić pliki

**Nie trzeba nic zmieniać w kodzie.** Strona sama wykrywa zdjęcia — wystarczy
wrzucić pliki do folderu **`assets/photos/`** o dokładnie tych nazwach (najlepiej `.jpg`):

| Plik | Gdzie się pojawi |
|---|---|
| `hero.jpg` | duże zdjęcie w sekcji powitalnej |
| `o-hodowli.jpg` | sekcja „O hodowli" |
| `chihuahua.jpg` | karta rasy Chihuahua |
| `maltanczyk.jpg` | karta rasy Maltańczyk |
| `szczeniak-1.jpg`, `szczeniak-2.jpg`, `szczeniak-3.jpg` | sekcja „Szczenięta" |
| `galeria-1.jpg` … `galeria-8.jpg` | galeria (8 zdjęć) |

Dopóki pliku nie ma — widać delikatny placeholder z łapką 🐾. Gdy wrzucisz plik,
zdjęcie pojawia się automatycznie po odświeżeniu strony (F5).

**Pobieranie zdjęć z Facebooka:** otwórz zdjęcie na profilu →
klik prawym przyciskiem → „Zapisz obraz jako…" → zapisz do `assets/photos/`
pod jedną z nazw z tabeli. (Pełna lista jest też w pliku
`assets/photos/_WRZUC_ZDJECIA_TUTAJ.txt`).

---

## 🐶 Loga — wystarczy wrzucić pliki (automatyczna podmiana)

Strona sama wykryje Twoje prawdziwe loga. **Nie trzeba nic zmieniać w kodzie** —
wystarczy wrzucić pliki do folderu `assets/` o dokładnie tych nazwach:

| Plik w `assets/` | Co to | Uwagi |
|---|---|---|
| `logo.png` | główne logo „Bajeczne Urwisy" (nagłówek) | najlepiej PNG z **przezroczystym** tłem |
| `logo-white.png` | to samo logo w wersji jasnej (stopka, ciemne tło) | jasne/białe, przezroczyste tło |
| `logo-swkipr.png` | logo SWKiPR | przezroczyste tło |
| `logo-wku.png` | logo WKU | przezroczyste tło |
| `logo-ppk.png` | logo PPK | przezroczyste tło |

Dopóki tych plików nie ma, strona pokazuje eleganckie zamienniki (napis + znaczki).
Gdy tylko wrzucisz pliki — pojawią się automatycznie po odświeżeniu strony.

> **Przezroczyste tło (bez białego prostokąta):** zapisz loga jako **PNG z kanałem
> alfa**. Jeśli masz tylko wersje na białym tle, mogę usunąć to tło za Ciebie —
> wystarczy, że wrzucisz pliki do `assets/` i dasz znać.

Formaty inne niż PNG (np. `.jpg`, `.webp`, `.svg`) też zadziałają — zmień wtedy
końcówkę nazwy w `index.html` (wyszukaj np. `logo-wku.png`).

---

## ✏️ Najczęstsze zmiany

| Co zmienić | Gdzie | Jak |
|---|---|---|
| Numer telefonu | `index.html` | wyszukaj `601 074 022` oraz `tel:+48601074022` |
| Link do Facebooka | `index.html` | wyszukaj `facebook.com/BajeczneUrwisy` |
| Dane szczeniąt | `index.html` | sekcja `id="szczenieta"` (imię, rasa, płeć, status) |
| Status szczeniaka | `index.html` | klasy: `status--free` / `status--booked` / `status--home` |
| Opinie klientów | `index.html` | sekcja `id="opinie"` |
| Kolory | `styles.css` | sekcja `:root` na samej górze pliku |

### Formularz kontaktowy (opcjonalnie e-mail)
Domyślnie formularz wyświetla podziękowanie. Jeśli chcesz, aby otwierał gotową
wiadomość e-mail, wpisz swój adres w `index.html`:

```html
<form ... id="contactForm" data-email="twoj-adres@email.pl" ...>
```

---

## 🌐 Jak opublikować stronę w internecie (za darmo)

Najłatwiejsze opcje (przeciągnij-i-upuść cały folder):

- **Netlify Drop** — https://app.netlify.com/drop
- **Cloudflare Pages** — https://pages.cloudflare.com
- **GitHub Pages** — dla osób korzystających z GitHuba

Po publikacji dostaniesz darmowy adres; można też podpiąć własną domenę.

---

🐾 *Małe pieski, wielka miłość.*
