import tkinter as tk
from collections.abc import Callable

from app.data.chords import CHORDS
from app.ui.components.widgets import ACCENT, BG, MUTED, PANEL, button, label


class GuitarHomeView(tk.Frame):
    def __init__(self, parent: tk.Misc, on_start: Callable[[str, str], None]) -> None:
        super().__init__(parent, bg=BG)
        label(self, "Guitar", 27, ACCENT).pack(anchor="w", pady=(14, 8))
        label(self, "Learn chords at your own pace.", 14).pack(anchor="w")
        label(
            self,
            "Choose manual guitar practice or simulate each shape on your laptop.",
            11,
            MUTED,
        ).pack(anchor="w", pady=(8, 16))
        for difficulty, title in (
            ("easy", "Easy: first chords"),
            ("medium", "Medium: open chords"),
            ("hard", "Hard: barre chords"),
        ):
            card = tk.Frame(self, bg=PANEL, padx=20, pady=14)
            card.pack(fill="x", pady=(0, 12))
            label(card, title, 17).pack(anchor="w")
            label(
                card,
                "   ·   ".join(
                    chord.name for chord in CHORDS if chord.difficulty == difficulty
                ),
                12,
                MUTED,
            ).pack(side="left", pady=(10, 0))
            actions = tk.Frame(card, bg=PANEL)
            actions.pack(side="right", pady=(8, 0))
            button(
                actions,
                "With guitar",
                lambda level=difficulty: on_start("chords", level),
            ).pack(side="left", padx=(0, 8))
            button(
                actions,
                "Laptop keys",
                lambda level=difficulty: on_start("chord_changes", level),
                primary=True,
            ).pack(side="left")
        label(
            self,
            "Laptop mode measures how quickly you form and change chord shapes.",
            10,
            MUTED,
        ).pack(anchor="w")
