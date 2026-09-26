import tkinter as tk
from collections.abc import Callable

from app.ui.components.widgets import ACCENT, BG, BORDER, MUTED, PANEL, button, label


class HomeView(tk.Frame):
    def __init__(
        self,
        parent: tk.Misc,
        modes: dict[str, str],
        on_start: Callable[[str, str], None],
    ) -> None:
        super().__init__(parent, bg=BG)
        eyebrow = label(self, "YOUR DAILY PRACTICE", 9, ACCENT)
        eyebrow.configure(font=("DejaVu Sans Mono", 9))
        eyebrow.pack(anchor="w", pady=(24, 12))
        label(self, "Find your typing rhythm.", 32).pack(anchor="w")
        label(
            self,
            "A little focus. A little practice. Steady progress.",
            12,
            MUTED,
        ).pack(anchor="w", pady=(10, 24))

        descriptions = {
            "words": "Build accuracy and flow with real words.",
            "random_keys": "One key at a time. Train your muscle memory.",
        }
        for index, (key, title) in enumerate(modes.items(), 1):
            card = tk.Frame(
                self,
                bg=PANEL,
                padx=24,
                pady=20,
                highlightthickness=1,
                highlightbackground=BORDER,
            )
            card.pack(fill="x", pady=(0, 14))
            top = tk.Frame(card, bg=PANEL)
            top.pack(fill="x")
            label(top, f"0{index}", 12, ACCENT).pack(side="left", padx=(0, 16))
            label(top, title, 21).pack(side="left")
            label(
                top, "ACCURACY + FLOW" if key == "words" else "MUSCLE MEMORY", 9, MUTED
            ).pack(side="right")
            label(card, descriptions.get(key, ""), 11, MUTED).pack(
                anchor="w", pady=(12, 20)
            )
            actions = tk.Frame(card, bg=PANEL)
            actions.pack(fill="x")
            if key == "words":
                for difficulty, caption in (
                    ("easy", "Easy: 1–2 words"),
                    ("medium", "Medium: 3–4 words"),
                    ("hard", "Hard: full exercise"),
                ):
                    button(
                        actions,
                        caption,
                        lambda level=difficulty: on_start("words", level),
                        primary=difficulty == "easy",
                    ).pack(side="left", padx=(0, 10))
            else:
                button(
                    actions,
                    "Start practice",
                    lambda name=key: on_start(name, "hard"),
                    primary=True,
                ).pack(side="left")
                for letter in ["F", "J"]:
                    tk.Label(
                        actions,
                        text=letter,
                        font=("DejaVu Sans Mono", 13),
                        fg=MUTED,
                        bg=BG,
                        padx=15,
                        pady=8,
                        highlightthickness=1,
                        highlightbackground=BORDER,
                    ).pack(side="right", padx=(8, 0))
        label(
            self, "Choose a level. The timer starts with the exercise.", 10, MUTED
        ).pack(anchor="w", pady=(4, 12))
