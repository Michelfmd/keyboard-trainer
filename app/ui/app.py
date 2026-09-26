import tkinter as tk
from tkinter import ttk
from typing import ClassVar

from app.activities import ACTIVITIES
from app.core.session import Session
from app.modes.base import BaseMode
from app.modes.random_keys import RandomKeysMode
from app.modes.words import WordsMode
from app.ui.components.motion import Motion
from app.ui.components.widgets import (
    ACCENT,
    BG,
    BORDER,
    MUTED,
    PANEL,
    TEXT,
    AnimatedButton,
    Navigation,
    button,
    label,
)
from app.ui.home import HomeView
from app.ui.i18n import LANGUAGES, tr
from app.ui.menu_view import MenuView
from app.ui.results_view import ResultsView
from app.ui.statistics_view import StatisticsView
from app.ui.test_view import TestView


class KeyboardTrainer(tk.Tk):
    mode_types: ClassVar[dict[str, type[BaseMode]]] = {
        "words": WordsMode,
        "random_keys": RandomKeysMode,
    }

    def __init__(self) -> None:
        super().__init__()
        self.title("Keyboard Trainer")
        self.geometry("1040x820")
        self.minsize(800, 740)
        self.configure(bg=BG)
        self.option_add("*Font", "{DejaVu Sans} 11")
        self.language = "en"
        self.reduced_motion = False
        self.active_page = "Menu"
        self.nav_buttons: dict[str, AnimatedButton] = {}
        self.history: list[Session] = []
        self.counts = {"words": 20, "random_keys": 40}
        self.word_difficulty = "hard"
        self.view: tk.Widget | None = None
        self._configure_theme()
        header = tk.Frame(self, bg=BG, padx=28, pady=20)
        header.pack(fill="x")
        tk.Label(
            header,
            text="KT",
            bg=ACCENT,
            fg=BG,
            font=("DejaVu Sans Mono", 14, "bold"),
            padx=10,
            pady=8,
        ).pack(side="left", padx=(0, 14))
        label(header, "Keyboard Trainer", 16).pack(side="left")
        self.navigation = Navigation(header, {})
        self.navigation.pack(side="right")
        self._refresh_navigation()
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=28)
        footer = tk.Frame(self, bg=BG, padx=30, pady=12)
        footer.pack(side="bottom", fill="x")
        self.footer_status = label(footer, "", 9, MUTED)
        self.footer_status.pack(side="left")
        self.footer_hint = label(footer, "", 9, MUTED)
        self.footer_hint.pack(side="right")
        self._refresh_footer()
        self.content = tk.Frame(self, bg=BG)
        self.content.pack(fill="both", expand=True, padx=30, pady=(8, 0))
        self.show_menu()

    def _refresh_navigation(self) -> None:
        for child in self.navigation.winfo_children():
            child.destroy()
        self.nav_buttons.clear()
        for title, action in {
            "Menu": self.show_menu,
            "Keyboard": self.show_home,
            "Statistics": self.show_statistics,
            "Settings": self.show_settings,
        }.items():
            item = button(self.navigation, title, action, quiet=True)
            item.pack(side="left", padx=(8, 0))
            item.set_selected(title == self.active_page)
            self.nav_buttons[title] = item

    def _refresh_footer(self) -> None:
        self.footer_status.configure(
            text=f"{tr(self, 'LOCAL PRACTICE')}   /   {self.language.upper()}"
        )
        self.footer_hint.configure(text=tr(self, "Esc to leave an exercise"))

    def _select_page(self, page: str) -> None:
        self.active_page = page
        for title, item in self.nav_buttons.items():
            item.set_selected(title == page)

    def _configure_theme(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(
            "TProgressbar", troughcolor=PANEL, background=ACCENT, borderwidth=0
        )
        style.configure(
            "Treeview",
            background=PANEL,
            fieldbackground=PANEL,
            foreground=TEXT,
            rowheight=28,
            borderwidth=0,
        )
        style.configure(
            "Treeview.Heading", background=BG, foreground=MUTED, relief="flat"
        )
        style.map("Treeview", background=[("selected", "#314a45")])
        style.configure(
            "TCombobox",
            fieldbackground=PANEL,
            background=BORDER,
            foreground=TEXT,
            arrowcolor=ACCENT,
            padding=7,
            bordercolor=BORDER,
            lightcolor=BORDER,
            darkcolor=BORDER,
        )
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", PANEL)],
            foreground=[("readonly", TEXT)],
            selectbackground=[("readonly", PANEL)],
            selectforeground=[("readonly", TEXT)],
        )
        style.configure(
            "TSpinbox",
            fieldbackground=PANEL,
            background=BORDER,
            foreground=TEXT,
            arrowcolor=ACCENT,
            insertcolor=TEXT,
            padding=6,
            bordercolor=BORDER,
            lightcolor=BORDER,
            darkcolor=BORDER,
        )
        style.configure(
            "Vertical.TScrollbar",
            background=BORDER,
            troughcolor=PANEL,
            arrowcolor=MUTED,
            bordercolor=PANEL,
            lightcolor=PANEL,
            darkcolor=PANEL,
        )
        self.option_add("*TCombobox*Listbox.background", PANEL)
        self.option_add("*TCombobox*Listbox.foreground", TEXT)
        self.option_add("*TCombobox*Listbox.selectBackground", BORDER)

    def _clear(self) -> None:
        if self.view is not None:
            self.view.destroy()
            self.view = None

    def _display(self, view: tk.Widget) -> None:
        self.view = view
        view.place(x=0, y=0, relwidth=1, relheight=1)
        if not isinstance(view, TestView):
            motion = Motion(view)
            motion.animate(
                "enter",
                lambda amount: view.place_configure(y=round(10 * (1 - amount))),
                180,
            )

    def show_menu(self) -> None:
        self._select_page("Menu")
        self._clear()
        self._display(
            MenuView(self.content, ACTIVITIES, self.open_activity, self.show_settings)
        )

    def open_activity(self, key: str) -> None:
        activity = next((item for item in ACTIVITIES if item.key == key), None)
        if activity is None or not activity.available:
            return
        routes = {"keyboard": self.show_home}
        route = routes.get(key)
        if route is not None:
            route()

    def show_home(self) -> None:
        self._select_page("Keyboard")
        self._clear()
        self._display(
            HomeView(
                self.content,
                {key: mode.label for key, mode in self.mode_types.items()},
                self.start_mode,
            )
        )

    def start_mode(self, name: str, difficulty: str | None = None) -> None:
        self._select_page("Keyboard")
        self._clear()
        if name == "words":
            if difficulty is not None:
                self.word_difficulty = difficulty
            mode = WordsMode(
                self.counts[name],
                difficulty=self.word_difficulty,
                language=self.language,
            )
        else:
            mode = self.mode_types[name](self.counts[name])
        self._display(TestView(self.content, mode, self.show_results, self.show_home))

    def show_results(self, session: Session) -> None:
        self.history.append(session)
        self._clear()
        self._display(
            ResultsView(self.content, session, lambda: self.start_mode(session.mode))
        )

    def show_statistics(self) -> None:
        self._select_page("Statistics")
        self._clear()
        self._display(
            StatisticsView(
                self.content,
                self.history,
                {key: mode.label for key, mode in self.mode_types.items()},
            )
        )

    def show_settings(self, saved: bool = False) -> None:
        self._select_page("Settings")
        self._clear()
        frame = tk.Frame(self.content, bg=BG)
        label(frame, "Settings", 26).pack(anchor="w", pady=16)
        label(
            frame, "Exercise length. Changes apply to the next session.", color=MUTED
        ).pack(anchor="w", pady=12)
        label(frame, "Language").pack(anchor="w", pady=(12, 8))
        language = tk.StringVar(value=LANGUAGES[self.language])
        ttk.Combobox(
            frame,
            textvariable=language,
            values=list(LANGUAGES.values()),
            state="readonly",
            width=18,
        ).pack(anchor="w")
        label(frame, "Interface and practice words", 10, MUTED).pack(anchor="w", pady=6)
        variables: dict[str, tk.StringVar] = {}
        for key, title in (
            ("words", "Words per Hard exercise"),
            ("random_keys", "Random key targets"),
        ):
            label(frame, title).pack(anchor="w", pady=(20, 8))
            variables[key] = tk.StringVar(value=str(self.counts[key]))
            ttk.Spinbox(
                frame,
                from_=1,
                to=200,
                textvariable=variables[key],
                width=8,
            ).pack(anchor="w")
        reduced_motion = tk.BooleanVar(value=self.reduced_motion)
        tk.Checkbutton(
            frame,
            text=tr(self, "Reduce motion"),
            variable=reduced_motion,
            bg=BG,
            fg=TEXT,
            activebackground=BG,
            activeforeground=ACCENT,
            selectcolor=PANEL,
            highlightthickness=0,
            cursor="hand2",
        ).pack(anchor="w", pady=(18, 0))
        status = label(
            frame,
            "Settings saved for this application run."
            if saved
            else "Settings are kept until the application closes.",
            10,
            MUTED,
        )
        status.pack(anchor="w", pady=20)

        def save() -> None:
            try:
                values = {
                    key: int(variable.get()) for key, variable in variables.items()
                }
                if not all(1 <= count <= 200 for count in values.values()):
                    raise ValueError
            except ValueError:
                status.config(text=tr(self, "Enter whole numbers between 1 and 200."))
                return
            self.counts.update(values)
            self.language = next(
                code for code, name in LANGUAGES.items() if name == language.get()
            )
            self.reduced_motion = reduced_motion.get()
            self._refresh_navigation()
            self._refresh_footer()
            self.show_settings(saved=True)

        button(frame, "Save settings", save, primary=True).pack(anchor="w")
        self._display(frame)


def run() -> None:
    application = KeyboardTrainer()
    application.mainloop()
