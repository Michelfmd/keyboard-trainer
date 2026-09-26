import tkinter as tk
from collections.abc import Callable
from tkinter import font

from app.ui.components.motion import Motion, blend
from app.ui.i18n import tr

BG = "#111718"
PANEL = "#1a2325"
BORDER = "#2b393b"
HOVER = "#293e3e"
TEXT = "#edf0e8"
MUTED = "#9baead"
ACCENT = "#a4e4cf"
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


class AnimatedButton(tk.Button):
    def __init__(
        self,
        parent: tk.Misc,
        text: str,
        command: Callable[[], None],
        *,
        primary: bool = False,
        quiet: bool = False,
    ) -> None:
        self.base_color = ACCENT if primary else parent.cget("bg") if quiet else BORDER
        self.hover_color = "#c3f1df" if primary else HOVER
        self.selected = False
        super().__init__(
            parent,
            text=tr(parent, text),
            command=command,
            bg=self.base_color,
            fg=BG if primary else TEXT,
            activebackground=self.hover_color,
            activeforeground=BG if primary else TEXT,
            relief="flat",
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=self.base_color,
            highlightcolor=ACCENT,
            font=("DejaVu Sans", 10),
            padx=16,
            pady=11,
            cursor="hand2",
        )
        self.motion = Motion(self)
        self.bind("<Enter>", lambda event: self._fade(self.hover_color))
        self.bind("<Leave>", lambda event: self._fade(self.base_color))

    def _fade(self, target: str) -> None:
        start = self.cget("bg")
        self.motion.animate(
            "hover",
            lambda amount: self.configure(
                bg=blend(start, target, amount),
                highlightbackground=ACCENT
                if self.selected
                else blend(start, target, amount),
            ),
            140,
        )

    def set_selected(self, selected: bool) -> None:
        self.motion.cancel("hover")
        self.selected = selected
        self.configure(
            fg=ACCENT if selected else MUTED,
            highlightbackground=ACCENT if selected else self.base_color,
        )


def button(
    parent: tk.Misc,
    text: str,
    command: Callable[[], None],
    *,
    primary: bool = False,
    quiet: bool = False,
) -> AnimatedButton:
    return AnimatedButton(parent, text, command, primary=primary, quiet=quiet)


class ProgressBar(tk.Canvas):
    def __init__(self, parent: tk.Misc) -> None:
        super().__init__(parent, height=4, bg=BORDER, highlightthickness=0)
        self.value = 0.0
        self.fill = self.create_rectangle(0, 0, 0, 4, fill=ACCENT, outline="")
        self.motion = Motion(self)
        self.bind("<Configure>", lambda event: self._draw())

    def _draw(self) -> None:
        self.coords(self.fill, 0, 0, self.winfo_width() * self.value, 4)

    def set(self, value: float) -> None:
        start = self.value
        target = max(0.0, min(1.0, value))

        def update(amount: float) -> None:
            self.value = start + (target - start) * amount
            self._draw()

        self.motion.animate("progress", update, 120)


class MetricCard(tk.Frame):
    def __init__(self, parent: tk.Misc, title: str) -> None:
        super().__init__(
            parent,
            bg=PANEL,
            padx=16,
            pady=14,
            highlightthickness=1,
            highlightbackground=BORDER,
        )
        label(self, title, 10, MUTED).pack(anchor="w")
        self.value = label(self, "—", 24, ACCENT)
        self.value.configure(font=("DejaVu Sans Mono", 24))
        self.value.pack(anchor="w", fill="x", pady=(5, 0))
        self.number_font = font.Font(self, family="DejaVu Sans Mono", size=24)
        self.value.configure(font=self.number_font)
        self.value.bind("<Configure>", lambda event: self._fit_value())

    def set(self, value: str) -> None:
        self.value.config(text=value)
        self._fit_value()

    def _fit_value(self) -> None:
        available = self.value.winfo_width()
        if available < 2:
            return
        size = 24
        self.number_font.configure(size=size)
        while (
            size > 10 and self.number_font.measure(self.value.cget("text")) > available
        ):
            size -= 1
            self.number_font.configure(size=size)


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
            borderwidth=0,
            highlightthickness=0,
            spacing1=5,
            spacing3=5,
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
        self.tag_configure(
            "current", background="#314a45", foreground=TEXT, underline=True
        )
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
