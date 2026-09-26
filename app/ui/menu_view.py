import tkinter as tk
from collections.abc import Callable

from app.activities import Activity
from app.ui.components.widgets import ACCENT, BG, BORDER, MUTED, PANEL, button, label
from app.ui.i18n import tr


class MenuView(tk.Frame):
    def __init__(
        self,
        parent: tk.Misc,
        activities: tuple[Activity, ...],
        on_open: Callable[[str], None],
        on_settings: Callable[[], None],
    ) -> None:
        super().__init__(parent, bg=BG)
        label(self, "YOUR PRACTICE SPACE", 9, ACCENT).pack(anchor="w", pady=(22, 12))
        label(self, "What would you like to practice?", 27).pack(anchor="w")
        label(self, "Choose an activity or adjust your preferences.", 11, MUTED).pack(
            anchor="w", pady=(10, 22)
        )
        for index, activity in enumerate(activities, 1):
            card = tk.Frame(
                self,
                bg=PANEL,
                padx=22,
                pady=16,
                highlightthickness=1,
                highlightbackground=BORDER,
            )
            card.pack(fill="x", pady=(0, 12))
            top = tk.Frame(card, bg=PANEL)
            top.pack(fill="x")
            label(top, f"0{index}", 11, ACCENT if activity.available else MUTED).pack(
                side="left", padx=(0, 14)
            )
            label(
                top, activity.title, 21, ACCENT if activity.available else MUTED
            ).pack(side="left")
            label(
                top, "Available" if activity.available else "Coming soon", 10, MUTED
            ).pack(side="right")
            label(card, activity.description, 11, MUTED).pack(anchor="w", pady=(10, 14))
            if activity.available:
                button(
                    card,
                    "Open Keyboard",
                    lambda key=activity.key: on_open(key),
                    primary=True,
                ).pack(anchor="w")
            else:
                tk.Button(
                    card,
                    text=tr(self, "Not available yet"),
                    state="disabled",
                    takefocus=False,
                    bg=BORDER,
                    disabledforeground=MUTED,
                    relief="flat",
                    borderwidth=0,
                    padx=16,
                    pady=10,
                ).pack(anchor="w")
        settings = tk.Frame(self, bg=BG)
        settings.pack(fill="x", pady=(8, 0))
        label(settings, "Language, exercise length and motion.", 11, MUTED).pack(
            side="left"
        )
        button(settings, "Settings", on_settings).pack(side="right")
