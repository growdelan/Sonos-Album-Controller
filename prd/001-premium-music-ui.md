# PRD: Premium music-first frontend

## 1. Streszczenie produktu

Celem przyrostu jest gruntowne przeprojektowanie obecnego frontendu Sonos Album Controller w kierunku prywatnej, nowoczesnej aplikacji muzycznej klasy premium. Zmiana dotyczy wyłącznie warstwy HTML, CSS i vanilla JavaScript: wyglądu, UX, responsywności, dostępności i jakości interakcji.

Nowy interfejs ma być music-first, czyli najpierw eksponować albumy, okładki, aktualnie odtwarzany utwór i szybkie sterowanie, a dopiero w drugiej kolejności statusy techniczne i diagnostykę. Aplikacja nie powinna sprawiać wrażenia panelu administracyjnego ani dashboardu backendowego.

W ramach tego PRD nie zmienia się logika backendu, endpointy API, model danych, integracja z Sonos ani zależności projektu.

## 2. Problem i cel

Obecny frontend spełnia funkcję MVP, ale wizualnie jest zbyt techniczny, surowy i dashboardowy. Statusy backendu oraz diagnostyka dominują nad właściwym doświadczeniem muzycznym.

Celem jest stworzenie interfejsu, który po otwarciu od razu komunikuje:

- prywatny kontroler muzyki;
- duże okładki jako główny materiał wizualny;
- szybki dostęp do albumów i playera;
- ciemny, kinowy, miękki wygląd z subtelną głębią;
- mało ramek, mało technicznego szumu i czytelną hierarchię.

Inspiracja kierunkowa to Apple Music, Sonos, Linear i nowoczesne media control UI, bez kopiowania konkretnej aplikacji.

## 3. Główny użytkownik

Głównym użytkownikiem pozostaje właściciel jednego Sonos Era 300, korzystający lokalnie z aplikacji w przeglądarce na desktopie i okazjonalnie na urządzeniu mobilnym. Użytkownik chce szybko wybrać album, rozpocząć odtwarzanie, kontrolować player i nie oglądać technicznych szczegółów, dopóki nie są potrzebne.

Interfejs ma być wygodny dla jednej osoby, bez logowania, bez onboardingów marketingowych i bez mechanizmów wieloużytkownikowych.

## 4. Zakres funkcjonalny

Zakres obejmuje:

- przeprojektowanie ekranu albumów jako eleganckiej biblioteki muzycznej;
- kompaktowy header z nazwą aplikacji, krótkim podpisem, małymi statusami i drugorzędnymi akcjami;
- stały dolny player bar widoczny w aplikacji i niezastawiający treści;
- premium widok szczegółów albumu z dużą okładką, metadanymi, przyciskiem odtwarzania i lekką tracklistą;
- wizualne dopracowanie przycisku pętli, slidera głośności, stanów playera i statusu `Nic nie odtwarza`;
- dopracowanie stanów loading, empty, error i cache warning;
- poprawę responsywności desktop, tablet i mobile;
- poprawę dostępności elementów interaktywnych;
- uporządkowanie CSS przez design tokens i sekcje tematyczne.

Zakres nie obejmuje dodawania nowych endpointów, zmiany semantyki istniejących endpointów, przebudowy backendu, dodawania frameworków ani zewnętrznych bibliotek.

## 5. Wymagania UX/UI

### 5.1. Visual thesis

Interfejs ma realizować kierunek:

> premium music control surface - ciemny, kinowy, miękki, przestrzenny, z dużymi okładkami, subtelnymi gradientami, wyraźną typografią i minimalnym chrome.

Okładki albumów mają budować atmosferę aplikacji. Nie powinny wyglądać jak małe miniatury w technicznych kartach.

### 5.2. Hierarchia aplikacji

Najważniejsze w UI są kolejno:

1. albumy;
2. okładki;
3. aktualnie odtwarzany utwór;
4. szybkie sterowanie;
5. widok albumu;
6. diagnostyka i status techniczny.

Statusy backendu i Sonosa muszą być kompaktowe, np. jako małe status pills lub kropki ze stanem. Nie mogą występować jako duże karty typu `Backend ready` albo `Integracja Sonos configured`.

### 5.3. Header

Header ma zastąpić duży techniczny nagłówek kompaktowym paskiem aplikacyjnym.

Header zawiera:

- nazwę aplikacji;
- krótki podpis;
- małe statusy połączenia;
- informację o ostatnim odświeżeniu;
- drugorzędne akcje: diagnostyka, test połączenia i odświeżenie.

Statusy mają być drugorzędne wizualnie, np. zielona kropka + `Backend online`, zielona kropka + `Sonos configured`, oraz przygaszony tekst z czasem ostatniego odświeżenia.

### 5.4. Widok albumów

Widok albumów jest główną powierzchnią aplikacji.

Wymagania:

- duże okładki;
- czysta siatka;
- mało ramek;
- duże odstępy;
- czytelna hierarchia;
- subtelne animacje wejścia i hover;
- tytuł albumu maksymalnie w dwóch liniach;
- wykonawca mniejszy i przygaszony;
- cała karta albumu klikalna.

Siatka:

- desktop: 4-5 kolumn;
- tablet: 3 kolumny;
- mobile: 2 kolumny;
- okładki zawsze 1:1.

Hover albumu:

- okładka skaluje się lekko, około `1.035`;
- pojawia się miękki overlay;
- pojawia się przycisk play;
- karta dostaje subtelny glow.

Nagłówek sekcji albumów zawiera `Albumy`, liczbę albumów, ostatnie odświeżenie i mały przycisk odświeżenia. Lekkie lokalne pole wyszukiwania może zostać dodane jako nice-to-have tylko wtedy, gdy nie komplikuje istniejącej logiki i nie wymaga zmian backendu.

### 5.5. Player bar

Player bar ma być stałym dolnym paskiem odtwarzania i najważniejszym elementem użytkowym poza biblioteką albumów.

Wymagania:

- zawsze widoczny na dole ekranu;
- `position: fixed`;
- półprzezroczyste tło z `backdrop-filter`;
- subtelna górna linia;
- wysokość około 88-104 px na desktopie;
- odpowiedni `padding-bottom` głównej treści, aby player nie zasłaniał UI.

Player zawiera:

- miniaturę okładki;
- tytuł aktualnego utworu;
- album albo wykonawcę;
- stan `Nic nie odtwarza`, gdy nic nie gra;
- poprzedni utwór;
- play/pause jako główny przycisk;
- następny utwór;
- jeden przycisk pętli;
- płynny slider głośności;
- widoczną wartość głośności, np. `34%`.

### 5.6. Pętla

Przycisk pętli jest jednym przyciskiem cyklicznie zmieniającym trzy stany:

1. brak pętli - ikona szara;
2. pętla listy lub albumu - ikona podświetlona;
3. pętla jednego utworu - ikona podświetlona z małą jedynką `1`.

Zmiana dotyczy prezentacji i ergonomii istniejącej logiki pętli. Nie wolno zmieniać kontraktu endpointu `POST /api/playback/repeat`.

### 5.7. Głośność

Głośność ma być regulowana płynnie wyłącznie sliderem.

Wymagania:

- brak ręcznego wpisywania liczby;
- slider w zakresie 0-100%;
- obok slidera widoczna aktualna wartość procentowa;
- kontrola dostępna od razu, także po wejściu w album i w stanie `Nic nie odtwarza`;
- wygląd slidera ma być dopracowany, nie domyślny systemowy.

### 5.8. Widok szczegółów albumu

Widok albumu ma być muzyczny i nietabelaryczny.

Układ desktop:

- po lewej duża okładka;
- po prawej metadane albumu;
- duży tytuł albumu;
- wykonawca;
- liczba utworów, jeśli jest znana;
- główny przycisk `Odtwórz album`;
- drugorzędny przycisk `Wróć`.

Widok może używać subtelnego tła bazującego na okładce:

- rozmyta wersja okładki jako glow;
- gradient za nagłówkiem albumu;
- efekt elegancki i spokojny, bez zewnętrznych bibliotek.

Tracklista:

- bez ciężkiej tabeli;
- każdy utwór jako elegancki wiersz;
- numer po lewej;
- tytuł w środku;
- czas trwania po prawej;
- hover z delikatnym podświetleniem;
- aktywnie odtwarzany utwór ma osobny stan;
- na hover numer może zmienić się w ikonę play;
- kliknięcie utworu uruchamia istniejącą akcję odtwarzania.

Pierwszy utwór nie może wyglądać jak aktywny tylko dlatego, że jest pierwszy. Aktywność wynika wyłącznie ze stanu odtwarzania.

### 5.9. Styl wizualny

Frontend ma używać CSS variables w `:root`.

Kierunek tokenów:

```css
:root {
  --bg: #0b0d10;
  --bg-elevated: #12161d;
  --surface: rgba(255, 255, 255, 0.055);
  --surface-strong: rgba(255, 255, 255, 0.09);
  --border: rgba(255, 255, 255, 0.11);

  --text: #f6f1e8;
  --text-muted: #b7b0a6;
  --text-soft: #7f7a72;

  --accent: #e4b84f;
  --accent-strong: #ffd36a;
  --accent-soft: rgba(228, 184, 79, 0.16);

  --success: #9adbbd;
  --danger: #ff8a8a;

  --radius-sm: 10px;
  --radius-md: 16px;
  --radius-lg: 24px;
  --radius-xl: 32px;

  --shadow-soft: 0 24px 80px rgba(0, 0, 0, 0.32);
}
```

Tło nie może być jednolitą czernią. Powinno zawierać radial gradient, subtelną winietę, delikatne światło i opcjonalny bardzo subtelny pattern lub noise w CSS.

Należy unikać fioletowego startupowego stylu. Akcent ma być ciepły, muzyczny, złoty albo bursztynowy.

### 5.10. Typografia

Nie wolno dodawać zewnętrznych fontów. Należy użyć systemowego stacku:

```css
font-family:
  ui-sans-serif,
  -apple-system,
  BlinkMacSystemFont,
  "SF Pro Display",
  "Segoe UI",
  sans-serif;
```

Skala typograficzna:

- nazwa aplikacji: 28-40 px;
- tytuł albumu w szczegółach: 40-64 px;
- tytuł karty albumu: 15-17 px;
- podpisy i metadane: 12-14 px;
- przyciski: 14-15 px, semibold.

Małe etykiety, np. `ALBUM`, mogą używać uppercase i większego letter-spacing.

### 5.11. Przyciski

Interfejs ma mieć trzy warianty przycisków.

Primary:

- dla play i `Odtwórz album`;
- złoty lub bursztynowy akcent;
- mocny kontrast;
- delikatny cień;
- hover z lekkim uniesieniem;
- aktywny stan po kliknięciu.

Secondary:

- dla akcji `Wróć`, `Odśwież`, `Pokaż albumy`;
- subtelna ramka;
- półprzezroczyste tło;
- spokojny hover.

Ghost:

- dla technicznych akcji, takich jak diagnostyka i test połączenia;
- najmniej dominujący;
- tekstowy lub bardzo lekko obramowany;
- nie konkuruje z play.

### 5.12. Animacje

Należy dodać 2-3 celowe animacje.

Wymagane kierunki:

- wejście albumów: `opacity: 0 -> 1`, `transform: translateY(12px) -> 0`, mały stagger zależny od indeksu;
- hover albumu: lekka skala okładki, overlay, wejście przycisku play;
- wejście widoku albumu: delikatny fade i przesunięcie okładki, tytułu i tracklisty;
- aktualizacja playera: krótki, subtelny feedback miniatury lub tytułu po zmianie utworu.

Animacje muszą respektować reduced motion:

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation: none !important;
    transition: none !important;
    scroll-behavior: auto !important;
  }
}
```

## 6. Wymagania responsywności

Desktop:

- wykorzystać szerokość ekranu lepiej niż obecnie;
- max-width głównej treści około 1280-1440 px;
- większe okładki;
- więcej oddechu;
- mniej pudełek.

Tablet:

- siatka albumów w 3 kolumnach;
- zachować czytelność headera i playera;
- uniknąć nakładania kontrolek.

Mobile:

- header bardziej kompaktowy;
- techniczne statusy mniejsze albo zawijane;
- albumy w 2 kolumnach;
- widok albumu w jednej kolumnie;
- player bar na dole;
- przyciski minimum 44 px wysokości;
- slider głośności może przejść do drugiego rzędu;
- żaden tekst ani kontrolka nie może wychodzić poza ekran.

## 7. Stany interfejsu

Loading:

- elegancki skeleton;
- kwadratowe placeholdery okładek;
- delikatny shimmer;
- tekst `Ładowanie biblioteki...`.

Empty:

- komunikat `Brak albumów do wyświetlenia`;
- przycisk `Odśwież albumy`.

Error:

- spokojny error banner;
- bez agresywnej czerwieni na całym ekranie;
- możliwość przejścia do diagnostyki.

Nothing playing:

- player pokazuje `Nic nie odtwarza`;
- neutralny placeholder okładki;
- kontrolki w stanie gotowości albo disabled zgodnie z obecną logiką;
- głośność i mute pozostają dostępne tam, gdzie są już dostępne w obecnym przepływie.

Cache warning:

- dane z cache są oznaczone czytelnie, ale spokojnie;
- ostrzeżenie nie dominuje nad albumami.

## 8. Dostępność

Wymagania:

- prawdziwe `<button>` dla akcji;
- `aria-label` dla przycisków ikonowych i symbolicznych;
- widoczny `focus-visible`;
- dobry kontrast tekstu, kontrolek i stanów;
- logiczna kolejność tabulacji;
- targety dotykowe minimum 44 px tam, gdzie użytkownik klika lub dotyka;
- brak informacji przekazywanej wyłącznie kolorem.

## 9. Ograniczenia techniczne

Nie wolno dodawać:

- Reacta;
- Tailwinda;
- Bootstrapa;
- frameworków frontendowych;
- bundlera;
- bibliotek CSS;
- zewnętrznych ikon;
- zewnętrznych fontów;
- bibliotek animacji;
- zależności npm;
- nowych zależności backendowych.

Nie wolno zmieniać:

- istniejących endpointów API;
- kontraktów odpowiedzi backendu;
- logiki Sonos/SoCo;
- cache;
- sposobu startu aplikacji;
- modelu danych.

CSS powinien zostać uporządkowany w sekcje:

```css
/* Design tokens */
/* Base */
/* Layout */
/* App header */
/* Album grid */
/* Album detail */
/* Track list */
/* Player bar */
/* Buttons */
/* States */
/* Animations */
/* Responsive */
```

## 10. Wymagania funkcjonalne

### FR-01: Music-first header

Kryteria akceptacji:

- header jest kompaktowy;
- nazwa aplikacji i krótki podpis są widoczne;
- statusy backendu i Sonosa są małymi wskaźnikami;
- diagnostyka, test połączenia i odświeżenie są drugorzędne wizualnie;
- nie ma dużych technicznych kart statusu na górze.

### FR-02: Premium album grid

Kryteria akceptacji:

- albumy są pokazane jako duża, czytelna siatka;
- okładka dominuje nad tekstem;
- tytuł ma maksymalnie dwie linie;
- wykonawca jest mniejszy i przygaszony;
- cała karta jest klikalna;
- hover ma subtelny overlay, play affordance i glow.

### FR-03: Always-visible player bar

Kryteria akceptacji:

- player jest widoczny na dole ekranu;
- player nie zasłania treści;
- zawiera miniaturę, tytuł, album lub wykonawcę, play/pause, previous, next, pętlę, głośność i wartość procentową;
- w stanie bez odtwarzania pokazuje `Nic nie odtwarza`.

### FR-04: Premium album detail

Kryteria akceptacji:

- widok albumu ma dużą okładkę i wyraźny tytuł;
- metadane są czytelne i drugorzędne;
- dostępne są `Odtwórz album` i `Wróć`;
- tracklista nie wygląda jak ciężka tabela;
- aktywny utwór wynika wyłącznie ze stanu odtwarzania.

### FR-05: Loop control states

Kryteria akceptacji:

- jeden przycisk pętli pokazuje trzy stany;
- brak pętli jest szary;
- pętla albumu/listy jest podświetlona;
- pętla jednego utworu pokazuje podświetlenie i małą cyfrę `1`;
- zachowanie backendowe pętli pozostaje bez zmian.

### FR-06: Premium volume control

Kryteria akceptacji:

- głośność jest sterowana sliderem;
- nie ma pola ręcznego wpisywania liczby;
- aktualna wartość procentowa jest widoczna;
- slider ma dopracowany styl;
- kontrola działa w obecnych przepływach bez zmiany API.

### FR-07: Polished UI states

Kryteria akceptacji:

- loading ma skeleton i shimmer;
- empty state zawiera `Brak albumów do wyświetlenia` oraz `Odśwież albumy`;
- error state jest spokojnym bannerem i pozwala przejść do diagnostyki;
- cache warning jest czytelny, ale nie dominuje;
- nothing-playing ma neutralny placeholder i jasny stan kontrolek.

### FR-08: Responsive and accessible UI

Kryteria akceptacji:

- desktop, tablet i mobile mają stabilny layout;
- mobile nie ma overflow poza ekran;
- przyciski mają minimum 44 px wysokości tam, gdzie dotyczy;
- przyciski ikonowe mają `aria-label`;
- focus jest widoczny;
- informacje statusowe nie zależą wyłącznie od koloru.

## 11. Kryteria akceptacji

Zmiana jest zaakceptowana, gdy:

- po wejściu do aplikacji użytkownik widzi nowoczesną aplikację muzyczną, nie dashboard backendowy;
- statusy techniczne są drugorzędne i kompaktowe;
- albumy i okładki dominują wizualnie na ekranie głównym;
- player jest zawsze widoczny na dole i nie zasłania treści;
- widok albumu jest muzyczny, responsywny i nietabelaryczny;
- loading, empty, error, cache warning i nothing-playing mają dopracowane stany wizualne;
- UI działa poprawnie na desktopie i mobile bez wychodzenia elementów poza ekran;
- akcje są dostępne przez prawdziwe `<button>`, mają `aria-label` tam, gdzie potrzeba, widoczny `focus-visible`, kontrast i targety minimum 44 px;
- nie dodano frameworków, bundlera, bibliotek CSS, ikon, fontów ani zależności npm;
- nie zmieniono backendu, endpointów ani logiki aplikacji.

## 12. Poza zakresem

Poza zakresem są:

- nowe funkcje backendowe;
- zmiany API;
- zmiany integracji SoCo;
- nowe źródła albumów;
- automatyczne pobieranie lokalnych okładek;
- logowanie użytkowników;
- tryb wielu głośników;
- zdalny dostęp;
- konteneryzacja;
- zmiana sposobu uruchamiania aplikacji;
- zależności frontendowe;
- redesign jako landing page albo marketingowa strona produktu.

## 13. Walidacja

Minimalna walidacja implementacji tego PRD:

- `uv run python -m unittest discover -s tests -p "test_*.py"`;
- `node --check src/sonos_album_controller/static/app.js`;
- `git diff --check`;
- Browser smoke na desktopowym viewportcie: start aplikacji, lista albumów, odświeżenie, wejście w album, start odtwarzania, pętla, głośność, mute, diagnostyka;
- Browser smoke na mobilnym viewportcie: lista albumów w 2 kolumnach, widok albumu w jednej kolumnie, player bez zasłaniania treści, brak poziomego overflow;
- kontrola reduced motion przez `prefers-reduced-motion`;
- kontrola klawiatury: tab order, focus-visible, aktywacja głównych przycisków;
- kontrola braku nowych zależności w `pyproject.toml`, `uv.lock` oraz braku plików npm.
