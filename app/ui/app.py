import tkinter as tk
from tkinter import ttk
from typing import ClassVar

from app.core.metrics import Metrics
from app.core.session import Session
from app.modes.base import BaseMode
from app.modes.random_keys import RandomKeysMode
from app.modes.words import WordsMode
from app.ui.components.widgets import BG, MUTED, PANEL, TEXT, Navigation, button, label
from app.ui.home import HomeView
from app.ui.i18n import LANGUAGES, tr
from app.ui.results_view import ResultsView
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
        self.history: list[Session] = []
        self.counts = {"words": 20, "random_keys": 40}
        self.word_difficulty = "hard"
        self.view: tk.Widget | None = None
        self._configure_theme()
        header = tk.Frame(self, bg=BG, padx=30, pady=20)
        header.pack(fill="x")
        label(header, "Keyboard Trainer", 22).pack(anchor="w", pady=(0, 18))
        self.navigation = Navigation(header, {})
        self.navigation.pack(anchor="w")
        self._refresh_navigation()
        self.content = tk.Frame(self, bg=BG, padx=30, pady=8)
        self.content.pack(fill="both", expand=True)
        self.show_home()

    def _refresh_navigation(self) -> None:
        for child in self.navigation.winfo_children():
            child.destroy()
        for title, action in {
            "Practice": self.show_home,
            "Statistics": self.show_statistics,
            "Settings": self.show_settings,
        }.items():
            button(self.navigation, title, action).pack(side="left", padx=(0, 8))

    def _configure_theme(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(
            "TProgressbar", troughcolor=PANEL, background="#9faaff", borderwidth=0
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
        style.map("Treeview", background=[("selected", "#414e80")])

    def _clear(self) -> None:
        if self.view is not None:
            self.view.destroy()
            self.view = None

    def _display(self, view: tk.Widget) -> None:
        self.view = view
        view.pack(fill="both", expand=True)

    def show_home(self) -> None:
        self._clear()
        self._display(
            HomeView(
                self.content,
                {key: mode.label for key, mode in self.mode_types.items()},
                self.start_mode,
            )
        )

    def start_mode(self, name: str, difficulty: str | None = None) -> None:
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
        self._clear()
        frame = tk.Frame(self.content, bg=BG)
        label(frame, "Statistics", 26).pack(anchor="w", pady=16)
        label(
            frame,
            "Completed sessions from this application run. History is kept in memory.",
            11,
            MUTED,
        ).pack(anchor="w", pady=(0, 20))
        if not self.history:
            label(
                frame, "Complete a practice session to see your progress.", color=MUTED
            ).pack(anchor="w")
        else:
            columns = ("session", "mode", "time", "wpm", "accuracy", "errors")
            table = ttk.Treeview(frame, columns=columns, show="headings")
            for column in columns:
                table.heading(column, text=tr(self, column.title()))
                table.column(column, width=110, minwidth=65)
            scrollbar = ttk.Scrollbar(frame, command=table.yview)
            table.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side="right", fill="y")
            table.pack(fill="both", expand=True)
            for index, session in enumerate(self.history, 1):
                metrics = Metrics.from_session(session)
                table.insert(
                    "",
                    "end",
                    values=(
                        index,
                        tr(self, self.mode_types[session.mode].label),
                        f"{metrics.elapsed_time:.1f}s",
                        f"{metrics.words_per_minute:.1f}",
                        f"{metrics.accuracy:.1f}%",
                        metrics.incorrect_inputs,
                    ),
                )
        self._display(frame)

    def show_settings(self, saved: bool = False) -> None:
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
            tk.Spinbox(
                frame,
                from_=1,
                to=200,
                textvariable=variables[key],
                width=8,
                bg=PANEL,
                fg=TEXT,
                buttonbackground=PANEL,
                insertbackground=TEXT,
            ).pack(anchor="w")
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
            self._refresh_navigation()
            self.show_settings(saved=True)

        button(frame, "Save settings", save).pack(anchor="w")
        self._display(frame)


def run() -> None:
    application = KeyboardTrainer()
    application.mainloop()
