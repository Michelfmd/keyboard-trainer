import tkinter as tk

from app.core.keyboard_layout import KeyboardLayout
from app.ui.components.motion import Motion, blend
from app.ui.components.widgets import ACCENT, BAD, BG, BORDER, GOOD, MUTED, PANEL, TEXT
from app.ui.i18n import tr


class KeyboardView(tk.Frame):
    def __init__(self, parent: tk.Misc, layout: KeyboardLayout | None = None) -> None:
        super().__init__(parent, bg=BG)
        self.layout = layout if layout is not None else KeyboardLayout()
        self.keys: dict[str, tk.Label] = {}
        self.expected = ""
        self.motion = Motion(self)
        self._timers: dict[str, str] = {}
        for row_index, row in enumerate(self.layout.rows):
            frame = tk.Frame(self, bg=BG)
            frame.pack(
                fill="x", padx=(int(self.layout.offsets[row_index] * 16), 0), pady=3
            )
            for column, key in enumerate(row):
                frame.columnconfigure(column, weight=1, uniform="keys")
                key_label = tk.Label(
                    frame,
                    text=tr(self, "SPACE") if key == " " else key.upper(),
                    bg=PANEL,
                    fg=MUTED,
                    font=("DejaVu Sans Mono", 12),
                    pady=5,
                    highlightthickness=1,
                    highlightbackground=BORDER,
                )
                key_label.grid(row=0, column=column, sticky="ew", padx=3)
                self.keys[key] = key_label

    def set_expected(self, key: str) -> None:
        self.expected = self.layout.normalize(key)
        for name, widget in self.keys.items():
            widget.config(
                highlightbackground=ACCENT if name == self.expected else BORDER
            )

    def flash(self, key: str, correct: bool) -> None:
        key = self.layout.normalize(key)
        if key not in self.keys:
            return
        if key in self._timers:
            self.after_cancel(self._timers.pop(key))
        self.motion.cancel(key)
        self.keys[key].config(bg=GOOD if correct else BAD, fg=BG)
        self._timers[key] = self.after(180, lambda: self._clear(key))

    def _clear(self, key: str) -> None:
        self._timers.pop(key, None)
        widget = self.keys[key]
        start = widget.cget("bg")
        self.motion.animate(
            key,
            lambda amount: widget.configure(
                bg=blend(start, PANEL, amount),
                fg=blend(BG, TEXT, amount),
            ),
            160,
        )

    def destroy(self) -> None:
        for timer in self._timers.values():
            self.after_cancel(timer)
        super().destroy()
