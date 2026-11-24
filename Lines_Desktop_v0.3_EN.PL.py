# --- Lines Desktop v0.3 - RDP - POPRAWKI (bez Win, bez Wybór, bez czarnej ramki, Shift+Del zawsze, krawędź od 1px) ---
# Wersja: 0.3
# Poprawki w tej wersji pliku:
#  - BEZ Win: baza Ctrl+Alt+Shift, bez klawisza Win. Bez polskich liter C/L/O -> K/J/W, żeby nie robić Ć/Ł/Ó przez AltGr.
#  - USUNIĘTY skrót Wybór (G). Został wybór bezpośredni Ctrl+Alt+Shift+1+X ... +0+Y.
#  - USUNIĘTY opis w czarnej ramce w trybie przesuwania. W trybie przesuwania nic nie pokazuje się u góry.
#  - Shift+Del ZAWSZE kasuje aktywną linię, nie tylko w trybie przesuwania. Globalny, blokuje Shift+Del w Eksploratorze gdy app działa.
#  - Grubość krawędzi ekranu (linijki): MIN 1px, nie 8px. Zakres 1-60px, domyślnie 24px.
#  - Strzałki: normalna = szybko 10px, Shift+strzałka = wolno 1px.
#  - Opisy linii: osobny QLabel, nie ucinane. Aktywna: tło czerwone, czcionka biała, bez zmiany grubości.
#  - Ustawienia: większe okno 660x580, czcionki 14-15px. 'Grubość krawędzi do chwytania linii:'.
#  - FIX crash: Naroznik.ramka jako self.ramka_naroznika, nie zmienna lokalna (NameError w aktualizuj_rozmiar).
# Zmiany vs 0.2:
#  - RDP: brak grabMouse(), przeciąganie przez polling QCursor.pos() + QApplication.mouseButtons()
#  - RDP: linijka ma hitbox 24px (wizualnie dalej kreska), linia ma konfigurowalny uchwyt 1-50px (domyślnie 24px)
#  - RDP: sprawdzanie odległości kliknięcia od środka linii, linie przestają się wzajemnie przykrywać
#  - Numeracja linii: H1..H10 (poziome, X) i V1..V10 (pionowe, Y), 0 = 10, numer nadawany przy tworzeniu
#  - Tworzenie skrótem: pozioma 20px od góry, pionowa 20px od lewej (kolejne +12px, żeby się nie nakładały)
#  - Wybór skrótem: Ctrl+Alt+Shift+G (tryb wyboru) + cyfra 1-0 + X/Y, lub bezpośrednio Ctrl+Alt+Shift+1+X itd.
#  - Po aktywacji: tryb przesuwania strzałkami (1px, Shift+strzałka = 10px, Esc = wyjście)
#  - Wszystkie skróty na bazie Ctrl+Alt+Shift, żeby nie kolidować z Windows / Office / Chrome / Firefox / Opera
#  - Ustawienia: grubość krawędzi do chwytania 1-50px
#  - Wersja 0.3 pokazywana w trayu, ustawieniach i podpowiedziach
#
# Uruchomienie:  py Lines_Desktop_v0.3.py
# Wymaga: pip install PyQt6 pystray Pillow keyboard

import sys
import os
import json
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QSizePolicy, QColorDialog,
                             QDialog, QSpinBox, QSlider, QPushButton, QVBoxLayout,
                             QFormLayout, QHBoxLayout, QLineEdit)
from PyQt6.QtGui import (QPainter, QColor, QPen, QCursor, QIcon, QPixmap, QBrush, QPalette, QFont)
from PyQt6.QtCore import (Qt, QPoint, QRect, QSize, QObject, pyqtSignal, QTimer, QLocale, QEvent)
import pystray
from PIL import Image, ImageDraw
import keyboard
import threading
import time
import math

# --- Wersja ---
WERSJA = "0.3"
NAZWA_APLIKACJI = f"Linie Pomocnicze v{WERSJA}"

# --- Stałe konfiguracyjne ---
ROZMIAR_LINIJKI = 24  # v0.3: było 1px, teraz 24px hitbox dla RDP. Wizualnie dalej cienka kreska + podziałka.
KOLOR_TLA_LINIJKI = QColor(238, 238, 238)
KOLOR_ZNACZNIKA_GLOWNEGO = QColor(0, 0, 0)
KOLOR_ZNACZNIKA_SREDNIEGO = QColor(102, 102, 102)
KOLOR_ZNACZNIKA_POMNIEJSZEGO = QColor(170, 170, 170)
KOLOR_RAMKI = QColor(204, 204, 204)
KOLOR_TLA_PODPOWIEDZI = QColor(0, 0, 0, 255)
KOLOR_TEKSTU_PODPOWIEDZI = QColor(255, 255, 255)
KOLOR_AKTYWNEJ_LINII = QColor(255, 170, 0)  # pomarańczowy obrys dla aktywnej linii
PLIK_STANU = os.path.join(os.path.expanduser("~"), ".gridlines_app_state.json")
DOMYSLNA_GRUBOSC_SIATKI = 1
DOMYSLNY_KOLOR_SIATKI = "#00FCEA"
DOMYSLNA_PRZEZROCZYSTOSC_SIATKI = 200
DOMYSLNA_POZYCJA_LINIJEK = 'top-left'
POZYCJE_LINIJEK = ['top-left', 'top-right', 'bottom-right', 'bottom-left']
MAKS_GRUBOSC_SIATKI = 20  # v0.3: było 3840, bez sensu dla linii. 1-20 pt wystarczy.
KROK_ZMIANY_GRUBOSCI = 1
DOMYSLNY_JEZYK = 'pl'

# --- v0.3: chwytanie / RDP ---
DOMYSLNA_GRUBOSC_CHWYTU = 24
DOMYSLNA_GRUBOSC_KRAWEDZI_EKRANU = 24  # grubość linijki na bokach i u góry, skąd się produkuje linie
MIN_GRUBOSC_KRAWEDZI_EKRANU = 1  # na życzenie: min 1px, nie 8px
MAX_GRUBOSC_KRAWEDZI_EKRANU = 60  # grubość niewidocznego uchwytu linii, 1-50px, ustawiane w Ustawieniach
MIN_GRUBOSC_CHWYTU = 1
MAX_GRUBOSC_CHWYTU = 50
DOMYSLNA_POZYCJA_NOWEJ_LINII = 20  # 20px od lewej (pionowa) lub od góry (pozioma)
KROK_POZYCJI_NOWEJ_LINII = 12  # kolejne linie +12px, żeby się nie nakładały na 20px
MAX_LICZBA_LINII_NA_ORIENTACJE = 10  # H1..H10 i V1..V10, 0 = 10
KROK_STRZALKA = 10  # normalna strzałka = SZYBKIE 10px
KROK_STRZALKA_SHIFT = 1  # Shift+strzałka = WOLNE 1px

# --- Skróty - BAZA: Ctrl+Alt+Shift, BEZ Win ---
# Bez Win na życzenie. Bez polskich liter C/L/O, żeby nie robić Ć/Ł/Ó przez AltGr.
# BAZA: Ctrl+Alt+Shift, BEZ klawisza Win (na życzenie) i BEZ polskich liter.
# Dlaczego bez C/L/O? Ctrl+Alt to AltGr w polskim układzie.
# Ctrl+Alt+Shift+C = Ć, Ctrl+Alt+Shift+L = Ł, Ctrl+Alt+Shift+O = Ó.
# Dlatego: Wyczyść C -> K (Kasuj), Język L -> J (Język), Widoczność O -> W (Widoczność).
# Pozostałe litery H/V/M/P/U/J/Q/K/W nie mają polskich odpowiedników przez AltGr, więc są bezpieczne.
# Bezpośrednie chords Ctrl+Alt+Shift+1+X wymagają też cyfry, więc samo Ż (AltGr+Shift+X) ich nie odpala.
SKROT_UTWORZ_POZIOMA = "ctrl+alt+shift+h"   # H = Horizontal / pozioma, bezpieczna
SKROT_UTWORZ_PIONOWA = "ctrl+alt+shift+v"    # V = Vertical / pionowa, bezpieczna
# SKROT_TRYB_WYBORU USUNIĘTY na życzenie - nie ma już skrótu Wybór (G). Został tylko wybór bezpośredni Ctrl+Alt+Shift+1+X ... +0+Y.
SKROT_TRYB_PRZESUWANIA = "ctrl+alt+shift+m"  # M = Move / przesuwanie
SKROT_WIDOCZNOSC = "ctrl+alt+shift+w"        # W = Widoczność (wcześniej O = Ó, konflikt PL)
SKROT_POZYCJA_LINIJEK = "ctrl+alt+shift+p"   # P = pozycja linijek
SKROT_WYCZYSC_WSZYSTKO = "ctrl+alt+shift+k"  # K = Kasuj (wcześniej C = Ć, konflikt PL)
SKROT_USTAWIENIA = "ctrl+alt+shift+u"        # U = ustawienia
SKROT_JEZYK = "ctrl+alt+shift+j"             # J = Język (wcześniej L = Ł, konflikt PL)
SKROT_WYJSCIE = "ctrl+alt+shift+q"           # Q = quit, NIE Ctrl+Alt+End (przechwytywane przez Windows)
SKROT_ZWIEKSZ_GRUBOSC = "ctrl+alt+shift+pageup"
SKROT_ZMNIEJSZ_GRUBOSC = "ctrl+alt+shift+pagedown"
SKROT_USUN_AKTYWNA = "shift+del"

# --- Edytowalne skróty: domyślne, bieżące w Aplikacja.skroty ---
DOMYSLNE_SKROTY = {
    'utworz_pozioma': "ctrl+alt+shift+h",
    'utworz_pionowa': "ctrl+alt+shift+v",
    'tryb_przesuwania': "ctrl+alt+shift+m",
    'widocznosc': "ctrl+alt+shift+w",
    'pozycja_linijek': "ctrl+alt+shift+p",
    'wyczysc_wszystko': "ctrl+alt+shift+k",
    'ustawienia': "ctrl+alt+shift+u",
    'jezyk': "ctrl+alt+shift+j",
    'wyjscie': "ctrl+alt+shift+q",
    'zwieksz_grubosc': "ctrl+alt+shift+pageup",
    'zmniejsz_grubosc': "ctrl+alt+shift+pagedown",
    'usun_aktywna': "shift+del",
}
NAZWY_SKROTOW_PL = {
    'utworz_pozioma': "Utwórz poziomą linię",
    'utworz_pionowa': "Utwórz pionową linię",
    'tryb_przesuwania': "Tryb przesuwania (włącz/wyłącz)",
    'widocznosc': "Pokaż / ukryj linie",
    'pozycja_linijek': "Zmień pozycję linijek",
    'wyczysc_wszystko': "Wyczyść wszystkie linie",
    'ustawienia': "Ustawienia",
    'jezyk': "Język PL / EN",
    'wyjscie': "Wyjście",
    'zwieksz_grubosc': "Zwiększ grubość linii",
    'zmniejsz_grubosc': "Zmniejsz grubość linii",
    'usun_aktywna': "Usuń aktywną linię",
}

NAZWY_SKROTOW_EN = {
    'utworz_pozioma': "Create horizontal line",
    'utworz_pionowa': "Create vertical line",
    'tryb_przesuwania': "Move mode (toggle)",
    'widocznosc': "Show / hide lines",
    'pozycja_linijek': "Change ruler position",
    'wyczysc_wszystko': "Clear all lines",
    'ustawienia': "Settings",
    'jezyk': "Language PL / EN",
    'wyjscie': "Quit",
    'zwieksz_grubosc': "Increase line thickness",
    'zmniejsz_grubosc': "Decrease line thickness",
    'usun_aktywna': "Delete active line",
}

def normalizuj_skrot(s):
    if not isinstance(s, str):
        return ""
    parts=[p.strip().lower() for p in s.split("+") if p.strip()]
    return "+".join(parts)
def pobierz_skrot(klucz):
    try:
        if instancja_aplikacji is not None and hasattr(instancja_aplikacji, 'skroty') and klucz in instancja_aplikacji.skroty:
            return instancja_aplikacji.skroty[klucz]
    except Exception:
        pass
    return DOMYSLNE_SKROTY.get(klucz, "")
def sprawdz_skroty(nowe):
    bledy=[]
    widziane={}
    for k,v in nowe.items():
        nv=normalizuj_skrot(v)
        if not nv:
            bledy.append(f"{k}: pusty skrót")
            continue
        if nv in widziane:
            bledy.append(f"Duplikat: {k} i {widziane[nv]} mają ten sam skrót {nv}")
        else:
            widziane[nv]=k
    return bledy
  # ZAWSZE kasuje aktywną linię, nie tylko w trybie przesuwania (na życzenie)

# --- Zmienne globalne ---
instancja_aplikacji = None
instancja_ikony_zasobnika = None
id_glownego_watku = None

# --- Konteksty tłumaczeń ---
KONTEKST_TRAY = "TrayMenu"
KONTEKST_SETTINGS = "SettingsDialog"
KONTEKST_GRIDLINE = "GridlineWidget"
KONTEKST_APP = "GridlinesApp"

SLOWNIK_TLUMACZEN = {
    'pl': {
        f"{KONTEKST_TRAY}|Ukryj/Pokaż Linie ({{}})": "Ukryj/Pokaż Linie ({})",
        f"{KONTEKST_TRAY}|Zmień Pozycję ({{}})": "Zmień Pozycję ({})",
        f"{KONTEKST_TRAY}|Wyczyść Wszystko ({{}})": "Wyczyść Wszystko ({})",
        f"{KONTEKST_TRAY}|Ustawienia Wyglądu...": "Ustawienia Wyglądu...",
        f"{KONTEKST_TRAY}|Język / Language": "Język / Language",
        f"{KONTEKST_TRAY}|Polski": "Polski",
        f"{KONTEKST_TRAY}|English": "English",
        f"{KONTEKST_TRAY}|Wyjście ({{}})": "Wyjście ({})",
        f"{KONTEKST_TRAY}|Linie Pomocnicze": "Linie Pomocnicze",
        f"{KONTEKST_TRAY}|Utwórz poziomą ({{}})": "Utwórz poziomą ({})",
        f"{KONTEKST_TRAY}|Utwórz pionową ({{}})": "Utwórz pionową ({})",
        f"{KONTEKST_TRAY}|Wybierz linię ({{}})": "Wybierz linię ({})",
        f"{KONTEKST_SETTINGS}|Ustawienia Linii Pomocniczych": "Ustawienia Linii Pomocniczych",
        f"{KONTEKST_SETTINGS}|Grubość:": "Grubość:",
        f"{KONTEKST_SETTINGS}| px": " px",
        f"{KONTEKST_SETTINGS}|Skróty: Zwiększ: {{}}, Zmniejsz: {{}}": "Skróty: Zwiększ: {}, Zmniejsz: {}",
        f"{KONTEKST_SETTINGS}|Kolor:": "Kolor:",
        f"{KONTEKST_SETTINGS}|Wybierz Kolor": "Wybierz Kolor",
        f"{KONTEKST_SETTINGS}|Wybierz Kolor Linii": "Wybierz Kolor Linii",
        f"{KONTEKST_SETTINGS}|Przezroczystość:": "Przezroczystość:",
        f"{KONTEKST_SETTINGS}|Zamknij": "Zamknij",
        f"{KONTEKST_SETTINGS}|Grubość krawędzi do chwytania:": "Grubość krawędzi do chwytania linii:",
        f"{KONTEKST_SETTINGS}|Podpowiedź chwytania": "RDP: 20-30 px. Im większa, tym łatwiej chwycić przez pulpit zdalny.",
        f"{KONTEKST_SETTINGS}|Grubość krawędzi ekranu:": "Grubość krawędzi ekranu (linijki):",
        f"{KONTEKST_SETTINGS}|Podpowiedź krawędzi ekranu": "Szerokość paska na bokach i u góry, skąd przeciągasz nowe linie. RDP: 24-32 px. Min 1 px.",
        f"{KONTEKST_GRIDLINE}|Y: {{pos}}px": "Y: {pos}px",
        f"{KONTEKST_GRIDLINE}|X: {{pos}}px": "X: {pos}px",
    },
    'en': {
        f"{KONTEKST_TRAY}|Ukryj/Pokaż Linie ({{}})": "Hide/Show Lines ({})",
        f"{KONTEKST_TRAY}|Zmień Pozycję ({{}})": "Change Position ({})",
        f"{KONTEKST_TRAY}|Wyczyść Wszystko ({{}})": "Clear All ({})",
        f"{KONTEKST_TRAY}|Ustawienia Wyglądu...": "Appearance Settings...",
        f"{KONTEKST_TRAY}|Język / Language": "Language",
        f"{KONTEKST_TRAY}|Polski": "Polish",
        f"{KONTEKST_TRAY}|English": "English",
        f"{KONTEKST_TRAY}|Wyjście ({{}})": "Exit ({})",
        f"{KONTEKST_TRAY}|Linie Pomocnicze": "Guide Lines",
        f"{KONTEKST_TRAY}|Utwórz poziomą ({{}})": "Create horizontal ({})",
        f"{KONTEKST_TRAY}|Utwórz pionową ({{}})": "Create vertical ({})",
        f"{KONTEKST_TRAY}|Wybierz linię ({{}})": "Select line ({})",
        f"{KONTEKST_SETTINGS}|Ustawienia Linii Pomocniczych": "Guide Lines Settings",
        f"{KONTEKST_SETTINGS}|Grubość:": "Thickness:",
        f"{KONTEKST_SETTINGS}| px": " px",
        f"{KONTEKST_SETTINGS}|Skróty: Zwiększ: {{}}, Zmniejsz: {{}}": "Shortcuts: Increase: {}, Decrease: {}",
        f"{KONTEKST_SETTINGS}|Kolor:": "Color:",
        f"{KONTEKST_SETTINGS}|Wybierz Kolor": "Select Color",
        f"{KONTEKST_SETTINGS}|Wybierz Kolor Linii": "Select Line Color",
        f"{KONTEKST_SETTINGS}|Przezroczystość:": "Transparency:",
        f"{KONTEKST_SETTINGS}|Zamknij": "Close",
        f"{KONTEKST_SETTINGS}|Grubość krawędzi do chwytania:": "Grab edge thickness of line:",
        f"{KONTEKST_SETTINGS}|Podpowiedź chwytania": "RDP: 20-30 px. Larger = easier to grab via remote desktop.",
        f"{KONTEKST_SETTINGS}|Grubość krawędzi ekranu:": "Screen edge thickness (rulers):",
        f"{KONTEKST_SETTINGS}|Podpowiedź krawędzi ekranu": "Width of the bar on sides and top where you drag new lines from. RDP: 24-32 px. Min 1 px.",
        f"{KONTEKST_GRIDLINE}|Y: {{pos}}px": "Y: {pos}px",
        f"{KONTEKST_GRIDLINE}|X: {{pos}}px": "X: {pos}px",
    }
}

def tlumacz(kontekst, tekst_zrodlowy):
    if instancja_aplikacji and hasattr(instancja_aplikacji, 'biezacy_jezyk'):
        biezacy_jezyk = instancja_aplikacji.biezacy_jezyk
    else:
        biezacy_jezyk = DOMYSLNY_JEZYK
    klucz = f"{kontekst}|{tekst_zrodlowy}"
    return SLOWNIK_TLUMACZEN.get(biezacy_jezyk, {}).get(klucz, tekst_zrodlowy)

def formatuj_skrot(skrot):
    # ctrl+alt+shift+h -> Ctrl+Alt+Shift+H
    return "+".join([p.capitalize() if p not in ("pageup","pagedown") else "PageUp" if p=="pageup" else "PageDown" for p in skrot.split("+")])

def numer_na_klawisz(nr):
    # 1..9 -> "1".."9", 10 -> "0"
    return "0" if nr == 10 else str(nr)

def klawisz_na_numer(klawisz):
    # "0" -> 10, "1".."9" -> 1..9, inne -> None
    if klawisz == "0":
        return 10
    if klawisz in "123456789":
        return int(klawisz)
    return None

def etykieta_linii(typ, nr):
    # typ 'h' -> H1, 'v' -> V1. X = pozioma, Y = pionowa (zgodnie ze specyfikacją)
    prefix = "H" if typ == 'h' else "V"
    return f"{prefix}{nr}"

# --- Sygnały (keyboard działa w innym wątku, więc wszystko przez sygnały do wątku Qt) ---
class EmiterSygnalow(QObject):
    zadanie_aktualizacji_zasobnika = pyqtSignal(bool)
    zadanie_przelaczenia_widocznosci = pyqtSignal()
    zadanie_wyczyszczenia_wszystkiego = pyqtSignal()
    zadanie_wyjscia_z_aplikacji = pyqtSignal()
    zadanie_zmiany_pozycji_linijek = pyqtSignal()
    zadanie_okna_ustawien = pyqtSignal()
    zadanie_zwiekszenia_grubosci = pyqtSignal()
    zadanie_zmniejszenia_grubosci = pyqtSignal()
    zadanie_zmiany_jezyka = pyqtSignal(str)
    zadanie_utworzenia_linii = pyqtSignal(str)
    zadanie_wyboru_linii = pyqtSignal(int, str)  # nr, typ 'h'/'v'
    zadanie_trybu_wyboru = pyqtSignal()
    zadanie_trybu_przesuwania = pyqtSignal()
    zadanie_przesuniecia_aktywnej = pyqtSignal(int, int)  # dx, dy
    zadanie_wyjscia_z_trybu = pyqtSignal()
    zadanie_usuniecia_aktywnej = pyqtSignal()

signal_emitter = EmiterSygnalow()


# --- Klasa bazowa dla okien nakładki ---
class OknoNakladki(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=None)
        self.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.hide()

# --- Mały pasek trybu (wybór / przesuwanie) - zawsze na wierzchu ---
class WskaznikTrybu(QLabel):
    def __init__(self):
        super().__init__(parent=None)
        self.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setWordWrap(True)
        self.setStyleSheet("background-color: rgba(0,0,0,230); color: white; padding: 10px 16px; border-radius: 8px; font-size: 14px; font-weight: bold;")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hide()
    def pokaz(self, tekst):
        ekran = QApplication.primaryScreen().geometry()
        max_szer = max(300, ekran.width() - 24)
        self.setMaximumWidth(max_szer)
        self.setMinimumWidth(320)
        self.setText(tekst)
        self.adjustSize()
        if self.width() > max_szer:
            self.setFixedWidth(max_szer)
            self.adjustSize()
        else:
            self.setMinimumWidth(0)
            self.setMaximumWidth(max_szer)
        x = ekran.center().x() - self.width() // 2
        x = max(ekran.left() + 4, min(x, ekran.right() - self.width() - 4))
        y = ekran.top() + 8
        self.move(x, y)
        self.show()
        self.raise_()

# --- Klasa dla linijek (v0.3: hitbox 24px, wizualnie kreska + podziałka) ---
class WidzetLinijki(OknoNakladki):
    sygnal_klikniecia = pyqtSignal(str, QPoint)
    def __init__(self, orientacja):
        super().__init__()
        self.orientacja = orientacja
        self.setObjectName("LinijkaPozioma" if orientacja == Qt.Orientation.Horizontal else "LinijkaPionowa")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setAutoFillBackground(True)
        paleta = self.palette()
        paleta.setColor(self.backgroundRole(), KOLOR_TLA_LINIJKI)
        self.setPalette(paleta)
        self.setMouseTracking(True)
        if self.orientacja == Qt.Orientation.Horizontal:
            self.setCursor(Qt.CursorShape.SplitVCursor)
            self.setFixedHeight(self._rozmiar_krawedzi())
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        else:
            self.setCursor(Qt.CursorShape.SplitHCursor)
            self.setFixedWidth(self._rozmiar_krawedzi())
            self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
    def _rozmiar_krawedzi(self):
        if instancja_aplikacji and hasattr(instancja_aplikacji, 'grubosc_krawedzi_ekranu'):
            return int(instancja_aplikacji.grubosc_krawedzi_ekranu)
        return ROZMIAR_LINIJKI
    def aktualizuj_rozmiar(self):
        if self.orientacja == Qt.Orientation.Horizontal:
            self.setFixedHeight(self._rozmiar_krawedzi())
        else:
            self.setFixedWidth(self._rozmiar_krawedzi())
        self.update()
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        prostokat = self.rect()
        pioro = QPen()
        pioro.setWidth(1)
        pioro.setColor(KOLOR_RAMKI)
        painter.setPen(pioro)
        if self.orientacja == Qt.Orientation.Horizontal:
            painter.drawLine(prostokat.bottomLeft(), prostokat.bottomRight())
        else:
            painter.drawLine(prostokat.topRight(), prostokat.bottomRight())
        odstep = 5
        if self.orientacja == Qt.Orientation.Horizontal:
            dlugosc = prostokat.width()
            start_abs_x = self.mapToGlobal(QPoint(0,0)).x()
            for x_abs in range(start_abs_x, start_abs_x + dlugosc + odstep, odstep):
                x_rel = x_abs - start_abs_x
                if x_rel < 0 or x_rel > dlugosc:
                    continue
                if x_abs % 50 == 0:
                    pioro.setColor(KOLOR_ZNACZNIKA_GLOWNEGO); wys = 12
                elif x_abs % 10 == 0:
                    pioro.setColor(KOLOR_ZNACZNIKA_SREDNIEGO); wys = 8
                else:
                    pioro.setColor(KOLOR_ZNACZNIKA_POMNIEJSZEGO); wys = 5
                painter.setPen(pioro)
                painter.drawLine(x_rel, prostokat.height() - wys, x_rel, prostokat.height()-1)
        else:
            dlugosc = prostokat.height()
            start_abs_y = self.mapToGlobal(QPoint(0,0)).y()
            for y_abs in range(start_abs_y, start_abs_y + dlugosc + odstep, odstep):
                y_rel = y_abs - start_abs_y
                if y_rel < 0 or y_rel > dlugosc:
                    continue
                if y_abs % 50 == 0:
                    pioro.setColor(KOLOR_ZNACZNIKA_GLOWNEGO); szer = 12
                elif y_abs % 10 == 0:
                    pioro.setColor(KOLOR_ZNACZNIKA_SREDNIEGO); szer = 8
                else:
                    pioro.setColor(KOLOR_ZNACZNIKA_POMNIEJSZEGO); szer = 5
                painter.setPen(pioro)
                painter.drawLine(prostokat.width() - szer, y_rel, prostokat.width()-1, y_rel)
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pozycja_globalna = event.globalPosition().toPoint()
            typ_linii = 'h' if self.orientacja == Qt.Orientation.Horizontal else 'v'
            if instancja_aplikacji:
                instancja_aplikacji.obsluz_klikniecie_linijki(typ_linii, pozycja_globalna)
            event.accept()
        else:
            event.ignore()

# --- Klasa dla pojedynczej linii siatki (v0.3: RDP polling, numer, aktywność) ---
class WidzetLiniiSiatki(OknoNakladki):
    def __init__(self, typ_orientacji, pozycja, id_siatki, numer=1):
        super().__init__()
        self.typ = typ_orientacji  # 'h' = pozioma (X), 'v' = pionowa (Y)
        self._pozycja = pozycja
        self.id = id_siatki
        self.numer = numer  # 1..10, 0 na klawiaturze = 10
        self.czy_przeciagane = False
        self.czy_aktywna = False
        self.przesuniecie_przeciagania = QPoint(0,0)
        self.podpowiedz = None
        self.setMouseTracking(True)
        # Timer RDP: zamiast polegać na mouseMoveEvent (gubionym przez Chrome Remote Desktop),
        # odpytujemy pozycję kursora z systemu co 16 ms, gdy trwa przeciąganie.
        self.timer_przeciagania = QTimer(self)
        self.timer_przeciagania.setInterval(16)
        self.timer_przeciagania.timeout.connect(self._polling_przeciagania)
        if self.typ == 'h':
            self.setCursor(Qt.CursorShape.SizeVerCursor)
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        else:
            self.setCursor(Qt.CursorShape.SizeHorCursor)
            self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        # Opis jako osobny QLabel, nie malowany w wąskim widżecie, żeby nie był ucinany
        self.etykieta_widget = QLabel(parent=None)
        self.etykieta_widget.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.etykieta_widget.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.etykieta_widget.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.etykieta_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._aktualizuj_geometrie()
        self._aktualizuj_etykiete()
    def _grubosc_chwytu(self):
        if instancja_aplikacji:
            return max(MIN_GRUBOSC_CHWYTU, min(MAX_GRUBOSC_CHWYTU, int(instancja_aplikacji.grubosc_chwytu)))
        return DOMYSLNA_GRUBOSC_CHWYTU
    def _rozmiar_krawedzi(self):
        if instancja_aplikacji and hasattr(instancja_aplikacji, 'grubosc_krawedzi_ekranu'):
            return int(instancja_aplikacji.grubosc_krawedzi_ekranu)
        return ROZMIAR_LINIJKI
    def _aktualizuj_geometrie(self):
        if not instancja_aplikacji:
            return
        chwyt = self._grubosc_chwytu()
        kraw = self._rozmiar_krawedzi()
        prostokat_ekranu = QApplication.primaryScreen().geometry()
        pozycja_linijek = instancja_aplikacji.pozycja_linijek
        widok_x = kraw if 'left' in pozycja_linijek else 0
        widok_y = kraw if 'top' in pozycja_linijek else 0
        szerokosc_widoku = prostokat_ekranu.width() - (kraw if 'left' in pozycja_linijek else 0) - (kraw if 'right' in pozycja_linijek else 0)
        wysokosc_widoku = prostokat_ekranu.height() - (kraw if 'top' in pozycja_linijek else 0) - (kraw if 'bottom' in pozycja_linijek else 0)
        szerokosc_widoku = max(0, szerokosc_widoku)
        wysokosc_widoku = max(0, wysokosc_widoku)
        if self.typ == 'h':
            self.setFixedHeight(chwyt)
            widzet_y = self._pozycja - chwyt // 2
            self.setGeometry(widok_x, widzet_y, szerokosc_widoku, chwyt)
        else:
            self.setFixedWidth(chwyt)
            widzet_x = self._pozycja - chwyt // 2
            self.setGeometry(widzet_x, widok_y, chwyt, wysokosc_widoku)
        try:
            self._aktualizuj_etykiete()
        except Exception:
            pass
    def pobierz_pozycje(self):
        return self._pozycja
    def ustaw_pozycje(self, poz):
        if self._pozycja != poz:
            self._pozycja = poz
            self._aktualizuj_geometrie()
            self.update()
    def pobierz_wyswietlana_pozycje(self):
        return self._pozycja
    def ustaw_aktywna(self, aktywna):
        self.czy_aktywna = aktywna
        self.update()
        try:
            self._aktualizuj_etykiete()
        except Exception:
            pass
    def _aktualizuj_etykiete(self):
        if not hasattr(self, 'etykieta_widget') or self.etykieta_widget is None:
            return
        tekst = ("NOWA" if self.numer == 0 else etykieta_linii(self.typ, self.numer))
        self.etykieta_widget.setText(tekst)
        # Aktywna NIE zmienia grubości, tylko tło opisu z żółtego na czerwone, czcionka biała
        if self.czy_aktywna:
            self.etykieta_widget.setStyleSheet("background-color: rgba(220,0,0,235); color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; border: 1px solid rgba(120,0,0,255);")
        else:
            self.etykieta_widget.setStyleSheet("background-color: rgba(255,255,190,235); color: black; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; border: 1px solid rgba(180,180,0,255);")
        self.etykieta_widget.adjustSize()
        ekran = QApplication.primaryScreen().geometry()
        kraw = self._rozmiar_krawedzi()
        w = self.etykieta_widget.width()
        h = self.etykieta_widget.height()
        if self.typ == 'h':
            x = ekran.left() + kraw + 6
            y = self._pozycja - h - 4
            if y < ekran.top() + 2:
                y = self._pozycja + 6
            if y + h > ekran.bottom() - 2:
                y = ekran.bottom() - h - 2
        else:
            y = ekran.top() + kraw + 6
            x = self._pozycja + 6
            if x + w > ekran.right() - 2:
                x = self._pozycja - w - 6
            if x < ekran.left() + 2:
                x = ekran.left() + 2
        self.etykieta_widget.move(int(x), int(y))
        if self.isVisible():
            self.etykieta_widget.show()
            self.etykieta_widget.raise_()
        else:
            self.etykieta_widget.hide()
    def zniszcz_etykiete(self):
        if hasattr(self, 'etykieta_widget') and self.etykieta_widget is not None:
            try:
                self.etykieta_widget.hide()
                self.etykieta_widget.deleteLater()
            except Exception:
                pass
            self.etykieta_widget = None
    def showEvent(self, event):
        super().showEvent(event)
        try:
            if hasattr(self, 'etykieta_widget') and self.etykieta_widget is not None:
                self._aktualizuj_etykiete()
        except Exception:
            pass
    def hideEvent(self, event):
        super().hideEvent(event)
        try:
            if hasattr(self, 'etykieta_widget') and self.etykieta_widget is not None:
                self.etykieta_widget.hide()
        except Exception:
            pass
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        if not instancja_aplikacji:
            return
        kolor = instancja_aplikacji.kolor_linii_siatki
        grubosc = instancja_aplikacji.grubosc_linii_siatki
        prostokat = self.rect()
        # Aktywna NIE zmienia grubości, tylko tło opisu (osobny QLabel)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(kolor, Qt.BrushStyle.SolidPattern))
        if self.typ == 'h':
            srodek_y = prostokat.height() // 2
            rysowany_y = srodek_y - math.ceil(grubosc / 2.0)
            painter.drawRect(0, int(rysowany_y), prostokat.width(), int(grubosc))
        else:
            srodek_x = prostokat.width() // 2
            rysowany_x = srodek_x - math.ceil(grubosc / 2.0)
            painter.drawRect(int(rysowany_x), 0, int(grubosc), prostokat.height())
        # Etykieta H1/V1 jest teraz osobnym QLabel, nie malowana tu, żeby nie była ucinana.
    def mousePressEvent(self, event):
        if not instancja_aplikacji:
            return
        if event.button() == Qt.MouseButton.LeftButton:
            # v0.3 FIX: odrzuć klik, jeśli jest dalej niż połowa uchwytu od środka linii.
            # Wcześniej uchwyt 3840px przejmował kliknięcia z całego ekranu.
            chwyt = self._grubosc_chwytu()
            pos_lokalna = event.position().toPoint()
            if self.typ == 'h':
                odleglosc = abs(pos_lokalna.y() - self.rect().height() // 2)
            else:
                odleglosc = abs(pos_lokalna.x() - self.rect().width() // 2)
            if odleglosc > chwyt // 2 + 2:
                event.ignore()
                return
            self.czy_przeciagane = True
            self.przesuniecie_przeciagania = pos_lokalna
            # v0.3: BRAK grabMouse() - łamało drag przez RDP. Zamiast tego polling.
            if instancja_aplikacji:
                instancja_aplikacji.ustaw_aktywna_linie(self.id, pokaz_wskaznik=False)
            self.stworz_podpowiedz()
            self.aktualizuj_podpowiedz(event.globalPosition().toPoint())
            self.timer_przeciagania.start()
            event.accept()
        else:
            event.ignore()
    def _polling_przeciagania(self):
        # RDP: czytamy pozycję z systemu, a nie czekamy na mouseMoveEvent.
        # Działa też, gdy Chrome Remote Desktop gubi pośrednie ruchy.
        if not self.czy_przeciagane or not instancja_aplikacji:
            self.timer_przeciagania.stop()
            return
        # Jeśli przycisk już puszczony (RDP zgubiło MouseRelease), zakończ przeciąganie.
        przyciski = QApplication.mouseButtons()
        if not (przyciski & Qt.MouseButton.LeftButton):
            self._zakoncz_przeciaganie()
            return
        biezaca_poz_globalna = QCursor.pos()
        self._przesun_do(biezaca_poz_globalna)
    def _przesun_do(self, biezaca_poz_globalna):
        prostokat_ekranu = QApplication.primaryScreen().geometry()
        kraw = self._rozmiar_krawedzi()
        min_poz_x = kraw if 'left' in instancja_aplikacji.pozycja_linijek else 0
        min_poz_y = kraw if 'top' in instancja_aplikacji.pozycja_linijek else 0
        maks_poz_x = prostokat_ekranu.width() - (kraw if 'right' in instancja_aplikacji.pozycja_linijek else 0)
        maks_poz_y = prostokat_ekranu.height() - (kraw if 'bottom' in instancja_aplikacji.pozycja_linijek else 0)
        chwyt = self._grubosc_chwytu()
        if self.typ == 'h':
            nowy_widzet_y = biezaca_poz_globalna.y() - self.przesuniecie_przeciagania.y()
            nowa_poz_abs = nowy_widzet_y + chwyt // 2
            nowa_poz_abs = max(min_poz_y, min(nowa_poz_abs, maks_poz_y))
        else:
            nowy_widzet_x = biezaca_poz_globalna.x() - self.przesuniecie_przeciagania.x()
            nowa_poz_abs = nowy_widzet_x + chwyt // 2
            nowa_poz_abs = max(min_poz_x, min(nowa_poz_abs, maks_poz_x))
        self.ustaw_pozycje(nowa_poz_abs)
        self.aktualizuj_podpowiedz(biezaca_poz_globalna)
    def mouseMoveEvent(self, event):
        # Zostawione dla lokalnego użycia, ale polling i tak to obsłuży przez RDP.
        if not instancja_aplikacji:
            return
        if self.czy_przeciagane:
            self._przesun_do(event.globalPosition().toPoint())
            event.accept()
        else:
            event.ignore()
    def _zakoncz_przeciaganie(self):
        if not self.czy_przeciagane:
            return
        self.czy_przeciagane = False
        self.timer_przeciagania.stop()
        self.zniszcz_podpowiedz()
        if instancja_aplikacji:
            instancja_aplikacji.aktualizuj_pozycje_linii_siatki(self.id, self._pozycja)
    def mouseReleaseEvent(self, event):
        if not instancja_aplikacji:
            return
        if event.button() == Qt.MouseButton.LeftButton and self.czy_przeciagane:
            self._zakoncz_przeciaganie()
            event.accept()
        else:
            event.ignore()
    def mouseDoubleClickEvent(self, event):
        if not instancja_aplikacji:
            return
        if event.button() == Qt.MouseButton.LeftButton:
            # Podwójny klik = usuń linię (jak w v0.2), zwolnij też numer
            instancja_aplikacji.usun_widzet_linii_siatki(self)
            event.accept()
        else:
            event.ignore()
    def enterEvent(self, event):
        pass
    def leaveEvent(self, event):
        if not self.czy_przeciagane:
            self.zniszcz_podpowiedz()
    def stworz_podpowiedz(self):
        if self.podpowiedz is None:
            self.podpowiedz = QLabel(parent=None)
            self.podpowiedz.setWindowFlags(Qt.WindowType.SplashScreen | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
            self.podpowiedz.setStyleSheet(f"background-color: rgba({KOLOR_TLA_PODPOWIEDZI.red()},{KOLOR_TLA_PODPOWIEDZI.green()},{KOLOR_TLA_PODPOWIEDZI.blue()},{KOLOR_TLA_PODPOWIEDZI.alphaF()}); color: rgb({KOLOR_TEKSTU_PODPOWIEDZI.red()},{KOLOR_TEKSTU_PODPOWIEDZI.green()},{KOLOR_TEKSTU_PODPOWIEDZI.blue()}); padding: 6px 10px; border-radius: 4px; font-size: 14px;")
            self.podpowiedz.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
            self.podpowiedz.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
    def aktualizuj_podpowiedz(self, pozycja_globalna_myszy):
        if not self.podpowiedz or not self.czy_przeciagane:
            self.zniszcz_podpowiedz()
            return
        prostokat_ekranu = QApplication.primaryScreen().geometry()
        wyswietlana_pozycja = self.pobierz_wyswietlana_pozycje()
        # Pokaż też numer linii, np. H2 - Y: 320px
        etykieta = etykieta_linii(self.typ, self.numer)
        tekst_zrodlowy = "Y: {pos}px" if self.typ == 'h' else "X: {pos}px"
        tekst = f"{etykieta} - " + tlumacz(KONTEKST_GRIDLINE, tekst_zrodlowy).format(pos=wyswietlana_pozycja)
        self.podpowiedz.setText(tekst)
        self.podpowiedz.adjustSize()
        podpowiedz_x = pozycja_globalna_myszy.x() + 15
        podpowiedz_y = pozycja_globalna_myszy.y() + 15
        if podpowiedz_x + self.podpowiedz.width() > prostokat_ekranu.right():
            podpowiedz_x = pozycja_globalna_myszy.x() - self.podpowiedz.width() - 15
        if podpowiedz_y + self.podpowiedz.height() > prostokat_ekranu.bottom():
            podpowiedz_y = pozycja_globalna_myszy.y() - self.podpowiedz.height() - 15
        if podpowiedz_x < prostokat_ekranu.left():
            podpowiedz_x = prostokat_ekranu.left() + 5
        if podpowiedz_y < prostokat_ekranu.top():
            podpowiedz_y = prostokat_ekranu.top() + 5
        self.podpowiedz.move(podpowiedz_x, podpowiedz_y)
        if not self.podpowiedz.isVisible():
            self.podpowiedz.show()
    def zniszcz_podpowiedz(self):
        if self.podpowiedz:
            self.podpowiedz.hide()
            self.podpowiedz.deleteLater()
            self.podpowiedz = None

# --- Narożnik ---
class Naroznik(OknoNakladki):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), KOLOR_TLA_LINIJKI)
        self.setPalette(p)
        rozmiar = int(instancja_aplikacji.grubosc_krawedzi_ekranu) if instancja_aplikacji and hasattr(instancja_aplikacji, 'grubosc_krawedzi_ekranu') else ROZMIAR_LINIJKI
        self.setFixedSize(rozmiar, rozmiar)
        # FIX crash: ramka jako self, nie zmienna lokalna
        self.ramka_naroznika = QLabel(self)
        self.ramka_naroznika.setStyleSheet(f"QLabel {{ border-right: 1px solid {KOLOR_RAMKI.name()}; border-bottom: 1px solid {KOLOR_RAMKI.name()}; }}")
        self.ramka_naroznika.setGeometry(0, 0, rozmiar, rozmiar)
        self.ramka_naroznika.lower()
    def aktualizuj_rozmiar(self):
        rozmiar = int(instancja_aplikacji.grubosc_krawedzi_ekranu) if instancja_aplikacji and hasattr(instancja_aplikacji, 'grubosc_krawedzi_ekranu') else ROZMIAR_LINIJKI
        self.setFixedSize(rozmiar, rozmiar)
        if hasattr(self, 'ramka_naroznika') and self.ramka_naroznika is not None:
            self.ramka_naroznika.setGeometry(0, 0, rozmiar, rozmiar)
            self.ramka_naroznika.lower()
        self.update()


# --- Dialog ustawień v0.3 ---
class DialogUstawien(QDialog):
    def __init__(self, app_ref, parent=None):
        super().__init__(parent)
        self.aplikacja = app_ref
        # Większe okno i większe czcionki, bo mało czytelne
        self.setMinimumSize(700, 700)
        self.resize(740, 880)
        self.setStyleSheet("QDialog { font-size: 14px; } QLabel { font-size: 14px; } QSpinBox { font-size: 15px; min-height: 32px; min-width: 90px; } QLineEdit { font-size: 14px; min-height: 32px; } QPushButton { font-size: 14px; min-height: 36px; padding: 6px 14px; } QSlider { min-height: 30px; }")
        self.wybrany_kolor_bazowy = QColor(DOMYSLNY_KOLOR_SIATKI)
        self.pole_grubosci = QSpinBox()
        self.pole_grubosci.setRange(1, MAKS_GRUBOSC_SIATKI)
        self.pole_grubosci.setKeyboardTracking(False)
        self.etykieta_skrotow_grubosci = QLabel()
        self.etykieta_skrotow_grubosci.setStyleSheet("font-size: 12px; color: gray;")
        self.przycisk_koloru = QPushButton()
        self.podglad_koloru = QLabel()
        self.podglad_koloru.setFixedSize(36, 36)
        self.podglad_koloru.setStyleSheet("border: 1px solid grey; background-color: transparent;")
        uklad_koloru = QHBoxLayout()
        uklad_koloru.addWidget(self.przycisk_koloru)
        uklad_koloru.addWidget(self.podglad_koloru)
        uklad_koloru.addStretch()
        self.suwak_przezroczystosci = QSlider(Qt.Orientation.Horizontal)
        self.suwak_przezroczystosci.setRange(0, 255)
        self.etykieta_przezroczystosci = QLabel()
        self.przycisk_zamknij = QPushButton()
        self.label_grubosc = QLabel()
        self.label_kolor = QLabel()
        self.label_przezroczystosc = QLabel()
        # v0.3: grubość krawędzi do chwytania 1-50px
        self.label_chwyt = QLabel()
        self.pole_chwytu = QSpinBox()
        self.pole_chwytu.setRange(MIN_GRUBOSC_CHWYTU, MAX_GRUBOSC_CHWYTU)
        self.pole_chwytu.setKeyboardTracking(False)
        self.etykieta_podpowiedz_chwytu = QLabel()
        self.etykieta_podpowiedz_chwytu.setStyleSheet("font-size: 12px; color: gray;")
        self.etykieta_podpowiedz_chwytu.setWordWrap(True)
        # NOWE: grubość krawędzi ekranu (linijki), min 1px
        self.label_krawedz = QLabel()
        self.pole_krawedzi = QSpinBox()
        self.pole_krawedzi.setRange(MIN_GRUBOSC_KRAWEDZI_EKRANU, MAX_GRUBOSC_KRAWEDZI_EKRANU)
        self.pole_krawedzi.setKeyboardTracking(False)
        self.etykieta_podpowiedz_krawedzi = QLabel()
        self.etykieta_podpowiedz_krawedzi.setStyleSheet("font-size: 12px; color: gray;")
        self.etykieta_podpowiedz_krawedzi.setWordWrap(True)
        self.etykieta_wersja = QLabel(f"Linie Pomocnicze v{WERSJA}  |  RDP: polling, bez grabMouse()")
        self.etykieta_wersja.setStyleSheet("font-size: 12px; color: gray;")
        self.etykieta_skroty = QLabel()
        self.etykieta_skroty.setStyleSheet("font-size: 12px; color: #333;")
        self.etykieta_skroty.setWordWrap(True)
        # --- Edytowalne skróty ---
        self.label_skroty_naglowek = QLabel()
        self.label_skroty_naglowek.setStyleSheet("font-size: 15px; font-weight: bold; margin-top: 12px;")
        self.label_skroty_naglowek.setWordWrap(True)
        self.etykieta_skroty_podpowiedz = QLabel()
        self.etykieta_skroty_podpowiedz.setStyleSheet("font-size: 12px; color: gray;")
        self.etykieta_skroty_podpowiedz.setWordWrap(True)
        self.pola_skrotow = {}
        self.etykiety_skrotow = {}
        self.uklad_skrotow = QFormLayout()
        for _klucz in DOMYSLNE_SKROTY.keys():
            _pole = QLineEdit()
            _pole.setPlaceholderText("np. Ctrl+Alt+Shift+H")
            self.pola_skrotow[_klucz] = _pole
            _lbl = QLabel(NAZWY_SKROTOW_PL.get(_klucz, _klucz))
            self.etykiety_skrotow[_klucz] = _lbl
            self.uklad_skrotow.addRow(_lbl, _pole)
        self.etykieta_bledow_skrotow = QLabel()
        self.etykieta_bledow_skrotow.setStyleSheet("font-size: 12px; color: red;")
        self.etykieta_bledow_skrotow.setWordWrap(True)
        self.przycisk_zastosuj_skroty = QPushButton()
        self.przycisk_reset_skrotow = QPushButton()
        uklad_skroty_przyciski = QHBoxLayout()
        uklad_skroty_przyciski.addWidget(self.przycisk_zastosuj_skroty)
        uklad_skroty_przyciski.addWidget(self.przycisk_reset_skrotow)
        uklad_skroty_przyciski.addStretch()
        uklad_formularza = QFormLayout()
        uklad_formularza.addRow(self.label_grubosc, self.pole_grubosci)
        uklad_formularza.addRow("", self.etykieta_skrotow_grubosci)
        uklad_formularza.addRow(self.label_kolor, uklad_koloru)
        uklad_formularza.addRow(self.label_przezroczystosc, self.suwak_przezroczystosci)
        uklad_formularza.addRow("", self.etykieta_przezroczystosci)
        uklad_formularza.addRow(self.label_chwyt, self.pole_chwytu)
        uklad_formularza.addRow("", self.etykieta_podpowiedz_chwytu)
        uklad_formularza.addRow(self.label_krawedz, self.pole_krawedzi)
        uklad_formularza.addRow("", self.etykieta_podpowiedz_krawedzi)
        uklad_przyciskow = QHBoxLayout()
        uklad_przyciskow.addStretch()
        uklad_przyciskow.addWidget(self.przycisk_zamknij)
        uklad_glowny = QVBoxLayout(self)
        uklad_glowny.addLayout(uklad_formularza)
        uklad_glowny.addLayout(uklad_przyciskow)
        uklad_glowny.addWidget(self.etykieta_skroty)
        uklad_glowny.addWidget(self.label_skroty_naglowek)
        uklad_glowny.addWidget(self.etykieta_skroty_podpowiedz)
        uklad_glowny.addLayout(self.uklad_skrotow)
        uklad_glowny.addWidget(self.etykieta_bledow_skrotow)
        uklad_glowny.addLayout(uklad_skroty_przyciski)
        uklad_glowny.addWidget(self.etykieta_wersja)
        self.pole_grubosci.valueChanged.connect(self.zmieniono_grubosc)
        self.przycisk_koloru.clicked.connect(self.wybierz_kolor)
        self.suwak_przezroczystosci.valueChanged.connect(self.zmieniono_przezroczystosc)
        self.przycisk_zamknij.clicked.connect(self.accept)
        self.pole_chwytu.valueChanged.connect(self.zmieniono_chwyt)
        self.pole_krawedzi.valueChanged.connect(self.zmieniono_krawedz)
        self.przycisk_zastosuj_skroty.clicked.connect(self.zastosuj_skroty_z_pol)
        self.przycisk_reset_skrotow.clicked.connect(self.resetuj_skroty_z_pol)
        self.retranslateUi()
    def retranslateUi(self):
        self.setWindowTitle(f"{tlumacz(KONTEKST_SETTINGS, 'Ustawienia Linii Pomocniczych')} - v{WERSJA}")
        _base_mod = "+".join(pobierz_skrot('utworz_pozioma').split("+")[:-1]) if "+" in pobierz_skrot('utworz_pozioma') else "ctrl+alt+shift"
        self.label_grubosc.setText(tlumacz(KONTEKST_SETTINGS, "Grubość:"))
        self.etykieta_skrotow_grubosci.setText(tlumacz(KONTEKST_SETTINGS, "Skróty: Zwiększ: {}, Zmniejsz: {}").format(formatuj_skrot(pobierz_skrot('zwieksz_grubosc')), formatuj_skrot(pobierz_skrot('zmniejsz_grubosc'))))
        self.label_kolor.setText(tlumacz(KONTEKST_SETTINGS, "Kolor:"))
        self.przycisk_koloru.setText(tlumacz(KONTEKST_SETTINGS, "Wybierz Kolor"))
        self.label_przezroczystosc.setText(tlumacz(KONTEKST_SETTINGS, "Przezroczystość:"))
        self.przycisk_zamknij.setText(tlumacz(KONTEKST_SETTINGS, "Zamknij"))
        self.label_chwyt.setText(tlumacz(KONTEKST_SETTINGS, "Grubość krawędzi do chwytania:"))
        self.etykieta_podpowiedz_chwytu.setText(tlumacz(KONTEKST_SETTINGS, "Podpowiedź chwytania"))
        self.label_krawedz.setText(tlumacz(KONTEKST_SETTINGS, "Grubość krawędzi ekranu:"))
        self.etykieta_podpowiedz_krawedzi.setText(tlumacz(KONTEKST_SETTINGS, "Podpowiedź krawędzi ekranu"))
        # Skróty v0.3 - pokazane w ustawieniach, żeby nie trzeba było pamiętać
        if self.aplikacja and getattr(self.aplikacja, 'biezacy_jezyk', 'pl') == 'en':
            self.etykieta_skroty.setText(
                f"Shortcuts (editable below, no Win key by default):\n"
                f"Create H: {formatuj_skrot(pobierz_skrot('utworz_pozioma'))}  |  Create V: {formatuj_skrot(pobierz_skrot('utworz_pionowa'))}\n"
                f"Select directly: {formatuj_skrot(_base_mod)}+1+X ... +0+Y (X=horizontal, Y=vertical, 0=10) - follows Create H modifiers\n"
                f"Move mode: {formatuj_skrot(pobierz_skrot('tryb_przesuwania'))}  |  Arrows = 10px (fast), Shift+Arrow = 1px (slow), Esc = exit  |  Shift+Del = delete active (always)"
            )
        else:
            self.etykieta_skroty.setText(
                f"Skróty (edytowalne poniżej, bez Win, bez polskich liter C/L/O = bez Ć/Ł/Ó):\n"
                f"Utwórz poziomą: {formatuj_skrot(pobierz_skrot('utworz_pozioma'))}  |  Utwórz pionową: {formatuj_skrot(pobierz_skrot('utworz_pionowa'))}\n"
                f"Wybór bezpośrednio: {formatuj_skrot(_base_mod)}+1+X ... +0+Y (X=pozioma, Y=pionowa, 0=10) - bierze modyfikatory z Utwórz poziomą\n"
                f"Tryb przesuwania: {formatuj_skrot(pobierz_skrot('tryb_przesuwania'))}  |  Strzałki = 10px (szybko), Shift+Strzałka = 1px (wolno), Esc = wyjście  |  Shift+Del = usuń aktywną (zawsze)"
            )
        if getattr(self.aplikacja, 'biezacy_jezyk', 'pl') == 'en':
            self.label_skroty_naglowek.setText("Shortcuts - edit and click Apply Shortcuts:")
            self.etykieta_skroty_podpowiedz.setText("Format: Ctrl+Alt+Shift+H, Shift+Del, Ctrl+Alt+Shift+PageUp. No duplicates. Direct select uses Create H modifiers + digit + X/Y.")
            self.przycisk_zastosuj_skroty.setText("Apply Shortcuts")
            self.przycisk_reset_skrotow.setText("Reset to Defaults")
        else:
            self.label_skroty_naglowek.setText("Skróty - edytuj i kliknij Zastosuj skróty:")
            self.etykieta_skroty_podpowiedz.setText("Format: Ctrl+Alt+Shift+H, Shift+Del, Ctrl+Alt+Shift+PageUp. Bez duplikatów. Wybór bezpośredni bierze modyfikatory z Utwórz poziomą + cyfra + X/Y.")
            self.przycisk_zastosuj_skroty.setText("Zastosuj skróty")
            self.przycisk_reset_skrotow.setText("Przywróć domyślne")
        # FIX: nazwy poszczególnych skrótów też się tłumaczą (ze screenshota: nagłówek był PL, a lista EN)
        _jezyk_skrotow = getattr(self.aplikacja, 'biezacy_jezyk', 'pl') if self.aplikacja else 'pl'
        _nazwy_skrotow = NAZWY_SKROTOW_EN if _jezyk_skrotow == 'en' else NAZWY_SKROTOW_PL
        for _k, _lbl in getattr(self, 'etykiety_skrotow', {}).items():
            _lbl.setText(_nazwy_skrotow.get(_k, _k))
        for _k, _pole in getattr(self, 'pola_skrotow', {}).items():
            _pole.setPlaceholderText("e.g. Ctrl+Alt+Shift+H" if _jezyk_skrotow == 'en' else "np. Ctrl+Alt+Shift+H")
        self.etykieta_wersja.setText(f"Linie Pomocnicze v{WERSJA}  |  RDP: polling, bez grabMouse()")
    def wczytaj_poczatkowe_ustawienia(self):
        app = self.aplikacja
        if not app:
            return
        self.pole_grubosci.blockSignals(True)
        self.pole_grubosci.setValue(app.grubosc_linii_siatki)
        self.pole_grubosci.blockSignals(False)
        self.wybrany_kolor_bazowy = QColor(app.kolor_linii_siatki)
        self.wybrany_kolor_bazowy.setAlpha(255)
        self.aktualizuj_podglad_koloru()
        self.suwak_przezroczystosci.blockSignals(True)
        self.suwak_przezroczystosci.setValue(app.kolor_linii_siatki.alpha())
        self.suwak_przezroczystosci.blockSignals(False)
        self.aktualizuj_etykiete_przezroczystosci()
        self.pole_chwytu.blockSignals(True)
        self.pole_chwytu.setValue(int(app.grubosc_chwytu))
        self.pole_chwytu.blockSignals(False)
        self.pole_krawedzi.blockSignals(True)
        self.pole_krawedzi.setValue(int(getattr(app, 'grubosc_krawedzi_ekranu', DOMYSLNA_GRUBOSC_KRAWEDZI_EKRANU)))
        self.pole_krawedzi.blockSignals(False)
        self.wczytaj_skroty_do_pol()
    def aktualizuj_podglad_koloru(self):
        kolor = QColor(self.wybrany_kolor_bazowy)
        if self.aplikacja:
            kolor.setAlpha(self.aplikacja.kolor_linii_siatki.alpha())
        self.podglad_koloru.setStyleSheet(f"border: 1px solid grey; background-color: rgba({kolor.red()},{kolor.green()},{kolor.blue()},{kolor.alpha()});")
    def aktualizuj_etykiete_przezroczystosci(self):
        self.etykieta_przezroczystosci.setText(f"{self.suwak_przezroczystosci.value()} / 255")
    def zmieniono_grubosc(self, wartosc):
        if self.aplikacja:
            self.aplikacja.zmien_grubosc(wartosc)
    def zmieniono_chwyt(self, wartosc):
        if self.aplikacja:
            self.aplikacja.zmien_grubosc_chwytu(wartosc)
    def zmieniono_krawedz(self, wartosc):
        if self.aplikacja:
            self.aplikacja.zmien_grubosc_krawedzi_ekranu(wartosc)
    def wczytaj_skroty_do_pol(self):
        app = self.aplikacja
        if not app or not hasattr(app, 'skroty'):
            return
        for _k, _pole in self.pola_skrotow.items():
            _pole.blockSignals(True)
            _pole.setText(formatuj_skrot(app.skroty.get(_k, DOMYSLNE_SKROTY.get(_k, ""))))
            _pole.blockSignals(False)
    def zastosuj_skroty_z_pol(self):
        if not self.aplikacja:
            return
        nowe={}
        for _k, _pole in self.pola_skrotow.items():
            nowe[_k]=normalizuj_skrot(_pole.text())
        bledy=sprawdz_skroty(nowe)
        ostrzezenia=[]
        for _k,_v in nowe.items():
            _low=_v.lower()
            if "win" in _low or "windows" in _low:
                ostrzezenia.append(f"{_k}: używa Win")
            if "ctrl+alt" in _low or "alt+ctrl" in _low:
                _last=_low.split("+")[-1]
                if _last in ("c","l","o"):
                    ostrzezenia.append(f"{_k}: Ctrl+Alt+{_last.upper()} = polskie Ć/Ł/Ó przez AltGr")
        if bledy:
            self.etykieta_bledow_skrotow.setText("Błędy: " + "; ".join(bledy))
            return
        bledy2=self.aplikacja.zmien_skroty(nowe)
        if bledy2:
            self.etykieta_bledow_skrotow.setText("Błędy: " + "; ".join(bledy2))
            return
        msg="Skróty zastosowane."
        if ostrzezenia:
            msg+=" Ostrzeżenia: " + "; ".join(ostrzezenia)
        self.etykieta_bledow_skrotow.setStyleSheet("font-size: 12px; color: green;")
        self.etykieta_bledow_skrotow.setText(msg)
        self.retranslateUi()
        self.wczytaj_skroty_do_pol()
    def resetuj_skroty_z_pol(self):
        if not self.aplikacja:
            return
        bledy=self.aplikacja.resetuj_skroty_do_domyslnych()
        if bledy:
            self.etykieta_bledow_skrotow.setText("Błędy: " + "; ".join(bledy))
            return
        self.etykieta_bledow_skrotow.setStyleSheet("font-size: 12px; color: green;")
        self.etykieta_bledow_skrotow.setText("Skróty przywrócone do domyślnych.")
        self.retranslateUi()
        self.wczytaj_skroty_do_pol()
    def wybierz_kolor(self):
        kolor_pocz = QColor(self.wybrany_kolor_bazowy)
        kolor = QColorDialog.getColor(kolor_pocz, self, tlumacz(KONTEKST_SETTINGS, "Wybierz Kolor Linii"))
        if kolor.isValid():
            self.wybrany_kolor_bazowy = QColor(kolor)
            self.wybrany_kolor_bazowy.setAlpha(255)
            if self.aplikacja:
                nowy = QColor(kolor)
                nowy.setAlpha(self.aplikacja.kolor_linii_siatki.alpha())
                self.aplikacja.zmien_kolor(nowy)
            self.aktualizuj_podglad_koloru()
    def zmieniono_przezroczystosc(self, wartosc):
        self.aktualizuj_etykiete_przezroczystosci()
        if self.aplikacja:
            self.aplikacja.zmien_przezroczystosc(wartosc)
        self.aktualizuj_podglad_koloru()


# --- Główna aplikacja ---
class AplikacjaLiniiPomocniczych(QObject):
    def __init__(self):
        super().__init__()
        self.qt_app = QApplication.instance()
        if not self.qt_app:
            self.qt_app = QApplication(sys.argv)
        self.qt_app.setQuitOnLastWindowClosed(False)
        global id_glownego_watku
        id_glownego_watku = threading.current_thread().ident
        self.linijki_widoczne = False
        self.dane_linii_siatki = []  # {'type':'h'/'v','pos':int,'id':int,'nr':1..10}
        self.nastepny_id_siatki = 0
        self.okna_nakladki = {"top": None, "left": None, "corner": None}
        self.aktywne_linie_siatki = {}
        self.przeciaganie_nowej_linii = False
        self.typ_nowej_linii = None
        self.widzet_nowej_linii = None
        self.przesuniecie_nowej_linii = QPoint(0,0)
        self.biezacy_jezyk = DOMYSLNY_JEZYK
        self.pozycja_linijek = DOMYSLNA_POZYCJA_LINIJEK
        self.grubosc_linii_siatki = DOMYSLNA_GRUBOSC_SIATKI
        self.grubosc_chwytu = DOMYSLNA_GRUBOSC_CHWYTU  # v0.3
        self.grubosc_krawedzi_ekranu = DOMYSLNA_GRUBOSC_KRAWEDZI_EKRANU  # pasek
        self.skroty = dict(DOMYSLNE_SKROTY)  # edytowalne skróty, wczytywane z pliku stanu  # pasek na bokach i u góry, skąd produkuje się linie, min 1px
        self.kolor_linii_siatki = QColor(DOMYSLNY_KOLOR_SIATKI)
        self.kolor_linii_siatki.setAlpha(DOMYSLNA_PRZEZROCZYSTOSC_SIATKI)
        self.dialog_ustawien = None
        # v0.3: aktywna linia + tryby
        self.aktywna_linia_id = None
        self.tryb_wyboru = False
        self.tryb_przesuwania = False
        self.oczekujacy_numer = None
        self._hotkeys_trybu = []  # uchwyty keyboard.add_hotkey do usunięcia przy wyjściu z trybu
        self._timer_wyboru = QTimer(self)
        self._timer_wyboru.setSingleShot(True)
        self._timer_wyboru.timeout.connect(self.wylacz_tryb_wyboru)
        self._timer_zapisu = QTimer(self)
        self._timer_zapisu.setSingleShot(True)
        self._timer_zapisu.setInterval(500)
        self._timer_zapisu.timeout.connect(self.zapisz_stan)
        self._timer_nowej_linii = QTimer(self)
        self._timer_nowej_linii.setInterval(16)
        self._timer_nowej_linii.timeout.connect(self._polling_nowej_linii)
        self.wskaznik_trybu = WskaznikTrybu()
        global instancja_aplikacji
        instancja_aplikacji = self
        self.wczytaj_stan()
        signal_emitter.zadanie_przelaczenia_widocznosci.connect(self.przelacz_widocznosc)
        signal_emitter.zadanie_wyczyszczenia_wszystkiego.connect(self.wyczysc_wszystkie_linie)
        signal_emitter.zadanie_wyjscia_z_aplikacji.connect(self.zamknij_aplikacje)
        signal_emitter.zadanie_zmiany_pozycji_linijek.connect(self.zmien_pozycje_linijek_cyklicznie)
        signal_emitter.zadanie_okna_ustawien.connect(self.pokaz_dialog_ustawien)
        signal_emitter.zadanie_zwiekszenia_grubosci.connect(self.slot_zwieksz_grubosc)
        signal_emitter.zadanie_zmniejszenia_grubosci.connect(self.slot_zmniejsz_grubosc)
        signal_emitter.zadanie_zmiany_jezyka.connect(self.slot_zmien_jezyk)
        signal_emitter.zadanie_utworzenia_linii.connect(self.utworz_linie_skrotem)
        signal_emitter.zadanie_wyboru_linii.connect(self.wybierz_linie)
        # USUNIĘTE: skrót Wybór (G) usunięty na życzenie, nie podłączamy wlacz_tryb_wyboru
        signal_emitter.zadanie_trybu_przesuwania.connect(self.przelacz_tryb_przesuwania)
        signal_emitter.zadanie_przesuniecia_aktywnej.connect(self.przesun_aktywna_linie)
        signal_emitter.zadanie_wyjscia_z_trybu.connect(self.wylacz_wszystkie_tryby)
        signal_emitter.zadanie_usuniecia_aktywnej.connect(self.usun_aktywna_linie)
        self.konfiguruj_ui()
        self._synchronizuj_widzety_linii_siatki()
        self._aktualizuj_geometrie_nakladki()
        # Przywróć aktywną linię po wczytaniu, jeśli jakaś istnieje
        if self.dane_linii_siatki:
            # domyślnie aktywna = ostatnia utworzona, ale bez wchodzenia w tryb przesuwania na starcie
            self.aktywna_linia_id = self.dane_linii_siatki[-1]['id']
            self._odswiez_aktywnosc_widzetow()
    # --- UI ---
    def konfiguruj_ui(self):
        if not self.okna_nakladki.get("top"):
            self.okna_nakladki["top"] = WidzetLinijki(Qt.Orientation.Horizontal)
            self.okna_nakladki["top"].sygnal_klikniecia.connect(self.obsluz_klikniecie_linijki)
        if not self.okna_nakladki.get("left"):
            self.okna_nakladki["left"] = WidzetLinijki(Qt.Orientation.Vertical)
            self.okna_nakladki["left"].sygnal_klikniecia.connect(self.obsluz_klikniecie_linijki)
        if not self.okna_nakladki.get("corner"):
            self.okna_nakladki["corner"] = Naroznik()
    def _synchronizuj_widzety_linii_siatki(self):
        biezace = set(self.aktywne_linie_siatki.keys())
        wczytane = set(item['id'] for item in self.dane_linii_siatki)
        for dane in self.dane_linii_siatki:
            if dane['id'] not in biezace:
                nr = dane.get('nr', 1)
                self.stworz_widzet_linii_siatki(dane['type'], dane['pos'], dane['id'], numer=nr, update_geom=False)
        for id_siatki in list(biezace - wczytane):
            self.usun_widzet_linii_siatki_po_id(id_siatki)
        maks_id = max((item['id'] for item in self.dane_linii_siatki), default=-1)
        self.nastepny_id_siatki = max(self.nastepny_id_siatki, maks_id + 1, 0)
    def _aktualizuj_geometrie_nakladki(self):
        prostokat_ekranu = QApplication.primaryScreen().geometry()
        szer_ekr, wys_ekr = prostokat_ekranu.width(), prostokat_ekranu.height()
        rozm_lin = int(self.grubosc_krawedzi_ekranu)
        if not all(self.okna_nakladki.values()):
            self.konfiguruj_ui()
            if not all(self.okna_nakladki.values()):
                return
        linijka_gorna = self.okna_nakladki["top"]
        linijka_lewa = self.okna_nakladki["left"]
        naroznik = self.okna_nakladki["corner"]
        gora_x, gora_y, lewa_x, lewa_y, naroznik_x, naroznik_y = 0, 0, 0, 0, 0, 0
        gora_szer, gora_wys = szer_ekr, rozm_lin
        lewa_szer, lewa_wys = rozm_lin, wys_ekr
        if self.pozycja_linijek == 'top-left':
            gora_x, gora_y = rozm_lin, 0; lewa_x, lewa_y = 0, rozm_lin; naroznik_x, naroznik_y = 0, 0
            gora_szer -= rozm_lin; lewa_wys -= rozm_lin
        elif self.pozycja_linijek == 'top-right':
            gora_x, gora_y = 0, 0; lewa_x, lewa_y = szer_ekr - rozm_lin, rozm_lin; naroznik_x, naroznik_y = szer_ekr - rozm_lin, 0
            gora_szer -= rozm_lin; lewa_wys -= rozm_lin
        elif self.pozycja_linijek == 'bottom-right':
            gora_x, gora_y = 0, wys_ekr - rozm_lin; lewa_x, lewa_y = szer_ekr - rozm_lin, 0; naroznik_x, naroznik_y = szer_ekr - rozm_lin, wys_ekr - rozm_lin
            gora_szer -= rozm_lin; lewa_wys -= rozm_lin
        elif self.pozycja_linijek == 'bottom-left':
            gora_x, gora_y = rozm_lin, wys_ekr - rozm_lin; lewa_x, lewa_y = 0, 0; naroznik_x, naroznik_y = 0, wys_ekr - rozm_lin
            gora_szer -= rozm_lin; lewa_wys -= rozm_lin
        gora_szer = max(0, gora_szer); lewa_wys = max(0, lewa_wys)
        linijka_gorna.move(gora_x, gora_y); linijka_gorna.resize(gora_szer, gora_wys)
        linijka_lewa.move(lewa_x, lewa_y); linijka_lewa.resize(lewa_szer, lewa_wys)
        naroznik.move(naroznik_x, naroznik_y); naroznik.resize(rozm_lin, rozm_lin)
        # Odśwież rozmiary linijek i narożnika po zmianie grubości krawędzi ekranu
        for klucz in ("top", "left", "corner"):
            w = self.okna_nakladki.get(klucz)
            if w and hasattr(w, 'aktualizuj_rozmiar'):
                w.aktualizuj_rozmiar()
        for widzet_linii in self.aktywne_linie_siatki.values():
            widzet_linii._aktualizuj_geometrie()
    def obsluz_klikniecie_linijki(self, typ_linii, pozycja_globalna):
        if threading.current_thread().ident != id_glownego_watku:
            return
        if self.przeciaganie_nowej_linii:
            return
        self.rozpocznij_przeciaganie_nowej_linii(typ_linii, pozycja_globalna)
    def _pokaz_wszystkie_nakladki(self):
        wszystkie = list(self.okna_nakladki.values()) + list(self.aktywne_linie_siatki.values())
        for widzet in wszystkie:
            if widzet:
                widzet.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
                widzet.show(); widzet.raise_()
    def _ukryj_wszystkie_nakladki(self):
        wszystkie = list(self.okna_nakladki.values()) + list(self.aktywne_linie_siatki.values())
        for widzet in wszystkie:
            if widzet:
                widzet.hide()
        if self.dialog_ustawien and self.dialog_ustawien.isVisible():
            self.dialog_ustawien.hide()
        self.wskaznik_trybu.hide()
    def pokaz_linijki(self):
        if threading.current_thread().ident != id_glownego_watku:
            QTimer.singleShot(0, self.pokaz_linijki); return
        self.linijki_widoczne = True
        self._aktualizuj_geometrie_nakladki()
        self._pokaz_wszystkie_nakladki()
        self.zapisz_stan()
        signal_emitter.zadanie_aktualizacji_zasobnika.emit(self.linijki_widoczne)
    def ukryj_linijki(self):
        if threading.current_thread().ident != id_glownego_watku:
            QTimer.singleShot(0, self.ukryj_linijki); return
        if self.przeciaganie_nowej_linii:
            self.anuluj_przeciaganie_nowej_linii()
        self.wylacz_wszystkie_tryby()
        self.linijki_widoczne = False
        self._ukryj_wszystkie_nakladki()
        self.zapisz_stan()
        signal_emitter.zadanie_aktualizacji_zasobnika.emit(self.linijki_widoczne)
    def przelacz_widocznosc(self):
        if threading.current_thread().ident != id_glownego_watku:
            QTimer.singleShot(0, self.przelacz_widocznosc); return
        if self.linijki_widoczne:
            self.ukryj_linijki()
        else:
            self.pokaz_linijki()
    def zmien_pozycje_linijek_cyklicznie(self):
        if threading.current_thread().ident != id_glownego_watku:
            QTimer.singleShot(0, self.zmien_pozycje_linijek_cyklicznie); return
        try:
            idx = POZYCJE_LINIJEK.index(self.pozycja_linijek)
            self.pozycja_linijek = POZYCJE_LINIJEK[(idx+1) % len(POZYCJE_LINIJEK)]
            self._aktualizuj_geometrie_nakladki()
            if self.linijki_widoczne:
                self._pokaz_wszystkie_nakladki()
            self.zapisz_stan()
        except ValueError:
            self.pozycja_linijek = DOMYSLNA_POZYCJA_LINIJEK
            self._aktualizuj_geometrie_nakladki()
            if self.linijki_widoczne:
                self._pokaz_wszystkie_nakladki()
            self.zapisz_stan()
    # --- Grubość / kolor / przezroczystość / chwyt ---
    def slot_zwieksz_grubosc(self):
        if threading.current_thread().ident != id_glownego_watku:
            QTimer.singleShot(0, self.slot_zwieksz_grubosc); return
        nowa = min(self.grubosc_linii_siatki + KROK_ZMIANY_GRUBOSCI, MAKS_GRUBOSC_SIATKI)
        if nowa != self.grubosc_linii_siatki:
            self.zmien_grubosc(nowa)
            if self.dialog_ustawien and self.dialog_ustawien.isVisible():
                self.dialog_ustawien.pole_grubosci.setValue(nowa)
    def slot_zmniejsz_grubosc(self):
        if threading.current_thread().ident != id_glownego_watku:
            QTimer.singleShot(0, self.slot_zmniejsz_grubosc); return
        nowa = max(1, self.grubosc_linii_siatki - KROK_ZMIANY_GRUBOSCI)
        if nowa != self.grubosc_linii_siatki:
            self.zmien_grubosc(nowa)
            if self.dialog_ustawien and self.dialog_ustawien.isVisible():
                self.dialog_ustawien.pole_grubosci.setValue(nowa)
    def zmien_grubosc(self, wartosc):
        if threading.current_thread().ident != id_glownego_watku:
            QTimer.singleShot(0, lambda: self.zmien_grubosc(wartosc)); return
        nowa = max(1, min(int(wartosc), MAKS_GRUBOSC_SIATKI))
        if self.grubosc_linii_siatki != nowa:
            self.grubosc_linii_siatki = nowa
            self.zapisz_stan()
            self.aktualizuj_istniejace_linie_siatki()
    def zmien_kolor(self, kolor: QColor):
        if threading.current_thread().ident != id_glownego_watku:
            QTimer.singleShot(0, lambda: self.zmien_kolor(kolor)); return
        if isinstance(kolor, QColor) and kolor.isValid():
            if self.kolor_linii_siatki != kolor:
                self.kolor_linii_siatki = QColor(kolor)
                self.zapisz_stan()
                self.aktualizuj_istniejace_linie_siatki()
    def zmien_przezroczystosc(self, wartosc):
        if threading.current_thread().ident != id_glownego_watku:
            QTimer.singleShot(0, lambda: self.zmien_przezroczystosc(wartosc)); return
        nowa_alfa = max(0, min(255, int(wartosc)))
        if self.kolor_linii_siatki.alpha() != nowa_alfa:
            self.kolor_linii_siatki.setAlpha(nowa_alfa)
            self.zapisz_stan()
            self.aktualizuj_istniejace_linie_siatki()
    def zmien_grubosc_chwytu(self, wartosc):
        # v0.3: 1-50px, ustawiane w Ustawieniach
        if threading.current_thread().ident != id_glownego_watku:
            QTimer.singleShot(0, lambda: self.zmien_grubosc_chwytu(wartosc)); return
        nowa = max(MIN_GRUBOSC_CHWYTU, min(MAX_GRUBOSC_CHWYTU, int(wartosc)))
        if self.grubosc_chwytu != nowa:
            self.grubosc_chwytu = nowa
            self.zapisz_stan()
            for widzet in self.aktywne_linie_siatki.values():
                widzet._aktualizuj_geometrie()
                widzet.update()
            if self.widzet_nowej_linii:
                self.widzet_nowej_linii._aktualizuj_geometrie()
    def zmien_grubosc_krawedzi_ekranu(self, wartosc):
        # Grubość paska na bokach i u góry, skąd produkuje się linie, min 1px
        if threading.current_thread().ident != id_glownego_watku:
            QTimer.singleShot(0, lambda: self.zmien_grubosc_krawedzi_ekranu(wartosc)); return
        nowa = max(MIN_GRUBOSC_KRAWEDZI_EKRANU, min(MAX_GRUBOSC_KRAWEDZI_EKRANU, int(wartosc)))
        if self.grubosc_krawedzi_ekranu != nowa:
            self.grubosc_krawedzi_ekranu = nowa
            self.zapisz_stan()
            self._aktualizuj_geometrie_nakladki()
            if self.linijki_widoczne:
                self._pokaz_wszystkie_nakladki()
    def zmien_skroty(self, nowe):
        czyste={k: normalizuj_skrot(v) for k,v in nowe.items() if k in DOMYSLNE_SKROTY}
        for k in DOMYSLNE_SKROTY:
            if k not in czyste:
                czyste[k]=self.skroty.get(k, DOMYSLNE_SKROTY[k])
        bledy=sprawdz_skroty(czyste)
        if bledy:
            return bledy
        if self.tryb_przesuwania:
            try:
                self.wylacz_tryb_przesuwania()
            except Exception:
                pass
        self.skroty=dict(czyste)
        self.zapisz_stan()
        try:
            przearejestruj_skroty()
        except Exception as e:
            print(f"Ponowna rejestracja skrótów nie powiodła się: {e}")
        return []
    def resetuj_skroty_do_domyslnych(self):
        return self.zmien_skroty(dict(DOMYSLNE_SKROTY))
    def aktualizuj_istniejace_linie_siatki(self):
        for widzet_linii in self.aktywne_linie_siatki.values():
            widzet_linii.update()
    def slot_zmien_jezyk(self, jezyk=None):
        # Przełączanie PL/EN skrótem Ctrl+Alt+Shift+J (bez argumentu = toggle, wcześniej L = Ł)
        if threading.current_thread().ident != id_glownego_watku:
            QTimer.singleShot(0, lambda: self.slot_zmien_jezyk(jezyk)); return
        if jezyk in ('pl','en'):
            self.biezacy_jezyk = jezyk
        else:
            self.biezacy_jezyk = 'en' if self.biezacy_jezyk == 'pl' else 'pl'
        self.zapisz_stan()
        if self.dialog_ustawien:
            self.dialog_ustawien.retranslateUi()
        signal_emitter.zadanie_aktualizacji_zasobnika.emit(self.linijki_widoczne)
    def pokaz_dialog_ustawien(self):
        if threading.current_thread().ident != id_glownego_watku:
            QTimer.singleShot(0, self.pokaz_dialog_ustawien); return
        if self.dialog_ustawien is None:
            self.dialog_ustawien = DialogUstawien(self)
        self.dialog_ustawien.retranslateUi()
        self.dialog_ustawien.wczytaj_poczatkowe_ustawienia()
        if not self.dialog_ustawien.isVisible():
            self.dialog_ustawien.show()
        self.dialog_ustawien.raise_()
        self.dialog_ustawien.activateWindow()
    # --- v0.3: numeracja, tworzenie skrótem, wybór, przesuwanie ---
    def znajdz_wolny_numer(self, typ):
        zajete = {d.get('nr', 0) for d in self.dane_linii_siatki if d.get('type') == typ}
        for nr in range(1, MAX_LICZBA_LINII_NA_ORIENTACJE + 1):
            if nr not in zajete:
                return nr
        return None
    def _odswiez_aktywnosc_widzetow(self):
        for widzet in self.aktywne_linie_siatki.values():
            widzet.ustaw_aktywna(widzet.id == self.aktywna_linia_id)
    def ustaw_aktywna_linie(self, id_siatki, pokaz_wskaznik=True):
        if threading.current_thread().ident != id_glownego_watku:
            QTimer.singleShot(0, lambda: self.ustaw_aktywna_linie(id_siatki, pokaz_wskaznik)); return
        if id_siatki not in self.aktywne_linie_siatki and id_siatki != -1:
            return
        self.aktywna_linia_id = id_siatki
        self._odswiez_aktywnosc_widzetow()
        if pokaz_wskaznik and self.tryb_przesuwania:
            self._pokaz_wskaznik_przesuwania()
    def utworz_linie_skrotem(self, typ):
        # typ 'h' = pozioma (X), 'v' = pionowa (Y). Domyślnie 20px od góry / lewej.
        if threading.current_thread().ident != id_glownego_watku:
            QTimer.singleShot(0, lambda: self.utworz_linie_skrotem(typ)); return
        if not self.linijki_widoczne:
            self.pokaz_linijki()
        nr = self.znajdz_wolny_numer(typ)
        if nr is None:
            tekst = "Brak wolnych numerów! Usuń linię (podwójny klik) albo wyczyść wszystko." if self.biezacy_jezyk == 'pl' else "No free numbers! Delete a line (double-click) or clear all."
            self.wskaznik_trybu.pokaz(f"{NAZWA_APLIKACJI} - {tekst}")
            QTimer.singleShot(2500, self.wskaznik_trybu.hide)
            return
        ekran = QApplication.primaryScreen().geometry()
        kraw = int(self.grubosc_krawedzi_ekranu)
        min_x = kraw if 'left' in self.pozycja_linijek else 0
        min_y = kraw if 'top' in self.pozycja_linijek else 0
        maks_x = ekran.width() - (kraw if 'right' in self.pozycja_linijek else 0)
        maks_y = ekran.height() - (kraw if 'bottom' in self.pozycja_linijek else 0)
        if typ == 'h':
            pozycja = DOMYSLNA_POZYCJA_NOWEJ_LINII + (nr - 1) * KROK_POZYCJI_NOWEJ_LINII
            pozycja = max(min_y, min(pozycja, maks_y))
        else:
            pozycja = DOMYSLNA_POZYCJA_NOWEJ_LINII + (nr - 1) * KROK_POZYCJI_NOWEJ_LINII
            pozycja = max(min_x, min(pozycja, maks_x))
        nowe_id = self.nastepny_id_siatki
        self.nastepny_id_siatki += 1
        self.dane_linii_siatki.append({'type': typ, 'pos': pozycja, 'id': nowe_id, 'nr': nr})
        widzet = self.stworz_widzet_linii_siatki(typ, pozycja, nowe_id, numer=nr, update_geom=True)
        if widzet:
            widzet.show(); widzet.raise_()
        self.ustaw_aktywna_linie(nowe_id, pokaz_wskaznik=False)
        self.zapisz_stan()
        # Po utworzeniu od razu tryb przesuwania, żeby można było ruszać strzałkami.
        self.wlacz_tryb_przesuwania()
    def wybierz_linie(self, nr, typ):
        if threading.current_thread().ident != id_glownego_watku:
            QTimer.singleShot(0, lambda: self.wybierz_linie(nr, typ)); return
        # Wyjdź z trybu wyboru, jeśli był włączony (wybór bezpośredni też tu trafia)
        if self.tryb_wyboru:
            self.wylacz_tryb_wyboru(pokaz_przesuwanie=False)
        znaleziony = None
        for dane in self.dane_linii_siatki:
            if dane.get('nr') == nr and dane.get('type') == typ:
                znaleziony = dane
                break
        if znaleziony is None:
            etykieta = etykieta_linii(typ, nr)
            tekst = f"Brak linii {etykieta}." if self.biezacy_jezyk == 'pl' else f"No line {etykieta}."
            self.wskaznik_trybu.pokaz(f"{NAZWA_APLIKACJI} - {tekst}")
            QTimer.singleShot(2000, self.wskaznik_trybu.hide)
            return
        if not self.linijki_widoczne:
            self.pokaz_linijki()
        self.ustaw_aktywna_linie(znaleziony['id'], pokaz_wskaznik=False)
        self.wlacz_tryb_przesuwania()
    def przesun_aktywna_linie(self, dx, dy):
        if threading.current_thread().ident != id_glownego_watku:
            QTimer.singleShot(0, lambda: self.przesun_aktywna_linie(dx, dy)); return
        if self.aktywna_linia_id is None:
            return
        widzet = self.aktywne_linie_siatki.get(self.aktywna_linia_id)
        if not widzet:
            return
        # Pozioma rusza się tylko góra/dół, pionowa tylko lewo/prawo
        if widzet.typ == 'h':
            if dy == 0:
                return
            nowa = widzet.pobierz_pozycje() + dy
        else:
            if dx == 0:
                return
            nowa = widzet.pobierz_pozycje() + dx
        ekran = QApplication.primaryScreen().geometry()
        kraw = int(self.grubosc_krawedzi_ekranu)
        min_x = kraw if 'left' in self.pozycja_linijek else 0
        min_y = kraw if 'top' in self.pozycja_linijek else 0
        maks_x = ekran.width() - (kraw if 'right' in self.pozycja_linijek else 0)
        maks_y = ekran.height() - (kraw if 'bottom' in self.pozycja_linijek else 0)
        if widzet.typ == 'h':
            nowa = max(min_y, min(nowa, maks_y))
        else:
            nowa = max(min_x, min(nowa, maks_x))
        widzet.ustaw_pozycje(nowa)
        self.aktualizuj_pozycje_linii_siatki(widzet.id, nowa)
        # Zapis z opóźnieniem, żeby nie zapisywać pliku przy każdym 1px
        self._timer_zapisu.start()
        if self.tryb_przesuwania:
            self._pokaz_wskaznik_przesuwania()
    def _pokaz_wskaznik_przesuwania(self):
        # USUNIĘTE na życzenie: brak opisu w czarnej ramce w trybie przesuwania.
        # Nic nie pokazujemy, żeby nie zasłaniać ekranu. Wskaznik jest ukryty.
        try:
            self.wskaznik_trybu.hide()
        except Exception:
            pass
        return
    # --- Tryby: wybór i przesuwanie (dynamiczne hotkeye, żeby nie blokować strzałek na stałe) ---
    def _usun_hotkeye_trybu(self):
        for h in list(self._hotkeys_trybu):
            try:
                keyboard.remove_hotkey(h)
            except Exception:
                pass
        self._hotkeys_trybu = []
    def wlacz_tryb_wyboru(self):
        # USUNIĘTE: skrót Wybór (G) usunięty na życzenie. Funkcja zostaje jako martwy kod, nie jest wywoływana (brak hotkeya i brak pozycji w tray). Wybór tylko bezpośrednio Ctrl+Alt+Shift+1+X ... +0+Y.
        if threading.current_thread().ident != id_glownego_watku:
            QTimer.singleShot(0, self.wlacz_tryb_wyboru); return
        if self.tryb_wyboru:
            return
        self.wylacz_tryb_przesuwania()
        self.tryb_wyboru = True
        self.oczekujacy_numer = None
        if self.biezacy_jezyk == 'pl':
            tekst = "WYBIERZ LINIĘ: naciśnij 1-0, potem X (pozioma) / Y (pionowa). Esc = anuluj."
        else:
            tekst = "SELECT LINE: press 1-0, then X (horizontal) / Y (vertical). Esc = cancel."
        self.wskaznik_trybu.pokaz(tekst)
        # Rejestrujemy TYLKO na czas trybu, żeby cyfry i X/Y nie były blokowane poza trybem.
        def _cyfra(nr):
            return lambda: self._wybor_cyfra(nr)
        for klawisz, nr in [("1",1),("2",2),("3",3),("4",4),("5",5),("6",6),("7",7),("8",8),("9",9),("0",10)]:
            try:
                h = keyboard.add_hotkey(klawisz, _cyfra(nr), suppress=True)
                self._hotkeys_trybu.append(h)
            except Exception as e:
                print(f"Nie udało się zarejestrować klawisza wyboru {klawisz}: {e}")
        for klawisz, typ in [("x",'h'),("y",'v')]:
            try:
                h = keyboard.add_hotkey(klawisz, lambda t=typ: self._wybor_orientacja(t), suppress=True)
                self._hotkeys_trybu.append(h)
            except Exception as e:
                print(f"Nie udało się zarejestrować klawisza wyboru {klawisz}: {e}")
        try:
            h = keyboard.add_hotkey("esc", lambda: signal_emitter.zadanie_wyjscia_z_trybu.emit(), suppress=True)
            self._hotkeys_trybu.append(h)
        except Exception:
            pass
        self._timer_wyboru.start(5000)
    def _wybor_cyfra(self, nr):
        # Wywoływane z wątku keyboard -> przez sygnał do wątku Qt
        # Tu jesteśmy w wątku keyboard, więc tylko zapisz numer i odśwież wskaznik przez QTimer
        self.oczekujacy_numer = nr
        # Odśwież wskaznik w wątku Qt
        QTimer.singleShot(0, lambda: self._pokaz_wskaznik_wyboru_po_cyfrze())
    def _pokaz_wskaznik_wyboru_po_cyfrze(self):
        if not self.tryb_wyboru or self.oczekujacy_numer is None:
            return
        if self.biezacy_jezyk == 'pl':
            tekst = f"WYBIERZ LINIĘ: wybrano {self.oczekujacy_numer} (0 = 10), teraz naciśnij X (pozioma) / Y (pionowa). Esc = anuluj."
        else:
            tekst = f"SELECT LINE: selected {self.oczekujacy_numer} (0 = 10), now press X (horizontal) / Y (vertical). Esc = cancel."
        self.wskaznik_trybu.pokaz(tekst)
        self._timer_wyboru.start(5000)
    def _wybor_orientacja(self, typ):
        nr = self.oczekujacy_numer
        if nr is None:
            return
        # Zapisz i wykonaj w wątku Qt
        QTimer.singleShot(0, lambda: self.wybierz_linie(nr, typ))
    def wylacz_tryb_wyboru(self, pokaz_przesuwanie=False):
        if threading.current_thread().ident != id_glownego_watku:
            QTimer.singleShot(0, lambda: self.wylacz_tryb_wyboru(pokaz_przesuwanie)); return
        if not self.tryb_wyboru:
            return
        self.tryb_wyboru = False
        self.oczekujacy_numer = None
        self._timer_wyboru.stop()
        self._usun_hotkeye_trybu()
        if not pokaz_przesuwanie and not self.tryb_przesuwania:
            self.wskaznik_trybu.hide()
    def wlacz_tryb_przesuwania(self):
        if threading.current_thread().ident != id_glownego_watku:
            QTimer.singleShot(0, self.wlacz_tryb_przesuwania); return
        if self.aktywna_linia_id is None:
            return
        if self.aktywna_linia_id not in self.aktywne_linie_siatki:
            return
        if self.tryb_przesuwania:
            return
        # Wyjdź z trybu wyboru, jeśli był
        if self.tryb_wyboru:
            self.tryb_wyboru = False
            self.oczekujacy_numer = None
            self._timer_wyboru.stop()
            self._usun_hotkeye_trybu()
        self.tryb_przesuwania = True
        self._pokaz_wskaznik_przesuwania()
        # Strzałki TYLKO w trybie przesuwania, z suppress=True, żeby nie ruszały kursora w Word/Chrome.
        def _ruch(dx, dy):
            return lambda: signal_emitter.zadanie_przesuniecia_aktywnej.emit(dx, dy)
        pary = [
            ("left", -KROK_STRZALKA, 0), ("right", KROK_STRZALKA, 0),
            ("up", 0, -KROK_STRZALKA), ("down", 0, KROK_STRZALKA),
            ("shift+left", -KROK_STRZALKA_SHIFT, 0), ("shift+right", KROK_STRZALKA_SHIFT, 0),
            ("shift+up", 0, -KROK_STRZALKA_SHIFT), ("shift+down", 0, KROK_STRZALKA_SHIFT),
        ]
        for klawisz, dx, dy in pary:
            try:
                h = keyboard.add_hotkey(klawisz, _ruch(dx, dy), suppress=True)
                self._hotkeys_trybu.append(h)
            except Exception as e:
                print(f"Nie udało się zarejestrować strzałki {klawisz}: {e}")
        try:
            h = keyboard.add_hotkey("esc", lambda: signal_emitter.zadanie_wyjscia_z_trybu.emit(), suppress=True)
            self._hotkeys_trybu.append(h)
        except Exception:
            pass
        # Enter też wychodzi z trybu (zatwierdzenie pozycji)
        try:
            h = keyboard.add_hotkey("enter", lambda: signal_emitter.zadanie_wyjscia_z_trybu.emit(), suppress=True)
            self._hotkeys_trybu.append(h)
        except Exception:
            pass
    def przelacz_tryb_przesuwania(self):
        if threading.current_thread().ident != id_glownego_watku:
            QTimer.singleShot(0, self.przelacz_tryb_przesuwania); return
        if self.tryb_przesuwania:
            self.wylacz_tryb_przesuwania()
        else:
            self.wlacz_tryb_przesuwania()
    def wylacz_tryb_przesuwania(self):
        if threading.current_thread().ident != id_glownego_watku:
            QTimer.singleShot(0, self.wylacz_tryb_przesuwania); return
        if not self.tryb_przesuwania:
            return
        self.tryb_przesuwania = False
        self._usun_hotkeye_trybu()
        self.wskaznik_trybu.hide()
        self.zapisz_stan()
    def usun_aktywna_linie(self):
        # Shift+Del ZAWSZE kasuje aktywną linię, nie tylko w trybie przesuwania (na życzenie).
        # Uwaga: globalny Shift+Del blokuje Shift+Del w Eksploratorze / Wordzie, gdy aplikacja działa.
        if threading.current_thread().ident != id_glownego_watku:
            QTimer.singleShot(0, self.usun_aktywna_linie); return
        if self.aktywna_linia_id is None:
            return
        id_do_usuniecia = self.aktywna_linia_id
        # Wyjdź z trybu przesuwania przed usunięciem, jeśli był włączony
        if self.tryb_przesuwania:
            self.wylacz_tryb_przesuwania()
        self.usun_widzet_linii_siatki_po_id(id_do_usuniecia)
    def wylacz_wszystkie_tryby(self):
        if threading.current_thread().ident != id_glownego_watku:
            QTimer.singleShot(0, self.wylacz_wszystkie_tryby); return
        byl_tryb = self.tryb_wyboru or self.tryb_przesuwania
        if self.tryb_wyboru:
            self.tryb_wyboru = False
            self.oczekujacy_numer = None
            self._timer_wyboru.stop()
        if self.tryb_przesuwania:
            self.tryb_przesuwania = False
            self.zapisz_stan()
        if byl_tryb:
            self._usun_hotkeye_trybu()
            self.wskaznik_trybu.hide()


    # --- Przeciąganie nowej linii z linijki (v0.3: polling RDP, brak eventFilter MouseMove) ---
    def rozpocznij_przeciaganie_nowej_linii(self, typ_linii, globalna_pozycja_startowa):
        if self.przeciaganie_nowej_linii:
            return
        self.przeciaganie_nowej_linii = True
        self.typ_nowej_linii = typ_linii
        ekran = QApplication.primaryScreen().geometry()
        kraw = int(self.grubosc_krawedzi_ekranu)
        min_x = kraw if 'left' in self.pozycja_linijek else 0
        min_y = kraw if 'top' in self.pozycja_linijek else 0
        maks_x = ekran.width() - (kraw if 'right' in self.pozycja_linijek else 0)
        maks_y = ekran.height() - (kraw if 'bottom' in self.pozycja_linijek else 0)
        if typ_linii == 'h':
            pozycja_pocz = max(min_y, min(globalna_pozycja_startowa.y(), maks_y))
        else:
            pozycja_pocz = max(min_x, min(globalna_pozycja_startowa.x(), maks_x))
        # Tymczasowy numer: 0 = podgląd, prawdziwy numer nadamy przy zakończeniu
        self.widzet_nowej_linii = WidzetLiniiSiatki(typ_linii, pozycja_pocz, -1, numer=0)
        self.widzet_nowej_linii.numer = 0  # 0 = nowa, nie ma jeszcze numeru
        self.widzet_nowej_linii._aktualizuj_geometrie()
        self.widzet_nowej_linii.show()
        self.widzet_nowej_linii.raise_()
        # Offset: gdzie kliknięto względem środka uchwytu
        chwyt = self.widzet_nowej_linii._grubosc_chwytu()
        if typ_linii == 'h':
            self.przesuniecie_nowej_linii = QPoint(0, globalna_pozycja_startowa.y() - (pozycja_pocz - chwyt // 2))
        else:
            self.przesuniecie_nowej_linii = QPoint(globalna_pozycja_startowa.x() - (pozycja_pocz - chwyt // 2), 0)
        self.widzet_nowej_linii.czy_przeciagane = True
        self.widzet_nowej_linii.stworz_podpowiedz()
        self.widzet_nowej_linii.aktualizuj_podpowiedz(globalna_pozycja_startowa)
        self._timer_nowej_linii.start()
    def _polling_nowej_linii(self):
        if not self.przeciaganie_nowej_linii or not self.widzet_nowej_linii:
            self._timer_nowej_linii.stop()
            return
        # Esc = anuluj (RDP: keyboard sprawdza stan globalnie)
        try:
            if keyboard.is_pressed('esc'):
                self._timer_nowej_linii.stop()
                self.anuluj_przeciaganie_nowej_linii()
                return
        except Exception:
            pass
        # Puszczony przycisk = zakończ (RDP gubi MouseRelease, więc sprawdzamy stan przycisku)
        przyciski = QApplication.mouseButtons()
        if not (przyciski & Qt.MouseButton.LeftButton):
            self._timer_nowej_linii.stop()
            self.zakoncz_przeciaganie_nowej_linii()
            return
        # Ruch = pozycja kursora z systemu
        biezaca = QCursor.pos()
        ekran = QApplication.primaryScreen().geometry()
        kraw = int(self.grubosc_krawedzi_ekranu)
        min_x = kraw if 'left' in self.pozycja_linijek else 0
        min_y = kraw if 'top' in self.pozycja_linijek else 0
        maks_x = ekran.width() - (kraw if 'right' in self.pozycja_linijek else 0)
        maks_y = ekran.height() - (kraw if 'bottom' in self.pozycja_linijek else 0)
        chwyt = self.widzet_nowej_linii._grubosc_chwytu()
        if self.typ_nowej_linii == 'h':
            nowy_y = biezaca.y() - self.przesuniecie_nowej_linii.y()
            nowa = max(min_y, min(nowy_y + chwyt // 2, maks_y))
        else:
            nowy_x = biezaca.x() - self.przesuniecie_nowej_linii.x()
            nowa = max(min_x, min(nowy_x + chwyt // 2, maks_x))
        self.widzet_nowej_linii.ustaw_pozycje(nowa)
        self.widzet_nowej_linii.aktualizuj_podpowiedz(biezaca)
    def zakoncz_przeciaganie_nowej_linii(self):
        if not self.przeciaganie_nowej_linii or not self.widzet_nowej_linii:
            return
        konczony = self.widzet_nowej_linii
        typ_linii = konczony.typ
        pozycja_koncowa = konczony.pobierz_pozycje()
        self.przeciaganie_nowej_linii = False
        self.typ_nowej_linii = None
        self.widzet_nowej_linii = None
        self.przesuniecie_nowej_linii = QPoint(0,0)
        self._timer_nowej_linii.stop()
        konczony.zniszcz_podpowiedz()
        konczony.czy_przeciagane = False
        ekran = QApplication.primaryScreen().geometry()
        kraw = int(self.grubosc_krawedzi_ekranu)
        gorna = kraw if 'top' in self.pozycja_linijek else -1
        dolna = ekran.height() - kraw if 'bottom' in self.pozycja_linijek else ekran.height() + 1
        lewa = kraw if 'left' in self.pozycja_linijek else -1
        prawa = ekran.width() - kraw if 'right' in self.pozycja_linijek else ekran.width() + 1
        usun = False
        if typ_linii == 'h':
            if pozycja_koncowa <= gorna or pozycja_koncowa >= dolna:
                usun = True
        else:
            if pozycja_koncowa <= lewa or pozycja_koncowa >= prawa:
                usun = True
        if usun:
            try:
                konczony.zniszcz_etykiete()
            except Exception:
                pass
            konczony.hide(); konczony.deleteLater()
        else:
            nr = self.znajdz_wolny_numer(typ_linii)
            if nr is None:
                try:
                    konczony.zniszcz_etykiete()
                except Exception:
                    pass
                konczony.hide(); konczony.deleteLater()
                self.wskaznik_trybu.pokaz("Brak wolnych numerów! Usuń linię (podwójny klik).")
                QTimer.singleShot(2500, self.wskaznik_trybu.hide)
                return
            nowe_id = self.nastepny_id_siatki
            self.nastepny_id_siatki += 1
            konczony.id = nowe_id
            konczony.numer = nr
            konczony.update()
            self.dane_linii_siatki.append({'type': typ_linii, 'pos': pozycja_koncowa, 'id': nowe_id, 'nr': nr})
            self.aktywne_linie_siatki[nowe_id] = konczony
            self.ustaw_aktywna_linie(nowe_id, pokaz_wskaznik=False)
            self.zapisz_stan()
            self.wlacz_tryb_przesuwania()
    def anuluj_przeciaganie_nowej_linii(self):
        if not self.przeciaganie_nowej_linii or not self.widzet_nowej_linii:
            return
        widzet = self.widzet_nowej_linii
        self.przeciaganie_nowej_linii = False
        self.typ_nowej_linii = None
        self.widzet_nowej_linii = None
        self.przesuniecie_nowej_linii = QPoint(0,0)
        self._timer_nowej_linii.stop()
        widzet.zniszcz_podpowiedz()
        try:
            widzet.zniszcz_etykiete()
        except Exception:
            pass
        widzet.hide(); widzet.deleteLater()
    def stworz_widzet_linii_siatki(self, typ_linii, pozycja, id_siatki, numer=1, update_geom=True):
        if id_siatki in self.aktywne_linie_siatki:
            return self.aktywne_linie_siatki[id_siatki]
        widzet = WidzetLiniiSiatki(typ_linii, pozycja, id_siatki, numer=numer)
        self.aktywne_linie_siatki[id_siatki] = widzet
        if not any(d['id'] == id_siatki for d in self.dane_linii_siatki):
            self.dane_linii_siatki.append({'type': typ_linii, 'pos': pozycja, 'id': id_siatki, 'nr': numer})
        if update_geom:
            widzet._aktualizuj_geometrie()
        widzet.ustaw_aktywna(widzet.id == self.aktywna_linia_id)
        if self.linijki_widoczne:
            widzet.show(); widzet.raise_()
        else:
            widzet.hide()
        return widzet
    def aktualizuj_pozycje_linii_siatki(self, id_siatki, nowa_pozycja):
        for i, dane in enumerate(self.dane_linii_siatki):
            if dane['id'] == id_siatki:
                if dane['pos'] != nowa_pozycja:
                    self.dane_linii_siatki[i]['pos'] = nowa_pozycja
                    self.zapisz_stan()
                return
    def usun_widzet_linii_siatki_po_id(self, id_siatki):
        widzet = self.aktywne_linie_siatki.pop(id_siatki, None)
        if widzet:
            widzet.zniszcz_podpowiedz()
            try:
                widzet.zniszcz_etykiete()
            except Exception:
                pass
            widzet.hide(); widzet.deleteLater()
        self.dane_linii_siatki = [d for d in self.dane_linii_siatki if d['id'] != id_siatki]
        if self.aktywna_linia_id == id_siatki:
            self.aktywna_linia_id = self.dane_linii_siatki[-1]['id'] if self.dane_linii_siatki else None
            self._odswiez_aktywnosc_widzetow()
            if self.aktywna_linia_id is None:
                self.wylacz_tryb_przesuwania()
        self.zapisz_stan()
    def usun_widzet_linii_siatki(self, widzet_do_usuniecia):
        if not widzet_do_usuniecia:
            return
        id_siatki = widzet_do_usuniecia.id
        if id_siatki == -1:
            if self.widzet_nowej_linii is widzet_do_usuniecia:
                self.anuluj_przeciaganie_nowej_linii()
            else:
                widzet_do_usuniecia.zniszcz_podpowiedz()
                try:
                    widzet_do_usuniecia.zniszcz_etykiete()
                except Exception:
                    pass
                widzet_do_usuniecia.hide(); widzet_do_usuniecia.deleteLater()
            return
        self.usun_widzet_linii_siatki_po_id(id_siatki)
    def wyczysc_wszystkie_linie(self):
        if threading.current_thread().ident != id_glownego_watku:
            QTimer.singleShot(0, self.wyczysc_wszystkie_linie); return
        self.wylacz_wszystkie_tryby()
        for id_siatki in list(self.aktywne_linie_siatki.keys()):
            widzet = self.aktywne_linie_siatki.pop(id_siatki)
            widzet.zniszcz_podpowiedz()
            try:
                widzet.zniszcz_etykiete()
            except Exception:
                pass
            widzet.hide(); widzet.deleteLater()
        self.dane_linii_siatki = []
        self.nastepny_id_siatki = 0
        self.aktywna_linia_id = None
        self.zapisz_stan()
    def zamknij_aplikacje(self):
        if threading.current_thread().ident != id_glownego_watku:
            QTimer.singleShot(0, self.zamknij_aplikacje); return
        self.wylacz_wszystkie_tryby()
        self.zapisz_stan()
        try:
            keyboard.unhook_all_hotkeys()
        except Exception:
            pass
        global instancja_ikony_zasobnika
        if instancja_ikony_zasobnika:
            try:
                instancja_ikony_zasobnika.stop()
            except Exception:
                pass
            instancja_ikony_zasobnika = None
        app = QApplication.instance()
        if app:
            app.quit()
    def zapisz_stan(self):
        maks_id = max((item['id'] for item in self.dane_linii_siatki), default=-1)
        self.nastepny_id_siatki = max(0, maks_id + 1)
        # Uzupełnij nr dla starych wpisów bez nr (migracja z v0.2)
        for dane in self.dane_linii_siatki:
            if 'nr' not in dane:
                wolny = self.znajdz_wolny_numer(dane['type'])
                dane['nr'] = wolny if wolny is not None else 1
        stan = {
            'wersja': WERSJA,
            'linijki_widoczne': self.linijki_widoczne,
            'pozycja_linijek': self.pozycja_linijek,
            'wyglad_linii_siatki': {'grubosc': self.grubosc_linii_siatki, 'kolor': self.kolor_linii_siatki.name(QColor.NameFormat.HexRgb), 'przezroczystosc': self.kolor_linii_siatki.alpha()},
            'grubosc_chwytu': int(self.grubosc_chwytu),
            'skroty': dict(self.skroty),
            'grubosc_krawedzi_ekranu': int(self.grubosc_krawedzi_ekranu),
            'linie_siatki': list(self.dane_linii_siatki),
            'nastepny_id_siatki': self.nastepny_id_siatki,
            'biezacy_jezyk': self.biezacy_jezyk,
            'aktywna_linia_id': self.aktywna_linia_id,
        }
        try:
            with open(PLIK_STANU, 'w', encoding='utf-8') as f:
                json.dump(stan, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Błąd zapisu stanu: {e}")
    def wczytaj_stan(self):
        stan = {}
        try:
            if os.path.exists(PLIK_STANU):
                with open(PLIK_STANU, 'r', encoding='utf-8') as f:
                    stan = json.load(f)
        except Exception as e:
            print(f"Błąd odczytu stanu: {e}. Używam domyślnych.")
            stan = {}
        self.linijki_widoczne = stan.get('linijki_widoczne', False)
        self.pozycja_linijek = stan.get('pozycja_linijek', DOMYSLNA_POZYCJA_LINIJEK)
        if self.pozycja_linijek not in POZYCJE_LINIJEK:
            self.pozycja_linijek = DOMYSLNA_POZYCJA_LINIJEK
        wyglad = stan.get('wyglad_linii_siatki', {})
        self.grubosc_linii_siatki = max(1, min(int(wyglad.get('grubosc', DOMYSLNA_GRUBOSC_SIATKI)), MAKS_GRUBOSC_SIATKI))
        kolor_hex = wyglad.get('kolor', DOMYSLNY_KOLOR_SIATKI)
        przez = max(0, min(int(wyglad.get('przezroczystosc', DOMYSLNA_PRZEZROCZYSTOSC_SIATKI)), 255))
        temp = QColor(kolor_hex)
        temp.setAlpha(przez)
        self.kolor_linii_siatki = temp
        self.grubosc_chwytu = max(MIN_GRUBOSC_CHWYTU, min(MAX_GRUBOSC_CHWYTU, int(stan.get('grubosc_chwytu', DOMYSLNA_GRUBOSC_CHWYTU))))
        self.grubosc_krawedzi_ekranu = max(MIN_GRUBOSC_KRAWEDZI_EKRANU, min(MAX_GRUBOSC_KRAWEDZI_EKRANU, int(stan.get('grubosc_krawedzi_ekranu', DOMYSLNA_GRUBOSC_KRAWEDZI_EKRANU))))
        zapisane = stan.get('skroty', {}) if isinstance(stan.get('skroty', {}), dict) else {}
        for _k in list(DOMYSLNE_SKROTY.keys()):
            if _k in zapisane and isinstance(zapisane[_k], str) and zapisane[_k].strip():
                self.skroty[_k] = normalizuj_skrot(zapisane[_k])
        self.dane_linii_siatki = stan.get('linie_siatki', [])
        # Migracja v0.2 -> v0.3: nadaj numery, jeśli brak
        zajete_h = set(); zajete_v = set()
        for dane in self.dane_linii_siatki:
            if 'nr' not in dane or dane.get('nr') not in range(1, 11):
                zajete = zajete_h if dane.get('type') == 'h' else zajete_v
                wolny = None
                for nr in range(1, 11):
                    if nr not in zajete:
                        wolny = nr; break
                dane['nr'] = wolny if wolny is not None else 1
            if dane.get('type') == 'h':
                zajete_h.add(dane['nr'])
            else:
                zajete_v.add(dane['nr'])
            dane['pos'] = int(dane.get('pos', DOMYSLNA_POZYCJA_NOWEJ_LINII))
        self.nastepny_id_siatki = stan.get('nastepny_id_siatki', 0)
        self.biezacy_jezyk = stan.get('biezacy_jezyk', DOMYSLNY_JEZYK)
        self.aktywna_linia_id = stan.get('aktywna_linia_id', None)
    def uruchom(self):
        QTimer.singleShot(50, self._poczatkowe_pokaz_ukryj)
    def _poczatkowe_pokaz_ukryj(self):
        if self.linijki_widoczne:
            self.pokaz_linijki()
        else:
            self.ukryj_linijki()


# --- Tray ---
def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def stworz_obraz_ikony(szer, wys, kol1_rgb, kol2_rgb):
    img = Image.new('RGBA', (szer, wys), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    for y in range(wys):
        t = y / max(1, wys-1)
        r = int(kol1_rgb[0] + (kol2_rgb[0]-kol1_rgb[0])*t)
        g = int(kol1_rgb[1] + (kol2_rgb[1]-kol1_rgb[1])*t)
        b = int(kol1_rgb[2] + (kol2_rgb[2]-kol1_rgb[2])*t)
        draw.line([(0,y),(szer,y)], fill=(r,g,b,255))
    draw.line([(0, wys//2),(szer, wys//2)], fill=(0,0,0,255), width=2)
    draw.line([(szer//2, 0),(szer//2, wys)], fill=(0,0,0,255), width=2)
    return img

def pobierz_obraz_ikony():
    return stworz_obraz_ikony(64, 64, (0, 252, 234), (0, 120, 200))

def po_kliknieciu_przelacz_tray(icon, item):
    signal_emitter.zadanie_przelaczenia_widocznosci.emit()
def po_kliknieciu_wyczysc_tray(icon, item):
    signal_emitter.zadanie_wyczyszczenia_wszystkiego.emit()
def po_kliknieciu_zmien_pozycje_tray(icon, item):
    signal_emitter.zadanie_zmiany_pozycji_linijek.emit()
def po_kliknieciu_ustawienia_tray(icon, item):
    signal_emitter.zadanie_okna_ustawien.emit()
def po_kliknieciu_wyjscie_tray(icon, item):
    signal_emitter.zadanie_wyjscia_z_aplikacji.emit()
def po_kliknieciu_jezyk_pl_tray(icon, item):
    signal_emitter.zadanie_zmiany_jezyka.emit('pl')
def po_kliknieciu_jezyk_en_tray(icon, item):
    signal_emitter.zadanie_zmiany_jezyka.emit('en')
def po_kliknieciu_utworz_pozioma_tray(icon, item):
    signal_emitter.zadanie_utworzenia_linii.emit('h')
def po_kliknieciu_utworz_pionowa_tray(icon, item):
    signal_emitter.zadanie_utworzenia_linii.emit('v')
# USUNIĘTE: po_kliknieciu_wybor_tray - skrót Wybór usunięty

def formatuj_skrot_klawiszowy(skrot):
    return formatuj_skrot(skrot)

def stworz_menu_zasobnika():
    # Tytuł z wersją 0.3
    menu = pystray.Menu(
        pystray.MenuItem(lambda text: f"{NAZWA_APLIKACJI}", None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem(lambda text: tlumacz(KONTEKST_TRAY, "Utwórz poziomą ({})").format(formatuj_skrot(pobierz_skrot('utworz_pozioma'))), po_kliknieciu_utworz_pozioma_tray),
        pystray.MenuItem(lambda text: tlumacz(KONTEKST_TRAY, "Utwórz pionową ({})").format(formatuj_skrot(pobierz_skrot('utworz_pionowa'))), po_kliknieciu_utworz_pionowa_tray),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem(lambda text: tlumacz(KONTEKST_TRAY, "Ukryj/Pokaż Linie ({})").format(formatuj_skrot(pobierz_skrot('widocznosc'))), po_kliknieciu_przelacz_tray, checked=lambda item: instancja_aplikacji.linijki_widoczne if instancja_aplikacji else False),
        pystray.MenuItem(lambda text: tlumacz(KONTEKST_TRAY, "Zmień Pozycję ({})").format(formatuj_skrot(pobierz_skrot('pozycja_linijek'))), po_kliknieciu_zmien_pozycje_tray),
        pystray.MenuItem(lambda text: tlumacz(KONTEKST_TRAY, "Wyczyść Wszystko ({})").format(formatuj_skrot(pobierz_skrot('wyczysc_wszystko'))), po_kliknieciu_wyczysc_tray),
        pystray.MenuItem(lambda text: tlumacz(KONTEKST_TRAY, "Ustawienia Wyglądu..."), po_kliknieciu_ustawienia_tray),
        pystray.MenuItem(lambda text: tlumacz(KONTEKST_TRAY, "Język / Language"), pystray.Menu(
            pystray.MenuItem(lambda text: tlumacz(KONTEKST_TRAY, "Polski"), po_kliknieciu_jezyk_pl_tray, checked=lambda item: instancja_aplikacji.biezacy_jezyk == 'pl' if instancja_aplikacji else True),
            pystray.MenuItem(lambda text: tlumacz(KONTEKST_TRAY, "English"), po_kliknieciu_jezyk_en_tray, checked=lambda item: instancja_aplikacji.biezacy_jezyk == 'en' if instancja_aplikacji else False),
        )),
        pystray.MenuItem(lambda text: tlumacz(KONTEKST_TRAY, "Wyjście ({})").format(formatuj_skrot(pobierz_skrot('wyjscie'))), po_kliknieciu_wyjscie_tray),
    )
    return menu

def aktualizuj_menu_zasobnika(ikona, widocznosc):
    try:
        ikona.menu = stworz_menu_zasobnika()
        ikona.update_menu()
    except Exception as e:
        print(f"Błąd aktualizacji menu tray: {e}")

def konfiguruj_ikone_zasobnika():
    global instancja_ikony_zasobnika
    obraz = pobierz_obraz_ikony()
    ikona = pystray.Icon("Gridlines", obraz, NAZWA_APLIKACJI, menu=stworz_menu_zasobnika())
    instancja_ikony_zasobnika = ikona
    signal_emitter.zadanie_aktualizacji_zasobnika.connect(lambda widocznosc: aktualizuj_menu_zasobnika(ikona, widocznosc))
    return ikona

# --- Obsługa skrótów (wywoływane z wątku keyboard, emitują sygnały do Qt) ---
def obsluz_widocznosc():
    signal_emitter.zadanie_przelaczenia_widocznosci.emit()
def obsluz_zmiane_pozycji():
    signal_emitter.zadanie_zmiany_pozycji_linijek.emit()
def obsluz_wyczysc_wszystko():
    signal_emitter.zadanie_wyczyszczenia_wszystkiego.emit()
def obsluz_wyjscie():
    signal_emitter.zadanie_wyjscia_z_aplikacji.emit()
def obsluz_zwieksz_grubosc():
    signal_emitter.zadanie_zwiekszenia_grubosci.emit()
def obsluz_zmniejsz_grubosc():
    signal_emitter.zadanie_zmniejszenia_grubosci.emit()
def obsluz_utworz_pozioma():
    signal_emitter.zadanie_utworzenia_linii.emit('h')
def obsluz_utworz_pionowa():
    signal_emitter.zadanie_utworzenia_linii.emit('v')
# USUNIĘTE: obsluz_tryb_wyboru - skrót Wybór usunięty

def obsluz_tryb_przesuwania():
    signal_emitter.zadanie_trybu_przesuwania.emit()
def obsluz_ustawienia():
    signal_emitter.zadanie_okna_ustawien.emit()
def obsluz_jezyk():
    # Toggle PL/EN, sygnał z pustym argumentem = toggle w slot_zmien_jezyk
    signal_emitter.zadanie_zmiany_jezyka.emit('')
def obsluz_wybor_bezposredni(nr, typ):
    signal_emitter.zadanie_wyboru_linii.emit(nr, typ)

def obsluz_usun_aktywna():
    # Shift+Del ZAWSZE - globalny, nie tylko w trybie przesuwania
    signal_emitter.zadanie_usuniecia_aktywnej.emit()
def przearejestruj_skroty():
    try:
        keyboard.unhook_all_hotkeys()
    except Exception:
        try:
            keyboard.clear_all_hotkeys()
        except Exception:
            pass
    konfiguruj_skroty_klawiszowe()
def konfiguruj_skroty_klawiszowe():
    print(f"Rejestrowanie skrótów globalnych (v{WERSJA}, baza Ctrl+Alt+Shift, bez Win, bez polskich C/L/O)...")
    try:
        if not hasattr(keyboard, 'add_hotkey'):
            raise ImportError("Brak keyboard.add_hotkey")
        keyboard.add_hotkey(pobierz_skrot('widocznosc'), obsluz_widocznosc, trigger_on_release=False)
        keyboard.add_hotkey(pobierz_skrot('pozycja_linijek'), obsluz_zmiane_pozycji, trigger_on_release=False)
        keyboard.add_hotkey(pobierz_skrot('wyczysc_wszystko'), obsluz_wyczysc_wszystko, trigger_on_release=False)
        keyboard.add_hotkey(pobierz_skrot('wyjscie'), obsluz_wyjscie, trigger_on_release=False)
        keyboard.add_hotkey(pobierz_skrot('zwieksz_grubosc'), obsluz_zwieksz_grubosc, trigger_on_release=False, suppress=False)
        keyboard.add_hotkey(pobierz_skrot('zmniejsz_grubosc'), obsluz_zmniejsz_grubosc, trigger_on_release=False, suppress=False)
        keyboard.add_hotkey(pobierz_skrot('utworz_pozioma'), obsluz_utworz_pozioma, trigger_on_release=False)
        keyboard.add_hotkey(pobierz_skrot('utworz_pionowa'), obsluz_utworz_pionowa, trigger_on_release=False)
        # USUNIĘTE: rejestracja Wybór (G) - skrót Wybór usunięty
        keyboard.add_hotkey(pobierz_skrot('tryb_przesuwania'), obsluz_tryb_przesuwania, trigger_on_release=False)
        keyboard.add_hotkey(pobierz_skrot('ustawienia'), obsluz_ustawienia, trigger_on_release=False)
        keyboard.add_hotkey(pobierz_skrot('jezyk'), obsluz_jezyk, trigger_on_release=False)
        # Shift+Del ZAWSZE kasuje aktywną linię (globalny). Uwaga: blokuje Shift+Del w Eksploratorze, gdy app działa.
        try:
            keyboard.add_hotkey(pobierz_skrot('usun_aktywna'), obsluz_usun_aktywna, trigger_on_release=False, suppress=True)
        except Exception as e:
            print(f"Nie udało się zarejestrować Shift+Del: {e}")
        # Bezpośredni wybór: Ctrl+Alt+Shift+1+X ... +0+Y (20 skrótów)
        # X = pozioma (H), Y = pionowa (V). 0 = linia nr 10.
        for nr in range(1, 11):
            klawisz_nr = numer_na_klawisz(nr)
            for litera, typ in [("x", 'h'), ("y", 'v')]:
                _base = pobierz_skrot('utworz_pozioma')
                _parts = _base.split("+")
                _base_mod = "+".join(_parts[:-1]) if len(_parts) > 1 else "ctrl+alt+shift"
                skrot = f"{_base_mod}+{klawisz_nr}+{litera}"
                try:
                    keyboard.add_hotkey(skrot, lambda n=nr, t=typ: obsluz_wybor_bezposredni(n, t), trigger_on_release=False)
                except Exception as e:
                    print(f"Nie udało się zarejestrować {skrot}: {e}")
        print("Skróty zarejestrowane:")
        print(f"  - Utwórz poziomą: {formatuj_skrot(pobierz_skrot('utworz_pozioma'))} (20px od góry)")
        print(f"  - Utwórz pionową: {formatuj_skrot(pobierz_skrot('utworz_pionowa'))} (20px od lewej)")
        print(f"  - Wybór bezpośrednio: Ctrl+Alt+Shift+1+X ... +0+Y (X=pozioma, Y=pionowa, 0=10) - skrót Wybór (G) usunięty")
        print(f"  - Tryb przesuwania: {formatuj_skrot(pobierz_skrot('tryb_przesuwania'))} | Strzałki=10px (szybko), Shift+Strzałka=1px (wolno), Esc=wyjście, bez czarnej ramki  |  Shift+Del=usuń aktywną (zawsze)")
        print(f"  - Widoczność: {formatuj_skrot(pobierz_skrot('widocznosc'))}")
        print(f"  - Pozycja linijek: {formatuj_skrot(pobierz_skrot('pozycja_linijek'))}")
        print(f"  - Wyczyść: {formatuj_skrot(pobierz_skrot('wyczysc_wszystko'))}")
        print(f"  - Usuń aktywną: Shift+Del (zawsze, nie tylko w trybie przesuwania)")
        print(f"  - Ustawienia: {formatuj_skrot(SKROT_USTAWIENIA)} | Język: {formatuj_skrot(SKROT_JEZYK)} | Wyjście: {formatuj_skrot(pobierz_skrot('wyjscie'))}")
        print(f"  - Grubość: {formatuj_skrot(SKROT_ZWIEKSZ_GRUBOSC)} / {formatuj_skrot(SKROT_ZMNIEJSZ_GRUBOSC)}")
        print("UWAGA: Baza Ctrl+Alt+Shift, bez Win. Bez polskich liter C/L/O (K/J/W zamiast), więc bez Ć/Ł/Ó. Shift+Del zawsze kasuje aktywną - blokuje Shift+Del w Eksploratorze, gdy app działa.")
        print("Strzałki działają TYLKO w trybie przesuwania, poza nim nie są blokowane.")
    except ImportError:
        print("BŁĄD: brak biblioteki 'keyboard'. Skróty wyłączone. pip install keyboard")
    except Exception as e:
        print(f"BŁĄD rejestracji skrótów: {e}")

# --- Główna funkcja ---
def main():
    print(f"Uruchamianie {NAZWA_APLIKACJI}...")
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    app.setApplicationName("Gridlines")
    app.setOrganizationName("Gridlines")
    app.setApplicationVersion(WERSJA)
    app.setQuitOnLastWindowClosed(False)
    global instancja_aplikacji
    instancja_aplikacji = AplikacjaLiniiPomocniczych()
    konfiguruj_skroty_klawiszowe()
    ikona = konfiguruj_ikone_zasobnika()
    instancja_aplikacji.uruchom()
    def run_icon():
        try:
            ikona.run()
        except Exception as e:
            print(f"Błąd tray: {e}")
    watek_ikony = threading.Thread(target=run_icon, name="PystrayThread", daemon=True)
    watek_ikony.start()
    print("Pętla Qt...")
    exit_code = app.exec()
    print(f"Koniec, kod: {exit_code}")
    if instancja_ikony_zasobnika and instancja_ikony_zasobnika.visible:
        try:
            instancja_ikony_zasobnika.stop()
        except:
            pass
    sys.exit(exit_code)

if __name__ == "__main__":
    main()

# --- KONIEC PLIKU Lines Desktop v0.3 ---
