import tkinter as tk

from app.core.chords import Chord
from app.ui.components.widgets import ACCENT, BG, MUTED, PANEL, TEXT


class GuitarDiagram(tk.Canvas):
    """Front-facing fretboard, low E at left; all coordinates scale to the view."""

    def __init__(self, parent: tk.Misc) -> None:
        super().__init__(parent, bg=PANEL, highlightthickness=0, width=300, height=240)
        self.chord: Chord | None = None
        self.bind("<Configure>", lambda event: self._draw())

    def set_chord(self, chord: Chord) -> None:
        self.chord = chord
        self._draw()

    def _draw(self) -> None:
        self.delete("all")
        if self.chord is None:
            return
        width, height = self.winfo_width(), self.winfo_height()
        spacing = min(44, (width - 80) / 5)
        fret_height = min(49, (height - 85) / 4)
        if spacing <= 0 or fret_height <= 0:
            return
        left, top = (width - spacing * 5) / 2, 40
        right, bottom = left + spacing * 5, top + fret_height * 4
        for index, note in enumerate(("E", "A", "D", "G", "B", "e")):
            x = left + index * spacing
            self.create_line(x, top, x, bottom, fill=MUTED, width=2 if index < 3 else 1)
            self.create_text(
                x,
                bottom + 22,
                text=f"{6 - index} · {note}",
                fill=MUTED,
                font=("DejaVu Sans", 10),
            )
            fret = self.chord.frets[index]
            if fret in (None, 0):
                self.create_text(
                    x,
                    top - 21,
                    text="X" if fret is None else "O",
                    fill=MUTED if fret is None else ACCENT,
                    font=("DejaVu Sans", 13, "bold"),
                )
        for fret in range(5):
            y = top + fret * fret_height
            self.create_line(
                left,
                y,
                right,
                y,
                fill=TEXT if fret == 0 else MUTED,
                width=5 if fret == 0 else 1,
            )
            if fret:
                self.create_text(
                    left - 25,
                    y - fret_height / 2,
                    text=str(fret),
                    fill=MUTED,
                    font=("DejaVu Sans", 10),
                )
        radius = min(14, spacing * 0.34, fret_height * 0.35)
        if self.chord.barre:
            fret, first, last = self.chord.barre
            x1, x2 = left + (6 - first) * spacing, left + (6 - last) * spacing
            y = top + (fret - 0.5) * fret_height
            self.create_line(
                x1, y, x2, y, fill=ACCENT, width=radius * 2, capstyle=tk.ROUND
            )
        for index, (fret, finger) in enumerate(
            zip(self.chord.frets, self.chord.fingers)
        ):
            if fret is None or fret == 0:
                continue
            x, y = left + index * spacing, top + (fret - 0.5) * fret_height
            self.create_oval(
                x - radius,
                y - radius,
                x + radius,
                y + radius,
                fill=ACCENT,
                outline=ACCENT,
            )
            self.create_text(
                x, y, text=str(finger), fill=BG, font=("DejaVu Sans", 11, "bold")
            )
