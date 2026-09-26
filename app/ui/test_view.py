import tkinter as tk
from collections.abc import Callable

from app.core.metrics import Metrics
from app.core.session import Session
from app.modes.base import BaseMode
from app.ui.components.widgets import (
    ACCENT,
    BAD,
    BG,
    GOOD,
    MUTED,
    PANEL,
    MetricCard,
    ProgressBar,
    TestText,
    button,
    label,
)
from app.ui.i18n import tr
from app.ui.keyboard_view import KeyboardView


class TestView(tk.Frame):
    def __init__(
        self,
        parent: tk.Misc,
        mode: BaseMode,
        on_finish: Callable[[Session], None],
        on_cancel: Callable[[], None],
    ) -> None:
        super().__init__(parent, bg=BG)
        self.mode = mode
        self.on_finish = on_finish
        self.on_cancel = on_cancel
        self._timer: str | None = None
        self._binding: str | None = None
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", pady=(8, 12))
        label(header, mode.label, 22, ACCENT).pack(side="left")
        self.stop_button = button(header, "Stop / Esc", self._stop)
        self.stop_button.pack(side="right")
        cards = tk.Frame(self, bg=BG)
        cards.pack(fill="x")
        self.cards: dict[str, MetricCard] = {}
        for column, title in enumerate(("Time", "WPM", "Accuracy", "Errors")):
            cards.columnconfigure(column, weight=1, uniform="metrics")
            card = MetricCard(cards, title)
            card.grid(row=0, column=column, sticky="ew", padx=(0, 8))
            self.cards[title] = card
        self.progress = ProgressBar(self)
        self.progress.pack(fill="x", pady=(14, 8))
        self.progress_label = label(self, "", 10, MUTED)
        self.progress_label.pack(anchor="w")
        self.text = TestText(self)
        if mode.show_keyboard:
            self.text.configure(height=1, pady=10, font=("DejaVu Sans Mono", 36))
            self.text.tag_configure("center", justify="center")
            self.text.tag_configure(
                "current", background=PANEL, foreground=ACCENT, underline=False
            )
        self.text.pack(fill="both", expand=True, pady=16)
        self.feedback = label(
            self, "Type the highlighted character to begin.", 11, MUTED
        )
        self.feedback.pack(anchor="w", pady=(0, 10))
        self.keyboard: KeyboardView | None = None
        if mode.show_keyboard:
            self.keyboard = KeyboardView(self)
            self.keyboard.pack(fill="x", pady=(0, 10))
        label(
            self,
            "Correct: green  •  Error: pink underline  •  Current: highlighted   |   Esc: cancel",
            10,
            MUTED,
        ).pack(anchor="w", pady=8)
        self.mode.start()
        self._render_target()
        self._binding = self.winfo_toplevel().bind("<KeyPress>", self._on_key, add="+")
        self.focus_set()
        self._tick()

    def _stop(self) -> None:
        self.mode.session.finish()
        self.on_cancel()

    def _on_key(self, event: tk.Event) -> str:
        if event.keysym == "Escape":
            self._stop()
            return "break"
        # Suppress Ctrl/Alt/Super shortcuts; Shift is allowed for printable input.
        if event.state & (0x4 | 0x8 | 0x40 | 0x80 | 0x20000):
            return "break"
        result = self.mode.handle_input(event.char)
        if result is None:
            return "break"
        expected = (
            tr(self, "SPACE") if result.expected_key == " " else result.expected_key
        )
        pressed = tr(self, "SPACE") if result.pressed_key == " " else result.pressed_key
        self.feedback.config(
            text=tr(
                self,
                "Expected: {expected}    Pressed: {pressed}    {result}    {time:.0f} ms",
                expected=expected,
                pressed=pressed,
                result=tr(self, "Correct" if result.correct else "Incorrect"),
                time=result.response_time * 1000,
            ),
            fg=GOOD if result.correct else BAD,
        )
        if self.keyboard:
            self.keyboard.flash(result.pressed_key, result.correct)
        self._render_target()
        if self.mode.is_finished():
            self.on_finish(self.mode.session)
        return "break"

    def _render_target(self) -> None:
        if self.mode.show_keyboard:
            self.text.show(self.mode.get_target(), 0, [])
            self.text.tag_add("center", "1.0", "end")
        else:
            self.text.show(self.mode.target, self.mode.position, self.mode.outcomes)
        self.progress.set(self.mode.progress)
        self.progress_label.config(
            text=tr(
                self,
                "{position} / {total} characters",
                position=self.mode.position,
                total=len(self.mode.target),
            )
        )
        if self.keyboard:
            self.keyboard.set_expected(self.mode.get_target())

    def _tick(self) -> None:
        metrics = Metrics.from_session(self.mode.session)
        for title, value in {
            "Time": f"{metrics.elapsed_time:.1f}s",
            "WPM": f"{metrics.words_per_minute:.1f}",
            "Accuracy": f"{metrics.accuracy:.1f}%",
            "Errors": str(metrics.incorrect_inputs),
        }.items():
            self.cards[title].set(value)
        self._timer = self.after(100, self._tick)

    def destroy(self) -> None:
        if self._timer:
            self.after_cancel(self._timer)
        if self._binding:
            self.winfo_toplevel().unbind("<KeyPress>", self._binding)
        super().destroy()
