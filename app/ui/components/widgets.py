import tkinter as tk
from collections.abc import Callable

from app.ui.i18n import tr

BG = "#10141e"
PANEL = "#1a2130"
TEXT = "#e7ecf5"
MUTED = "#98a5bd"
ACCENT = "#9faaff"
GOOD = "#6eddb3"
BAD = "#ff8797"


def label(parent: tk.Misc, text: str, size: int = 12, color: str = TEXT) -> tk.Label:
    return tk.Label(
        parent,
        text=tr(parent, text),
        font=("DejaVu Sans", size),
        fg=color,
        bg=parent.cget("bg"),
        anchor="w",
        justify="left",
    )


def button(parent: tk.Misc, text: str, command: Callable[[], None]) -> tk.Button:
    return tk.Button(
        parent,
        text=tr(parent, text),
        command=command,
        bg=PANEL,
        fg=TEXT,
        activebackground=ACCENT,
        activeforeground=BG,
        relief="flat",
        font=("DejaVu Sans", 11),
        padx=18,
        pady=10,
        cursor="hand2",
    )


class MetricCard(tk.Frame):
    def __init__(self, parent: tk.Misc, title: str) -> None:
        super().__init__(parent, bg=PANEL, padx=16, pady=12)
        label(self, title, 10, MUTED).pack(anchor="w")
        self.value = label(self, "—", 22)
        self.value.pack(anchor="w", pady=(5, 0))

    def set(self, value: str) -> None:
        self.value.config(text=value)


class Navigation(tk.Frame):
    def __init__(self, parent: tk.Misc, actions: dict[str, Callable[[], None]]) -> None:
        super().__init__(parent, bg=BG)
        for title, action in actions.items():
            button(self, title, action).pack(side="left", padx=(0, 8))


class TestText(tk.Text):
    def __init__(self, parent: tk.Misc) -> None:
        super().__init__(
            parent,
            bg=PANEL,
            fg=MUTED,
            relief="flat",
            wrap="word",
            font=("DejaVu Sans Mono", 21),
            padx=24,
            pady=24,
            height=5,
            width=1,
            cursor="arrow",
            takefocus=False,
            exportselection=False,
        )
        self.tag_configure("correct", foreground=GOOD)
        self.tag_configure("incorrect", foreground=BAD, underline=True)
        self.tag_configure("current", background=ACCENT, foreground=BG)
        self.bind("<Button-1>", lambda event: "break")

    def show(self, target: str, position: int, outcomes: list[bool]) -> None:
        self.config(state="normal")
        self.delete("1.0", "end")
        self.insert("1.0", target)
        for index, correct in enumerate(outcomes):
            self.tag_add(
                "correct" if correct else "incorrect",
                f"1.0+{index}c",
                f"1.0+{index + 1}c",
            )
        self.tag_add("current", f"1.0+{position}c", f"1.0+{position + 1}c")
        self.see(f"1.0+{position}c")
        self.config(state="disabled")
