YouTube (click image)
[![Show on YouTube](https://img.youtube.com/vi/Nl8CV5NyW24/0.jpg)](https://www.youtube.com/watch?v=Nl8CV5NyW24)


# Guide Lines — Desktop v0.3

Desktop guide lines for Windows. Draw thin horizontal / vertical lines over any app, move them precisely, and keep them while you work.

Built for **Remote Desktop / Chrome Remote Desktop**: no `grabMouse()`, dragging via polling, big hitboxes, so lines stay grabbable over RDP.

> English version: `Lines_Desktop_v0.3_EN.py` — default language is English.
> Polish version: `Lines_Desktop_v0.3.py` — same features, Polish UI.
> Shortcuts are **editable in Settings** in both versions.

---

## Requirements

- Windows
- Python 3.10+
- `pip install PyQt6 pystray Pillow keyboard`

Run as administrator if global hotkeys do not register (the `keyboard` library needs it on some systems).

## Run

```bash
py Lines_Desktop_v0.3_EN.py
```

The app lives in the system tray. Right-click the tray icon for quick actions.

State (lines, colours, thickness, ruler position, language, **shortcuts**) is saved to:

```
%USERPROFILE%\\.gridlines_app_state.json
```

## How it works

- **Rulers** sit on the top and left by default. Drag a new line out of a ruler, or use a shortcut.
- **Create by shortcut:** a new horizontal line appears 20 px from the top, a new vertical line 20 px from the left. Next lines are offset by +12 px so they do not overlap.
- **Numbering:** `H1..H10` horizontal, `V1..V10` vertical. `0` means line `10`. The number is assigned on creation.
- **Labels:** each line has a separate label (`H1`, `V3`, …) next to the edge, never truncated.
- **Active line:** does **not** change thickness. Only its label changes: yellow background → red background, white font.
- **Double-click** a line to delete it. Drag a line to move it. Drag a line back onto a ruler to delete it.

## Settings

Open with `Ctrl+Alt+Shift+U` or from the tray: **Appearance Settings…**

| Setting | Range | Default |
|---|---:|---:|
| Line thickness | 1–20 | 1 |
| Transparency | 0–255 | 200 |
| Colour | picker | `#00FCEA` |
| Grab edge thickness of line | 1–50 px | 24 px |
| Screen edge thickness (rulers) | 1–60 px | 24 px |

- **Grab edge thickness of line:** how wide the invisible grab handle of a line is. RDP: 20–30 px.
- **Screen edge thickness (rulers):** how wide the ruler bar on the sides / top is, where you drag new lines from. RDP: 24–32 px. Minimum is **1 px**.
- Settings window is large (740×880) with 14–15 px fonts, so it stays readable.

### Editable shortcuts

In **Settings → Shortcuts**, every default shortcut below can be changed.

- Type a shortcut as `Ctrl+Alt+Shift+H`, `Shift+Del`, `Ctrl+Alt+Shift+PageUp`, …
- Click **Apply Shortcuts** to save and re-register immediately. No restart needed.
- Click **Reset to Defaults** to restore the table below.
- No duplicates allowed. Empty shortcuts are rejected.
- Warnings (not errors): a shortcut that uses `Win`, or `Ctrl+Alt+C / L / O` (Polish `Ć / Ł / Ó` via `AltGr`), shows a warning.

> **Direct select** (`Ctrl+Alt+Shift+1+X …`) is not a separate field. It follows the modifiers of **Create horizontal line**. If you change Create horizontal to `Ctrl+Shift+H`, direct select becomes `Ctrl+Shift+1+X …`.

Shortcuts are saved to the state JSON file under `"skroty"`.

## Shortcuts

Default shortcuts. All of them are editable in Settings, except direct select (see above).

| Action | Shortcut | Notes |
|---|:---:|---|
| Create horizontal line | `Ctrl+Alt+Shift+H` | 20 px from top, next +12 px |
| Create vertical line | `Ctrl+Alt+Shift+V` | 20 px from left, next +12 px |
| Move mode (toggle) | `Ctrl+Alt+Shift+M` | Needs an active line |
| Show / hide lines | `Ctrl+Alt+Shift+W` | Hides rulers + lines |
| Change ruler position | `Ctrl+Alt+Shift+P` | Cycles `top-left` → `top-right` → … |
| Clear all lines | `Ctrl+Alt+Shift+K` | Deletes every line |
| Settings | `Ctrl+Alt+Shift+U` | Opens Settings |
| Language PL / EN | `Ctrl+Alt+Shift+J` | Toggles Polish / English |
| Quit | `Ctrl+Alt+Shift+Q` | Quits the app |
| Increase line thickness | `Ctrl+Alt+Shift+PageUp` | +1, up to 20 |
| Decrease line thickness | `Ctrl+Alt+Shift+PageDown` | −1, down to 1 |
| Delete active line | `Shift+Del` | **Always**, not only in move mode |

### Move mode

First select a line (see below), then press **Move mode**. No black bar is shown in move mode.

| Action | Key |
|---|:---:|
| Move left / right / up / down | `←` / `→` / `↑` / `↓` |
| Move fast | Arrow = **10 px** |
| Move slow / precise | `Shift+Arrow` = **1 px** |
| Exit move mode | `Esc` or `Enter` |

Arrows work **only** in move mode. Outside move mode they are not blocked, so they keep working in Word / Chrome / etc.

### Select a line directly

No separate Select mode (`G`) — it was removed. Select directly:

| Action | Shortcut |
|---|:---:|
| Select horizontal line 1 | `Ctrl+Alt+Shift+1+X` |
| Select horizontal line 2 | `Ctrl+Alt+Shift+2+X` |
| … | … |
| Select horizontal line 10 | `Ctrl+Alt+Shift+0+X` |
| Select vertical line 1 | `Ctrl+Alt+Shift+1+Y` |
| Select vertical line 2 | `Ctrl+Alt+Shift+2+Y` |
| … | … |
| Select vertical line 10 | `Ctrl+Alt+Shift+0+Y` |

- `X` = horizontal (`H`), `Y` = vertical (`V`), `0` = line `10`.
- After selecting, press **Move mode** to move with arrows, or press `Shift+Del` to delete.

## Why these shortcuts?

- **No `Win` key** — on request.
- **Base `Ctrl+Alt+Shift`** — not used by Windows / Office / Chrome / Firefox / Opera for these letters.
- **No Polish letters `C / L / O`** — `Ctrl+Alt` is `AltGr` on a Polish layout, so `Ctrl+Alt+Shift+C` = `Ć`, `L` = `Ł`, `O` = `Ó`. That is why the defaults use:
  - Visibility `W` (not `O`),
  - Clear `K` (not `C`),
  - Language `J` (not `L`).
- Direct select needs a digit too (`Ctrl+Alt+Shift+1+X`), so plain `Ż` (`AltGr+Shift+X`) does **not** trigger it.

## Notes

- **Shift+Del is global.** While the app runs, `Shift+Del` in Explorer / Word is blocked, because it deletes the active line. Close the app to get Explorer `Shift+Del` back.
- **No black bar in move mode** — the top `MOVE MODE: …` bar was removed on request.
- **Active line** never gets thicker. Only its label turns red with white text.
- **RDP:** polling every ~16 ms, no `grabMouse()`, so dragging works through Chrome Remote Desktop.
- **Snap to lines in PowerPoint:** not implemented in v0.3 (left for later).

## Version

**v0.3** — shown in the tray menu, Settings window, and title bar.

Changelog v0.3 vs v0.2:

- RDP polling, no `grabMouse()`
- Line numbering `H1..H10` / `V1..V10`
- Create by shortcut, 20 px + 12 px offset
- Direct select, move mode with arrows
- Editable shortcuts in Settings (EN version)
- Screen edge thickness 1–60 px, min 1 px
- Fixed truncated labels, fixed corner crash (`self.ramka_naroznika`)
  
---

# Linie Pomocnicze — Desktop v0.3

Linie pomocnicze na pulpit w Windows. Rysuj cienkie poziome / pionowe linie na dowolnej aplikacji, przesuwaj je precyzyjnie i trzymaj podczas pracy.

Zrobione pod **pulpit zdalny / Chrome Remote Desktop**: brak `grabMouse()`, przeciąganie przez polling, duże hitboxy, więc linie da się chwycić przez RDP.

> Wersja polska: `Lines_Desktop_v0.3.py` — domyślnie język polski.
> Wersja angielska: `Lines_Desktop_v0.3_EN.py` — ten sam program, UI po angielsku.
> Skróty są **edytowalne w Ustawieniach** w obu wersjach.

---

## Wymagania

- Windows
- Python 3.10+
- `pip install PyQt6 pystray Pillow keyboard`

Jeśli skróty globalne się nie rejestrują, uruchom jako administrator (biblioteka `keyboard` na niektórych systemach tego wymaga).

## Uruchomienie

```bash
py Lines_Desktop_v0.3.py
```

Program siedzi w zasobniku systemowym (tray). Prawy klik na ikonę = szybkie akcje.

Stan (linie, kolor, grubość, pozycja linijek, język, **skróty**) zapisywany jest do:

```
%USERPROFILE%\\.gridlines_app_state.json
```

## Jak to działa

- **Linijki** domyślnie na górze i z lewej. Przeciągnij nową linię z linijki albo użyj skrótu.
- **Tworzenie skrótem:** nowa pozioma linia pojawia się 20 px od góry, nowa pionowa 20 px od lewej. Kolejne linie +12 px, żeby się nie nakładały.
- **Numeracja:** `H1..H10` poziome, `V1..V10` pionowe. `0` oznacza linię `10`. Numer nadawany przy tworzeniu.
- **Etykiety:** każda linia ma osobną etykietę (`H1`, `V3`, …) przy krawędzi, nigdy nie ucinaną.
- **Aktywna linia:** **nie** zmienia grubości. Zmienia się tylko jej etykieta: żółte tło → czerwone tło, biała czcionka.
- **Podwójny klik** na linię usuwa ją. Przeciąganie przesuwa linię. Przeciągnięcie linii z powrotem na linijkę usuwa ją.

## Ustawienia

Otwórz `Ctrl+Alt+Shift+U` albo z tray: **Ustawienia Wyglądu…**

| Ustawienie | Zakres | Domyślnie |
|---|---:|---:|
| Grubość linii | 1–20 | 1 |
| Przezroczystość | 0–255 | 200 |
| Kolor | wybór | `#00FCEA` |
| Grubość krawędzi do chwytania linii | 1–50 px | 24 px |
| Grubość krawędzi ekranu (linijki) | 1–60 px | 24 px |

- **Grubość krawędzi do chwytania linii:** jak szeroki jest niewidoczny uchwyt linii. RDP: 20–30 px.
- **Grubość krawędzi ekranu (linijki):** jak szeroki jest pasek linijki na bokach / górze, skąd przeciągasz nowe linie. RDP: 24–32 px. Minimum to **1 px**.
- Okno Ustawień jest duże (740×880), czcionki 14–15 px, żeby było czytelne.

### Edytowalne skróty

W **Ustawienia → Skróty** każdy domyślny skrót poniżej da się zmienić.

- Wpisz skrót jako `Ctrl+Alt+Shift+H`, `Shift+Del`, `Ctrl+Alt+Shift+PageUp`, …
- Kliknij **Zastosuj skróty**, żeby zapisać i od razu prze-rejestrować. Bez restartu.
- Kliknij **Przywróć domyślne**, żeby wrócić do tabeli poniżej.
- Bez duplikatów. Puste skróty odrzucane.
- Ostrzeżenia (nie błędy): skrót z `Win` albo `Ctrl+Alt+C / L / O` (polskie `Ć / Ł / Ó` przez `AltGr`) pokaże ostrzeżenie.

> **Wybór bezpośredni** (`Ctrl+Alt+Shift+1+X …`) nie ma osobnego pola. Bierze modyfikatory z **Utwórz poziomą**. Jak zmienisz Utwórz poziomą na `Ctrl+Shift+H`, to wybór bezpośredni zrobi się `Ctrl+Shift+1+X …`.

Skróty zapisywane są w pliku stanu pod `"skroty"`.

> Nazwy skrótów w Ustawieniach tłumaczą się razem z językiem. Przełącz `Ctrl+Alt+Shift+J` i cała lista w Ustawieniach przechodzi na PL / EN, bez restartu.

## Skróty

Domyślne skróty. Wszystkie da się zmienić w Ustawieniach, oprócz wyboru bezpośredniego (patrz wyżej).

| Akcja | Skrót | Uwagi |
|---|:---:|---|
| Utwórz poziomą linię | `Ctrl+Alt+Shift+H` | 20 px od góry, kolejna +12 px |
| Utwórz pionową linię | `Ctrl+Alt+Shift+V` | 20 px od lewej, kolejna +12 px |
| Tryb przesuwania (włącz/wyłącz) | `Ctrl+Alt+Shift+M` | Trzeba mieć aktywną linię |
| Pokaż / ukryj linie | `Ctrl+Alt+Shift+W` | Ukrywa linijki + linie |
| Zmień pozycję linijek | `Ctrl+Alt+Shift+P` | Cyklicznie `góra-lewo` → `góra-prawo` → … |
| Wyczyść wszystkie linie | `Ctrl+Alt+Shift+K` | Usuwa wszystkie linie |
| Ustawienia | `Ctrl+Alt+Shift+U` | Otwiera Ustawienia |
| Język PL / EN | `Ctrl+Alt+Shift+J` | Przełącza polski / angielski |
| Wyjście | `Ctrl+Alt+Shift+Q` | Zamyka program |
| Zwiększ grubość linii | `Ctrl+Alt+Shift+PageUp` | +1, maks. 20 |
| Zmniejsz grubość linii | `Ctrl+Alt+Shift+PageDown` | −1, min. 1 |
| Usuń aktywną linię | `Shift+Del` | **Zawsze**, nie tylko w trybie przesuwania |

### Tryb przesuwania

Najpierw wybierz linię (patrz niżej), potem włącz **tryb przesuwania**. W trybie przesuwania **nie ma** czarnej ramki u góry.

| Akcja | Klawisz |
|---|:---:|
| Przesuń w lewo / prawo / górę / dół | `←` / `→` / `↑` / `↓` |
| Przesuń szybko | Strzałka = **10 px** |
| Przesuń wolno / precyzyjnie | `Shift+Strzałka` = **1 px** |
| Wyjdź z trybu przesuwania | `Esc` albo `Enter` |

Strzałki działają **tylko** w trybie przesuwania. Poza nim nie są blokowane, więc dalej działają w Wordzie / Chrome itd.

### Wybór linii bezpośrednio

Nie ma osobnego trybu Wybór (`G`) — został usunięty. Wybieraj bezpośrednio:

| Akcja | Skrót |
|---|:---:|
| Wybierz poziomą linię 1 | `Ctrl+Alt+Shift+1+X` |
| Wybierz poziomą linię 2 | `Ctrl+Alt+Shift+2+X` |
| … | … |
| Wybierz poziomą linię 10 | `Ctrl+Alt+Shift+0+X` |
| Wybierz pionową linię 1 | `Ctrl+Alt+Shift+1+Y` |
| Wybierz pionową linię 2 | `Ctrl+Alt+Shift+2+Y` |
| … | … |
| Wybierz pionową linię 10 | `Ctrl+Alt+Shift+0+Y` |

- `X` = pozioma (`H`), `Y` = pionowa (`V`), `0` = linia `10`.
- Po wybraniu wciśnij **tryb przesuwania**, żeby ruszać strzałkami, albo `Shift+Del`, żeby usunąć.

## Dlaczego takie skróty?

- **Bez klawisza `Win`** — na życzenie.
- **Baza `Ctrl+Alt+Shift`** — nie używana przez Windows / Office / Chrome / Firefox / Opera dla tych liter.
- **Bez polskich liter `C / L / O`** — `Ctrl+Alt` to `AltGr` w polskim układzie, więc `Ctrl+Alt+Shift+C` = `Ć`, `L` = `Ł`, `O` = `Ó`. Dlatego domyślnie:
  - Widoczność `W` (nie `O`),
  - Wyczyść `K` (nie `C`),
  - Język `J` (nie `L`).
- Wybór bezpośredni wymaga też cyfry (`Ctrl+Alt+Shift+1+X`), więc samo `Ż` (`AltGr+Shift+X`) go **nie** odpala.

## Uwagi

- **Shift+Del jest globalny.** Gdy program działa, `Shift+Del` w Eksploratorze / Wordzie jest blokowany, bo kasuje aktywną linię. Zamknij program, żeby odzyskać `Shift+Del` w Eksploratorze.
- **Brak czarnej ramki w trybie przesuwania** — pasek u góry `TRYB PRZESUWANIA: …` został usunięty na życzenie.
- **Aktywna linia** nigdy nie robi się grubsza. Tylko jej etykieta robi się czerwona z białą czcionką.
- **RDP:** polling co ~16 ms, brak `grabMouse()`, więc przeciąganie działa przez Chrome Remote Desktop.
- **Snap do linii w PowerPoint:** nie ma w v0.3 (do zrobienia później).


## Wersja

**v0.3** — pokazywana w tray, w Ustawieniach i w tytule.

Zmiany v0.3 vs v0.2:

- RDP polling, brak `grabMouse()`
- Numeracja linii `H1..H10` / `V1..V10`
- Tworzenie skrótem, 20 px + 12 px
- Wybór bezpośredni, tryb przesuwania strzałkami
- Edytowalne skróty w Ustawieniach
- Grubość krawędzi ekranu 1–60 px, min 1 px
- Poprawione ucinane etykiety, fix crasha narożnika (`self.ramka_naroznika`)

