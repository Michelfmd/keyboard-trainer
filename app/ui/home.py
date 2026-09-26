import tkinter as tk
from collections.abc import Callable

from app.ui.components.widgets import ACCENT, BG, MUTED, PANEL, button, label


class HomeView(tk.Frame):
    def __init__(
        self,
        parent: tk.Misc,
        modes: dict[str, str],
        on_start: Callable[[str, str], None],
    ) -> None:
        super().__init__(parent, bg=BG)
        label(self, "Make every keystroke count.", 28).pack(anchor="w", pady=(30, 10))
        label(
            self,
            "Build speed, improve accuracy, and understand your typing.",
            color=MUTED,
        ).pack(anchor="w", pady=(0, 30))
        descriptions = {
            "words": "Practice a sequence of local words.\nEach character advances the exercise.",
            "random_keys": "Train individual keys with a live keyboard.\nHit the correct key to continue.",
        }
        for key, title in modes.items():
            card = tk.Frame(self, bg=PANEL, padx=24, pady=22)
            card.pack(fill="x", pady=8)
            label(card, title, 20, ACCENT).pack(anchor="w")
            label(card, descriptions.get(key, ""), color=MUTED).pack(
                anchor="w", pady=12
            )
            if key == "words":
                actions = tk.Frame(card, bg=PANEL)
                actions.pack(anchor="w")
                for difficulty, caption in (
                    ("easy", "Easy: 1–2 words"),
                    ("medium", "Medium: 3–4 words"),
                    ("hard", "Hard: full exercise"),
                ):
                    button(
                        actions,
                        caption,
                        lambda level=difficulty: on_start("words", level),
                    ).pack(side="left", padx=(0, 8))
            else:
                button(
                    card, "Start practice", lambda name=key: on_start(name, "hard")
                ).pack(anchor="w")
        label(
            self,
            "Timing starts when the exercise appears. Escape returns to Practice.",
            10,
            MUTED,
        ).pack(anchor="w", pady=20)
