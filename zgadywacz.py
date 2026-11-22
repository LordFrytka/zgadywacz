import json
import os
import random
import sys
import tkinter as tk

PLIK_ZAPISU = "zapis.json"
BG_MAIN = "#0f172a"
BG_CARD = "#1e293b"
BG_INPUT = "#0f172a"
FG_TEXT = "#f8fafc"
FG_MUTED = "#94a3b8"
BG_MUTED = "#3b3f44"
PURPLE_DARK = "#a855f7"
PURPLE_LIGHT = "#c084fc"
TOO_MUCH = "#63CA60"
TOO_LESS = "#d31b1b"
SUCCESS = "#22c55e"
WARNING = "#f59e0b"
DANGER = "#ef4444"
BTN_BASE = "#334155"
CENA_PODPOWIEDZI = 10000
CENA_BOOSTERA = 25000
BOOSTER_GIER = 5
BOOSTER_MMR = 10
SZEROKOSC_PODPOWIEDZI = 10
BONUS_BANKRUTA = 500
BONUS_HAZARDZISTY = 5000
PROG_HAZARDZISTY = 25000
FONT_FAMILY = "Trebuchet MS"
KOLORY_RANG = {
    "Stracono": "#ef4444",
    "Brąz": "#d97706",
    "Srebro": "#cbd5e1",
    "Złoto": "#facc15",
    "Platyna": "#5eead4",
    "Diament": "#67e8f9",
    "Master Zgadywacz": "#e879f9"
}

def formatowanie(liczba):
    return f"{int(liczba):,}".replace(",", ".")

class ZgadywaczApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("ZGADYWACZ - Edycja Okienkowa")
        self._geometria_okna = "700x720"
        self.root.geometry(self._geometria_okna)
        self.root.minsize(600, 680)
        self.root.configure(bg=BG_MAIN)
        self.domyslne_dane()
        self.wczytaj_dane()
        self.fullscreen = False
        self.wybrany_fullscreen = False
        self._odswiez_ekran_ustawien = None
        self.mode = None
        self.losowa = 0
        self.dzielnik = 1
        self.obstawione = 0
        self.min_val = 10
        self.max_val = 100
        self.gra_w_toku = False
        self.podpowiedz_uzyta = False
        self.btn_hint = None
        self.lbl_hint = None
        self.btn_replay = None
        self._zbuduj_szkielet()
        self.pokaz_menu()
        self.root.protocol("WM_DELETE_WINDOW", self.wyjdz_z_gry)
        self.root.bind("<F11>", self._przelacz_pelny_ekran)
        self.root.bind("<Configure>", self._dostosuj_do_rozmiaru)

    def domyslne_dane(self):
        self.ogolne_mmr = 200
        self.ogolne_pkt = 0.0
        self.dolary = 1000
        self.nierank_gry = 0
        self.nierank_proby = 0
        self.rank_gry = 0
        self.rank_proby = 0
        self.najwieksza_wygrana = 0
        self.lacznie_wygrane = 0
        self.podpowiedzi = 0
        self.booster_gry = 0
        self.hazard_odebrane = 0

    def wczytaj_dane(self):
        if os.path.exists(PLIK_ZAPISU):
            try:
                with open(PLIK_ZAPISU, "r", encoding="utf-8") as plik:
                    dane = json.load(plik)
                    self.ogolne_mmr = dane.get("ogolne_mmr", 200)
                    self.ogolne_pkt = float(dane.get("ogolne_pkt", 0.0))
                    self.dolary = dane.get("dolary", 1000)
                    self.nierank_gry = dane.get("nierank_gry", 0)
                    self.nierank_proby = dane.get("nierank_proby", 0)
                    self.rank_gry = dane.get("rank_gry", 0)
                    self.rank_proby = dane.get("rank_proby", 0)
                    self.najwieksza_wygrana = dane.get("najwieksza_wygrana", 0)
                    self.lacznie_wygrane = dane.get("lacznie_wygrane", 0)
                    self.podpowiedzi = dane.get("podpowiedzi", 0)
                    self.booster_gry = dane.get("booster_gry", 0)
                    self.hazard_odebrane = dane.get("hazard_odebrane", 0)
            except Exception:
                pass

    def zapisz_dane(self):
        dane = {
            "ogolne_mmr": self.ogolne_mmr,
            "ogolne_pkt": self.ogolne_pkt,
            "dolary": self.dolary,
            "nierank_gry": self.nierank_gry,
            "nierank_proby": self.nierank_proby,
            "rank_gry": self.rank_gry,
            "rank_proby": self.rank_proby,
            "najwieksza_wygrana": self.najwieksza_wygrana,
            "lacznie_wygrane": self.lacznie_wygrane,
            "podpowiedzi": self.podpowiedzi,
            "booster_gry": self.booster_gry,
            "hazard_odebrane": self.hazard_odebrane,
        }
        with open(PLIK_ZAPISU, "w", encoding="utf-8") as plik:
            json.dump(dane, plik, ensure_ascii=False, indent=4)

    def zaladuj_range(self):
        if self.ogolne_mmr <= 0:
            self.ogolne_mmr = 0
            return "Stracono"
        elif self.ogolne_mmr < 500:
            return "Brąz"
        elif self.ogolne_mmr < 1000:
            return "Srebro"
        elif self.ogolne_mmr < 1500:
            return "Złoto"
        elif self.ogolne_mmr < 2000:
            return "Platyna"
        elif self.ogolne_mmr < 2500:
            return "Diament"
        else:
            return "Master Zgadywacz"

    def kolor_rangi(self, ranga=None):
        if ranga is None:
            ranga = self.zaladuj_range()
        return KOLORY_RANG.get(ranga, FG_TEXT)

    def _zastosuj_tryb_ekranu(self, wlacz_pelny_ekran: bool):
        if wlacz_pelny_ekran and not self.fullscreen:
            if self.root.state() == "normal":
                self._geometria_okna = self.root.geometry()
            self.fullscreen = True
            self.wybrany_fullscreen = True
            self.root.attributes("-fullscreen", True)
            self.root.update_idletasks()
        elif not wlacz_pelny_ekran and self.fullscreen:
            self.fullscreen = False
            self.wybrany_fullscreen = False
            self.root.attributes("-fullscreen", False)
            self.root.state("normal")
            self.root.geometry(self._geometria_okna)
            self.root.update_idletasks()

    def _odswiez_przycisk_ekranu_jesli_jest(self):
        if self._odswiez_ekran_ustawien:
            self._odswiez_ekran_ustawien()

    def _przelacz_pelny_ekran(self, _event=None):
        self._zastosuj_tryb_ekranu(not self.fullscreen)
        self._odswiez_przycisk_ekranu_jesli_jest()

    def _dostosuj_do_rozmiaru(self, _event=None):
        if not self.fullscreen and self.root.state() == "normal":
            geom = self.root.geometry()
            if geom:
                self._geometria_okna = geom
        szerokosc = max(self.root.winfo_width(), 600)
        pad_xy = 64 if szerokosc > 1000 else 24
        self.container.config(padx=pad_xy, pady=pad_xy)

    def _zbuduj_szkielet(self):
        self.container = tk.Frame(self.root, bg=BG_MAIN, padx=24, pady=24)
        self.container.pack(fill="both", expand=True)

    def _wyczysc_ekran(self):
        self._odswiez_ekran_ustawien = None
        for widget in self.container.winfo_children():
            widget.destroy()

    def _karta(self, parent=None, padx=28, pady=24):
        card = tk.Frame(
            parent or self.container,
            bg=BG_CARD,
            padx=padx,
            pady=pady,
            highlightbackground=PURPLE_DARK,
            highlightcolor=PURPLE_DARK,
            highlightthickness=1
        )
        card.pack(fill="both", expand=True)
        return card

    def _przycisk(self, parent, text, command, width=28, pady=10, base_bg=None, base_fg=None, hover_bg=None, hover_fg=None):
        bg_normal = base_bg if base_bg is not None else BTN_BASE
        fg_normal = base_fg if base_fg is not None else FG_TEXT
        bg_hover = hover_bg if hover_bg is not None else PURPLE_LIGHT
        fg_hover = hover_fg if hover_fg is not None else "#0f172a"
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            font=(FONT_FAMILY, 11, "bold"),
            bg=bg_normal,
            fg=fg_normal,
            activebackground=bg_hover,
            activeforeground=fg_hover,
            relief="flat",
            cursor="hand2",
            width=width,
            pady=pady,
            bd=0,
            highlightthickness=0
        )
        def on_enter(_e):
            if str(btn["state"]) != "disabled":
                btn.config(bg=bg_hover, fg=fg_hover)
        def on_leave(_e):
            if str(btn["state"]) != "disabled":
                btn.config(bg=bg_normal, fg=fg_normal)
        def on_press(_e):
            if str(btn["state"]) != "disabled":
                btn.config(bg=bg_hover, fg=fg_hover)
        def on_release(e):
            if str(btn["state"]) != "disabled":
                inside = 0 <= e.x <= btn.winfo_width() and 0 <= e.y <= btn.winfo_height()
                btn.config(
                    bg=bg_hover if inside else bg_normal,
                    fg=fg_hover if inside else fg_normal,
                )
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        btn.bind("<ButtonPress-1>", on_press)
        btn.bind("<ButtonRelease-1>", on_release)
        return btn

    def _wylacz_przycisk(self, btn):
        btn.config(state="disabled", bg=BTN_BASE, fg=FG_MUTED, cursor="arrow")

    def _panel_tekstowy(self, parent, fragmenty, height=11, width=58):
        txt = tk.Text(
            parent,
            font=(FONT_FAMILY, 10, "bold"),
            bg=BG_MAIN,
            fg=FG_TEXT,
            relief="flat",
            wrap="word",
            height=height,
            width=width,
            padx=18,
            pady=14,
            highlightbackground="#334155",
            highlightcolor="#334155",
            highlightthickness=1,
            cursor="arrow"
        )
        txt.tag_configure("text", font=(FONT_FAMILY, 10, "bold"), foreground=FG_TEXT)
        txt.tag_configure("header", font=(FONT_FAMILY, 12, "bold"), foreground=PURPLE_LIGHT)
        for tekst, styl, *kolor in fragmenty:
            if kolor:
                tag_name = f"{styl}_{kolor[0]}"
                font_cfg = (FONT_FAMILY, 12, "bold") if styl == "header" else (FONT_FAMILY, 10, "bold")
                txt.tag_configure(tag_name, font=font_cfg, foreground=kolor[0])
                txt.insert("end", tekst, tag_name)
            else:
                txt.insert("end", tekst, styl)
        txt.config(state="disabled")
        txt.pack(pady=(0, 16))
        return txt

    def _pokaz_blad_walidacji(self, tytul: str, komunikat: str):
        win = tk.Toplevel(self.root)
        win.title(tytul)
        win.configure(bg=BG_MAIN)
        win.resizable(False, False)
        win.transient(self.root)
        win.grab_set()
        frame = tk.Frame(
            win,
            bg=BG_CARD,
            padx=24,
            pady=24,
            highlightbackground=PURPLE_DARK,
            highlightthickness=1
        )
        frame.pack(fill="both", expand=True, padx=24, pady=24)
        tk.Label(
            frame,
            text=tytul.upper(),
            font=(FONT_FAMILY, 18, "bold"),
            bg=BG_CARD,
            fg=DANGER
        ).pack(pady=(0, 8))
        tk.Label(
            frame,
            text=komunikat,
            font=(FONT_FAMILY, 12, "bold"),
            bg=BG_CARD,
            fg=FG_TEXT,
            justify="center",
            wraplength=340
        ).pack(pady=(0, 16))
        self._przycisk(frame, "OK", win.destroy, width=16, pady=8).pack()
        win.update_idletasks()
        w = win.winfo_width()
        h = win.winfo_height()
        rx = self.root.winfo_rootx()
        ry = self.root.winfo_rooty()
        rw = self.root.winfo_width()
        rh = self.root.winfo_height()
        x = rx + max((rw - w) // 2, 0)
        y = ry + max((rh - h) // 2, 0)
        win.geometry(f"+{x}+{y}")
        win.wait_window()

    def _otworz_okno_resetu(self):
        win = tk.Toplevel(self.root)
        win.title("Reset statystyk — ZGADYWACZ")
        win.configure(bg=BG_MAIN)
        win.resizable(False, False)
        win.transient(self.root)
        win.grab_set()
        outer = tk.Frame(
            win,
            bg=BG_CARD,
            padx=24,
            pady=24,
            highlightbackground=PURPLE_DARK,
            highlightthickness=1
        )
        outer.pack(fill="both", expand=True, padx=24, pady=24)
        lbl_tytul = tk.Label(
            outer,
            text="RESET STATYSTYK",
            font=(FONT_FAMILY, 18, "bold"),
            bg=BG_CARD,
            fg=PURPLE_LIGHT
        )
        lbl_tytul.pack(pady=(0, 10))
        info_box = tk.Frame(
            outer,
            bg=BG_MAIN,
            padx=16,
            pady=12,
            highlightbackground="#334155",
            highlightthickness=1
        )
        info_box.pack(fill="x", pady=(0, 18))
        lbl_opis = tk.Label(
            info_box,
            text=(
                "Czy na pewno chcesz trwale zresetować\nwszystkie statystyki?"
            ),
            font=(FONT_FAMILY, 10, "bold"),
            bg=BG_MAIN,
            fg=FG_TEXT,
            justify="left"
        )
        lbl_opis.pack()
        btn_row = tk.Frame(outer, bg=BG_CARD)
        btn_row.pack()
        def potwierdz_reset():
            self.domyslne_dane()
            self.zapisz_dane()
            lbl_tytul.config(text="ZRESETOWANO", fg=SUCCESS)
            lbl_opis.config(
                text="Wszystkie statystyki zostały przywrócone\ndo wartości początkowych.",
                justify="left"
            )
            for child in btn_row.winfo_children():
                child.destroy()
            self._przycisk(btn_row, "OK", win.destroy, width=18, pady=9).pack()
        btn_tak = self._przycisk(
            btn_row,
            "Resetuj",
            potwierdz_reset,
            width=14,
            pady=9,
            base_bg="#7f1d1d",
            base_fg=FG_TEXT,
            hover_bg="#dc2626",
            hover_fg=FG_TEXT
        )
        btn_tak.pack(side="left", padx=(0, 8))
        btn_nie = self._przycisk(btn_row, "Anuluj", win.destroy, width=14, pady=9)
        btn_nie.pack(side="left", padx=(8, 0))
        win.bind("<Escape>", lambda _e: win.destroy())
        win.update_idletasks()
        w = win.winfo_width()
        h = win.winfo_height()
        rx = self.root.winfo_rootx()
        ry = self.root.winfo_rooty()
        rw = self.root.winfo_width()
        rh = self.root.winfo_height()
        x = rx + max((rw - w) // 2, 0)
        y = ry + max((rh - h) // 2, 0)
        win.geometry(f"+{x}+{y}")
        win.wait_window()

    def _powrot_do_menu_z_gry(self):
        if self.gra_w_toku:
            return
        self.pokaz_menu()

    def _zagraj_ponownie(self):
        if self.gra_w_toku:
            return
        if self.mode == "wager":
            # w trybie zakładowym trzeba ponownie wybrać stawkę
            self.konfiguracja_gry("wager")
        else:
            self.rozpocznij_gre(min_val=self.min_val, max_val=self.max_val, obstawione=0)

    def pokaz_menu(self):
        self._wyczysc_ekran()
        card = self._karta(pady=30)
        center = tk.Frame(card, bg=BG_CARD)
        center.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(
            center,
            text="ZGADYWACZ",
            font=(FONT_FAMILY, 54, "bold"),
            bg=BG_CARD,
            fg=PURPLE_LIGHT
        ).pack(pady=(0, 24))
        self._przycisk(center, "Start gry", self.pokaz_tryby).pack(pady=6)
        self._przycisk(center, "Ustawienia", self.pokaz_ustawienia).pack(pady=6)
        self._przycisk(center, "Sklep rankingowy", self.pokaz_sklep).pack(pady=6)
        self._przycisk(center, "Dodatkowe opcje", self.pokaz_dodatkowe).pack(pady=6)
        self._przycisk(center, "Wyjdź z gry", self.wyjdz_z_gry).pack(pady=6)

    def pokaz_tryby(self):
        self._wyczysc_ekran()
        card = self._karta(pady=22)
        wrapper = tk.Frame(card, bg=BG_CARD, width=560)
        wrapper.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(
            wrapper,
            text="WYBIERZ TRYB GRY",
            font=(FONT_FAMILY, 20, "bold"),
            bg=BG_CARD,
            fg=PURPLE_DARK
        ).pack(pady=(0, 14))
        tryby_info = [
            ("Tryb nierankingowy", "Własny przedział liczb • Punkty ogólne", "unranked"),
            ("Tryb rankingowy", "Przedział 10–100 • Punkty MMR i rangi", "ranked"),
            ("Tryb zakładowy", "Obstawianie dolarów • Max 5 prób • Wygrana x2\t\t", "wager"),
        ]
        for nazwa, opis, tryb_id in tryby_info:
            box = tk.Frame(
                wrapper,
                bg=BG_MAIN,
                padx=18,
                pady=12,
                highlightbackground="#334155",
                highlightthickness=1
            )
            box.pack(fill="x", pady=6)
            left = tk.Frame(box, bg=BG_MAIN)
            left.pack(side="left", fill="y")
            tk.Label(left, text=nazwa, font=(FONT_FAMILY, 12, "bold"), bg=BG_MAIN, fg=FG_TEXT, anchor="w").pack(anchor="w")
            tk.Label(left, text=opis, font=(FONT_FAMILY, 9, "bold"), bg=BG_MAIN, fg=FG_MUTED, anchor="w").pack(anchor="w")
            self._przycisk(
                box,
                "Wybierz",
                lambda m=tryb_id: self.konfiguracja_gry(m),
                width=12,
                pady=7
            ).pack(side="right")
        self._przycisk(wrapper, "Powrót do menu", self.pokaz_menu, width=22, pady=9).pack(pady=(18, 0))

    def pokaz_sklep(self, komunikat="", kolor=SUCCESS):
        self._wyczysc_ekran()
        card = self._karta(pady=22)
        wrapper = tk.Frame(card, bg=BG_CARD, width=560)
        wrapper.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(
            wrapper,
            text="SKLEP RANKINGOWY",
            font=(FONT_FAMILY, 20, "bold"),
            bg=BG_CARD,
            fg=PURPLE_DARK
        ).pack(pady=(0, 6))
        tk.Label(
            wrapper,
            text=f"Twoje saldo: {formatowanie(self.dolary)}$",
            font=(FONT_FAMILY, 12, "bold"),
            bg=BG_CARD,
            fg=FG_MUTED
        ).pack(pady=(0, 4))
        if komunikat:
            tk.Label(
                wrapper,
                text=komunikat,
                font=(FONT_FAMILY, 12, "bold"),
                bg=BG_CARD,
                fg=kolor,
                height=1
            ).pack(pady=(0, 6))
        przedmioty = [
            (
                "Podpowiedź",
                f"Pokazuje przedział {SZEROKOSC_PODPOWIEDZI} liczb z wylosowaną.",
                CENA_PODPOWIEDZI,
                self.kup_podpowiedz,
            ),
            (
                f"Booster MMR",
                f"+{BOOSTER_MMR} MMR za rundę przez {BOOSTER_GIER} następnych gier.",
                CENA_BOOSTERA,
                self.kup_booster,
            ),
        ]
        for nazwa, opis, cena, akcja in przedmioty:
            box = tk.Frame(
                wrapper,
                bg=BG_MAIN,
                padx=18,
                pady=12,
                highlightbackground="#334155",
                highlightthickness=1
            )
            box.pack(fill="x", pady=6)
            left = tk.Frame(box, bg=BG_MAIN)
            left.pack(side="left", fill="y")
            tk.Label(left, text=nazwa, font=(FONT_FAMILY, 12, "bold"), bg=BG_MAIN, fg=FG_TEXT, anchor="w").pack(anchor="w")
            tk.Label(left, text=opis, font=(FONT_FAMILY, 9, "bold"), bg=BG_MAIN, fg=FG_MUTED, anchor="w", wraplength=290, justify="left").pack(anchor="w")
            self._przycisk(
                box,
                f"Kup ({formatowanie(cena)}$)",
                akcja,
                width=13,
                pady=7
            ).pack(side="right", padx=(10, 0))
        self._przycisk(wrapper, "Powrót do menu", self.pokaz_menu, width=22, pady=9).pack(pady=(18, 0))

    def _sprawdz_stac_cie(self, cena):
        if self.dolary < cena:
            self._pokaz_blad_walidacji(
                "Brak środków",
                f"Potrzebujesz {formatowanie(cena)}$, a masz tylko {formatowanie(self.dolary)}$!"
            )
            return False
        return True

    def kup_podpowiedz(self):
        if not self._sprawdz_stac_cie(CENA_PODPOWIEDZI):
            return
        self.dolary -= CENA_PODPOWIEDZI
        self.podpowiedzi += 1
        self.zapisz_dane()
        self.pokaz_sklep("Kupiono podpowiedź!")

    def kup_booster(self):
        if not self._sprawdz_stac_cie(CENA_BOOSTERA):
            return
        self.dolary -= CENA_BOOSTERA
        self.booster_gry += BOOSTER_GIER
        self.zapisz_dane()
        self.pokaz_sklep(f"Kupiono booster MMR!")

    def pokaz_bonusy(self, komunikat="", kolor=SUCCESS):
        self._wyczysc_ekran()
        card = self._karta(pady=22)
        wrapper = tk.Frame(card, bg=BG_CARD, width=560)
        wrapper.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(
            wrapper,
            text="BONUSY",
            font=(FONT_FAMILY, 20, "bold"),
            bg=BG_CARD,
            fg=PURPLE_DARK
        ).pack(pady=(0, 6))
        tk.Label(
            wrapper,
            text=f"Twoje saldo: {formatowanie(self.dolary)}$",
            font=(FONT_FAMILY, 12, "bold"),
            bg=BG_CARD,
            fg=FG_MUTED
        ).pack(pady=(0, 4))
        if komunikat:
            tk.Label(
                wrapper,
                text=komunikat,
                font=(FONT_FAMILY, 12, "bold"),
                bg=BG_CARD,
                fg=kolor,
                height=1
            ).pack(pady=(0, 6))
        dostepne = self.dostepne_bonusy_hazardzisty()
        box1 = tk.Frame(wrapper, bg=BG_MAIN, padx=18, pady=12, highlightbackground="#334155", highlightthickness=1)
        box1.pack(fill="x", pady=6)
        left1 = tk.Frame(box1, bg=BG_MAIN)
        left1.pack(side="left", fill="y")
        tk.Label(left1, text=f"Bonus Bankruta ({formatowanie(BONUS_BANKRUTA)}$)", font=(FONT_FAMILY, 12, "bold"), bg=BG_MAIN, fg=FG_TEXT, anchor="w").pack(anchor="w")
        tk.Label(
            left1,
            text=f"Dostępny tylko przy saldzie 0$.",
            font=(FONT_FAMILY, 9, "bold"),
            bg=BG_MAIN,
            fg=FG_MUTED,
            anchor="w",
            wraplength=290,
            justify="left"
        ).pack(anchor="w")
        btn1 = self._przycisk(box1, "Odbierz", self.odbierz_bonus_bankruta, width=13, pady=7)
        btn1.pack(side="right", padx=(10, 0))
        if self.dolary != 0:
            self._wylacz_przycisk(btn1)
        box2 = tk.Frame(wrapper, bg=BG_MAIN, padx=18, pady=12, highlightbackground="#334155", highlightthickness=1)
        box2.pack(fill="x", pady=6)
        left2 = tk.Frame(box2, bg=BG_MAIN)
        left2.pack(side="left", fill="y")
        tk.Label(left2, text=f"Bonus Hazardzisty ({formatowanie(BONUS_HAZARDZISTY)}$)", font=(FONT_FAMILY, 12, "bold"), bg=BG_MAIN, fg=FG_TEXT, anchor="w").pack(anchor="w")
        tk.Label(
            left2,
            text=(
                f"Dostępny za każde {formatowanie(PROG_HAZARDZISTY)}$ łącznych wygranych.\t"
            ),
            font=(FONT_FAMILY, 9, "bold"),
            bg=BG_MAIN,
            fg=FG_MUTED,
            anchor="w",
            wraplength=290,
            justify="left"
        ).pack(anchor="w")
        btn2 = self._przycisk(box2, "Odbierz", self.odbierz_bonus_hazardzisty, width=13, pady=7)
        btn2.pack(side="right", padx=(10, 0))
        if dostepne <= 0:
            self._wylacz_przycisk(btn2)
        self._przycisk(wrapper, "Powrót", self.pokaz_dodatkowe, width=22, pady=9).pack(pady=(18, 0))

    def dostepne_bonusy_hazardzisty(self):
        return max(0, self.lacznie_wygrane // PROG_HAZARDZISTY - self.hazard_odebrane)

    def odbierz_bonus_bankruta(self):
        if self.dolary != 0:
            self._pokaz_blad_walidacji("Niedostępne", "Bonus bankruta jest dostępny tylko przy saldzie 0$!")
            return
        self.dolary += BONUS_BANKRUTA
        self.zapisz_dane()
        self.pokaz_bonusy(f"Odebrano bonus bankruta (+{formatowanie(BONUS_BANKRUTA)}$)")

    def odbierz_bonus_hazardzisty(self):
        ile = self.dostepne_bonusy_hazardzisty()
        if ile <= 0:
            self._pokaz_blad_walidacji(
                "Niedostępne",
                f"Wygraj jeszcze {formatowanie(PROG_HAZARDZISTY - (self.lacznie_wygrane % PROG_HAZARDZISTY))}$ aby odblokować bonus!"
            )
            return
        kwota = ile * BONUS_HAZARDZISTY
        self.hazard_odebrane += ile
        self.dolary += kwota
        self.zapisz_dane()
        self.pokaz_bonusy(f"Odebrano bonus hazardzisty (+{formatowanie(kwota)}$)")

    def konfiguracja_gry(self, mode):
        self.mode = mode
        if mode == "ranked":
            self.rozpocznij_gre(min_val=10, max_val=100, obstawione=0)
            return
        self._wyczysc_ekran()
        card = self._karta(pady=24)
        center = tk.Frame(card, bg=BG_CARD)
        center.place(relx=0.5, rely=0.5, anchor="center")
        if mode == "unranked":
            tk.Label(center, text="TRYB NIERANKINGOWY", font=(FONT_FAMILY, 18, "bold"), bg=BG_CARD, fg=PURPLE_DARK).pack(pady=(0, 14))
            tk.Label(center, text="Minimalna liczba (min. 5):", font=(FONT_FAMILY, 12, "bold"), bg=BG_CARD, fg=FG_TEXT).pack()
            entry_min = tk.Entry(
                center,
                font=(FONT_FAMILY, 12, "bold"),
                bg=BG_INPUT,
                fg=FG_TEXT,
                disabledbackground=BG_INPUT,
                disabledforeground=FG_MUTED,
                insertbackground=PURPLE_LIGHT,
                highlightthickness=1,
                highlightbackground=FG_TEXT,
                highlightcolor=PURPLE_DARK,
                justify="center",
                width=16
            )
            entry_min.insert(0, "10")
            entry_min.pack(pady=(4, 12))
            tk.Label(center, text="Maksymalna liczba (min. 10, większa od min):", font=(FONT_FAMILY, 12, "bold"), bg=BG_CARD, fg=FG_TEXT).pack()
            entry_max = tk.Entry(
                center,
                font=(FONT_FAMILY, 12, "bold"),
                bg=BG_INPUT,
                fg=FG_TEXT,
                disabledbackground=BG_INPUT,
                disabledforeground=FG_MUTED,
                insertbackground=PURPLE_LIGHT,
                highlightthickness=1,
                highlightbackground=FG_TEXT,
                highlightcolor=PURPLE_DARK,
                justify="center",
                width=16
            )
            entry_max.insert(0, "100")
            entry_max.pack(pady=(4, 18))
            def zatwierdz_unranked():
                try:
                    w_min = int(entry_min.get())
                    w_max = int(entry_max.get())
                except ValueError:
                    self._pokaz_blad_walidacji("Błąd", "Wpisz poprawne liczby!")
                    return
                if w_min < 5 or w_max < 10 or w_min >= w_max:
                    self._pokaz_blad_walidacji(
                        "Błędny przedział",
                        "Minimalna => 5, maksymalna => 10 oraz minimalna < maksymalnej!",
                    )
                    return
                self.rozpocznij_gre(min_val=w_min, max_val=w_max, obstawione=0)
            self._przycisk(center, "Rozpocznij grę", zatwierdz_unranked, width=22).pack(pady=6)
        elif mode == "wager":
            tk.Label(center, text="TRYB ZAKŁADOWY", font=(FONT_FAMILY, 18, "bold"), bg=BG_CARD, fg=WARNING).pack(pady=(0, 8))
            tk.Label(
                center,
                text=f"Twoje saldo: {formatowanie(self.dolary)}$\nZgadnij liczbę (10–100) w max 5 próbach, aby podwoić stawkę!",
                font=(FONT_FAMILY, 12, "bold"),
                bg=BG_CARD,
                fg=FG_MUTED,
                justify="center"
            ).pack(pady=(0, 14))
            if self.dolary < 100:
                tk.Label(center, text="Masz za mało dolarów (minimum to 100$).", font=(FONT_FAMILY, 12, "bold"), bg=BG_CARD, fg=DANGER).pack(pady=10)
            else:
                tk.Label(center, text="Kwota zakładu (min. 100$):", font=(FONT_FAMILY, 12, "bold"), bg=BG_CARD, fg=FG_TEXT).pack()
                entry_bet = tk.Entry(
                    center,
                    font=(FONT_FAMILY, 12, "bold"),
                    bg=BG_INPUT,
                    fg=FG_TEXT,
                    disabledbackground=BG_INPUT,
                    disabledforeground=FG_MUTED,
                    insertbackground=PURPLE_LIGHT,
                    highlightthickness=1,
                    highlightbackground=FG_TEXT,
                    highlightcolor=PURPLE_DARK,
                    justify="center",
                    width=16
                )
                entry_bet.insert(0, "100")
                entry_bet.pack(pady=(6, 16))
                def zatwierdz_wager():
                    try:
                        stawka = int(entry_bet.get())
                    except ValueError:
                        self._pokaz_blad_walidacji("Błąd", "Wpisz poprawną kwotę!")
                        return
                    if stawka < 100 or stawka > self.dolary:
                        self._pokaz_blad_walidacji(
                            "Błędna kwota",
                            f"Kwota musi wynosić od 100$ do {formatowanie(self.dolary)}$!",
                        )
                        return
                    self.dolary -= stawka
                    self.rozpocznij_gre(min_val=10, max_val=100, obstawione=stawka)
                self._przycisk(center, "Postaw i zacznij", zatwierdz_wager, width=22).pack(pady=6)
        self._przycisk(center, "Powrót do trybów", self.pokaz_tryby, width=22, pady=8).pack(pady=(14, 0))

    def rozpocznij_gre(self, min_val, max_val, obstawione):
        self.min_val = min_val
        self.max_val = max_val
        self.obstawione = obstawione
        self.losowa = random.randint(min_val, max_val)
        self.dzielnik = 1
        self.gra_w_toku = True
        self.podpowiedz_uzyta = False
        self.btn_hint = None
        self.lbl_hint = None
        self.btn_replay = None
        self._wyczysc_ekran()
        card = self._karta(pady=22)
        center = tk.Frame(card, bg=BG_CARD)
        center.place(relx=0.5, rely=0.5, anchor="center")
        tytul_trybu = {
            "unranked": "TRYB NIERANKINGOWY",
            "ranked": "TRYB RANKINGOWY",
            "wager": f"TRYB ZAKŁADOWY"
        }[self.mode]
        tk.Label(center, text=tytul_trybu, font=(FONT_FAMILY, 15, "bold"), bg=BG_CARD, fg=PURPLE_DARK).pack()
        tk.Label(
            center,
            text=f"Wylosowano liczbę z przedziału <{min_val};{max_val}>",
            font=(FONT_FAMILY, 12, "bold"),
            bg=BG_CARD,
            fg=FG_TEXT
        ).pack(pady=(4, 12))
        self.lbl_proba = tk.Label(
            center,
            text="Próba nr 1" + (" / 5" if self.mode == "wager" else ""),
            font=(FONT_FAMILY, 12, "bold"),
            bg=BG_CARD,
            fg=FG_MUTED
        )
        self.lbl_proba.pack()
        self.wynik_frame = tk.Frame(center, bg=BG_CARD, pady=12)
        self.wynik_frame.pack()
        self.lbl_podpowiedz = tk.Label(
            self.wynik_frame,
            text="Wpisz swoją liczbę i wciśnij Enter.",
            font=(FONT_FAMILY, 13, "bold"),
            bg=BG_CARD,
            fg=FG_TEXT,
            justify="center"
        )
        self.lbl_podpowiedz.pack()
        self.ranga_wynik_frame = tk.Frame(self.wynik_frame, bg=BG_CARD)
        self.ranga_wynik_frame.pack()
        self.lbl_ranga_prefix = tk.Label(
            self.ranga_wynik_frame,
            text="",
            font=(FONT_FAMILY, 12, "bold"),
            bg=BG_CARD,
            fg=FG_TEXT
        )
        self.lbl_ranga_prefix.pack(side="left")
        self.lbl_ranga_nazwa = tk.Label(
            self.ranga_wynik_frame,
            text="",
            font=(FONT_FAMILY, 12, "bold"),
            bg=BG_CARD,
            fg=FG_TEXT
        )
        self.lbl_ranga_nazwa.pack(side="left")
        self.lbl_ranga_zmiana = tk.Label(
            self.ranga_wynik_frame,
            text="",
            font=(FONT_FAMILY, 12, "bold"),
            bg=BG_CARD,
            fg=FG_TEXT
        )
        self.lbl_ranga_zmiana.pack(side="left")
        self.entry_zgad = tk.Entry(
            center,
            font=(FONT_FAMILY, 16, "bold"),
            bg=BG_INPUT,
            fg=FG_TEXT,
            disabledbackground=BG_MUTED,
            disabledforeground=FG_MUTED,
            insertbackground=PURPLE_LIGHT,
            highlightthickness=1,
            highlightbackground=FG_TEXT,
            highlightcolor=PURPLE_DARK,
            justify="center",
            width=12
        )
        self.entry_zgad.pack(pady=(0, 10))
        self.entry_zgad.focus_set()
        self.entry_zgad.bind("<Return>", lambda _e: self.sprawdz_liczbe())
        self.btn_zgadnij = self._przycisk(center, "Zgadnij", self.sprawdz_liczbe, width=22)
        self.btn_zgadnij.pack()

        if self.mode == "ranked":
            self.btn_hint = self._przycisk(
                center,
                f"Użyj podpowiedzi ({self.podpowiedzi})",
                self.uzyj_podpowiedzi,
                width=22,
                pady=8
            )
            self.btn_hint.pack(pady=(6, 0))
            if self.podpowiedzi <= 0:
                self._wylacz_przycisk(self.btn_hint)
            self.lbl_hint = tk.Label(
                center,
                text="",
                font=(FONT_FAMILY, 10, "bold"),
                bg=BG_CARD,
                fg=PURPLE_LIGHT
            )

        self.btn_replay = self._przycisk(center, "Zagraj ponownie", self._zagraj_ponownie, width=22, pady=8)
        self._wylacz_przycisk(self.btn_replay)
        self.btn_replay.pack(pady=(6, 0))

        self.btn_powrot_menu = self._przycisk(center, "Powrót do menu", self._powrot_do_menu_z_gry, width=22, pady=8)
        self.btn_powrot_menu.config(state="disabled", bg=BTN_BASE, fg=FG_MUTED)
        self.btn_powrot_menu.pack(pady=(6, 0))

    def uzyj_podpowiedzi(self):
        if not self.gra_w_toku or self.mode != "ranked":
            return
        if self.podpowiedz_uzyta or self.podpowiedzi <= 0:
            return
        self.podpowiedzi -= 1
        self.podpowiedz_uzyta = True
        szer = SZEROKOSC_PODPOWIEDZI
        najmniejszy_start = max(self.min_val, self.losowa - szer + 1)
        najwiekszy_start = min(self.losowa, self.max_val - szer + 1)
        start = random.randint(najmniejszy_start, najwiekszy_start)
        koniec = start + szer - 1
        self.zapisz_dane()
        self.lbl_hint.config(text=f"Podpowiedź: Liczba jest w przedziale <{start};{koniec}>")
        self.btn_hint.config(text=f"Użyj podpowiedzi ({self.podpowiedzi})")
        self.lbl_hint.pack(pady=(4, 0), before=self.btn_replay)
        self._wylacz_przycisk(self.btn_hint)
        self.entry_zgad.focus_set()

    def sprawdz_liczbe(self):
        try:
            liczba = int(self.entry_zgad.get())
        except ValueError:
            self.lbl_podpowiedz.config(text="To musi być liczba całkowita!", fg=DANGER)
            self.entry_zgad.delete(0, "end")
            return
        self.entry_zgad.delete(0, "end")
        if liczba == self.losowa:
            self._obsluz_wygrana()
            return
        if self.mode == "wager":
            if self.dzielnik >= 5:
                self._obsluz_przegrana_zaklad()
                return
            self.dzielnik += 1
            self.lbl_proba.config(text=f"Próba {self.dzielnik} / 5")
        else:
            self.dzielnik += 1
            self.lbl_proba.config(text=f"Próba {self.dzielnik}")
        if abs(liczba - self.losowa) == 1:
            self.lbl_podpowiedz.config(text="Jesteś bardzo blisko!", fg=WARNING)
        elif liczba < self.losowa:
            self.lbl_podpowiedz.config(text="Za mało!", fg=TOO_LESS)
        else:
            self.lbl_podpowiedz.config(text="Za dużo!", fg=TOO_MUCH)

    def _zakoncz_gre_ui(self):
        self.entry_zgad.config(state="disabled", disabledforeground=FG_MUTED, highlightbackground=FG_MUTED, highlightcolor=FG_MUTED)
        self.btn_zgadnij.config(state="disabled", bg=BTN_BASE, fg=FG_MUTED)
        if self.btn_hint is not None:
            self._wylacz_przycisk(self.btn_hint)
        if self.btn_replay is not None:
            self.btn_replay.config(state="normal", bg=BTN_BASE, fg=FG_TEXT, cursor="hand2")
        self.btn_powrot_menu.config(state="normal", bg=BTN_BASE, fg=FG_TEXT)

    def _obsluz_wygrana(self):
        self.lbl_ranga_prefix.config(text="")
        self.lbl_ranga_nazwa.config(text="")
        self.lbl_ranga_zmiana.config(text="")
        kolor_komunikatu = SUCCESS
        if self.mode == "unranked":
            zdobyte = 100.0 / self.dzielnik
            self.ogolne_pkt += zdobyte
            self.nierank_gry += 1
            self.nierank_proby += self.dzielnik
            komunikat = (
                f"Gratulacje! Udało ci się zgadnąć przy {self.dzielnik} próbie!\n"
                f"Zdobywasz {zdobyte:.2f} punktów!"
            )
        elif self.mode == "ranked":
            stara_ranga = self.zaladuj_range()
            mmr = 30 - (5 * self.dzielnik)
            bonus_mmr = 0
            if self.booster_gry > 0:
                bonus_mmr = BOOSTER_MMR
                self.booster_gry -= 1
            mmr += bonus_mmr
            self.ogolne_mmr += mmr
            self.rank_gry += 1
            self.rank_proby += self.dzielnik
            nowa_ranga = self.zaladuj_range()
            if mmr > 0:
                komunikat = (
                    f"Gratulacje! Udało ci się zgadnąć przy {self.dzielnik} próbie!\n"
                    f"Zdobywasz {mmr} MMR!"
                )
            elif mmr == 0:
                komunikat = (
                    f"Udało ci się zgadnąć przy {self.dzielnik} próbie!\n"
                    "Nie zdobywasz żadnego MMR!"
                )
                kolor_komunikatu = WARNING
            else:
                komunikat = (
                    f"Udało ci się zgadnąć przy {self.dzielnik} próbie!\n"
                    f"Tracisz {abs(mmr)} MMR!"
                )
                kolor_komunikatu = DANGER
            if bonus_mmr:
                komunikat += f" (+{bonus_mmr} MMR Boost)"
            self.lbl_ranga_prefix.config(text="Twoja aktualna ranga:", fg=FG_TEXT)
            self.lbl_ranga_nazwa.config(text=nowa_ranga, fg=self.kolor_rangi(nowa_ranga))
            kolejnosc = list(KOLORY_RANG)
            if kolejnosc.index(nowa_ranga) > kolejnosc.index(stara_ranga):
                self.lbl_ranga_zmiana.config(text="(awans!)", fg=SUCCESS)
            elif kolejnosc.index(nowa_ranga) < kolejnosc.index(stara_ranga):
                self.lbl_ranga_zmiana.config(text="(degrad!)", fg=DANGER)
        else:
            wygrana = self.obstawione * 2
            self.dolary += wygrana
            self.lacznie_wygrane += wygrana
            if self.najwieksza_wygrana < wygrana:
                self.najwieksza_wygrana = wygrana
            komunikat = (
                f"Gratulacje! Udało ci się zgadnąć przy {self.dzielnik} próbie!\n"
                f"Wygrywasz {formatowanie(wygrana)}$! Łącznie masz {formatowanie(self.dolary)}$!"
            )
        self.gra_w_toku = False
        self.zapisz_dane()
        self.lbl_podpowiedz.config(text=komunikat, fg=kolor_komunikatu)
        self._zakoncz_gre_ui()

    def _obsluz_przegrana_zaklad(self):
        komunikat = (
            f"Skończyły ci się próby! Wylosowana liczba to: {self.losowa}\n"
            f"Tracisz {formatowanie(self.obstawione)}$! Łącznie masz {formatowanie(self.dolary)}$!"
        )
        self.gra_w_toku = False
        self.zapisz_dane()
        self.lbl_podpowiedz.config(text=komunikat, fg=DANGER)
        self._zakoncz_gre_ui()

    def pokaz_ustawienia(self):
        self._wyczysc_ekran()
        self.wybrany_fullscreen = self.fullscreen
        card = self._karta(pady=26)
        center = tk.Frame(card, bg=BG_CARD)
        center.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(center, text="USTAWIENIA", font=(FONT_FAMILY, 20, "bold"), bg=BG_CARD, fg=PURPLE_DARK).pack(pady=(0, 22))
        def odswiez_przycisk_ekranu():
            btn_ekran.config(text="Pełen ekran: WŁ" if self.wybrany_fullscreen else "Pełen ekran: WYŁ")
        def przelacz_wybor():
            self.wybrany_fullscreen = not self.wybrany_fullscreen
            odswiez_przycisk_ekranu()
        def zastosuj_ekran():
            self._zastosuj_tryb_ekranu(self.wybrany_fullscreen)
            odswiez_przycisk_ekranu()
        self._odswiez_ekran_ustawien = odswiez_przycisk_ekranu
        btn_ekran = self._przycisk(center, "", przelacz_wybor, width=28)
        btn_ekran.pack(pady=7)
        odswiez_przycisk_ekranu()
        self._przycisk(center, "Resetuj statystyki", self._otworz_okno_resetu, width=28).pack(pady=7)
        bottom_row = tk.Frame(center, bg=BG_CARD)
        bottom_row.pack(pady=(18, 0))
        self._przycisk(bottom_row, "Zastosuj", zastosuj_ekran, width=13, pady=9).pack(side="left", padx=(0, 6))
        self._przycisk(bottom_row, "Powrót", self.pokaz_menu, width=13, pady=9).pack(side="left", padx=(6, 0))

    def pokaz_dodatkowe(self):
        self._wyczysc_ekran()
        card = self._karta(pady=24)
        center = tk.Frame(card, bg=BG_CARD)
        center.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(center, text="OPCJE DODATKOWE", font=(FONT_FAMILY, 20, "bold"), bg=BG_CARD, fg=PURPLE_DARK).pack(pady=(0, 20))
        self._przycisk(center, "Statystyki", self.pokaz_statystyki, width=26).pack(pady=7)
        self._przycisk(center, "Informacje", self.pokaz_informacje, width=26).pack(pady=7)
        self._przycisk(center, "Nowości", self.pokaz_nowosci, width=26).pack(pady=7)
        self._przycisk(center, "Bonusy", self.pokaz_bonusy, width=26).pack(pady=7)
        self._przycisk(center, "Powrót do menu", self.pokaz_menu, width=26).pack(pady=7)

    def pokaz_statystyki(self):
        self._wyczysc_ekran()
        card = self._karta(pady=20)
        center = tk.Frame(card, bg=BG_CARD)
        center.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(center, text="STATYSTYKI", font=(FONT_FAMILY, 20, "bold"), bg=BG_CARD, fg=PURPLE_DARK).pack(pady=(0, 14))
        srednia_nierank = (self.nierank_proby / self.nierank_gry) if self.nierank_gry > 0 else 0.0
        srednia_rank = (self.rank_proby / self.rank_gry) if self.rank_gry > 0 else 0.0
        aktualna_ranga = self.zaladuj_range()
        fragmenty = [
            ("NIERANKINGOWE\n", "header"),
            (f"• Zdobyte punkty: {self.ogolne_pkt:.2f}  |  Średnia prób: {srednia_nierank:.2f}\n\n", "text"),
            ("RANKINGOWE\n", "header"),
            ("• Ranga: ", "text"),
            (aktualna_ranga, "text", self.kolor_rangi(aktualna_ranga)),
            (f" ({self.ogolne_mmr} MMR)  |  Średnia prób: {srednia_rank:.2f}\n\n", "text"),
            ("ZAKŁADY\n", "header"),
            (
                f"• Saldo: {formatowanie(self.dolary)}$  |  Największa wygrana: {formatowanie(self.najwieksza_wygrana)}$"
                f"  |  Łącznie wygrane: {formatowanie(self.lacznie_wygrane)}$\n\n",
                "text"
            ),
            ("EKWIPUNEK\n", "header"),
            (f"• Podpowiedzi: {self.podpowiedzi}  |  Booster MMR: {self.booster_gry} gier", "text"),
        ]
        self._panel_tekstowy(center, fragmenty, height=14, width=58)
        self._przycisk(center, "Powrót", self.pokaz_dodatkowe, width=20, pady=8).pack()

    def pokaz_informacje(self):
        self._wyczysc_ekran()
        card = self._karta(pady=20)
        center = tk.Frame(card, bg=BG_CARD)
        center.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(center, text="INFORMACJE", font=(FONT_FAMILY, 20, "bold"), bg=BG_CARD, fg=PURPLE_DARK).pack(pady=(0, 14))
        fragmenty = [
            ("Zgadywacz", "header"),
            (" to gra, w której musisz odgadnąć wylosowaną liczbę z określonego przedziału.\n\n", "text"),
            ("• Tryb nierankingowy: ", "header"),
            ("Ustalasz swój własny przedział i zdobywasz punkty ogólne.\n", "text"),
            ("• Tryb rankingowy: ", "header"),
            ("Masz stały przedział 10–100 i zdobywasz punkty MMR, dzięki którym odblokowujesz kolejne rangi.\n", "text"),
            ("• Tryb zakładowy: ", "header"),
            (
                "Obstawiasz dolary (min. 100$) i w maksymalnie 5 prób musisz zgadnąć "
                "liczbę z zakresu 10–100. Wygrana podwaja stawkę, a przegrana zabiera obstawioną kwotę.\n",
                "text",
            )
        ]
        self._panel_tekstowy(center, fragmenty, height=12, width=58)
        self._przycisk(center, "Powrót", self.pokaz_dodatkowe, width=20, pady=8).pack()

    def pokaz_nowosci(self):
        self._wyczysc_ekran()
        card = self._karta(pady=20)
        center = tk.Frame(card, bg=BG_CARD)
        center.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(center, text="NOWOŚCI", font=(FONT_FAMILY, 20, "bold"), bg=BG_CARD, fg=PURPLE_DARK).pack(pady=(0, 14))
        fragmenty = [
            ("WERSJA 1.3:\n", "header"),
            ("• Dodano sklep rankingowego\n", "text"),
            ("• Dodano zakładkę z bonusami\n", "text"),
            ("• Dodano ekwipunek do statystyk\n", "text"),
            ("• Dodano przycisk ponownego zagrania trybu\n", "text"),
            ("WERSJA 1.2:\n", "header"),
            ("• Przeniesiono grę z konsoli do okienka\n", "text"),
            ("• Dodano opcję pełnego ekranu do ustawień\n", "text"),
            ("• Dodano więcej zabezpieczeń\n", "text"),
            ("WERSJA 1.1:\n", "header"),
            ("• Dodano tryb zakładów i walutę do trybu\n", "text"),
            ("• Dodano zakładkę z dodatkowymi opcjami\n", "text"),
            ("• Dodano resetowanie statystyk w ustawieniach\n", "text"),
            ("• Naprawiono błędy z brakiem powrotu do menu", "text")
        ]
        self._panel_tekstowy(center, fragmenty, height=15, width=58)
        self._przycisk(center, "Powrót", self.pokaz_dodatkowe, width=20, pady=8).pack()

    def wyjdz_z_gry(self):
        self.zapisz_dane()
        self.root.destroy()
        sys.exit(0)

if __name__ == "__main__":
    root = tk.Tk()
    app = ZgadywaczApp(root)
    root.mainloop()

# MADE BY FRYTA
