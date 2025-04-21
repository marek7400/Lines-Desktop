# --- START OF FILE Lines Desktop.py ---

import sys
import os
import json
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QSizePolicy, QColorDialog,
                             QDialog, QSpinBox, QSlider, QPushButton, QVBoxLayout,
                             QFormLayout, QHBoxLayout, QStyle)
from PyQt6.QtGui import (QPainter, QColor, QPen, QCursor, QIcon, QPixmap, QCloseEvent,
                         QBrush, QPalette) # Added QPalette
from PyQt6.QtCore import (Qt, QPoint, QRect, QSize, QObject, pyqtSignal, QTimer,
                          QLocale, QEvent)
import pystray
from PIL import Image, ImageDraw
import keyboard # Keep keyboard import
import threading
import time
import math

# --- Stałe Konfiguracyjne ---
ROZMIAR_LINIJKI = 1
KOLOR_TLA_LINIJKI = QColor(238, 238, 238)
KOLOR_ZNACZNIKA_GLOWNEGO = QColor(0, 0, 0)
KOLOR_ZNACZNIKA_SREDNIEGO = QColor(102, 102, 102)
KOLOR_ZNACZNIKA_POMNIEJSZEGO = QColor(170, 170, 170)
KOLOR_RAMKI = QColor(204, 204, 204)
KOLOR_TLA_PODPOWIEDZI = QColor(0, 0, 0, 255)
KOLOR_TEKSTU_PODPOWIEDZI = QColor(255, 255, 255)
SZEROKOSC_UCHWYTU_SIATKI = 3840
PLIK_STANU = os.path.join(os.path.expanduser("~"), ".gridlines_app_state.json")
DOMYSLNA_GRUBOŚĆ_SIATKI = 1
DOMYSLNY_KOLOR_SIATKI = "#00FCEA"
DOMYSLNA_PRZEZROCZYSTOŚĆ_SIATKI = 200
DOMYSLNA_POZYCJA_LINIJEK = 'top-left'
POZYCJE_LINIJEK = ['top-left', 'top-right', 'bottom-right', 'bottom-left']
MAKS_GRUBOŚĆ_SIATKI = 3840
KROK_ZMIANY_GRUBOSCI = 1
DOMYSLNY_JEZYK = 'pl'

# --- Skróty Klawiaturowe ---
SKROT_WIDOCZNOSC = "alt+shift+home"
SKROT_POZYCJA_LINIJEK = "alt+shift+pageup"
SKROT_WYCZYSC_WSZYSTKO = "ctrl+alt+f9"
# WARNING: Ctrl+Alt+End is often intercepted by the OS (e.g., Windows Security Screen)
# and may not be reliably captured by the 'keyboard' library. Consider a different shortcut.
SKROT_WYJSCIE = "ctrl+alt+end"
SKROT_ZWIEKSZ_GRUBOSC = "ctrl+alt+pageup"
SKROT_ZMNIEJSZ_GRUBOSC = "ctrl+alt+pagedown"

# --- Zmienne globalne ---
instancja_aplikacji = None
instancja_ikony_zasobnika = None
id_glownego_watku = None

# --- Konteksty Tłumaczeń ---
KONTEKST_TRAY = "TrayMenu"
KONTEKST_SETTINGS = "SettingsDialog"
KONTEKST_GRIDLINE = "GridlineWidget"
KONTEKST_APP = "GridlinesApp"

# --- Słownik Tłumaczeń ---
SLOWNIK_TLUMACZEN = {
    'pl': {
        # TrayMenu
        f"{KONTEKST_TRAY}|Ukryj/Pokaż Linie ({{}})": "Ukryj/Pokaż Linie ({})",
        f"{KONTEKST_TRAY}|Zmień Pozycję ({{}})": "Zmień Pozycję ({})",
        f"{KONTEKST_TRAY}|Wyczyść Wszystko ({{}})": "Wyczyść Wszystko ({})",
        f"{KONTEKST_TRAY}|Ustawienia Wyglądu...": "Ustawienia Wyglądu...",
        f"{KONTEKST_TRAY}|Język / Language": "Język / Language",
        f"{KONTEKST_TRAY}|Polski": "Polski",
        f"{KONTEKST_TRAY}|English": "English",
        f"{KONTEKST_TRAY}|Wyjście ({{}})": "Wyjście ({})",
        f"{KONTEKST_TRAY}|Linie Pomocnicze": "Linie Pomocnicze",
        # SettingsDialog
        f"{KONTEKST_SETTINGS}|Ustawienia Linii Pomocniczych": "Ustawienia Linii Pomocniczych",
        f"{KONTEKST_SETTINGS}|Grubość:": "Grubość:",
        f"{KONTEKST_SETTINGS}| px": " px",
        f"{KONTEKST_SETTINGS}|Skróty: Zwiększ: {{}}, Zmniejsz: {{}}": "Skróty: Zwiększ: {}, Zmniejsz: {}",
        f"{KONTEKST_SETTINGS}|Kolor:": "Kolor:",
        f"{KONTEKST_SETTINGS}|Wybierz Kolor": "Wybierz Kolor",
        f"{KONTEKST_SETTINGS}|Wybierz Kolor Linii": "Wybierz Kolor Linii",
        f"{KONTEKST_SETTINGS}|Przezroczystość:": "Przezroczystość:",
        f"{KONTEKST_SETTINGS}|Zamknij": "Zamknij",
        # GridlineWidget
        f"{KONTEKST_GRIDLINE}|Y: {{pos}}px": "Y: {pos}px",
        f"{KONTEKST_GRIDLINE}|X: {{pos}}px": "X: {pos}px",
    },
    'en': {
        # TrayMenu
        f"{KONTEKST_TRAY}|Ukryj/Pokaż Linie ({{}})": "Hide/Show Lines ({})",
        f"{KONTEKST_TRAY}|Zmień Pozycję ({{}})": "Change Position ({})",
        f"{KONTEKST_TRAY}|Wyczyść Wszystko ({{}})": "Clear All ({})",
        f"{KONTEKST_TRAY}|Ustawienia Wyglądu...": "Appearance Settings...",
        f"{KONTEKST_TRAY}|Język / Language": "Language",
        f"{KONTEKST_TRAY}|Polski": "Polish",
        f"{KONTEKST_TRAY}|English": "English",
        f"{KONTEKST_TRAY}|Wyjście ({{}})": "Exit ({})",
        f"{KONTEKST_TRAY}|Linie Pomocnicze": "Guide Lines",
        # SettingsDialog
        f"{KONTEKST_SETTINGS}|Ustawienia Linii Pomocniczych": "Guide Lines Settings",
        f"{KONTEKST_SETTINGS}|Grubość:": "Thickness:",
        f"{KONTEKST_SETTINGS}| px": " px",
        f"{KONTEKST_SETTINGS}|Skróty: Zwiększ: {{}}, Zmniejsz: {{}}": "Shortcuts: Increase: {}, Decrease: {}",
        f"{KONTEKST_SETTINGS}|Kolor:": "Color:",
        f"{KONTEKST_SETTINGS}|Wybierz Kolor": "Select Color",
        f"{KONTEKST_SETTINGS}|Wybierz Kolor Linii": "Select Line Color",
        f"{KONTEKST_SETTINGS}|Przezroczystość:": "Transparency:",
        f"{KONTEKST_SETTINGS}|Zamknij": "Close",
        # GridlineWidget
        f"{KONTEKST_GRIDLINE}|Y: {{pos}}px": "Y: {pos}px",
        f"{KONTEKST_GRIDLINE}|X: {{pos}}px": "X: {pos}px",
    }
}

# --- Pomocnik tłumaczenia ---
def tłumacz(kontekst, tekst_zrodlowy):
    if instancja_aplikacji and hasattr(instancja_aplikacji, 'biezacy_jezyk'):
        biezacy_jezyk = instancja_aplikacji.biezacy_jezyk
    else:
        biezacy_jezyk = DOMYSLNY_JEZYK
    klucz = f"{kontekst}|{tekst_zrodlowy}"
    tlumaczenie = SLOWNIK_TLUMACZEN.get(biezacy_jezyk, {}).get(klucz, tekst_zrodlowy)
    return tlumaczenie

# --- Sygnały ---
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
signal_emitter = EmiterSygnalow()

# --- Klasa Bazowa dla Okien Nakładki ---
class OknoNakladki(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=None)
        self.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.hide()

# --- Klasa dla Linijek ---
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
            self.setFixedHeight(ROZMIAR_LINIJKI)
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        else:
            self.setCursor(Qt.CursorShape.SplitHCursor)
            self.setFixedWidth(ROZMIAR_LINIJKI)
            self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

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
        odstep_znacznika = 5
        prostokat_ekranu = QApplication.primaryScreen().geometry()
        przesuniecie_x = 0
        przesuniecie_y = 0
        pozycja_linijek = DOMYSLNA_POZYCJA_LINIJEK
        if instancja_aplikacji and hasattr(instancja_aplikacji, 'pozycja_linijek'):
            pozycja_linijek = instancja_aplikacji.pozycja_linijek
        if 'left' in pozycja_linijek:
            przesuniecie_x = ROZMIAR_LINIJKI
        if 'top' in pozycja_linijek:
            przesuniecie_y = ROZMIAR_LINIJKI
        if self.orientacja == Qt.Orientation.Horizontal:
            dlugosc = prostokat.width()
            start_abs_x = self.mapToGlobal(QPoint(0,0)).x()
            for x_abs in range(start_abs_x, start_abs_x + dlugosc + odstep_znacznika, odstep_znacznika):
                x_rel = x_abs - start_abs_x
                if x_rel < 0 or x_rel > dlugosc:
                     continue
                if x_abs == 0 and start_abs_x != 0: # Avoid drawing at 0 if ruler starts elsewhere
                    continue
                if x_abs % 50 == 0:
                    pioro.setColor(KOLOR_ZNACZNIKA_GLOWNEGO)
                    wysokosc_znacznika = 10
                elif x_abs % 10 == 0:
                    pioro.setColor(KOLOR_ZNACZNIKA_SREDNIEGO)
                    wysokosc_znacznika = 7
                else:
                    pioro.setColor(KOLOR_ZNACZNIKA_POMNIEJSZEGO)
                    wysokosc_znacznika = 4
                painter.setPen(pioro)
                painter.drawLine(x_rel, prostokat.height() - wysokosc_znacznika, x_rel, prostokat.height()-1)
        else:
            dlugosc = prostokat.height()
            start_abs_y = self.mapToGlobal(QPoint(0,0)).y()
            for y_abs in range(start_abs_y, start_abs_y + dlugosc + odstep_znacznika, odstep_znacznika):
                y_rel = y_abs - start_abs_y
                if y_rel < 0 or y_rel > dlugosc:
                    continue
                if y_abs == 0 and start_abs_y != 0: # Avoid drawing at 0 if ruler starts elsewhere
                     continue
                if y_abs % 50 == 0:
                    pioro.setColor(KOLOR_ZNACZNIKA_GLOWNEGO)
                    szerokosc_znacznika = 10
                elif y_abs % 10 == 0:
                    pioro.setColor(KOLOR_ZNACZNIKA_SREDNIEGO)
                    szerokosc_znacznika = 7
                else:
                    pioro.setColor(KOLOR_ZNACZNIKA_POMNIEJSZEGO)
                    szerokosc_znacznika = 4
                painter.setPen(pioro)
                painter.drawLine(prostokat.width() - szerokosc_znacznika, y_rel, prostokat.width()-1, y_rel)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pozycja_globalna = event.globalPosition().toPoint()
            typ_linii = 'h' if self.orientacja == Qt.Orientation.Horizontal else 'v'
            if instancja_aplikacji:
                 instancja_aplikacji.obsluz_klikniecie_linijki(typ_linii, pozycja_globalna)
            event.accept()
        else:
            event.ignore()


# --- Klasa dla pojedynczej linii siatki ---
class WidzetLiniiSiatki(OknoNakladki):
    def __init__(self, typ_orientacji, pozycja, id_siatki):
        super().__init__()
        self.typ = typ_orientacji
        self._pozycja = pozycja
        self.id = id_siatki
        self.czy_przeciagane = False
        self.przesuniecie_przeciagania = QPoint(0,0)
        self.podpowiedz = None
        self.setMouseTracking(True)
        if self.typ == 'h':
            self.setFixedHeight(SZEROKOSC_UCHWYTU_SIATKI)
            self.setCursor(Qt.CursorShape.SizeVerCursor)
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        else:
            self.setFixedWidth(SZEROKOSC_UCHWYTU_SIATKI)
            self.setCursor(Qt.CursorShape.SizeHorCursor)
            self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

    def _aktualizuj_geometrie(self):
        if not instancja_aplikacji: return
        prostokat_ekranu = QApplication.primaryScreen().geometry()
        pozycja_linijek = instancja_aplikacji.pozycja_linijek
        widok_x = ROZMIAR_LINIJKI if 'left' in pozycja_linijek else 0
        widok_y = ROZMIAR_LINIJKI if 'top' in pozycja_linijek else 0
        szerokosc_widoku = prostokat_ekranu.width() \
                           - (ROZMIAR_LINIJKI if 'left' in pozycja_linijek else 0) \
                           - (ROZMIAR_LINIJKI if 'right' in pozycja_linijek else 0)
        wysokosc_widoku = prostokat_ekranu.height() \
                           - (ROZMIAR_LINIJKI if 'top' in pozycja_linijek else 0) \
                           - (ROZMIAR_LINIJKI if 'bottom' in pozycja_linijek else 0)
        szerokosc_widoku = max(0, szerokosc_widoku)
        wysokosc_widoku = max(0, wysokosc_widoku)
        if self.typ == 'h':
            # Center the *grab handle* widget around the *logical* line position
            widzet_y = self._pozycja - SZEROKOSC_UCHWYTU_SIATKI // 2
            self.setGeometry(widok_x, widzet_y, szerokosc_widoku, SZEROKOSC_UCHWYTU_SIATKI)
        else:
            # Center the *grab handle* widget around the *logical* line position
            widzet_x = self._pozycja - SZEROKOSC_UCHWYTU_SIATKI // 2
            self.setGeometry(widzet_x, widok_y, SZEROKOSC_UCHWYTU_SIATKI, wysokosc_widoku)

    def pobierz_pozycje(self):
        return self._pozycja
    def ustaw_pozycje(self, poz):
        if self._pozycja != poz:
            self._pozycja = poz
            self._aktualizuj_geometrie()
            self.update() # Redraw the line in the new position

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        if not instancja_aplikacji: return

        kolor = instancja_aplikacji.kolor_linii_siatki
        grubosc = instancja_aplikacji.grubosc_linii_siatki
        prostokat = self.rect() # The rectangle of the *grab handle* widget

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(kolor, Qt.BrushStyle.SolidPattern))

        # Draw the actual line *centered* within the grab handle area
        if self.typ == 'h':
            srodek_y = prostokat.height() // 2
            # Calculate top-left corner for the rectangle representing the line
            rysowany_y = srodek_y - math.ceil(grubosc / 2.0)
            painter.drawRect(0, int(rysowany_y), prostokat.width(), int(grubosc))
        else:
            srodek_x = prostokat.width() // 2
            # Calculate top-left corner for the rectangle representing the line
            rysowany_x = srodek_x - math.ceil(grubosc / 2.0)
            painter.drawRect(int(rysowany_x), 0, int(grubosc), prostokat.height())

    def pobierz_wyswietlana_pozycje(self):
        # This returns the logical position (the line's coordinate)
        return self._pozycja

    def mousePressEvent(self, event):
        if not instancja_aplikacji: return
        if event.button() == Qt.MouseButton.LeftButton:
            self.czy_przeciagane = True
            # Store the offset *within* the grab handle widget where the click occurred
            self.przesuniecie_przeciagania = event.position().toPoint()
            self.grabMouse()
            self.stworz_podpowiedz()
            self.aktualizuj_podpowiedz(event.globalPosition().toPoint())
            event.accept()
        else:
            event.ignore()

    def mouseMoveEvent(self, event):
        if not instancja_aplikacji: return
        if self.czy_przeciagane:
            biezaca_poz_globalna = event.globalPosition().toPoint()
            prostokat_ekranu = QApplication.primaryScreen().geometry()

            # Calculate screen boundaries for the line position, accounting for rulers
            min_poz_x = ROZMIAR_LINIJKI if 'left' in instancja_aplikacji.pozycja_linijek else 0
            min_poz_y = ROZMIAR_LINIJKI if 'top' in instancja_aplikacji.pozycja_linijek else 0
            maks_poz_x = prostokat_ekranu.width() - (ROZMIAR_LINIJKI if 'right' in instancja_aplikacji.pozycja_linijek else 0)
            maks_poz_y = prostokat_ekranu.height() - (ROZMIAR_LINIJKI if 'bottom' in instancja_aplikacji.pozycja_linijek else 0)

            if self.typ == 'h':
                # Calculate the desired global Y position of the *top* of the widget
                nowy_widzet_y = biezaca_poz_globalna.y() - self.przesuniecie_przeciagania.y()
                # Calculate the corresponding *logical* Y position of the line (center of the handle)
                nowa_poz_abs = nowy_widzet_y + SZEROKOSC_UCHWYTU_SIATKI // 2
                # Clamp the logical position within the valid screen area
                nowa_poz_abs = max(min_poz_y, nowa_poz_abs)
                nowa_poz_abs = min(nowa_poz_abs, maks_poz_y)
            else: # self.typ == 'v'
                # Calculate the desired global X position of the *left* of the widget
                nowy_widzet_x = biezaca_poz_globalna.x() - self.przesuniecie_przeciagania.x()
                # Calculate the corresponding *logical* X position of the line (center of the handle)
                nowa_poz_abs = nowy_widzet_x + SZEROKOSC_UCHWYTU_SIATKI // 2
                # Clamp the logical position within the valid screen area
                nowa_poz_abs = max(min_poz_x, nowa_poz_abs)
                nowa_poz_abs = min(nowa_poz_abs, maks_poz_x)

            # Update the logical position, which triggers geometry update and redraw
            self.ustaw_pozycje(nowa_poz_abs)
            self.aktualizuj_podpowiedz(biezaca_poz_globalna)
            event.accept()
        else:
            event.ignore()

    def mouseReleaseEvent(self, event):
        if not instancja_aplikacji: return
        if event.button() == Qt.MouseButton.LeftButton and self.czy_przeciagane:
            self.czy_przeciagane = False
            self.releaseMouse()
            self.zniszcz_podpowiedz()
            # Update the central data store with the final position
            instancja_aplikacji.aktualizuj_pozycje_linii_siatki(self.id, self._pozycja)
            event.accept()
        else:
            event.ignore()

    def mouseDoubleClickEvent(self, event):
        if not instancja_aplikacji: return
        if event.button() == Qt.MouseButton.LeftButton:
            instancja_aplikacji.usun_widzet_linii_siatki(self)
            event.accept()
        else:
            event.ignore()

    def enterEvent(self, event):
        # Could potentially show tooltip on hover here if not dragging
        pass
    def leaveEvent(self, event):
        if not self.czy_przeciagane:
            # Hide tooltip if mouse leaves and we are not dragging
            self.zniszcz_podpowiedz()

    def stworz_podpowiedz(self):
        if self.podpowiedz is None:
            self.podpowiedz = QLabel(parent=None) # Create tooltip as a top-level window
            # Flags to make it appear like a tooltip (borderless, stays on top)
            self.podpowiedz.setWindowFlags(Qt.WindowType.SplashScreen | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
            # Styling for the tooltip
            self.podpowiedz.setStyleSheet(f"""
                background-color: rgba({KOLOR_TLA_PODPOWIEDZI.red()},
                                       {KOLOR_TLA_PODPOWIEDZI.green()},
                                       {KOLOR_TLA_PODPOWIEDZI.blue()},
                                       {KOLOR_TLA_PODPOWIEDZI.alphaF()});
                color: rgb({KOLOR_TEKSTU_PODPOWIEDZI.red()},
                           {KOLOR_TEKSTU_PODPOWIEDZI.green()},
                           {KOLOR_TEKSTU_PODPOWIEDZI.blue()});
                padding: 6px 10px;
                border-radius: 4px;
                font-size: 14px;
            """)
            # Prevent the tooltip from stealing focus or interfering with mouse events
            self.podpowiedz.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
            self.podpowiedz.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def aktualizuj_podpowiedz(self, pozycja_globalna_myszy):
        # Only show/update if dragging and tooltip exists
        if not self.podpowiedz or not self.czy_przeciagane:
             self.zniszcz_podpowiedz() # Ensure it's hidden if conditions aren't met
             return

        prostokat_ekranu = QApplication.primaryScreen().geometry()
        wyswietlana_pozycja = self.pobierz_wyswietlana_pozycje() # Get the logical line position
        tekst_zrodlowy = "Y: {pos}px" if self.typ == 'h' else "X: {pos}px"
        tekst = tłumacz(KONTEKST_GRIDLINE, tekst_zrodlowy).format(pos=wyswietlana_pozycja)
        self.podpowiedz.setText(tekst)
        self.podpowiedz.adjustSize() # Resize label to fit text

        # Position tooltip near the cursor, avoiding screen edges
        podpowiedz_x = pozycja_globalna_myszy.x() + 15
        podpowiedz_y = pozycja_globalna_myszy.y() + 15

        # Adjust if tooltip goes off-screen right
        if podpowiedz_x + self.podpowiedz.width() > prostokat_ekranu.right():
            podpowiedz_x = pozycja_globalna_myszy.x() - self.podpowiedz.width() - 15
        # Adjust if tooltip goes off-screen bottom
        if podpowiedz_y + self.podpowiedz.height() > prostokat_ekranu.bottom():
            podpowiedz_y = pozycja_globalna_myszy.y() - self.podpowiedz.height() - 15
        # Adjust if tooltip goes off-screen left (less common)
        if podpowiedz_x < prostokat_ekranu.left():
            podpowiedz_x = prostokat_ekranu.left() + 5
        # Adjust if tooltip goes off-screen top (less common)
        if podpowiedz_y < prostokat_ekranu.top():
            podpowiedz_y = prostokat_ekranu.top() + 5


        self.podpowiedz.move(podpowiedz_x, podpowiedz_y)

        # Show the tooltip if it's not already visible
        if not self.podpowiedz.isVisible():
            self.podpowiedz.show()

    def zniszcz_podpowiedz(self):
        if self.podpowiedz:
            self.podpowiedz.hide()
            self.podpowiedz.deleteLater() # Schedule for deletion
            self.podpowiedz = None

# --- Klasa Narożnika ---
class Naroznik(OknoNakladki):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), KOLOR_TLA_LINIJKI)
        self.setPalette(p)
        self.setFixedSize(ROZMIAR_LINIJKI, ROZMIAR_LINIJKI)

        # Add a simple QLabel for the border lines
        ramka_naroznika = QLabel(self)
        ramka_naroznika.setStyleSheet(f"""
            QLabel {{
                border-right: 1px solid {KOLOR_RAMKI.name()};
                border-bottom: 1px solid {KOLOR_RAMKI.name()};
            }}
        """)
        ramka_naroznika.setGeometry(0, 0, ROZMIAR_LINIJKI, ROZMIAR_LINIJKI)
        ramka_naroznika.lower() # Ensure it's drawn behind any potential future content


# --- Dialog Ustawień ---
class DialogUstawien(QDialog):
    def __init__(self, app_ref, parent=None):
        super().__init__(parent)
        self.aplikacja = app_ref
        # Store the base color (RGB) separately from alpha
        self.wybrany_kolor_bazowy = QColor(DOMYSLNY_KOLOR_SIATKI) # Initialize with default

        # --- Widgets ---
        self.pole_grubosci = QSpinBox()
        self.pole_grubosci.setRange(1, MAKS_GRUBOŚĆ_SIATKI)
        self.pole_grubosci.setKeyboardTracking(False) # Emit signal only on Enter or focus loss

        self.etykieta_skrotow_grubosci = QLabel()
        self.etykieta_skrotow_grubosci.setStyleSheet("font-size: 10px; color: gray;")

        self.przycisk_koloru = QPushButton() # Text set via retranslateUi
        self.podglad_koloru = QLabel()
        self.podglad_koloru.setFixedSize(20, 20)
        # Set initial border, background will be updated dynamically
        self.podglad_koloru.setStyleSheet("border: 1px solid grey; background-color: transparent;")

        uklad_koloru = QHBoxLayout()
        uklad_koloru.addWidget(self.przycisk_koloru)
        uklad_koloru.addWidget(self.podglad_koloru)
        uklad_koloru.addStretch()

        self.suwak_przezroczystosci = QSlider(Qt.Orientation.Horizontal)
        self.suwak_przezroczystosci.setRange(0, 255) # Alpha range
        self.etykieta_przezroczystosci = QLabel() # Text updated dynamically

        self.przycisk_zamknij = QPushButton() # Text/Icon set via retranslateUi

        # Labels for form rows (text set via retranslateUi)
        self.label_grubosc = QLabel()
        self.label_kolor = QLabel()
        self.label_przezroczystosc = QLabel()

        # --- Layout ---
        uklad_formularza = QFormLayout()
        uklad_formularza.addRow(self.label_grubosc, self.pole_grubosci)
        uklad_formularza.addRow("", self.etykieta_skrotow_grubosci) # Shortcut hint below thickness
        uklad_formularza.addRow(self.label_kolor, uklad_koloru)
        uklad_formularza.addRow(self.label_przezroczystosc, self.suwak_przezroczystosci)
        uklad_formularza.addRow("", self.etykieta_przezroczystosci) # Alpha value display below slider

        uklad_przyciskow = QHBoxLayout()
        uklad_przyciskow.addStretch()
        uklad_przyciskow.addWidget(self.przycisk_zamknij)

        uklad_glowny = QVBoxLayout(self)
        uklad_glowny.addLayout(uklad_formularza)
        uklad_glowny.addLayout(uklad_przyciskow)

        # --- Connections ---
        self.pole_grubosci.valueChanged.connect(self.zmieniono_grubosc)
        self.przycisk_koloru.clicked.connect(self.wybierz_kolor)
        self.suwak_przezroczystosci.valueChanged.connect(self.zmieniono_przezroczystosc)
        self.przycisk_zamknij.clicked.connect(self.accept) # Standard QDialog close

        # --- Initialization ---
        self.retranslateUi() # Set initial language-dependent texts
        # Actual settings are loaded just before showing the dialog via wczytaj_poczatkowe_ustawienia

    def wczytaj_poczatkowe_ustawienia(self):
        """Loads current settings from the main application into the dialog controls."""
        # print("[DEBUG] DialogUstawien.wczytaj_poczatkowe_ustawienia() - START") # DEBUG
        # Block signals during programmatic value changes to prevent loops/extra updates
        self.pole_grubosci.blockSignals(True)
        self.suwak_przezroczystosci.blockSignals(True)

        # Load thickness
        self.pole_grubosci.setValue(self.aplikacja.grubosc_linii_siatki)
        # print(f"[DEBUG] Wczytano grubość: {self.aplikacja.grubosc_linii_siatki}") # DEBUG

        # Load color and transparency
        aktualny_kolor_aplikacji = QColor(self.aplikacja.kolor_linii_siatki)
        # print(f"[DEBUG] Odczytano kolor z aplikacji: {aktualny_kolor_aplikacji.name(QColor.NameFormat.HexArgb)}") # DEBUG

        # Store the base RGB color separately
        self.wybrany_kolor_bazowy = QColor(aktualny_kolor_aplikacji.red(),
                                         aktualny_kolor_aplikacji.green(),
                                         aktualny_kolor_aplikacji.blue())
        # print(f"[DEBUG] Ustawiono bazowy kolor (RGB) na: {self.wybrany_kolor_bazowy.name(QColor.NameFormat.HexRgb)}") # DEBUG

        # Load alpha/transparency
        alfa = aktualny_kolor_aplikacji.alpha()
        self.suwak_przezroczystosci.setValue(alfa)
        self.aktualizuj_etykiete_przezroczystosci(alfa) # Update the "XXX / 255" label
        # print(f"[DEBUG] Wczytano przezroczystość (alfa): {alfa}") # DEBUG

        # Update the visual color preview swatch using the base (opaque) color
        self.aktualizuj_podglad_koloru()

        # Re-enable signals
        self.pole_grubosci.blockSignals(False)
        self.suwak_przezroczystosci.blockSignals(False)
        # print("[DEBUG] DialogUstawien.wczytaj_poczatkowe_ustawienia() - KONIEC") # DEBUG

    def aktualizuj_podglad_koloru(self):
        """Updates the color preview swatch based on self.wybrany_kolor_bazowy."""
        # Use the stored base color (which should be opaque) for the preview
        kolor_podgladu = QColor(self.wybrany_kolor_bazowy)
        # print(f"[DEBUG] aktualizuj_podglad_koloru() z kolorem: {kolor_podgladu.name(QColor.NameFormat.HexRgb)}") # DEBUG

        # Set the background color using stylesheet for reliability
        self.podglad_koloru.setStyleSheet(
            f"border: 1px solid grey; background-color: {kolor_podgladu.name(QColor.NameFormat.HexRgb)};"
        )
        # Force an immediate repaint to ensure the change is visible
        # self.podglad_koloru.update() # May not be immediate enough
        self.podglad_koloru.repaint() # Forces synchronous repaint
        # print("[DEBUG] Ustawiono stylesheet podglądu koloru i wymuszono repaint.") # DEBUG

    def aktualizuj_etykiete_przezroczystosci(self, wartosc):
        """Updates the label showing the current alpha value."""
        self.etykieta_przezroczystosci.setText(f"{wartosc} / 255")

    def zmieniono_grubosc(self, wartosc):
        """Slot called when the thickness spinbox value changes."""
        self.aplikacja.zmien_grubosc(wartosc)

    def wybierz_kolor(self):
        """Opens the color chooser dialog and updates the application and preview."""
        # Start the dialog with the current *base* (opaque) color selected
        kolor_poczatkowy_dla_dialogu = QColor(self.wybrany_kolor_bazowy)

        # Open the color dialog
        nowy_wybrany_kolor_rgb = QColorDialog.getColor(
            kolor_poczatkowy_dla_dialogu,
            self, # Parent
            tłumacz(KONTEKST_SETTINGS, "Wybierz Kolor Linii") # Title
            # Options can be added here, e.g., QColorDialog.ColorDialogOption.ShowAlphaChannel
            # but we manage alpha separately with the slider, so we don't show it here.
        )

        # Check if the user selected a valid color (didn't cancel)
        if nowy_wybrany_kolor_rgb.isValid():
            # Store the newly selected base (RGB) color
            self.wybrany_kolor_bazowy = QColor(nowy_wybrany_kolor_rgb)

            # Get the current alpha value from the slider
            biezaca_alfa = self.suwak_przezroczystosci.value()

            # Create the final color (RGB + Alpha) to send to the application
            kolor_do_aplikacji = QColor(self.wybrany_kolor_bazowy)
            kolor_do_aplikacji.setAlpha(biezaca_alfa)

            # Update the color setting in the main application
            self.aplikacja.zmien_kolor(kolor_do_aplikacji)

            # Update the visual color preview in this dialog
            self.aktualizuj_podglad_koloru()

    def zmieniono_przezroczystosc(self, wartosc):
        """Slot called when the transparency slider value changes."""
        self.aktualizuj_etykiete_przezroczystosci(wartosc)
        # Update the alpha value in the main application
        # (The app's zmien_przezroczystosc method should combine the base color + new alpha)
        self.aplikacja.zmien_przezroczystosc(wartosc)

    def closeEvent(self, event: QCloseEvent):
        """Handles the dialog being closed (e.g., by window manager 'X' button)."""
        # print("[DEBUG] DialogUstawien closeEvent received.")
        event.accept() # Allow the dialog to close

    def changeEvent(self, event: QEvent):
        """Handles events like language changes."""
        if event.type() == QEvent.Type.LanguageChange:
            # print("[DEBUG] DialogUstawien LanguageChange event received.")
            self.retranslateUi() # Update all translatable texts
        super().changeEvent(event) # Call base class implementation

    def retranslateUi(self):
        """Updates all user-visible text elements according to the current language."""
        # print(f"[DEBUG] DialogUstawien retranslateUi() called for language: {self.aplikacja.biezacy_jezyk}")
        self.setWindowTitle(tłumacz(KONTEKST_SETTINGS, "Ustawienia Linii Pomocniczych"))
        self.label_grubosc.setText(tłumacz(KONTEKST_SETTINGS, "Grubość:"))
        self.label_kolor.setText(tłumacz(KONTEKST_SETTINGS, "Kolor:"))
        self.label_przezroczystosc.setText(tłumacz(KONTEKST_SETTINGS, "Przezroczystość:"))
        self.pole_grubosci.setSuffix(tłumacz(KONTEKST_SETTINGS, " px"))

        # Format keyboard shortcuts for display
        skrot_plus = formatuj_skrot_klawiszowy(SKROT_ZWIEKSZ_GRUBOSC)
        skrot_minus = formatuj_skrot_klawiszowy(SKROT_ZMNIEJSZ_GRUBOSC)
        self.etykieta_skrotow_grubosci.setText(
            tłumacz(KONTEKST_SETTINGS, "Skróty: Zwiększ: {}, Zmniejsz: {}").format(skrot_plus, skrot_minus)
        )

        self.przycisk_koloru.setText(tłumacz(KONTEKST_SETTINGS, "Wybierz Kolor"))
        self.przycisk_zamknij.setText(tłumacz(KONTEKST_SETTINGS, "Zamknij"))
        # Set a standard icon for the close button
        self.przycisk_zamknij.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogCloseButton))

        # Update the transparency label text as well, as it contains numbers but could potentially
        # have its format changed in different languages in the future.
        if hasattr(self, 'suwak_przezroczystosci'): # Check if slider exists
             self.aktualizuj_etykiete_przezroczystosci(self.suwak_przezroczystosci.value())
        # print("[DEBUG] DialogUstawien retranslateUi() completed.")


# --- Główna klasa aplikacji ---
class AplikacjaLiniiPomocniczych(QObject):
    def __init__(self):
        super().__init__()
        self.qt_app = QApplication.instance()
        if not self.qt_app:
            self.qt_app = QApplication(sys.argv)
        # Don't quit when overlay windows are closed, only on explicit exit or tray quit
        self.qt_app.setQuitOnLastWindowClosed(False)

        global id_glownego_watku
        id_glownego_watku = threading.current_thread().ident

        # --- State Variables ---
        self.linijki_widoczne = False
        self.dane_linii_siatki = [] # List of dicts: {'type': 'h'/'v', 'pos': int, 'id': int}
        self.nastepny_id_siatki = 0
        self.okna_nakladki = {"top": None, "left": None, "corner": None} # Ruler widgets
        self.aktywne_linie_siatki = {} # dict mapping id -> WidzetLiniiSiatki instance
        self.przeciaganie_nowej_linii = False # Flag indicating if dragging a *new* line from a ruler
        self.typ_nowej_linii = None # 'h' or 'v' for the line being dragged
        self.widzet_nowej_linii = None # Temporary widget for the line being dragged
        self.przesuniecie_nowej_linii = QPoint(0,0) # Mouse offset during new line drag
        self.biezacy_jezyk = DOMYSLNY_JEZYK
        self.pozycja_linijek = DOMYSLNA_POZYCJA_LINIJEK
        self.grubosc_linii_siatki = DOMYSLNA_GRUBOŚĆ_SIATKI
        # Initialize color with default and alpha
        self.kolor_linii_siatki = QColor(DOMYSLNY_KOLOR_SIATKI)
        self.kolor_linii_siatki.setAlpha(DOMYSLNA_PRZEZROCZYSTOŚĆ_SIATKI)
        self.dialog_ustawien = None # Settings dialog instance

        global instancja_aplikacji
        instancja_aplikacji = self # Make self globally accessible (used by some widgets/callbacks)

        self.wczytaj_stan() # Load previous state from file

        # --- Signal Connections ---
        signal_emitter.zadanie_przelaczenia_widocznosci.connect(self.przelacz_widocznosc)
        signal_emitter.zadanie_wyczyszczenia_wszystkiego.connect(self.wyczysc_wszystkie_linie)
        signal_emitter.zadanie_wyjscia_z_aplikacji.connect(self.zamknij_aplikacje)
        signal_emitter.zadanie_zmiany_pozycji_linijek.connect(self.zmien_pozycje_linijek_cyklicznie)
        signal_emitter.zadanie_okna_ustawien.connect(self.pokaz_dialog_ustawien)
        signal_emitter.zadanie_zwiekszenia_grubosci.connect(self.slot_zwieksz_grubosc)
        signal_emitter.zadanie_zmniejszenia_grubosci.connect(self.slot_zmniejsz_grubosc)
        signal_emitter.zadanie_zmiany_jezyka.connect(self.slot_zmien_jezyk)

        # --- UI Setup ---
        self.konfiguruj_ui() # Create ruler widgets
        self._synchronizuj_widzety_linii_siatki() # Create gridline widgets based on loaded state
        self._aktualizuj_geometrie_nakladki() # Position all overlay widgets


    def konfiguruj_ui(self):
        """Creates the ruler and corner overlay widgets if they don't exist."""
        if not self.okna_nakladki.get("top"):
            self.okna_nakladki["top"] = WidzetLinijki(Qt.Orientation.Horizontal)
            self.okna_nakladki["top"].sygnal_klikniecia.connect(self.obsluz_klikniecie_linijki)
        if not self.okna_nakladki.get("left"):
            self.okna_nakladki["left"] = WidzetLinijki(Qt.Orientation.Vertical)
            self.okna_nakladki["left"].sygnal_klikniecia.connect(self.obsluz_klikniecie_linijki)
        if not self.okna_nakladki.get("corner"):
            self.okna_nakladki["corner"] = Naroznik()

    def _synchronizuj_widzety_linii_siatki(self):
        """Ensures active gridline widgets match the data in self.dane_linii_siatki."""
        biezace_id_widzetow = set(self.aktywne_linie_siatki.keys())
        wczytane_id_danych = set(item['id'] for item in self.dane_linii_siatki)

        # Create widgets for data items that don't have one
        for dane in self.dane_linii_siatki:
            if dane['id'] not in biezace_id_widzetow:
                self.stworz_widzet_linii_siatki(dane['type'], dane['pos'], dane['id'], update_geom=False) # Geometry updated later

        # Remove widgets that no longer have corresponding data
        id_do_usunięcia = biezace_id_widzetow - wczytane_id_danych
        if id_do_usunięcia:
            # print(f"[DEBUG] Synchronizing: Removing widgets with IDs: {id_do_usunięcia}")
            for id_siatki in list(id_do_usunięcia): # Iterate over a copy
                 self.usun_widzet_linii_siatki_po_id(id_siatki)

        # Update the next available ID based on loaded data
        maks_id = max((item['id'] for item in self.dane_linii_siatki), default=-1)
        self.nastepny_id_siatki = max(self.nastepny_id_siatki, maks_id + 1, 0)
        # print(f"[DEBUG] Synchronization complete. Next gridline ID: {self.nastepny_id_siatki}")

    def _aktualizuj_geometrie_nakladki(self):
        """Positions the rulers, corner, and all active gridlines based on screen size and ruler position setting."""
        prostokat_ekranu = QApplication.primaryScreen().geometry()
        szer_ekr, wys_ekr = prostokat_ekranu.width(), prostokat_ekranu.height()
        rozm_lin = ROZMIAR_LINIJKI

        # Ensure widgets exist
        if not all(self.okna_nakladki.values()):
            self.konfiguruj_ui()
            if not all(self.okna_nakladki.values()):
                print("Error: Failed to create overlay widgets.")
                return # Cannot proceed without widgets

        linijka_gorna = self.okna_nakladki["top"]
        linijka_lewa = self.okna_nakladki["left"]
        naroznik = self.okna_nakladki["corner"]

        # Default geometry (top-left without margins)
        gora_x, gora_y, lewa_x, lewa_y, naroznik_x, naroznik_y = 0, 0, 0, 0, 0, 0
        gora_szer, gora_wys = szer_ekr, rozm_lin
        lewa_szer, lewa_wys = rozm_lin, wys_ekr

        # Adjust geometry based on the selected corner position
        if self.pozycja_linijek == 'top-left':
            gora_x, gora_y = rozm_lin, 0          # Top ruler starts right of corner
            lewa_x, lewa_y = 0, rozm_lin          # Left ruler starts below corner
            naroznik_x, naroznik_y = 0, 0          # Corner at top-left
            gora_szer -= rozm_lin                  # Adjust width/height for corner
            lewa_wys -= rozm_lin
        elif self.pozycja_linijek == 'top-right':
            gora_x, gora_y = 0, 0                  # Top ruler starts at left edge
            lewa_x, lewa_y = szer_ekr - rozm_lin, rozm_lin # Left ruler at right edge, below corner
            naroznik_x, naroznik_y = szer_ekr - rozm_lin, 0 # Corner at top-right
            gora_szer -= rozm_lin
            lewa_wys -= rozm_lin
        elif self.pozycja_linijek == 'bottom-right':
            gora_x, gora_y = 0, wys_ekr - rozm_lin # Top ruler at bottom edge
            lewa_x, lewa_y = szer_ekr - rozm_lin, 0 # Left ruler at right edge
            naroznik_x, naroznik_y = szer_ekr - rozm_lin, wys_ekr - rozm_lin # Corner at bottom-right
            gora_szer -= rozm_lin
            lewa_wys -= rozm_lin
        elif self.pozycja_linijek == 'bottom-left':
            gora_x, gora_y = rozm_lin, wys_ekr - rozm_lin # Top ruler at bottom edge, right of corner
            lewa_x, lewa_y = 0, 0                  # Left ruler at left edge
            naroznik_x, naroznik_y = 0, wys_ekr - rozm_lin # Corner at bottom-left
            gora_szer -= rozm_lin
            lewa_wys -= rozm_lin

        # Ensure non-negative dimensions
        gora_szer = max(0, gora_szer)
        lewa_wys = max(0, lewa_wys)

        # Apply geometries
        # Use move() and resize() for potentially better performance than setGeometry()
        linijka_gorna.move(gora_x, gora_y)
        linijka_gorna.resize(gora_szer, gora_wys)
        linijka_lewa.move(lewa_x, lewa_y)
        linijka_lewa.resize(lewa_szer, lewa_wys)
        naroznik.move(naroznik_x, naroznik_y)
        naroznik.resize(rozm_lin, rozm_lin) # Size is fixed

        # Update geometry for all existing gridlines
        for widzet_linii in self.aktywne_linie_siatki.values():
            widzet_linii._aktualizuj_geometrie() # Let each line reposition itself

    def obsluz_klikniecie_linijki(self, typ_linii, pozycja_globalna):
        """Handles a left-click on a ruler to start dragging a new line."""
        # Ensure this runs on the main GUI thread
        if threading.current_thread().ident != id_glownego_watku:
            # QTimer.singleShot(0, lambda: self.obsluz_klikniecie_linijki(typ_linii, pozycja_globalna)) # Reschedule if needed
            return # Or simply ignore clicks from other threads

        if self.przeciaganie_nowej_linii:
            # print("[DEBUG] Ignoring ruler click while already dragging a new line.")
            return # Don't start a new drag if one is already in progress

        # print(f"[DEBUG] Ruler clicked. Type: {typ_linii}, Pos: {pozycja_globalna}")
        self.rozpocznij_przeciaganie_nowej_linii(typ_linii, pozycja_globalna)

    def _pokaz_wszystkie_nakladki(self):
        """Makes all ruler, corner, and gridline widgets visible."""
        wszystkie_widzety = list(self.okna_nakladki.values()) + list(self.aktywne_linie_siatki.values())
        for widzet in wszystkie_widzety:
            if widzet:
                # Ensure flags are set correctly (might be needed if hidden previously)
                widzet.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
                widzet.show()
                widzet.raise_() # Bring to front

    def _ukryj_wszystkie_nakladki(self):
        """Hides all ruler, corner, and gridline widgets."""
        wszystkie_widzety = list(self.okna_nakladki.values()) + list(self.aktywne_linie_siatki.values())
        for widzet in wszystkie_widzety:
            if widzet:
                widzet.hide()
        # Also hide the settings dialog if it's open when hiding lines
        if self.dialog_ustawien and self.dialog_ustawien.isVisible():
            self.dialog_ustawien.hide()

    def pokaz_linijki(self):
        """Shows the rulers and gridlines."""
        # Ensure this runs on the main GUI thread
        if threading.current_thread().ident != id_glownego_watku:
            QTimer.singleShot(0, self.pokaz_linijki)
            return

        # print("[DEBUG] Showing overlays...")
        self.linijki_widoczne = True
        self._aktualizuj_geometrie_nakladki() # Ensure positions are correct before showing
        self._pokaz_wszystkie_nakladki()
        self.zapisz_stan() # Save visibility state
        signal_emitter.zadanie_aktualizacji_zasobnika.emit(self.linijki_widoczne) # Update tray menu check state

    def ukryj_linijki(self):
        """Hides the rulers and gridlines."""
         # Ensure this runs on the main GUI thread
        if threading.current_thread().ident != id_glownego_watku:
            QTimer.singleShot(0, self.ukryj_linijki)
            return

        if self.przeciaganie_nowej_linii:
            # print("[DEBUG] Hiding overlays - Cancelling active new line drag.")
            self.anuluj_przeciaganie_nowej_linii() # Cancel drag if active

        # print("[DEBUG] Hiding overlays...")
        self.linijki_widoczne = False
        self._ukryj_wszystkie_nakladki()
        self.zapisz_stan() # Save visibility state
        signal_emitter.zadanie_aktualizacji_zasobnika.emit(self.linijki_widoczne) # Update tray menu check state

    def przelacz_widocznosc(self):
        """Toggles the visibility of the rulers and gridlines."""
        # Ensure this runs on the main GUI thread
        if threading.current_thread().ident != id_glownego_watku:
            QTimer.singleShot(0, self.przelacz_widocznosc)
            return

        # print(f"[DEBUG] Toggling visibility. Current state: {'Visible' if self.linijki_widoczne else 'Hidden'}")
        if self.linijki_widoczne:
            self.ukryj_linijki()
        else:
            self.pokaz_linijki()

    def zmien_pozycje_linijek_cyklicznie(self):
        """Cycles through the available ruler positions (top-left, top-right, etc.)."""
        # Ensure this runs on the main GUI thread
        if threading.current_thread().ident != id_glownego_watku:
            QTimer.singleShot(0, self.zmien_pozycje_linijek_cyklicznie)
            return

        try:
            biezacy_indeks = POZYCJE_LINIJEK.index(self.pozycja_linijek)
            nastepny_indeks = (biezacy_indeks + 1) % len(POZYCJE_LINIJEK)
            self.pozycja_linijek = POZYCJE_LINIJEK[nastepny_indeks]
            # print(f"[DEBUG] Changing ruler position to: {self.pozycja_linijek}")
            self._aktualizuj_geometrie_nakladki() # Reposition everything
            if self.linijki_widoczne:
                # Make sure widgets are still visible and raised after potential geometry changes
                self._pokaz_wszystkie_nakladki()
            self.zapisz_stan()
        except ValueError:
            # Fallback if current position is somehow invalid
            # print(f"[WARN] Invalid ruler position '{self.pozycja_linijek}' found. Resetting to default.")
            self.pozycja_linijek = DOMYSLNA_POZYCJA_LINIJEK
            self._aktualizuj_geometrie_nakladki()
            if self.linijki_widoczne: self._pokaz_wszystkie_nakladki()
            self.zapisz_stan()
        except Exception as e:
            print(f"Error changing ruler position: {e}")

    def slot_zwieksz_grubosc(self):
        """Increases the gridline thickness via shortcut."""
        if threading.current_thread().ident != id_glownego_watku:
            QTimer.singleShot(0, self.slot_zwieksz_grubosc)
            return
        nowa_grubosc = min(self.grubosc_linii_siatki + KROK_ZMIANY_GRUBOSCI, MAKS_GRUBOŚĆ_SIATKI)
        if nowa_grubosc != self.grubosc_linii_siatki:
            # print(f"[DEBUG] Increasing thickness to {nowa_grubosc} via shortcut.")
            self.zmien_grubosc(nowa_grubosc)
            # Update settings dialog if it's open
            if self.dialog_ustawien and self.dialog_ustawien.isVisible():
                 self.dialog_ustawien.pole_grubosci.setValue(nowa_grubosc)

    def slot_zmniejsz_grubosc(self):
        """Decreases the gridline thickness via shortcut."""
        if threading.current_thread().ident != id_glownego_watku:
             QTimer.singleShot(0, self.slot_zmniejsz_grubosc)
             return
        nowa_grubosc = max(1, self.grubosc_linii_siatki - KROK_ZMIANY_GRUBOSCI)
        if nowa_grubosc != self.grubosc_linii_siatki:
            # print(f"[DEBUG] Decreasing thickness to {nowa_grubosc} via shortcut.")
            self.zmien_grubosc(nowa_grubosc)
             # Update settings dialog if it's open
            if self.dialog_ustawien and self.dialog_ustawien.isVisible():
                 self.dialog_ustawien.pole_grubosci.setValue(nowa_grubosc)

    def zmien_grubosc(self, wartosc):
        """Sets the gridline thickness and updates UI."""
        if threading.current_thread().ident != id_glownego_watku:
             QTimer.singleShot(0, lambda: self.zmien_grubosc(wartosc))
             return

        nowa_grubosc = max(1, min(int(wartosc), MAKS_GRUBOŚĆ_SIATKI))
        if self.grubosc_linii_siatki != nowa_grubosc:
            # print(f"[DEBUG] Setting thickness to: {nowa_grubosc}")
            self.grubosc_linii_siatki = nowa_grubosc
            self.zapisz_stan()
            self.aktualizuj_istniejace_linie_siatki() # Redraw lines with new thickness

    def zmien_kolor(self, kolor: QColor):
        """Sets the gridline color (including alpha) and updates UI."""
        if threading.current_thread().ident != id_glownego_watku:
             QTimer.singleShot(0, lambda: self.zmien_kolor(kolor))
             return

        if isinstance(kolor, QColor) and kolor.isValid():
            if self.kolor_linii_siatki != kolor:
                # print(f"[DEBUG] Setting color to: {kolor.name(QColor.NameFormat.HexArgb)}")
                self.kolor_linii_siatki = QColor(kolor) # Make a copy
                self.zapisz_stan()
                self.aktualizuj_istniejace_linie_siatki() # Redraw lines with new color/alpha
        else:
            print(f"Warning: zmien_kolor called with invalid color: {kolor}")

    def zmien_przezroczystosc(self, wartosc):
        """Sets the alpha component of the gridline color and updates UI."""
        if threading.current_thread().ident != id_glownego_watku:
             QTimer.singleShot(0, lambda: self.zmien_przezroczystosc(wartosc))
             return

        nowa_alfa = max(0, min(255, int(wartosc)))
        if self.kolor_linii_siatki.alpha() != nowa_alfa:
             # print(f"[DEBUG] Setting transparency (Alpha) to: {nowa_alfa}")
             # Modify the alpha of the existing color
             self.kolor_linii_siatki.setAlpha(nowa_alfa)
             self.zapisz_stan()
             self.aktualizuj_istniejace_linie_siatki() # Redraw lines with new alpha

    def aktualizuj_istniejace_linie_siatki(self):
        """Forces a repaint of all active gridline widgets."""
        # print("[DEBUG] Updating appearance of existing gridlines.")
        for widzet_linii in self.aktywne_linie_siatki.values():
            widzet_linii.update() # Trigger paintEvent

    def pokaz_dialog_ustawien(self):
        """Creates (if necessary) and shows the settings dialog."""
        if threading.current_thread().ident != id_glownego_watku:
            QTimer.singleShot(0, self.pokaz_dialog_ustawien)
            return

        # print("[DEBUG] Showing settings dialog...")
        if self.dialog_ustawien is None:
            # print("[DEBUG] Creating new settings dialog instance.")
            self.dialog_ustawien = DialogUstawien(self)
            # Optional: Connect finished signal if you need to know when it's closed
            # self.dialog_ustawien.finished.connect(self.dialog_ustawien_zamkniety)

        # Ensure texts are correct for the current language
        self.dialog_ustawien.retranslateUi()
        # Load current settings into the dialog's controls
        self.dialog_ustawien.wczytaj_poczatkowe_ustawienia()

        if not self.dialog_ustawien.isVisible():
            self.dialog_ustawien.show()
        self.dialog_ustawien.raise_() # Bring to front
        self.dialog_ustawien.activateWindow() # Try to give it focus

    # Optional: Slot if you need to do something when the dialog closes
    # def dialog_ustawien_zamkniety(self, result):
    #     print(f"[DEBUG] Settings dialog closed with result: {result}")
    #     # Maybe set self.dialog_ustawien = None here if you want to recreate it every time
    #     pass

    def rozpocznij_przeciaganie_nowej_linii(self, typ_linii, globalna_pozycja_startowa):
        """Creates a temporary gridline widget when dragging from a ruler."""
        if self.przeciaganie_nowej_linii: return # Should not happen due to check in caller

        self.przeciaganie_nowej_linii = True
        self.typ_nowej_linii = typ_linii
        id_siatki = -1 # Use a temporary ID for the dragged line

        # Determine initial position based on click and clamp within valid area
        prostokat_ekranu = QApplication.primaryScreen().geometry()
        min_poz_x = ROZMIAR_LINIJKI if 'left' in self.pozycja_linijek else 0
        min_poz_y = ROZMIAR_LINIJKI if 'top' in self.pozycja_linijek else 0
        maks_poz_x = prostokat_ekranu.width() - (ROZMIAR_LINIJKI if 'right' in self.pozycja_linijek else 0)
        maks_poz_y = prostokat_ekranu.height() - (ROZMIAR_LINIJKI if 'bottom' in self.pozycja_linijek else 0)

        if typ_linii == 'h':
            pozycja_poczatkowa = globalna_pozycja_startowa.y()
            pozycja_poczatkowa = max(min_poz_y, min(pozycja_poczatkowa, maks_poz_y))
        else: # typ_linii == 'v'
            pozycja_poczatkowa = globalna_pozycja_startowa.x()
            pozycja_poczatkowa = max(min_poz_x, min(pozycja_poczatkowa, maks_poz_x))

        # print(f"[DEBUG] Starting new line drag. Type: {typ_linii}, Initial Pos: {pozycja_poczatkowa}")

        # Create the temporary widget
        self.widzet_nowej_linii = WidzetLiniiSiatki(typ_linii, pozycja_poczatkowa, id_siatki)
        self.widzet_nowej_linii._aktualizuj_geometrie() # Position it
        self.widzet_nowej_linii.show()
        self.widzet_nowej_linii.raise_()

        # Set up for dragging
        self.widzet_nowej_linii.czy_przeciagane = True # Mark the widget itself as being dragged
        self.widzet_nowej_linii.stworz_podpowiedz()
        self.widzet_nowej_linii.aktualizuj_podpowiedz(globalna_pozycja_startowa)

        # Calculate mouse offset relative to the *widget's* top-left corner
        widget_pos = self.widzet_nowej_linii.pos()
        self.przesuniecie_nowej_linii = globalna_pozycja_startowa - widget_pos
        # print(f"[DEBUG]   Widget Pos: {widget_pos}, Mouse Offset: {self.przesuniecie_nowej_linii}")

        # Install global event filter to capture mouse move/release anywhere on screen
        self.qt_app.installEventFilter(self)

    def eventFilter(self, watched_object, event):
        """Global event filter to handle mouse movements and release during new line drag."""
        if self.przeciaganie_nowej_linii and self.widzet_nowej_linii:
            event_type = event.type()

            # --- Mouse Move ---
            if event_type == QEvent.Type.MouseMove:
                if not instancja_aplikacji: return False # Safety check

                biezaca_poz_globalna = event.globalPosition().toPoint()

                # Calculate valid boundaries for the line's *logical* position
                prostokat_ekranu = QApplication.primaryScreen().geometry()
                min_poz_x = ROZMIAR_LINIJKI if 'left' in instancja_aplikacji.pozycja_linijek else 0
                min_poz_y = ROZMIAR_LINIJKI if 'top' in instancja_aplikacji.pozycja_linijek else 0
                maks_poz_x = prostokat_ekranu.width() - (ROZMIAR_LINIJKI if 'right' in instancja_aplikacji.pozycja_linijek else 0)
                maks_poz_y = prostokat_ekranu.height() - (ROZMIAR_LINIJKI if 'bottom' in instancja_aplikacji.pozycja_linijek else 0)

                # Calculate the target top-left position of the *widget* based on mouse and offset
                nowa_pozycja_widżetu = biezaca_poz_globalna - self.przesuniecie_nowej_linii

                # Calculate the corresponding *logical* position of the line (center of handle)
                if self.typ_nowej_linii == 'h':
                    nowa_poz_abs = nowa_pozycja_widżetu.y() + SZEROKOSC_UCHWYTU_SIATKI // 2
                    # Clamp logical position
                    nowa_poz_abs = max(min_poz_y, min(nowa_poz_abs, maks_poz_y))
                else: # self.typ_nowej_linii == 'v'
                    nowa_poz_abs = nowa_pozycja_widżetu.x() + SZEROKOSC_UCHWYTU_SIATKI // 2
                    # Clamp logical position
                    nowa_poz_abs = max(min_poz_x, min(nowa_poz_abs, maks_poz_x))

                # Update the temporary widget's position and tooltip
                self.widzet_nowej_linii.ustaw_pozycje(nowa_poz_abs)
                self.widzet_nowej_linii.aktualizuj_podpowiedz(biezaca_poz_globalna)
                return True # Event handled

            # --- Mouse Button Release ---
            elif event_type == QEvent.Type.MouseButtonRelease and event.button() == Qt.MouseButton.LeftButton:
                # print("[DEBUG] Mouse released during new line drag.")
                # Remove the event filter *before* processing the drop
                try:
                    self.qt_app.removeEventFilter(self)
                except Exception as e:
                    print(f"Warning: Error removing event filter on release: {e}")
                self.zakoncz_przeciaganie_nowej_linii() # Finalize or discard the line
                return True # Event handled

            # --- Escape Key Press ---
            elif event_type == QEvent.Type.KeyPress and event.key() == Qt.Key.Key_Escape:
                # print("[DEBUG] Escape pressed during new line drag.")
                 # Remove the event filter *before* cancelling
                try:
                     self.qt_app.removeEventFilter(self)
                except Exception as e:
                    print(f"Warning: Error removing event filter on escape: {e}")
                self.anuluj_przeciaganie_nowej_linii() # Cancel the drag
                return True # Event handled

        # Pass unhandled events or events not related to the drag to the base class filter
        try:
             # Check if the base class implementation exists and call it
             # This avoids potential errors if QObject's eventFilter is called directly
             # on an object that hasn't reimplemented it in a specific way.
             base_filter = getattr(super(), 'eventFilter', None)
             if callable(base_filter):
                 return base_filter(watched_object, event)
             else:
                 return False # No base implementation to call
        except RuntimeError as e:
             # This can happen if the object is being deleted during event processing
             # print(f"Warning: RuntimeError in eventFilter: {e}")
             return False

    def zakoncz_przeciaganie_nowej_linii(self):
        """Finalizes the drag of a new line, either creating it permanently or deleting the temporary one."""
        if not self.przeciaganie_nowej_linii or not self.widzet_nowej_linii:
             # print("[DEBUG] zakoncz_przeciaganie_nowej_linii called inappropriately.")
             return

        konczony_widzet = self.widzet_nowej_linii # Keep reference to the widget
        typ_linii = konczony_widzet.typ
        pozycja_koncowa = konczony_widzet.pobierz_pozycje() # Get the final logical position

        # Reset dragging state immediately
        self.przeciaganie_nowej_linii = False
        self.typ_nowej_linii = None
        self.widzet_nowej_linii = None
        self.przesuniecie_nowej_linii = QPoint(0,0)

        # Clean up the temporary widget's visuals
        konczony_widzet.zniszcz_podpowiedz()
        konczony_widzet.czy_przeciagane = False # Mark widget as not being dragged anymore

        # --- Determine if the line should be kept or discarded ---
        usun_linie = False
        prostokat_ekranu = QApplication.primaryScreen().geometry()
        pozycja_linijek = self.pozycja_linijek

        # Define "deletion zones" (the areas covered by the rulers)
        # Note: These are thresholds for the *logical* line position
        gorna_strefa_usuniecia = ROZMIAR_LINIJKI if 'top' in pozycja_linijek else -1
        dolna_strefa_usuniecia = prostokat_ekranu.height() - ROZMIAR_LINIJKI if 'bottom' in pozycja_linijek else prostokat_ekranu.height() + 1
        lewa_strefa_usuniecia = ROZMIAR_LINIJKI if 'left' in pozycja_linijek else -1
        prawa_strefa_usuniecia = prostokat_ekranu.width() - ROZMIAR_LINIJKI if 'right' in pozycja_linijek else prostokat_ekranu.width() + 1

        # Check if the final position falls within a deletion zone
        if typ_linii == 'h':
            if pozycja_koncowa <= gorna_strefa_usuniecia or pozycja_koncowa >= dolna_strefa_usuniecia:
                usun_linie = True
        elif typ_linii == 'v':
            if pozycja_koncowa <= lewa_strefa_usuniecia or pozycja_koncowa >= prawa_strefa_usuniecia:
                usun_linie = True

        # --- Action based on deletion check ---
        if usun_linie:
            # print(f"[DEBUG] New line dropped in deletion zone (Pos: {pozycja_koncowa}). Discarding.")
            konczony_widzet.hide()
            konczony_widzet.deleteLater() # Remove the temporary widget
        else:
            # print(f"[DEBUG] New line dropped at Pos: {pozycja_koncowa}. Creating permanently.")
            # Assign a permanent ID
            nowe_id = self.nastepny_id_siatki
            self.nastepny_id_siatki += 1
            konczony_widzet.id = nowe_id # Update the widget's ID

            # Add to data store
            self.dane_linii_siatki.append({'type': typ_linii, 'pos': pozycja_koncowa, 'id': nowe_id})

            # Add to active widgets dictionary (transfer ownership from temp variable)
            self.aktywne_linie_siatki[nowe_id] = konczony_widzet

            # Make the widget respond to double-clicks, etc. (remove temp behaviors if any)
            # (Already done by setting czy_przeciagane=False and assigning ID)

            # Save the new state
            self.zapisz_stan()

    def anuluj_przeciaganie_nowej_linii(self):
        """Cancels the drag of a new line (e.g., on Escape press)."""
        if not self.przeciaganie_nowej_linii or not self.widzet_nowej_linii:
            # print("[DEBUG] anuluj_przeciaganie_nowej_linii called inappropriately.")
            return

        # print("[DEBUG] Cancelling new line drag.")
        widzet_do_usuniecia = self.widzet_nowej_linii

        # Reset dragging state
        self.przeciaganie_nowej_linii = False
        self.typ_nowej_linii = None
        self.widzet_nowej_linii = None
        self.przesuniecie_nowej_linii = QPoint(0,0)

        # Clean up and remove the temporary widget
        widzet_do_usuniecia.zniszcz_podpowiedz()
        widzet_do_usuniecia.hide()
        widzet_do_usuniecia.deleteLater()

        # Ensure event filter is removed if Escape was the cause
        # (Should already be removed by eventFilter itself, but belt-and-suspenders)
        try:
            self.qt_app.removeEventFilter(self)
        except Exception:
            pass # Ignore errors if already removed

    def stworz_widzet_linii_siatki(self, typ_linii, pozycja, id_siatki, update_geom=True):
        """Creates a gridline widget instance, adds it to tracking, and optionally shows it."""
        # Avoid creating duplicates if called unnecessarily
        if id_siatki in self.aktywne_linie_siatki:
            # print(f"[WARN] Attempted to create duplicate widget for ID {id_siatki}.")
            return self.aktywne_linie_siatki[id_siatki]

        # print(f"[DEBUG] Creating gridline widget. ID: {id_siatki}, Type: {typ_linii}, Pos: {pozycja}")
        widzet = WidzetLiniiSiatki(typ_linii, pozycja, id_siatki)
        self.aktywne_linie_siatki[id_siatki] = widzet

        # Ensure data store consistency (should normally be called after adding to data)
        if not any(d['id'] == id_siatki for d in self.dane_linii_siatki):
            print(f"[WARN] Creating widget for ID {id_siatki} which is not in data store. Adding it.")
            self.dane_linii_siatki.append({'type': typ_linii, 'pos': pozycja, 'id': id_siatki})
            # Consider saving state here if this path indicates an issue
            # self.zapisz_stan()

        if update_geom:
             widzet._aktualizuj_geometrie() # Position the new widget

        # Show if overlays are currently meant to be visible
        if self.linijki_widoczne:
            widzet.show()
            widzet.raise_()
        else:
            widzet.hide() # Ensure it's hidden if created while overlays are off

        return widzet

    def aktualizuj_pozycje_linii_siatki(self, id_siatki, nowa_pozycja):
        """Updates the position of a gridline in the central data store."""
        pozycja_zmieniona = False
        znaleziono = False
        for i, dane in enumerate(self.dane_linii_siatki):
            if dane['id'] == id_siatki:
                znaleziono = True
                if dane['pos'] != nowa_pozycja:
                    # print(f"[DEBUG] Updating position in data store for ID {id_siatki}: {dane['pos']} -> {nowa_pozycja}")
                    self.dane_linii_siatki[i]['pos'] = nowa_pozycja
                    pozycja_zmieniona = True
                break

        if not znaleziono:
             # This might happen briefly if a line is deleted while being dragged, ignore ID -1 (temp line)
             if id_siatki != -1:
                  print(f"Warning: Could not find line {id_siatki} in data store to update position.")
             return # Don't save if not found

        if pozycja_zmieniona:
            self.zapisz_stan() # Save state only if position actually changed

    def usun_widzet_linii_siatki_po_id(self, id_siatki):
        """Removes a gridline widget and its data based on ID."""
        # print(f"[DEBUG] Removing gridline by ID: {id_siatki}")
        widzet = self.aktywne_linie_siatki.pop(id_siatki, None)
        if widzet:
            # print(f"[DEBUG]   Found widget for ID {id_siatki}. Cleaning up.")
            widzet.zniszcz_podpowiedz() # Clean up tooltip if exists
            widzet.hide()
            widzet.deleteLater() # Schedule for deletion
        else:
             print(f"[WARN]   Widget for ID {id_siatki} not found in active widgets during removal.")


        # Remove from data store
        pocz_dl = len(self.dane_linii_siatki)
        self.dane_linii_siatki = [dane for dane in self.dane_linii_siatki if dane['id'] != id_siatki]
        dane_usuniete = len(self.dane_linii_siatki) < pocz_dl

        if dane_usuniete:
            # print(f"[DEBUG]   Removed data for ID {id_siatki}. Saving state.")
            self.zapisz_stan()
        elif id_siatki != -1: # Don't warn for temporary ID -1
             print(f"[WARN]   Data for ID {id_siatki} not found in data store during removal.")


    def usun_widzet_linii_siatki(self, widzet_do_usuniecia: WidzetLiniiSiatki):
        """Removes a specific gridline widget instance."""
        if not widzet_do_usuniecia:
             # print("[WARN] usun_widzet_linii_siatki called with None widget.")
             return

        id_siatki = widzet_do_usuniecia.id
        # print(f"[DEBUG] Request to remove widget with ID: {id_siatki}")

        # Handle the case where it might be the temporary line being dragged (-1)
        if id_siatki == -1:
            # This typically happens on double-click *during* the initial drag
            # Or if anuluj_przeciaganie was called just before this
            # print(f"[DEBUG]   Widget is the temporary line (ID -1).")
            if self.widzet_nowej_linii is widzet_do_usuniecia:
                 # print(f"[DEBUG]   It's the currently dragged line. Cancelling drag.")
                 # Ensure the main drag state is also reset properly
                 # (anuluj should handle filter removal and cleanup)
                 self.anuluj_przeciaganie_nowej_linii()
            else:
                 # Widget with ID -1 exists but isn't the active drag target? Unusual. Clean it up anyway.
                 print(f"[WARN]   Found widget with ID -1 but it's not the active new line drag. Cleaning up.")
                 widzet_do_usuniecia.zniszcz_podpowiedz()
                 widzet_do_usuniecia.hide()
                 widzet_do_usuniecia.deleteLater()
            return # No data store update needed for ID -1

        # If it's a permanent line, use the ID-based removal
        self.usun_widzet_linii_siatki_po_id(id_siatki)

    def wyczysc_wszystkie_linie(self):
        """Removes all gridlines."""
        if threading.current_thread().ident != id_glownego_watku:
            QTimer.singleShot(0, self.wyczysc_wszystkie_linie)
            return

        # print("[DEBUG] Clearing all gridlines...")
        # Get IDs before iterating, as we modify the dictionary
        id_do_usunięcia = list(self.aktywne_linie_siatki.keys())
        # print(f"[DEBUG]   IDs to remove: {id_do_usunięcia}")

        for id_siatki in id_do_usunięcia:
            if id_siatki in self.aktywne_linie_siatki: # Check if not already removed somehow
                widzet = self.aktywne_linie_siatki.pop(id_siatki)
                widzet.zniszcz_podpowiedz()
                widzet.hide()
                widzet.deleteLater()
            # else: # Should not happen if list is taken from keys before loop
            #     print(f"[WARN]   Widget ID {id_siatki} not found during clear all loop.")


        # Clear data store and reset ID counter
        self.dane_linii_siatki = []
        self.nastepny_id_siatki = 0
        # print("[DEBUG]   All data cleared and ID counter reset.")
        self.zapisz_stan()

    def zapisz_stan(self):
        """Saves the current application state (visibility, position, lines, settings) to a JSON file."""
        # Ensure next ID is correct before saving
        maks_id = max((item['id'] for item in self.dane_linii_siatki), default=-1)
        self.nastepny_id_siatki = max(0, maks_id + 1)

        stan = {
            'linijki_widoczne': self.linijki_widoczne,
            'pozycja_linijek': self.pozycja_linijek,
            'wyglad_linii_siatki': {
                'grubosc': self.grubosc_linii_siatki,
                # Save color as HexRGB and alpha separately for clarity/compatibility
                'kolor': self.kolor_linii_siatki.name(QColor.NameFormat.HexRgb),
                'przezroczystosc': self.kolor_linii_siatki.alpha()
            },
            'linie_siatki': list(self.dane_linii_siatki), # Ensure it's a list copy
            'nastepny_id_siatki': self.nastepny_id_siatki,
            'biezacy_jezyk': self.biezacy_jezyk
        }
        # print(f"[DEBUG] Saving state to {PLIK_STANU}: {stan}")
        try:
            with open(PLIK_STANU, 'w', encoding='utf-8') as f:
                json.dump(stan, f, indent=4, ensure_ascii=False)
            # print("[DEBUG] State saved successfully.")
        except IOError as e:
            print(f"Error saving state to {PLIK_STANU}: {e}")
        except Exception as e:
             print(f"Unexpected error saving state: {e}")

    def wczytaj_stan(self):
        """Loads application state from the JSON file."""
        stan = {}
        # print(f"[DEBUG] Attempting to load state from: {PLIK_STANU}")
        try:
            if os.path.exists(PLIK_STANU):
                with open(PLIK_STANU, 'r', encoding='utf-8') as f:
                    stan = json.load(f)
                # print("[DEBUG] State file loaded and parsed successfully.")
            else:
                # print("[DEBUG] State file not found. Using default values.")
                pass # Keep stan as empty dict, defaults will be used
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error reading or parsing state file ({PLIK_STANU}): {e}. Using default values.")
            stan = {} # Ensure stan is empty on error
        except Exception as e:
             print(f"Unexpected error loading state: {e}. Using defaults.")
             stan = {} # Ensure stan is empty on error

        # --- Apply loaded state or defaults ---
        self.linijki_widoczne = stan.get('linijki_widoczne', False)
        self.pozycja_linijek = stan.get('pozycja_linijek', DOMYSLNA_POZYCJA_LINIJEK)
        if self.pozycja_linijek not in POZYCJE_LINIJEK:
            # print(f"[WARN] Loaded invalid ruler position '{self.pozycja_linijek}'. Resetting to default.")
            self.pozycja_linijek = DOMYSLNA_POZYCJA_LINIJEK

        wyglad = stan.get('wyglad_linii_siatki', {})
        self.grubosc_linii_siatki = wyglad.get('grubosc', DOMYSLNA_GRUBOŚĆ_SIATKI)
        self.grubosc_linii_siatki = max(1, min(int(self.grubosc_linii_siatki), MAKS_GRUBOŚĆ_SIATKI)) # Sanitize

        kolor_hex = wyglad.get('kolor', DOMYSLNY_KOLOR_SIATKI)
        przezroczystosc = wyglad.get('przezroczystosc', DOMYSLNA_PRZEZROCZYSTOŚĆ_SIATKI)
        przezroczystosc = max(0, min(int(przezroczystosc), 255)) # Sanitize

        temp_kolor = QColor(kolor_hex)
        if not temp_kolor.isValid():
            # print(f"[WARN] Loaded invalid color hex '{kolor_hex}'. Using default.")
            temp_kolor = QColor(DOMYSLNY_KOLOR_SIATKI)
        temp_kolor.setAlpha(przezroczystosc)
        self.kolor_linii_siatki = temp_kolor

        wczytane_linie = stan.get('linie_siatki', [])
        # Basic validation: ensure it's a list and items look like dicts with required keys
        if isinstance(wczytane_linie, list):
             self.dane_linii_siatki = [
                 item for item in wczytane_linie
                 if isinstance(item, dict) and 'id' in item and 'type' in item and 'pos' in item
             ]
             if len(self.dane_linii_siatki) != len(wczytane_linie):
                 print("[WARN] Some loaded gridline entries were invalid and ignored.")
        else:
             print("[WARN] Loaded 'linie_siatki' is not a list. Ignoring.")
             self.dane_linii_siatki = []

        # Determine the next ID based on loaded data, ensuring it's at least 0
        wczytany_nastepny_id = stan.get('nastepny_id_siatki', 0)
        maks_id_wczytany = max((item['id'] for item in self.dane_linii_siatki), default=-1)
        self.nastepny_id_siatki = max(int(wczytany_nastepny_id), maks_id_wczytany + 1, 0) # Sanitize

        self.biezacy_jezyk = stan.get('biezacy_jezyk', DOMYSLNY_JEZYK)
        if self.biezacy_jezyk not in SLOWNIK_TLUMACZEN:
            # print(f"[WARN] Loaded invalid language code '{self.biezacy_jezyk}'. Using default '{DOMYSLNY_JEZYK}'.")
            self.biezacy_jezyk = DOMYSLNY_JEZYK

        # print(f"[DEBUG] State loaded. Visible: {self.linijki_widoczne}, Pos: {self.pozycja_linijek}, "
        #       f"Thickness: {self.grubosc_linii_siatki}, Color: {self.kolor_linii_siatki.name(QColor.NameFormat.HexArgb)}, "
        #       f"Lines: {len(self.dane_linii_siatki)}, NextID: {self.nastepny_id_siatki}, Lang: {self.biezacy_jezyk}")


    def slot_zmien_jezyk(self, kod_jezyka):
        """Changes the application language and updates UI elements."""
        if threading.current_thread().ident != id_glownego_watku:
            QTimer.singleShot(0, lambda: self.slot_zmien_jezyk(kod_jezyka))
            return

        if self.biezacy_jezyk == kod_jezyka:
            # print(f"[DEBUG] Language '{kod_jezyka}' is already active.")
            return # No change needed

        if kod_jezyka not in SLOWNIK_TLUMACZEN:
            print(f"[ERROR] Attempted to switch to unsupported language: {kod_jezyka}")
            return

        # print(f"[DEBUG] Changing language from '{self.biezacy_jezyk}' to '{kod_jezyka}'")
        self.biezacy_jezyk = kod_jezyka
        QLocale.setDefault(QLocale(self.biezacy_jezyk)) # Inform Qt about the language change
        self.zapisz_stan()

        # Trigger UI updates that depend on language
        # 1. Update Tray Menu (via signal which calls aktualizuj_menu_zasobnika)
        signal_emitter.zadanie_aktualizacji_zasobnika.emit(self.linijki_widoczne)
        # 2. Update Settings Dialog if it exists and is visible
        if self.dialog_ustawien:
            # Use QEvent.LanguageChange to trigger retranslateUi reliably
            QApplication.sendEvent(self.dialog_ustawien, QEvent(QEvent.Type.LanguageChange))
            # Alternative (direct call, might be less robust if dialog is complex):
            # if self.dialog_ustawien.isVisible():
            #    self.dialog_ustawien.retranslateUi()
        # 3. Update tooltips (if any are visible - they should recreate with new text)
        #    Tooltips on gridlines are dynamic and use tłumacz directly.
        #    Other potential static translatable UI elements would need updating here.
        # print("[DEBUG] Language change processed.")

    def uruchom(self):
        """Initial setup after __init__, called before starting the event loop."""
        # Use QTimer to ensure this runs after the event loop has started
        # and initial state (visible/hidden) is applied correctly.
        # print("[DEBUG] Scheduling initial show/hide based on loaded state.")
        QTimer.singleShot(50, self._poczatkowe_pokaz_ukryj) # Short delay

    def _poczatkowe_pokaz_ukryj(self):
        """Applies the initial visibility state loaded from the file."""
        # Ensure this runs on the main GUI thread
        if threading.current_thread().ident != id_glownego_watku:
            QTimer.singleShot(0, self._poczatkowe_pokaz_ukryj)
            return

        # print(f"[DEBUG] Applying initial visibility state: {'Show' if self.linijki_widoczne else 'Hide'}")
        if self.linijki_widoczne:
            # Call pokaz_linijki which handles geometry updates and showing widgets
            self.pokaz_linijki()
        else:
            # Call ukryj_linijki which handles hiding widgets
            self.ukryj_linijki()
         # No need to save state here, it was just loaded

    def zamknij_aplikacje(self):
        """Handles the application shutdown sequence."""
        # Ensure this runs on the main GUI thread
        if threading.current_thread().ident != id_glownego_watku:
             # print("[DEBUG] Received exit signal on non-main thread. Rescheduling.")
             QTimer.singleShot(0, self.zamknij_aplikacje)
             return

        print("Exit application request received.")
        print("  Saving final state...")
        self.zapisz_stan() # Save state one last time

        # Close any open dialogs gracefully
        if self.dialog_ustawien:
            print("  Closing settings dialog...")
            self.dialog_ustawien.close() # Ask it to close

        global instancja_ikony_zasobnika
        if instancja_ikony_zasobnika:
            print("  Stopping pystray icon...")
            try:
                # pystray runs in a separate thread, stop() signals it to exit
                instancja_ikony_zasobnika.stop()
                # Give the thread a moment to potentially stop
                # Note: This might not be strictly necessary if daemon=True
                # but can sometimes help ensure cleaner shutdown.
                # time.sleep(0.1)
            except Exception as e:
                print(f"    Error stopping pystray: {e}")
            instancja_ikony_zasobnika = None # Clear reference

        print("  Unregistering keyboard hotkeys...")
        try:
            # Use try-except as keyboard might not be hooked if it failed initially
            keyboard.unhook_all_hotkeys()
            print("    Hotkeys unhooked.")
        except NameError:
             print("    'keyboard' module not available or hotkeys weren't hooked, skipping unhook.")
        except Exception as e:
             print(f"    Error unhooking hotkeys: {e}")

        print("  Quitting Qt application...")
        # This will terminate the Qt event loop started by app.exec()
        self.qt_app.quit()
        print("Application shutdown sequence complete.")


# --- Helper function to find the base path for data files ---
def get_base_path():
    """ Get the base path for data files, accommodating PyInstaller/Nuitka """
    # Check for PyInstaller/Nuitka 'frozen' attribute
    if getattr(sys, 'frozen', False):
        # If run from bundle:
        # _MEIPASS is PyInstaller's temp dir attribute
        # If not _MEIPASS, use the executable's directory (common for Nuitka or one-folder)
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
        # print(f"[DEBUG] Running frozen. Base path: {base_path}") # Optional debug
    else:
        # If not frozen (running as script), use the script's directory
        base_path = os.path.dirname(os.path.abspath(__file__))
        # print(f"[DEBUG] Running as script. Base path: {base_path}") # Optional debug
    return base_path

# --- Pystray Functions ---
def stworz_obraz_ikony(szer, wys, kol1_rgb, kol2_rgb):
    """Generates a simple default checkerboard icon."""
    obraz = Image.new('RGB', (szer, wys), kol1_rgb)
    dc = ImageDraw.Draw(obraz)
    # Create a simple 2x2 checkerboard pattern
    dc.rectangle((szer//2, 0, szer, wys//2), fill=kol2_rgb)
    dc.rectangle((0, wys//2, szer//2, wys), fill=kol2_rgb)
    return obraz

def pobierz_obraz_ikony():
    """
    Loads the icon image ('icon.png') from the correct location,
    whether running as a script or as a bundled executable.
    Falls back to a generated default icon if 'icon.png' is not found.
    """
    icon_filename = "icon.png"
    base_dir = get_base_path() # Get the correct base directory
    # Construct the full, absolute path to the icon file
    sciezka = os.path.join(base_dir, icon_filename)
    print(f"[DEBUG] Attempting to load icon from: {sciezka}") # Debugging output

    # Define default icon parameters
    kol1_rgb = (211, 211, 211) # Light grey
    kol2_rgb = (105, 105, 105) # Dark grey
    ikona_dom = stworz_obraz_ikony(64, 64, kol1_rgb, kol2_rgb) # Generate default

    if os.path.exists(sciezka):
        try:
            print(f"[DEBUG] Icon file found at {sciezka}. Loading...") # Debug
            # Open the image using Pillow and ensure it's RGB
            loaded_icon = Image.open(sciezka).convert("RGB")
            print(f"[DEBUG] Icon loaded successfully.") # Debug
            return loaded_icon
        except Exception as e:
            print(f"Error loading icon file '{sciezka}': {e}. Using default icon.")
            return ikona_dom # Fallback on loading error
    else:
        print(f"[DEBUG] Icon file NOT found at {sciezka}. Using default icon.") # Debug
        return ikona_dom # Fallback if file doesn't exist

# --- Tray Menu Click Handlers ---
def po_kliknieciu_przelacz_tray(icon, item):
    # Emit signal to be handled by the main application thread
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

def formatuj_skrot_klawiszowy(skrot):
    """Formats a shortcut string like 'alt+shift+home' to 'Alt+Shift+Home'."""
    return '+'.join(part.capitalize() for part in skrot.split('+'))

def stworz_menu_zasobnika():
    """Creates the pystray Menu object based on the current application state and language."""
    # Ensure the application instance exists before accessing its state
    if not instancja_aplikacji:
        print("[ERROR] stworz_menu_zasobnika called before application instance exists.")
        return pystray.Menu(pystray.MenuItem("Error: App not ready", None))

    # Get current language and format shortcuts using the current language
    # biez_jez = instancja_aplikacji.biezacy_jezyk # Language is handled by tłumacz now
    skrot_widocznosc_fmt = formatuj_skrot_klawiszowy(SKROT_WIDOCZNOSC)
    skrot_pozycja_fmt = formatuj_skrot_klawiszowy(SKROT_POZYCJA_LINIJEK)
    skrot_wyczysc_fmt = formatuj_skrot_klawiszowy(SKROT_WYCZYSC_WSZYSTKO)
    skrot_wyjscie_fmt = formatuj_skrot_klawiszowy(SKROT_WYJSCIE)

    # Get translated menu item texts
    tytul_przelacz = tłumacz(KONTEKST_TRAY, "Ukryj/Pokaż Linie ({})").format(skrot_widocznosc_fmt)
    tytul_zmien_poz = tłumacz(KONTEKST_TRAY, "Zmień Pozycję ({})").format(skrot_pozycja_fmt)
    tytul_wyczysc = tłumacz(KONTEKST_TRAY, "Wyczyść Wszystko ({})").format(skrot_wyczysc_fmt)
    tytul_ustawienia = tłumacz(KONTEKST_TRAY, "Ustawienia Wyglądu...")
    tytul_jezyk = tłumacz(KONTEKST_TRAY, "Język / Language")
    tytul_jezyk_pl = tłumacz(KONTEKST_TRAY, "Polski")
    tytul_jezyk_en = tłumacz(KONTEKST_TRAY, "English")
    tytul_wyjscie = tłumacz(KONTEKST_TRAY, "Wyjście ({})").format(skrot_wyjscie_fmt)

    # Create language submenu
    menu_jezyk = pystray.Menu(
        pystray.MenuItem(
            tytul_jezyk_pl,
            po_kliknieciu_jezyk_pl_tray,
            # Check dynamically which language is selected
            checked=lambda item: instancja_aplikacji.biezacy_jezyk == 'pl',
            radio=True # Indicate radio button behavior
        ),
        pystray.MenuItem(
             tytul_jezyk_en,
             po_kliknieciu_jezyk_en_tray,
             checked=lambda item: instancja_aplikacji.biezacy_jezyk == 'en',
             radio=True
         )
    )

    # Create main menu
    menu = pystray.Menu(
        pystray.MenuItem(tytul_przelacz, po_kliknieciu_przelacz_tray,
                         # checked=lambda item: instancja_aplikacji.linijki_widoczne # Checkmark if visible
                         # Checkmark is less common for toggle actions, often implied by text
                         ),
        pystray.MenuItem(tytul_zmien_poz, po_kliknieciu_zmien_pozycje_tray),
        pystray.MenuItem(tytul_wyczysc, po_kliknieciu_wyczysc_tray),
        pystray.MenuItem(tytul_ustawienia, po_kliknieciu_ustawienia_tray),
        pystray.MenuItem(tytul_jezyk, menu_jezyk), # Add the language submenu
        pystray.Menu.SEPARATOR,
        pystray.MenuItem(tytul_wyjscie, po_kliknieciu_wyjscie_tray)
    )
    return menu

def aktualizuj_menu_zasobnika(ikona, widocznosc):
    """Callback function to update the tray icon's menu when state changes (like language)."""
    # print("[DEBUG] Updating tray menu...")
    if ikona and instancja_aplikacji:
        ikona.menu = stworz_menu_zasobnika() # Recreate the menu with current translations/state
        # Tell pystray to update the menu if the icon thread is running
        if ikona._thread and ikona._thread.is_alive():
             try:
                 ikona.update_menu()
                 # print("[DEBUG] Tray menu updated.")
             except Exception as e:
                 # This can sometimes happen during shutdown, catch potential errors
                 print(f"Warning: Error updating tray menu: {e}")
        #else:
             #print("[DEBUG] Tray icon thread not running, menu not updated live.")

    # The 'widocznosc' parameter is passed by the signal but often not directly needed here
    # as the menu generation checks the app state directly. It's kept for signal signature consistency.


def konfiguruj_ikone_zasobnika():
    """Configures and creates the pystray Icon object."""
    # print("[DEBUG] Configuring system tray icon...")
    obraz = pobierz_obraz_ikony() # Load the (potentially custom) icon
    tytul_ikony = tłumacz(KONTEKST_TRAY, "Linie Pomocnicze") # Get initial tooltip text
    # print(f"[DEBUG] Tray icon title set to: '{tytul_ikony}'")

    # Create the icon instance
    ikona = pystray.Icon("gridlines_app", obraz, tytul_ikony)
    # Set the initial menu
    ikona.menu = stworz_menu_zasobnika()

    global instancja_ikony_zasobnika
    instancja_ikony_zasobnika = ikona # Store the instance globally

    # Connect the signal emitter to the menu update function
    # This allows the main thread to request a menu update from the pystray thread
    signal_emitter.zadanie_aktualizacji_zasobnika.connect(
        # Use a lambda to pass the icon instance to the update function
        lambda wid: aktualizuj_menu_zasobnika(ikona, wid)
    )
    # print("[DEBUG] System tray icon configured.")
    return ikona

# --- Keyboard Hotkey Callbacks ---
# These functions simply emit signals to be handled safely on the main Qt thread.
def obsluz_widocznosc():
    signal_emitter.zadanie_przelaczenia_widocznosci.emit()

def obsluz_zmiane_pozycji():
    signal_emitter.zadanie_zmiany_pozycji_linijek.emit()

def obsluz_wyczysc_wszystko():
    signal_emitter.zadanie_wyczyszczenia_wszystkiego.emit()

def obsluz_wyjscie():
    # Note: This might run in the keyboard listener thread, not the main Qt thread.
    # The signal emission handles the cross-thread communication.
    print(f"Hotkey '{SKROT_WYJSCIE}' detected in thread {threading.current_thread().ident}. Emitting exit signal.")
    # Note: If this print doesn't show up, the OS is likely intercepting the key combo.
    signal_emitter.zadanie_wyjscia_z_aplikacji.emit()

def obsluz_zwieksz_grubosc():
    signal_emitter.zadanie_zwiekszenia_grubosci.emit()

def obsluz_zmniejsz_grubosc():
    signal_emitter.zadanie_zmniejszenia_grubosci.emit()

def konfiguruj_skróty_klawiszowe():
    """Registers the global keyboard hotkeys using the 'keyboard' library."""
    print("Registering global keyboard hotkeys...")
    try:
        # Check if keyboard module seems functional (basic check)
        if not hasattr(keyboard, 'add_hotkey'):
             raise ImportError("Keyboard module loaded but seems incomplete.")

        # Register hotkeys - these run callbacks in a separate listener thread
        keyboard.add_hotkey(SKROT_WIDOCZNOSC, obsluz_widocznosc, trigger_on_release=False)
        keyboard.add_hotkey(SKROT_POZYCJA_LINIJEK, obsluz_zmiane_pozycji, trigger_on_release=False)
        keyboard.add_hotkey(SKROT_WYCZYSC_WSZYSTKO, obsluz_wyczysc_wszystko, trigger_on_release=False)
        # WARNING: SKROT_WYJSCIE (Ctrl+Alt+End) might be intercepted by the OS
        keyboard.add_hotkey(SKROT_WYJSCIE, obsluz_wyjscie, trigger_on_release=False)
        keyboard.add_hotkey(SKROT_ZWIEKSZ_GRUBOSC, obsluz_zwieksz_grubosc, trigger_on_release=False, suppress=False) # Allow repeat?
        keyboard.add_hotkey(SKROT_ZMNIEJSZ_GRUBOSC, obsluz_zmniejsz_grubosc, trigger_on_release=False, suppress=False) # Allow repeat?

        print("Global hotkeys registered:")
        print(f"  - Toggle Visibility: {SKROT_WIDOCZNOSC}")
        print(f"  - Change Position: {SKROT_POZYCJA_LINIJEK}")
        print(f"  - Clear All: {SKROT_WYCZYSC_WSZYSTKO}")
        print(f"  - Exit: {SKROT_WYJSCIE} (Note: May be intercepted by OS)")
        print(f"  - Increase Thickness: {SKROT_ZWIEKSZ_GRUBOSC}")
        print(f"  - Decrease Thickness: {SKROT_ZMNIEJSZ_GRUBOSC}")
        print("NOTE: Hotkeys require necessary OS permissions (e.g., Accessibility on macOS, run as admin if needed on Windows).")

    except ImportError:
         print("-------------------------------------------------------------")
         print("ERROR: 'keyboard' library not installed or not functional.")
         print("Global hotkeys will be DISABLED.")
         print("Please install it: pip install keyboard")
         print("On Linux, you might need to run as root or set up uinput.")
         print("On macOS, you may need Accessibility permissions.")
         print("-------------------------------------------------------------")
    except Exception as e:
        print("-------------------------------------------------------------")
        print(f"ERROR: Failed to register global hotkeys: {e}")
        print("Hotkeys will likely not function.")
        print("Check permissions or run as administrator/root if necessary.")
        print("Ensure no other application is aggressively grabbing keys.")
        print("-------------------------------------------------------------")

# --- Główna funkcja ---
def main():
    print("Starting Gridlines Application...")

    # Explicitly set locale early if needed, though usually handled by Qt/OS
    # locale.setlocale(locale.LC_ALL, '') # Set to default user locale

    # Get or create the QApplication instance
    # Important to do this before creating any QWidgets/QObjects
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    # Set application metadata (optional, but good practice)
    app.setApplicationName("Gridlines")
    app.setOrganizationName("YourNameOrOrg") # Replace if desired
    app.setApplicationVersion("1.0") # Example version

    # Prevent app exit when the (invisible) overlay windows close
    app.setQuitOnLastWindowClosed(False)

    # --- Create the main application logic instance ---
    # This also loads state and connects internal signals
    global instancja_aplikacji
    instancja_aplikacji = AplikacjaLiniiPomocniczych()

    # --- Setup external components ---
    # Register global hotkeys (runs in a separate thread managed by 'keyboard')
    konfiguruj_skróty_klawiszowe()

    # Configure system tray icon (runs in its own thread managed by 'pystray')
    ikona = konfiguruj_ikone_zasobnika()

    # --- Start the application ---
    # Schedule the initial show/hide based on loaded state (runs after event loop starts)
    instancja_aplikacji.uruchom()

    # --- Start the pystray icon thread ---
    def run_icon():
        """Target function for the pystray thread."""
        # print("[DEBUG] Pystray thread starting...")
        try:
             # This blocks until ikona.stop() is called
             ikona.run()
             # print("[DEBUG] Pystray thread finished.")
        except Exception as e:
             # Catch errors within the thread to prevent silent failures
             print(f"Error in pystray thread: {e}")
             # Optionally, try to signal the main app to quit if the tray fails critically
             # signal_emitter.zadanie_wyjscia_z_aplikacji.emit()

    # Start pystray in a daemonic thread so it doesn't prevent app exit
    # if the main Qt loop terminates first.
    watek_ikony = threading.Thread(target=run_icon, name="PystrayThread", daemon=True)
    watek_ikony.start()

    # --- Start the Qt Event Loop ---
    print("Starting Qt event loop...")
    # This blocks until app.quit() is called (usually by zamknij_aplikacje)
    exit_code = app.exec()
    print(f"Qt event loop finished. Exit code: {exit_code}")

    # --- Cleanup (optional, as daemonic threads might exit abruptly) ---
    # Ensure the pystray thread is asked to stop if it hasn't already
    if instancja_ikony_zasobnika and instancja_ikony_zasobnika.visible:
        try:
            instancja_ikony_zasobnika.stop()
        except: pass # Ignore errors during final cleanup

    # Ensure the keyboard listener is stopped (if possible and necessary)
    # Note: unhook_all_hotkeys might be sufficient, but `keyboard.wait()` is usually
    #       used in scripts that *only* listen. Here, Qt's loop is primary.
    # try:
    #     # Attempt to stop the listener if keyboard module has a way
    #     pass # keyboard library doesn't have an explicit stop function for the listener thread easily accessible
    # except: pass

    print("Gridlines application exiting.")
    sys.exit(exit_code) # Exit with the code from Qt app

if __name__ == "__main__":
    # Set high DPI scaling attribute *before* QApplication is created
    # For Qt6, usually automatic, but can be set explicitly if needed:
    # QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    # os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1" # For Qt5 compatibility mode if used
    main()

# --- END OF FILE Lines Desktop.py ---