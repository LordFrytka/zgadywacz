import json
import os
import random
import sys
import tkinter as tk

SAVE_FILE = "zapis.json"
BACKGROUND_MAIN = "#0f172a"
BACKGROUND_CARD = "#1e293b"
BACKGROUND_INPUT = "#0f172a"
FOREGROUND_TEXT = "#f8fafc"
FOREGROUND_MUTED = "#94a3b8"
BACKGROUND_MUTED = "#3b3f44"
PURPLE_DARK = "#a855f7"
PURPLE_LIGHT = "#c084fc"
TOO_HIGH = "#63CA60"
TOO_LOW = "#d31b1b"
SUCCESS = "#22c55e"
WARNING = "#f59e0b"
DANGER = "#ef4444"
BUTTON_BASE = "#334155"
SCROLLBAR_THUMB = "#475569"
HINT_PRICE = 10000
BOOSTER_PRICE = 25000
BOOSTER_GAMES = 5
BOOSTER_MMR = 10
HINT_RANGE_WIDTH = 10
BANKRUPT_BONUS = 500
GAMBLER_BONUS = 5000
GAMBLER_BONUS_THRESHOLD = 25000
FONT_FAMILY = "Trebuchet MS"
RANK_COLORS = {
    "Stracono": "#ef4444",
    "Brąz": "#d97706",
    "Srebro": "#cbd5e1",
    "Złoto": "#facc15",
    "Platyna": "#5eead4",
    "Diament": "#67e8f9",
    "Master Zgadywacz": "#e879f9"
}
LEGACY_SAVE_KEYS = {
    "total_mmr": "ogolne_mmr",
    "total_points": "ogolne_pkt",
    "dollars": "dolary",
    "unranked_games": "nierank_gry",
    "unranked_attempts": "nierank_proby",
    "ranked_games": "rank_gry",
    "ranked_attempts": "rank_proby",
    "biggest_win": "najwieksza_wygrana",
    "total_winnings": "lacznie_wygrane",
    "hints": "podpowiedzi",
    "booster_games_left": "booster_gry",
    "gambler_bonuses_claimed": "hazard_odebrane",
}

def format_number(number):
    return f"{int(number):,}".replace(",", ".")

class StyledScrollbar(tk.Canvas):
    MINIMUM_THUMB_LENGTH = 28
    THUMB_WIDTH = 6
    def __init__(self, parent, command, width=12):
        super().__init__(
            parent,
            width=width,
            bg=BACKGROUND_MAIN,
            highlightthickness=0,
            bd=0
        )
        self.command = command
        self.first = 0.0
        self.last = 1.0
        self._thumb_top = 0.0
        self._thumb_length = 0.0
        self._drag_offset = None
        self._hovered = False
        self.bind("<Configure>", lambda _event: self._draw())
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<B1-Motion>", self._on_drag)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
    def set(self, first, last):
        self.first = float(first)
        self.last = float(last)
        self._draw()
    def _draw(self):
        self.delete("all")
        height = self.winfo_height()
        span = self.last - self.first
        if height <= 1 or span >= 1.0:
            self._thumb_length = 0.0
            return
        self._thumb_length = max(span * height, self.MINIMUM_THUMB_LENGTH)
        scrollable = 1.0 - span
        track_length = height - self._thumb_length
        self._thumb_top = (self.first / scrollable) * track_length if scrollable > 0 else 0.0
        center_x = self.winfo_width() / 2
        radius = self.THUMB_WIDTH / 2
        active = self._hovered or self._drag_offset is not None
        self.create_line(
            center_x,
            self._thumb_top + radius,
            center_x,
            self._thumb_top + self._thumb_length - radius,
            width=self.THUMB_WIDTH,
            capstyle="round",
            fill=PURPLE_LIGHT if active else SCROLLBAR_THUMB
        )
    def _on_press(self, event):
        if self._thumb_length <= 0:
            return
        if self._thumb_top <= event.y <= self._thumb_top + self._thumb_length:
            self._drag_offset = event.y - self._thumb_top
            self._draw()
        elif event.y < self._thumb_top:
            self.command("scroll", -1, "pages")
        else:
            self.command("scroll", 1, "pages")
    def _on_drag(self, event):
        if self._drag_offset is None:
            return
        track_length = self.winfo_height() - self._thumb_length
        if track_length <= 0:
            return
        position = min(max(event.y - self._drag_offset, 0), track_length) / track_length
        span = self.last - self.first
        self.command("moveto", position * (1.0 - span))
    def _on_release(self, _event):
        self._drag_offset = None
        self._draw()
    def _on_enter(self, _event):
        self._hovered = True
        self._draw()
    def _on_leave(self, _event):
        self._hovered = False
        self._draw()

class NumGuesser:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("ZGADYWACZ - Edycja Okienkowa")
        self._window_geometry = "700x720"
        self.root.geometry(self._window_geometry)
        self.root.minsize(600, 680)
        self.root.configure(bg=BACKGROUND_MAIN)
        self.set_default_data()
        self.load_data()
        self.fullscreen = False
        self.selected_fullscreen = False
        self._refresh_settings_screen = None
        self._back_action = None
        self.mode = None
        self.secret_number = 0
        self.current_attempt = 1
        self.wagered_amount = 0
        self.min_value = 10
        self.max_value = 100
        self.game_in_progress = False
        self.hint_used = False
        self.hint_button = None
        self.hint_label = None
        self.replay_button = None
        self._build_skeleton()
        self.show_menu()
        self.root.protocol("WM_DELETE_WINDOW", self.quit_game)
        self.root.bind("<F11>", self._toggle_fullscreen)
        self.root.bind("<Configure>", self._adjust_to_size)
        self.root.bind("<KeyPress-r>", self._on_replay_key)
        self.root.bind("<KeyPress-R>", self._on_replay_key)
        self.root.bind("<BackSpace>", self._on_back_key)

    def set_default_data(self):
        self.total_mmr = 200
        self.total_points = 0.0
        self.dollars = 1000
        self.unranked_games = 0
        self.unranked_attempts = 0
        self.ranked_games = 0
        self.ranked_attempts = 0
        self.biggest_win = 0
        self.total_winnings = 0
        self.hints = 0
        self.booster_games_left = 0
        self.gambler_bonuses_claimed = 0

    def load_data(self):
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, "r", encoding="utf-8") as save_file:
                    data = json.load(save_file)
                    def read_value(key, default):
                        return data.get(key, data.get(LEGACY_SAVE_KEYS[key], default))
                    self.total_mmr = read_value("total_mmr", 200)
                    self.total_points = float(read_value("total_points", 0.0))
                    self.dollars = read_value("dollars", 1000)
                    self.unranked_games = read_value("unranked_games", 0)
                    self.unranked_attempts = read_value("unranked_attempts", 0)
                    self.ranked_games = read_value("ranked_games", 0)
                    self.ranked_attempts = read_value("ranked_attempts", 0)
                    self.biggest_win = read_value("biggest_win", 0)
                    self.total_winnings = read_value("total_winnings", 0)
                    self.hints = read_value("hints", 0)
                    self.booster_games_left = read_value("booster_games_left", 0)
                    self.gambler_bonuses_claimed = read_value("gambler_bonuses_claimed", 0)
            except Exception:
                pass

    def save_data(self):
        data = {
            "total_mmr": self.total_mmr,
            "total_points": self.total_points,
            "dollars": self.dollars,
            "unranked_games": self.unranked_games,
            "unranked_attempts": self.unranked_attempts,
            "ranked_games": self.ranked_games,
            "ranked_attempts": self.ranked_attempts,
            "biggest_win": self.biggest_win,
            "total_winnings": self.total_winnings,
            "hints": self.hints,
            "booster_games_left": self.booster_games_left,
            "gambler_bonuses_claimed": self.gambler_bonuses_claimed,
        }
        with open(SAVE_FILE, "w", encoding="utf-8") as save_file:
            json.dump(data, save_file, ensure_ascii=False, indent=4)

    def get_rank(self):
        if self.total_mmr <= 0:
            self.total_mmr = 0
            return "Stracono"
        elif self.total_mmr < 500:
            return "Brąz"
        elif self.total_mmr < 1000:
            return "Srebro"
        elif self.total_mmr < 1500:
            return "Złoto"
        elif self.total_mmr < 2000:
            return "Platyna"
        elif self.total_mmr < 2500:
            return "Diament"
        else:
            return "Master Zgadywacz"

    def get_rank_color(self, rank=None):
        if rank is None:
            rank = self.get_rank()
        return RANK_COLORS.get(rank, FOREGROUND_TEXT)

    def _apply_screen_mode(self, enable_fullscreen: bool):
        if enable_fullscreen and not self.fullscreen:
            if self.root.state() == "normal":
                self._window_geometry = self.root.geometry()
            self.fullscreen = True
            self.selected_fullscreen = True
            self.root.attributes("-fullscreen", True)
            self.root.update_idletasks()
        elif not enable_fullscreen and self.fullscreen:
            self.fullscreen = False
            self.selected_fullscreen = False
            self.root.attributes("-fullscreen", False)
            self.root.state("normal")
            self.root.geometry(self._window_geometry)
            self.root.update_idletasks()

    def _refresh_screen_button_if_present(self):
        if self._refresh_settings_screen:
            self._refresh_settings_screen()

    def _toggle_fullscreen(self, _event=None):
        self._apply_screen_mode(not self.fullscreen)
        self._refresh_screen_button_if_present()

    def _adjust_to_size(self, _event=None):
        if not self.fullscreen and self.root.state() == "normal":
            geometry = self.root.geometry()
            if geometry:
                self._window_geometry = geometry
        width = max(self.root.winfo_width(), 600)
        padding = 64 if width > 1000 else 24
        self.container.config(padx=padding, pady=padding)

    def _build_skeleton(self):
        self.container = tk.Frame(self.root, bg=BACKGROUND_MAIN, padx=24, pady=24)
        self.container.pack(fill="both", expand=True)

    def _clear_screen(self, back_action=None):
        self._refresh_settings_screen = None
        self._back_action = back_action
        self.replay_button = None
        for widget in self.container.winfo_children():
            widget.destroy()

    def _create_card(self, parent=None, padx=28, pady=24):
        card = tk.Frame(
            parent or self.container,
            bg=BACKGROUND_CARD,
            padx=padx,
            pady=pady,
            highlightbackground=PURPLE_DARK,
            highlightcolor=PURPLE_DARK,
            highlightthickness=1
        )
        card.pack(fill="both", expand=True)
        return card

    def _create_button(self, parent, text, command, width=28, pady=10, base_background=None, base_foreground=None, hover_background=None, hover_foreground=None):
        normal_background = base_background if base_background is not None else BUTTON_BASE
        normal_foreground = base_foreground if base_foreground is not None else FOREGROUND_TEXT
        hovered_background = hover_background if hover_background is not None else PURPLE_LIGHT
        hovered_foreground = hover_foreground if hover_foreground is not None else "#0f172a"
        button = tk.Button(
            parent,
            text=text,
            command=command,
            font=(FONT_FAMILY, 11, "bold"),
            bg=normal_background,
            fg=normal_foreground,
            activebackground=hovered_background,
            activeforeground=hovered_foreground,
            relief="flat",
            cursor="hand2",
            width=width,
            pady=pady,
            bd=0,
            highlightthickness=0
        )
        def on_enter(_event):
            if str(button["state"]) != "disabled":
                button.config(bg=hovered_background, fg=hovered_foreground)
        def on_leave(_event):
            if str(button["state"]) != "disabled":
                button.config(bg=normal_background, fg=normal_foreground)
        def on_press(_event):
            if str(button["state"]) != "disabled":
                button.config(bg=hovered_background, fg=hovered_foreground)
        def on_release(event):
            if str(button["state"]) != "disabled":
                inside = 0 <= event.x <= button.winfo_width() and 0 <= event.y <= button.winfo_height()
                button.config(
                    bg=hovered_background if inside else normal_background,
                    fg=hovered_foreground if inside else normal_foreground,
                )
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        button.bind("<ButtonPress-1>", on_press)
        button.bind("<ButtonRelease-1>", on_release)
        return button

    def _disable_button(self, button):
        button.config(state="disabled", bg=BUTTON_BASE, fg=FOREGROUND_MUTED, cursor="arrow")

    def _create_text_panel(self, parent, fragments, height=11, width=58):
        holder = tk.Frame(
            parent,
            bg=BACKGROUND_MAIN,
            highlightbackground="#334155",
            highlightcolor="#334155",
            highlightthickness=1
        )
        holder.pack(pady=(0, 16))
        text_widget = tk.Text(
            holder,
            font=(FONT_FAMILY, 10, "bold"),
            bg=BACKGROUND_MAIN,
            fg=FOREGROUND_TEXT,
            relief="flat",
            wrap="word",
            height=height,
            width=width,
            padx=18,
            pady=14,
            bd=0,
            highlightthickness=0,
            cursor="arrow"
        )
        scrollbar = StyledScrollbar(holder, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        text_widget.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns", padx=(0, 4), pady=6)
        text_widget.tag_configure("text", font=(FONT_FAMILY, 10, "bold"), foreground=FOREGROUND_TEXT)
        text_widget.tag_configure("header", font=(FONT_FAMILY, 12, "bold"), foreground=PURPLE_LIGHT)
        for text, style, *color in fragments:
            if color:
                tag_name = f"{style}_{color[0]}"
                font_config = (FONT_FAMILY, 12, "bold") if style == "header" else (FONT_FAMILY, 10, "bold")
                text_widget.tag_configure(tag_name, font=font_config, foreground=color[0])
                text_widget.insert("end", text, tag_name)
            else:
                text_widget.insert("end", text, style)
        text_widget.config(state="disabled")

        def on_mouse_wheel(event):
            if event.num == 4 or event.delta > 0:
                text_widget.yview_scroll(-3, "units")
            elif event.num == 5 or event.delta < 0:
                text_widget.yview_scroll(3, "units")
            return "break"

        for sequence in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            text_widget.bind(sequence, on_mouse_wheel)
            scrollbar.bind(sequence, on_mouse_wheel)
        return text_widget

    def _show_error_popup(self, title: str, message: str):
        window = tk.Toplevel(self.root)
        window.title(title)
        window.configure(bg=BACKGROUND_MAIN)
        window.resizable(False, False)
        window.transient(self.root)
        window.grab_set()
        frame = tk.Frame(
            window,
            bg=BACKGROUND_CARD,
            padx=24,
            pady=24,
            highlightbackground=PURPLE_DARK,
            highlightthickness=1
        )
        frame.pack(fill="both", expand=True, padx=24, pady=24)
        tk.Label(
            frame,
            text=title.upper(),
            font=(FONT_FAMILY, 18, "bold"),
            bg=BACKGROUND_CARD,
            fg=DANGER
        ).pack(pady=(0, 8))
        tk.Label(
            frame,
            text=message,
            font=(FONT_FAMILY, 12, "bold"),
            bg=BACKGROUND_CARD,
            fg=FOREGROUND_TEXT,
            justify="center",
            wraplength=340
        ).pack(pady=(0, 16))
        self._create_button(frame, "OK", window.destroy, width=16, pady=8).pack()
        window.bind("<BackSpace>", lambda _event: window.destroy())
        window.bind("<Escape>", lambda _event: window.destroy())
        window.update_idletasks()
        window_width = window.winfo_width()
        window_height = window.winfo_height()
        root_x = self.root.winfo_rootx()
        root_y = self.root.winfo_rooty()
        root_width = self.root.winfo_width()
        root_height = self.root.winfo_height()
        position_x = root_x + max((root_width - window_width) // 2, 0)
        position_y = root_y + max((root_height - window_height) // 2, 0)
        window.geometry(f"+{position_x}+{position_y}")
        window.focus_set()
        window.wait_window()

    def _open_reset_window(self):
        window = tk.Toplevel(self.root)
        window.title("Reset statystyk — ZGADYWACZ")
        window.configure(bg=BACKGROUND_MAIN)
        window.resizable(False, False)
        window.transient(self.root)
        window.grab_set()
        outer_frame = tk.Frame(
            window,
            bg=BACKGROUND_CARD,
            padx=24,
            pady=24,
            highlightbackground=PURPLE_DARK,
            highlightthickness=1
        )
        outer_frame.pack(fill="both", expand=True, padx=24, pady=24)
        title_label = tk.Label(
            outer_frame,
            text="RESET STATYSTYK",
            font=(FONT_FAMILY, 18, "bold"),
            bg=BACKGROUND_CARD,
            fg=PURPLE_LIGHT
        )
        title_label.pack(pady=(0, 10))
        info_frame = tk.Frame(
            outer_frame,
            bg=BACKGROUND_MAIN,
            padx=16,
            pady=12,
            highlightbackground="#334155",
            highlightthickness=1
        )
        info_frame.pack(fill="x", pady=(0, 18))
        description_label = tk.Label(
            info_frame,
            text=(
                "Czy na pewno chcesz trwale zresetować\nwszystkie statystyki?"
            ),
            font=(FONT_FAMILY, 10, "bold"),
            bg=BACKGROUND_MAIN,
            fg=FOREGROUND_TEXT,
            justify="left"
        )
        description_label.pack()
        button_row = tk.Frame(outer_frame, bg=BACKGROUND_CARD)
        button_row.pack()
        def confirm_reset():
            self.set_default_data()
            self.save_data()
            title_label.config(text="ZRESETOWANO", fg=SUCCESS)
            description_label.config(
                text="Wszystkie statystyki zostały przywrócone\ndo wartości początkowych.",
                justify="left"
            )
            for child in button_row.winfo_children():
                child.destroy()
            self._create_button(button_row, "OK", window.destroy, width=18, pady=9).pack()
        confirm_button = self._create_button(
            button_row,
            "Resetuj",
            confirm_reset,
            width=14,
            pady=9,
            base_background="#7f1d1d",
            base_foreground=FOREGROUND_TEXT,
            hover_background="#dc2626",
            hover_foreground=FOREGROUND_TEXT
        )
        confirm_button.pack(side="left", padx=(0, 8))
        cancel_button = self._create_button(button_row, "Anuluj", window.destroy, width=14, pady=9)
        cancel_button.pack(side="left", padx=(8, 0))
        window.bind("<Escape>", lambda _event: window.destroy())
        window.bind("<BackSpace>", lambda _event: window.destroy())
        window.update_idletasks()
        window_width = window.winfo_width()
        window_height = window.winfo_height()
        root_x = self.root.winfo_rootx()
        root_y = self.root.winfo_rooty()
        root_width = self.root.winfo_width()
        root_height = self.root.winfo_height()
        position_x = root_x + max((root_width - window_width) // 2, 0)
        position_y = root_y + max((root_height - window_height) // 2, 0)
        window.geometry(f"+{position_x}+{position_y}")
        window.focus_set()
        window.wait_window()

    def _return_to_menu_from_game(self):
        if self.game_in_progress:
            return
        self.show_menu()

    def _play_again(self):
        if self.game_in_progress:
            return
        if self.mode == "wager":
            self.configure_game("wager")
        else:
            self.start_game(min_value=self.min_value, max_value=self.max_value, wagered_amount=0)

    def _on_replay_key(self, _event=None):
        button = self.replay_button
        if button is None or not button.winfo_exists():
            return
        if str(button["state"]) != "normal":
            return
        self._play_again()

    def _on_back_key(self, _event=None):
        focused_widget = self.root.focus_get()
        if isinstance(focused_widget, tk.Entry) and str(focused_widget["state"]) == "normal":
            return
        if self.game_in_progress:
            return
        if self._back_action is not None:
            self._back_action()

    def show_menu(self):
        self._clear_screen()
        card = self._create_card(pady=30)
        center = tk.Frame(card, bg=BACKGROUND_CARD)
        center.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(
            center,
            text="ZGADYWACZ",
            font=(FONT_FAMILY, 54, "bold"),
            bg=BACKGROUND_CARD,
            fg=PURPLE_LIGHT
        ).pack(pady=(0, 24))
        self._create_button(center, "Start gry", self.show_modes).pack(pady=6)
        self._create_button(center, "Ustawienia", self.show_settings).pack(pady=6)
        self._create_button(center, "Sklep rankingowy", self.show_shop).pack(pady=6)
        self._create_button(center, "Dodatkowe opcje", self.show_extras).pack(pady=6)
        self._create_button(center, "Wyjdź z gry", self.quit_game).pack(pady=6)

    def show_modes(self):
        self._clear_screen(self.show_menu)
        card = self._create_card(pady=22)
        wrapper = tk.Frame(card, bg=BACKGROUND_CARD, width=560)
        wrapper.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(
            wrapper,
            text="WYBIERZ TRYB GRY",
            font=(FONT_FAMILY, 20, "bold"),
            bg=BACKGROUND_CARD,
            fg=PURPLE_DARK
        ).pack(pady=(0, 14))
        modes_info = [
            ("Tryb nierankingowy", "Własny przedział • Punkty ogólne", "unranked"),
            ("Tryb rankingowy", "Przedział <10;100> • Punkty MMR i rangi", "ranked"),
            ("Tryb zakładowy", "Obstawianie dolarów • Max 5 prób • Wygrana x2\t\t", "wager"),
        ]
        for name, description, mode_id in modes_info:
            box = tk.Frame(
                wrapper,
                bg=BACKGROUND_MAIN,
                padx=18,
                pady=12,
                highlightbackground="#334155",
                highlightthickness=1
            )
            box.pack(fill="x", pady=6)
            left = tk.Frame(box, bg=BACKGROUND_MAIN)
            left.pack(side="left", fill="y")
            tk.Label(left, text=name, font=(FONT_FAMILY, 12, "bold"), bg=BACKGROUND_MAIN, fg=FOREGROUND_TEXT, anchor="w").pack(anchor="w")
            tk.Label(left, text=description, font=(FONT_FAMILY, 9, "bold"), bg=BACKGROUND_MAIN, fg=FOREGROUND_MUTED, anchor="w").pack(anchor="w")
            self._create_button(
                box,
                "Wybierz",
                lambda selected_mode=mode_id: self.configure_game(selected_mode),
                width=12,
                pady=7
            ).pack(side="right")
        self._create_button(wrapper, "Powrót do menu", self.show_menu, width=22, pady=9).pack(pady=(18, 0))

    def show_shop(self, message="", color=SUCCESS):
        self._clear_screen(self.show_menu)
        card = self._create_card(pady=22)
        wrapper = tk.Frame(card, bg=BACKGROUND_CARD, width=560)
        wrapper.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(
            wrapper,
            text="SKLEP RANKINGOWY",
            font=(FONT_FAMILY, 20, "bold"),
            bg=BACKGROUND_CARD,
            fg=PURPLE_DARK
        ).pack(pady=(0, 6))
        tk.Label(
            wrapper,
            text=f"Twoje saldo: {format_number(self.dollars)}$",
            font=(FONT_FAMILY, 12, "bold"),
            bg=BACKGROUND_CARD,
            fg=FOREGROUND_MUTED
        ).pack(pady=(0, 4))
        if message:
            tk.Label(
                wrapper,
                text=message,
                font=(FONT_FAMILY, 12, "bold"),
                bg=BACKGROUND_CARD,
                fg=color,
                height=1
            ).pack(pady=(0, 6))
        items = [
            (
                f"Podpowiedź ({format_number(HINT_PRICE)}$)",
                f"Pokazuje przedział {HINT_RANGE_WIDTH} liczb z wylosowaną.",
                self.buy_hint,
            ),
            (
                f"Booster MMR ({format_number(BOOSTER_PRICE)}$)",
                f"+{BOOSTER_MMR} MMR za rundę przez {BOOSTER_GAMES} następnych gier.\t",
                self.buy_booster,
            ),
        ]
        for name, description, action in items:
            box = tk.Frame(
                wrapper,
                bg=BACKGROUND_MAIN,
                padx=18,
                pady=12,
                highlightbackground="#334155",
                highlightthickness=1
            )
            box.pack(fill="x", pady=6)
            left = tk.Frame(box, bg=BACKGROUND_MAIN)
            left.pack(side="left", fill="y")
            tk.Label(left, text=name, font=(FONT_FAMILY, 12, "bold"), bg=BACKGROUND_MAIN, fg=FOREGROUND_TEXT, anchor="w").pack(anchor="w")
            tk.Label(left, text=description, font=(FONT_FAMILY, 9, "bold"), bg=BACKGROUND_MAIN, fg=FOREGROUND_MUTED, anchor="w", wraplength=290, justify="left").pack(anchor="w")
            self._create_button(
                box,
                "Kup",
                action,
                width=13,
                pady=7
            ).pack(side="right", padx=(10, 0))
        self._create_button(wrapper, "Powrót do menu", self.show_menu, width=22, pady=9).pack(pady=(18, 0))

    def _check_can_afford(self, price):
        if self.dollars < price:
            self._show_error_popup(
                "Brak środków",
                f"Potrzebujesz {format_number(price)}$, a masz tylko {format_number(self.dollars)}$!"
            )
            return False
        return True

    def buy_hint(self):
        if not self._check_can_afford(HINT_PRICE):
            return
        self.dollars -= HINT_PRICE
        self.hints += 1
        self.save_data()
        self.show_shop("Kupiono podpowiedź!")

    def buy_booster(self):
        if not self._check_can_afford(BOOSTER_PRICE):
            return
        self.dollars -= BOOSTER_PRICE
        self.booster_games_left += BOOSTER_GAMES
        self.save_data()
        self.show_shop(f"Kupiono booster MMR!")

    def show_bonuses(self, message="", color=SUCCESS):
        self._clear_screen(self.show_extras)
        card = self._create_card(pady=22)
        wrapper = tk.Frame(card, bg=BACKGROUND_CARD, width=560)
        wrapper.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(
            wrapper,
            text="BONUSY",
            font=(FONT_FAMILY, 20, "bold"),
            bg=BACKGROUND_CARD,
            fg=PURPLE_DARK
        ).pack(pady=(0, 6))
        tk.Label(
            wrapper,
            text=f"Twoje saldo: {format_number(self.dollars)}$",
            font=(FONT_FAMILY, 12, "bold"),
            bg=BACKGROUND_CARD,
            fg=FOREGROUND_MUTED
        ).pack(pady=(0, 4))
        if message:
            tk.Label(
                wrapper,
                text=message,
                font=(FONT_FAMILY, 12, "bold"),
                bg=BACKGROUND_CARD,
                fg=color,
                height=1
            ).pack(pady=(0, 6))
        available = self.available_gambler_bonuses()
        bankrupt_box = tk.Frame(wrapper, bg=BACKGROUND_MAIN, padx=18, pady=12, highlightbackground="#334155", highlightthickness=1)
        bankrupt_box.pack(fill="x", pady=6)
        bankrupt_left = tk.Frame(bankrupt_box, bg=BACKGROUND_MAIN)
        bankrupt_left.pack(side="left", fill="y")
        tk.Label(bankrupt_left, text=f"Bonus Bankruta ({format_number(BANKRUPT_BONUS)}$)", font=(FONT_FAMILY, 12, "bold"), bg=BACKGROUND_MAIN, fg=FOREGROUND_TEXT, anchor="w").pack(anchor="w")
        tk.Label(
            bankrupt_left,
            text=f"Dostępny tylko przy saldzie 0$.",
            font=(FONT_FAMILY, 9, "bold"),
            bg=BACKGROUND_MAIN,
            fg=FOREGROUND_MUTED,
            anchor="w",
            wraplength=290,
            justify="left"
        ).pack(anchor="w")
        bankrupt_button = self._create_button(bankrupt_box, "Odbierz", self.claim_bankrupt_bonus, width=13, pady=7)
        bankrupt_button.pack(side="right", padx=(10, 0))
        if self.dollars != 0:
            self._disable_button(bankrupt_button)
        gambler_box = tk.Frame(wrapper, bg=BACKGROUND_MAIN, padx=18, pady=12, highlightbackground="#334155", highlightthickness=1)
        gambler_box.pack(fill="x", pady=6)
        gambler_left = tk.Frame(gambler_box, bg=BACKGROUND_MAIN)
        gambler_left.pack(side="left", fill="y")
        tk.Label(gambler_left, text=f"Bonus Hazardzisty ({format_number(GAMBLER_BONUS)}$)", font=(FONT_FAMILY, 12, "bold"), bg=BACKGROUND_MAIN, fg=FOREGROUND_TEXT, anchor="w").pack(anchor="w")
        tk.Label(
            gambler_left,
            text=(
                f"Dostępny za każde {format_number(GAMBLER_BONUS_THRESHOLD)}$ łącznych wygranych.\t\t"
            ),
            font=(FONT_FAMILY, 9, "bold"),
            bg=BACKGROUND_MAIN,
            fg=FOREGROUND_MUTED,
            anchor="w",
            wraplength=290,
            justify="left"
        ).pack(anchor="w")
        gambler_button = self._create_button(gambler_box, "Odbierz", self.claim_gambler_bonus, width=13, pady=7)
        gambler_button.pack(side="right", padx=(10, 0))
        if available <= 0:
            self._disable_button(gambler_button)
        self._create_button(wrapper, "Powrót", self.show_extras, width=22, pady=9).pack(pady=(18, 0))

    def available_gambler_bonuses(self):
        return max(0, self.total_winnings // GAMBLER_BONUS_THRESHOLD - self.gambler_bonuses_claimed)

    def claim_bankrupt_bonus(self):
        if self.dollars != 0:
            self._show_error_popup("Niedostępne", "Bonus bankruta jest dostępny tylko przy saldzie 0$!")
            return
        self.dollars += BANKRUPT_BONUS
        self.save_data()
        self.show_bonuses(f"Odebrano bonus bankruta (+{format_number(BANKRUPT_BONUS)}$)")

    def claim_gambler_bonus(self):
        count = self.available_gambler_bonuses()
        if count <= 0:
            self._show_error_popup(
                "Niedostępne",
                f"Wygraj jeszcze {format_number(GAMBLER_BONUS_THRESHOLD - (self.total_winnings % GAMBLER_BONUS_THRESHOLD))}$ aby odblokować bonus!"
            )
            return
        amount = count * GAMBLER_BONUS
        self.gambler_bonuses_claimed += count
        self.dollars += amount
        self.save_data()
        self.show_bonuses(f"Odebrano bonus hazardzisty (+{format_number(amount)}$)")

    def configure_game(self, mode):
        self.mode = mode
        if mode == "ranked":
            self.start_game(min_value=10, max_value=100, wagered_amount=0)
            return
        self._clear_screen(self.show_modes)
        card = self._create_card(pady=24)
        center = tk.Frame(card, bg=BACKGROUND_CARD)
        center.place(relx=0.5, rely=0.5, anchor="center")
        if mode == "unranked":
            tk.Label(center, text="TRYB NIERANKINGOWY", font=(FONT_FAMILY, 18, "bold"), bg=BACKGROUND_CARD, fg=PURPLE_DARK).pack(pady=(0, 14))
            tk.Label(center, text="Minimalna liczba (min. 5):", font=(FONT_FAMILY, 12, "bold"), bg=BACKGROUND_CARD, fg=FOREGROUND_TEXT).pack()
            min_entry = tk.Entry(
                center,
                font=(FONT_FAMILY, 12, "bold"),
                bg=BACKGROUND_INPUT,
                fg=FOREGROUND_TEXT,
                disabledbackground=BACKGROUND_INPUT,
                disabledforeground=FOREGROUND_MUTED,
                insertbackground=PURPLE_LIGHT,
                highlightthickness=1,
                highlightbackground=FOREGROUND_TEXT,
                highlightcolor=PURPLE_DARK,
                justify="center",
                width=16
            )
            min_entry.insert(0, "10")
            min_entry.pack(pady=(4, 12))
            tk.Label(center, text="Maksymalna liczba (min. 10, większa od min):", font=(FONT_FAMILY, 12, "bold"), bg=BACKGROUND_CARD, fg=FOREGROUND_TEXT).pack()
            max_entry = tk.Entry(
                center,
                font=(FONT_FAMILY, 12, "bold"),
                bg=BACKGROUND_INPUT,
                fg=FOREGROUND_TEXT,
                disabledbackground=BACKGROUND_INPUT,
                disabledforeground=FOREGROUND_MUTED,
                insertbackground=PURPLE_LIGHT,
                highlightthickness=1,
                highlightbackground=FOREGROUND_TEXT,
                highlightcolor=PURPLE_DARK,
                justify="center",
                width=16
            )
            max_entry.insert(0, "100")
            max_entry.pack(pady=(4, 18))
            def confirm_unranked():
                try:
                    chosen_min = int(min_entry.get())
                    chosen_max = int(max_entry.get())
                except ValueError:
                    self._show_error_popup("Błąd", "Wpisz poprawne liczby!")
                    return
                if chosen_min < 5 or chosen_max < 10 or chosen_min >= chosen_max:
                    self._show_error_popup(
                        "Błędny przedział",
                        "Minimalna => 5, maksymalna => 10 oraz minimalna < maksymalnej!",
                    )
                    return
                self.start_game(min_value=chosen_min, max_value=chosen_max, wagered_amount=0)
            self._create_button(center, "Rozpocznij grę", confirm_unranked, width=22).pack(pady=6)
        elif mode == "wager":
            tk.Label(center, text="TRYB ZAKŁADOWY", font=(FONT_FAMILY, 18, "bold"), bg=BACKGROUND_CARD, fg=WARNING).pack(pady=(0, 8))
            tk.Label(
                center,
                text=f"Twoje saldo: {format_number(self.dollars)}$",
                font=(FONT_FAMILY, 12, "bold"),
                bg=BACKGROUND_CARD,
                fg=FOREGROUND_MUTED,
                justify="center"
            ).pack(pady=(0, 14))
            if self.dollars < 100:
                tk.Label(center, text="Masz za mało dolarów (minimum to 100$).", font=(FONT_FAMILY, 12, "bold"), bg=BACKGROUND_CARD, fg=DANGER).pack(pady=10)
            else:
                tk.Label(center, text="Kwota zakładu (min. 100$):", font=(FONT_FAMILY, 12, "bold"), bg=BACKGROUND_CARD, fg=FOREGROUND_TEXT).pack()
                bet_entry = tk.Entry(
                    center,
                    font=(FONT_FAMILY, 12, "bold"),
                    bg=BACKGROUND_INPUT,
                    fg=FOREGROUND_TEXT,
                    disabledbackground=BACKGROUND_INPUT,
                    disabledforeground=FOREGROUND_MUTED,
                    insertbackground=PURPLE_LIGHT,
                    highlightthickness=1,
                    highlightbackground=FOREGROUND_TEXT,
                    highlightcolor=PURPLE_DARK,
                    justify="center",
                    width=16
                )
                bet_entry.insert(0, "100")
                bet_entry.pack(pady=(6, 16))
                def confirm_wager():
                    try:
                        stake = int(bet_entry.get())
                    except ValueError:
                        self._show_error_popup("Błąd", "Wpisz poprawną kwotę!")
                        return
                    if stake < 100 or stake > self.dollars:
                        self._show_error_popup(
                            "Błędna kwota",
                            f"Kwota musi wynosić od 100$ do {format_number(self.dollars)}$!",
                        )
                        return
                    self.dollars -= stake
                    self.start_game(min_value=10, max_value=100, wagered_amount=stake)
                self._create_button(center, "Postaw i zacznij", confirm_wager, width=22).pack(pady=6)
        self._create_button(center, "Powrót do trybów", self.show_modes, width=22, pady=8).pack(pady=(14, 0))

    def start_game(self, min_value, max_value, wagered_amount):
        self.min_value = min_value
        self.max_value = max_value
        self.wagered_amount = wagered_amount
        self.secret_number = random.randint(min_value, max_value)
        self.current_attempt = 1
        self.game_in_progress = True
        self.hint_used = False
        self.hint_button = None
        self.hint_label = None
        self._clear_screen()
        card = self._create_card(pady=22)
        center = tk.Frame(card, bg=BACKGROUND_CARD)
        center.place(relx=0.5, rely=0.5, anchor="center")
        mode_title = {
            "unranked": "TRYB NIERANKINGOWY",
            "ranked": "TRYB RANKINGOWY",
            "wager": f"TRYB ZAKŁADOWY"
        }[self.mode]
        tk.Label(center, text=mode_title, font=(FONT_FAMILY, 15, "bold"), bg=BACKGROUND_CARD, fg=PURPLE_DARK).pack()
        tk.Label(
            center,
            text=f"Wylosowano liczbę z przedziału <{min_value};{max_value}>",
            font=(FONT_FAMILY, 12, "bold"),
            bg=BACKGROUND_CARD,
            fg=FOREGROUND_TEXT
        ).pack(pady=(4, 12))
        self.attempt_label = tk.Label(
            center,
            text="Próba nr 1" + (" / 5" if self.mode == "wager" else ""),
            font=(FONT_FAMILY, 12, "bold"),
            bg=BACKGROUND_CARD,
            fg=FOREGROUND_MUTED
        )
        self.attempt_label.pack()
        self.result_frame = tk.Frame(center, bg=BACKGROUND_CARD, pady=12)
        self.result_frame.pack()
        self.feedback_label = tk.Label(
            self.result_frame,
            text="Wpisz swoją liczbę i wciśnij Enter.",
            font=(FONT_FAMILY, 13, "bold"),
            bg=BACKGROUND_CARD,
            fg=FOREGROUND_TEXT,
            justify="center"
        )
        self.feedback_label.pack()
        self.rank_result_frame = tk.Frame(self.result_frame, bg=BACKGROUND_CARD)
        self.rank_result_frame.pack()
        self.rank_prefix_label = tk.Label(
            self.rank_result_frame,
            text="",
            font=(FONT_FAMILY, 12, "bold"),
            bg=BACKGROUND_CARD,
            fg=FOREGROUND_TEXT
        )
        self.rank_prefix_label.pack(side="left")
        self.rank_name_label = tk.Label(
            self.rank_result_frame,
            text="",
            font=(FONT_FAMILY, 12, "bold"),
            bg=BACKGROUND_CARD,
            fg=FOREGROUND_TEXT
        )
        self.rank_name_label.pack(side="left")
        self.rank_change_label = tk.Label(
            self.rank_result_frame,
            text="",
            font=(FONT_FAMILY, 12, "bold"),
            bg=BACKGROUND_CARD,
            fg=FOREGROUND_TEXT
        )
        self.rank_change_label.pack(side="left")
        self.guess_entry = tk.Entry(
            center,
            font=(FONT_FAMILY, 16, "bold"),
            bg=BACKGROUND_INPUT,
            fg=FOREGROUND_TEXT,
            disabledbackground=BACKGROUND_MUTED,
            disabledforeground=FOREGROUND_MUTED,
            insertbackground=PURPLE_LIGHT,
            highlightthickness=1,
            highlightbackground=FOREGROUND_TEXT,
            highlightcolor=PURPLE_DARK,
            justify="center",
            width=12
        )
        self.guess_entry.pack(pady=(0, 10))
        self.guess_entry.focus_set()
        self.guess_entry.bind("<Return>", lambda _event: self.check_guess())
        self.guess_button = self._create_button(center, "Zgadnij", self.check_guess, width=22)
        self.guess_button.pack()
        if self.mode == "ranked":
            self.hint_button = self._create_button(
                center,
                f"Użyj podpowiedzi ({self.hints})",
                self.use_hint,
                width=22,
                pady=8
            )
            self.hint_button.pack(pady=(6, 0))
            if self.hints <= 0:
                self._disable_button(self.hint_button)
            self.hint_label = tk.Label(
                center,
                text="",
                font=(FONT_FAMILY, 10, "bold"),
                bg=BACKGROUND_CARD,
                fg=PURPLE_LIGHT
            )
        self.replay_button = self._create_button(center, "Zagraj ponownie", self._play_again, width=22, pady=8)
        self._disable_button(self.replay_button)
        self.replay_button.pack(pady=(6, 0))
        self.back_to_menu_button = self._create_button(center, "Powrót do menu", self._return_to_menu_from_game, width=22, pady=8)
        self.back_to_menu_button.config(state="disabled", bg=BUTTON_BASE, fg=FOREGROUND_MUTED)
        self.back_to_menu_button.pack(pady=(6, 0))

    def use_hint(self):
        if not self.game_in_progress or self.mode != "ranked":
            return
        if self.hint_used or self.hints <= 0:
            return
        self.hints -= 1
        self.hint_used = True
        width = HINT_RANGE_WIDTH
        lowest_start = max(self.min_value, self.secret_number - width + 1)
        highest_start = min(self.secret_number, self.max_value - width + 1)
        range_start = random.randint(lowest_start, highest_start)
        range_end = range_start + width - 1
        self.save_data()
        self.hint_label.config(text=f"Podpowiedź: Liczba jest w przedziale <{range_start};{range_end}>")
        self.hint_button.config(text=f"Użyj podpowiedzi ({self.hints})")
        self.hint_label.pack(pady=(4, 0), before=self.replay_button)
        self._disable_button(self.hint_button)
        self.guess_entry.focus_set()

    def check_guess(self):
        try:
            number = int(self.guess_entry.get())
        except ValueError:
            self.feedback_label.config(text="To musi być liczba całkowita!", fg=DANGER)
            self.guess_entry.delete(0, "end")
            return
        self.guess_entry.delete(0, "end")
        if number == self.secret_number:
            self._handle_win()
            return
        if self.mode == "wager":
            if self.current_attempt >= 5:
                self._handle_wager_loss()
                return
            self.current_attempt += 1
            self.attempt_label.config(text=f"Próba {self.current_attempt} / 5")
        else:
            self.current_attempt += 1
            self.attempt_label.config(text=f"Próba {self.current_attempt}")
        if abs(number - self.secret_number) == 1:
            self.feedback_label.config(text="Jesteś bardzo blisko!", fg=WARNING)
        elif number < self.secret_number:
            self.feedback_label.config(text="Za mało!", fg=TOO_LOW)
        else:
            self.feedback_label.config(text="Za dużo!", fg=TOO_HIGH)

    def _finish_game_ui(self):
        self.guess_entry.config(state="disabled", disabledforeground=FOREGROUND_MUTED, highlightbackground=FOREGROUND_MUTED, highlightcolor=FOREGROUND_MUTED)
        self.guess_button.config(state="disabled", bg=BUTTON_BASE, fg=FOREGROUND_MUTED)
        if self.hint_button is not None:
            self._disable_button(self.hint_button)
        if self.replay_button is not None:
            self.replay_button.config(state="normal", bg=BUTTON_BASE, fg=FOREGROUND_TEXT, cursor="hand2")
        self.back_to_menu_button.config(state="normal", bg=BUTTON_BASE, fg=FOREGROUND_TEXT)
        self._back_action = self.show_menu

    def _handle_win(self):
        self.rank_prefix_label.config(text="")
        self.rank_name_label.config(text="")
        self.rank_change_label.config(text="")
        message_color = SUCCESS
        if self.mode == "unranked":
            earned_points = 100.0 / self.current_attempt
            self.total_points += earned_points
            self.unranked_games += 1
            self.unranked_attempts += self.current_attempt
            message = (
                f"Gratulacje! Udało ci się zgadnąć przy {self.current_attempt} próbie!\n"
                f"Zdobywasz {earned_points:.2f} punktów!"
            )
        elif self.mode == "ranked":
            old_rank = self.get_rank()
            mmr_change = 30 - (5 * self.current_attempt)
            booster_mmr_bonus = 0
            if self.booster_games_left > 0:
                booster_mmr_bonus = BOOSTER_MMR
                self.booster_games_left -= 1
            mmr_change += booster_mmr_bonus
            self.total_mmr += mmr_change
            self.ranked_games += 1
            self.ranked_attempts += self.current_attempt
            new_rank = self.get_rank()
            if mmr_change > 0:
                message = (
                    f"Gratulacje! Udało ci się zgadnąć przy {self.current_attempt} próbie!\n"
                    f"Zdobywasz {mmr_change} MMR!"
                )
            elif mmr_change == 0:
                message = (
                    f"Udało ci się zgadnąć przy {self.current_attempt} próbie!\n"
                    "Nie zdobywasz żadnego MMR!"
                )
                message_color = WARNING
            else:
                message = (
                    f"Udało ci się zgadnąć przy {self.current_attempt} próbie!\n"
                    f"Tracisz {abs(mmr_change)} MMR!"
                )
                message_color = DANGER
            if booster_mmr_bonus:
                message += f" (+{booster_mmr_bonus} MMR Boost)"
            self.rank_prefix_label.config(text="Twoja aktualna ranga:", fg=FOREGROUND_TEXT)
            self.rank_name_label.config(text=new_rank, fg=self.get_rank_color(new_rank))
            rank_order = list(RANK_COLORS)
            if rank_order.index(new_rank) > rank_order.index(old_rank):
                self.rank_change_label.config(text="(awans!)", fg=SUCCESS)
            elif rank_order.index(new_rank) < rank_order.index(old_rank):
                self.rank_change_label.config(text="(degrad!)", fg=DANGER)
        else:
            winnings = self.wagered_amount * 2
            self.dollars += winnings
            self.total_winnings += winnings
            if self.biggest_win < winnings:
                self.biggest_win = winnings
            message = (
                f"Gratulacje! Udało ci się zgadnąć przy {self.current_attempt} próbie!\n"
                f"Wygrywasz {format_number(winnings)}$! Łącznie masz {format_number(self.dollars)}$!"
            )
        self.game_in_progress = False
        self.save_data()
        self.feedback_label.config(text=message, fg=message_color)
        self._finish_game_ui()

    def _handle_wager_loss(self):
        message = (
            f"Skończyły ci się próby! Wylosowana liczba to: {self.secret_number}\n"
            f"Tracisz {format_number(self.wagered_amount)}$! Łącznie masz {format_number(self.dollars)}$!"
        )
        self.game_in_progress = False
        self.save_data()
        self.feedback_label.config(text=message, fg=DANGER)
        self._finish_game_ui()

    def show_settings(self):
        self._clear_screen(self.show_menu)
        self.selected_fullscreen = self.fullscreen
        card = self._create_card(pady=26)
        center = tk.Frame(card, bg=BACKGROUND_CARD)
        center.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(center, text="USTAWIENIA", font=(FONT_FAMILY, 20, "bold"), bg=BACKGROUND_CARD, fg=PURPLE_DARK).pack(pady=(0, 22))
        def refresh_screen_button():
            screen_button.config(text="Pełen ekran: WŁ" if self.selected_fullscreen else "Pełen ekran: WYŁ")
        def toggle_selection():
            self.selected_fullscreen = not self.selected_fullscreen
            refresh_screen_button()
        def apply_screen():
            self._apply_screen_mode(self.selected_fullscreen)
            refresh_screen_button()
        self._refresh_settings_screen = refresh_screen_button
        screen_button = self._create_button(center, "", toggle_selection, width=28)
        screen_button.pack(pady=7)
        refresh_screen_button()
        self._create_button(center, "Resetuj statystyki", self._open_reset_window, width=28).pack(pady=7)
        bottom_row = tk.Frame(center, bg=BACKGROUND_CARD)
        bottom_row.pack(pady=(18, 0))
        self._create_button(bottom_row, "Zastosuj", apply_screen, width=13, pady=9).pack(side="left", padx=(0, 6))
        self._create_button(bottom_row, "Powrót", self.show_menu, width=13, pady=9).pack(side="left", padx=(6, 0))

    def show_extras(self):
        self._clear_screen(self.show_menu)
        card = self._create_card(pady=24)
        center = tk.Frame(card, bg=BACKGROUND_CARD)
        center.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(center, text="OPCJE DODATKOWE", font=(FONT_FAMILY, 20, "bold"), bg=BACKGROUND_CARD, fg=PURPLE_DARK).pack(pady=(0, 20))
        self._create_button(center, "Statystyki", self.show_statistics, width=26).pack(pady=7)
        self._create_button(center, "Informacje", self.show_information, width=26).pack(pady=7)
        self._create_button(center, "Nowości", self.show_news, width=26).pack(pady=7)
        self._create_button(center, "Bonusy", self.show_bonuses, width=26).pack(pady=7)
        self._create_button(center, "Powrót do menu", self.show_menu, width=26).pack(pady=7)

    def show_statistics(self):
        self._clear_screen(self.show_extras)
        card = self._create_card(pady=20)
        center = tk.Frame(card, bg=BACKGROUND_CARD)
        center.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(center, text="STATYSTYKI", font=(FONT_FAMILY, 20, "bold"), bg=BACKGROUND_CARD, fg=PURPLE_DARK).pack(pady=(0, 14))
        unranked_average = (self.unranked_attempts / self.unranked_games) if self.unranked_games > 0 else 0.0
        ranked_average = (self.ranked_attempts / self.ranked_games) if self.ranked_games > 0 else 0.0
        current_rank = self.get_rank()
        fragments = [
            ("NIERANKINGOWE:\n", "header"),
            (f"• Zdobyte punkty: {self.total_points:.2f}\n", "text"),
            (f"• Średnia prób: {unranked_average:.2f}\n", "text"),
            ("RANKINGOWE:\n", "header"),
            ("• Ranga: ", "text"),
            (current_rank, "text", self.get_rank_color(current_rank)),
            (f" ({self.total_mmr} MMR)\n", "text"),
            (f"• Średnia prób: {ranked_average:.2f}\n", "text"),
            ("ZAKŁADOWE:\n", "header"),
            (f"• Saldo: {format_number(self.dollars)}$\n", "text"),
            (f"• Największa wygrana: {format_number(self.biggest_win)}$\n", "text"),
            (f"• Łącznie wygrane: {format_number(self.total_winnings)}$\n", "text"),
            ("EKWIPUNEK:\n", "header"),
            (f"• Podpowiedzi: {self.hints}\n", "text"),
            (f"• Booster MMR: {self.booster_games_left} gier", "text")
        ]
        self._create_text_panel(center, fragments, height=14, width=58)
        self._create_button(center, "Powrót", self.show_extras, width=20, pady=8).pack()

    def show_information(self):
        self._clear_screen(self.show_extras)
        card = self._create_card(pady=20)
        center = tk.Frame(card, bg=BACKGROUND_CARD)
        center.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(center, text="INFORMACJE", font=(FONT_FAMILY, 20, "bold"), bg=BACKGROUND_CARD, fg=PURPLE_DARK).pack(pady=(0, 14))
        fragments = [
            ("Zgadywacz ", "header"),
            ("to gra, w której musisz odgadnąć wylosowaną liczbę z określonego przedziału. Każdy tryb ma swoje własne zasady.\n", "text"),
            ("Tryb nierankingowy: ", "header"),
            ("Ustalasz swój własny przedział i zdobywasz punkty ogólne. Punkty nie mają tutaj żadnego większego znaczenia.\n", "text"),
            ("Prawdopodobnie najlepszy i najzdrowszy sposób na granie w tą grę.\n", "text"),
            ("Tryb rankingowy: ", "header"),
            ("Masz stały przedział <10;100> i zdobywasz punkty MMR, dzięki którym odblokowujesz kolejne rangi. ", "text"),
            ("Zaczynasz z 200 MMR i brązem. Możesz spaść do 0 MMR i stracić rangę, albo zdobyć srebro za 500 MMR i awansować co każde 500 MMR, aż do Master Zgadywacza za 2500 MMR. ", "text"),
            ("1 rundę gry rankingowej zaczynasz z meczowym 25 MMR i spada ono z każdą kolejną próbą o -5, przez co po 6 próbie można skończyć z ujemnym MMR. ", "text"),
            ("Na końcu meczu jest ono dodawane, niezmienione lub odejmowane od ogólnego MMR w zależności od wyniku.\n", "text"),
            ("Tryb zakładowy: ", "header"),
            ("Obstawiasz dolary (minimum 100$) i w maksymalnie 5 prób musisz zgadnąć liczbę ze stałego przedziału <10;100>. ", "text"),
            ("Wygrana podwaja stawkę, a przegrana zabiera obstawioną kwotę.\n", "text"),
            ("Sklep rankingowy: ", "header"),
            ("W menu głównym możesz odwiedzić sklep, w którym możesz za dolary z trybu zakładowego, kupić przedmioty wspomagające do trybu rankingowego. ", "text"),
            ("Możesz tam kupić:\n", "text"),
            ("• Podpowiedź - Daje przedział 10 liczb, w którym jest wylosowana.\n", "text"),
            ("• Booster MMR - Daje +10 MMR przy każdym wyniku przez 5 rund.\n", "text"),
            ("Bonusy: ", "header"),
            ("Są one do odebrania w dodatkowych opcjach przy spełnieniu odpowiednich wymagań. Te bonusy to:\n", "text"),
            ("• Bonus Bankruta - Daje 500$, jeżeli twoje saldo wynosi 0$.\n", "text"),
            ("• Bonus Hazardzisty - Daje 5.000$ za każde 25.000$ łącznych wygranych.\n", "text"),
            ("Skróty klawiszowe: ", "header"),
            ("\n• Backspace - Powrót do poprzedniego menu", "text"),
            ("\n• R - Zagraj ponownie", "text"),
            ("\n• F11 - Włącz/wyłącz pełen ekran", "text")
        ]
        self._create_text_panel(center, fragments, height=14, width=58)
        self._create_button(center, "Powrót", self.show_extras, width=20, pady=8).pack()

    def show_news(self):
        self._clear_screen(self.show_extras)
        card = self._create_card(pady=20)
        center = tk.Frame(card, bg=BACKGROUND_CARD)
        center.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(center, text="NOWOŚCI", font=(FONT_FAMILY, 20, "bold"), bg=BACKGROUND_CARD, fg=PURPLE_DARK).pack(pady=(0, 14))
        fragments = [
            ("WERSJA 1.3.2:\n", "header"),
            ("• Dodano kilka skrótów klawiszowych\n", "text"),
            ("• Dodano scrollbar do okienek informacyjnych\n", "text"),
            ("• Naprawiono błąd z naliczaniem łącznych wygranych\n", "text"),
            ("• Poprawiono kilka elementów wizualnych\n", "text"),
            ("WERSJA 1.3.1:\n", "header"),
            ("• Dodano tracenie -25 MMR przy wyjściu z gry rankingowej\n", "text"),
            ("• Poprawiono kilka literówek\n", "text"),
            ("WERSJA 1.3:\n", "header"),
            ("• Dodano sklep rankingowy\n", "text"),
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
        self._create_text_panel(center, fragments, height=14, width=58)
        self._create_button(center, "Powrót", self.show_extras, width=20, pady=8).pack()

    def quit_game(self):
        if self.game_in_progress and self.mode == "ranked":
            self.total_mmr = max(0, self.total_mmr - 25)
        self.save_data()
        self.root.destroy()
        sys.exit(0)

if __name__ == "__main__":
    root = tk.Tk()
    app = NumGuesser(root)
    root.mainloop()

# MADE BY FRYTA
