import tkinter as tk
from collections.abc import Callable

from app.core.events import LaptopChordAttempt
from app.core.laptop_chord_metrics import LaptopChordMetrics
from app.core.session import Session
from app.core.sound import sound_player
from app.modes.laptop_chord import FRET_KEYS, LaptopChordMode
from app.ui.components.guitar_diagram import GuitarDiagram
from app.ui.components.widgets import (
    ACCENT,
    BAD,
    BG,
    BORDER,
    GOOD,
    MUTED,
    PANEL,
    MetricCard,
    ProgressBar,
    button,
    label,
)
from app.ui.i18n import tr


class LaptopChordView(tk.Frame):
    def __init__(
        self,
        parent: tk.Misc,
        mode: LaptopChordMode,
        on_finish: Callable[[Session[LaptopChordAttempt]], None],
        on_cancel: Callable[[], None],
    ) -> None:
        super().__init__(parent, bg=BG)
        self.mode, self.on_finish, self.on_cancel = mode, on_finish, on_cancel
        self._bindings: list[tuple[str, str]] = []
        self._timer: str | None = None
        self._release_jobs: dict[str, tuple[str, int]] = {}
        self.keycaps: dict[str, tk.Label] = {}
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", pady=(8, 8))
        label(header, "Laptop chord changes", 22, ACCENT).pack(side="left")
        button(header, "Stop / Esc", self._stop).pack(side="right")
        label(
            self,
            "Complete the highlighted shape. The next chord appears immediately.",
            10,
            MUTED,
        ).pack(anchor="w")
        cards = tk.Frame(self, bg=BG)
        cards.pack(fill="x", pady=(10, 8))
        self.cards: dict[str, MetricCard] = {}
        for column, title in enumerate(
            ("Timer", "Changes", "Avg. change", "Accuracy", "Errors")
        ):
            cards.columnconfigure(column, weight=1, uniform="laptop_metrics")
            card = MetricCard(cards, title)
            card.grid(row=0, column=column, sticky="ew", padx=(0, 7))
            self.cards[title] = card
        self.progress = ProgressBar(self)
        self.progress.pack(fill="x", pady=(4, 8))
        body = tk.Frame(self, bg=PANEL, padx=14, pady=8)
        body.pack(fill="both", expand=True)
        left = tk.Frame(body, bg=PANEL)
        left.pack(side="left", fill="both", expand=True)
        self.title_label = label(left, "", 24, ACCENT)
        self.title_label.pack()
        self.diagram = GuitarDiagram(left)
        self.diagram.pack(fill="both", expand=True)
        right = tk.Frame(body, bg=PANEL, padx=10)
        right.pack(side="right", fill="y")
        label(right, "Laptop fret grid", 13).pack(anchor="w", pady=(5, 10))
        label(right, "Each column represents strings 6 → 1.", 9, MUTED).pack(anchor="w")
        for fret, keys in FRET_KEYS.items():
            row = tk.Frame(right, bg=PANEL)
            row.pack(anchor="w", pady=5)
            label(row, f"{tr(self, 'Fret')} {fret}", 9, MUTED).pack(
                side="left", padx=(0, 8)
            )
            for key in keys:
                cap = tk.Label(
                    row,
                    text=key.upper(),
                    width=2,
                    pady=4,
                    bg=BG,
                    fg=MUTED,
                    font=("DejaVu Sans Mono", 10, "bold"),
                    highlightthickness=1,
                    highlightbackground=BORDER,
                )
                cap.pack(side="left", padx=2)
                self.keycaps[key] = cap
        self.feedback = label(self, "", 10, MUTED)
        self.feedback.pack(anchor="w", pady=8)
        self.mode.start()
        root = self.winfo_toplevel()
        self._bindings = [
            ("<KeyPress>", root.bind("<KeyPress>", self._key_down, add="+")),
            ("<KeyRelease>", root.bind("<KeyRelease>", self._key_up, add="+")),
            ("<FocusOut>", root.bind("<FocusOut>", self._focus_out, add="+")),
        ]
        self._render()
        self._tick()

    def _key_down(self, event: tk.Event) -> str | None:
        if event.keysym == "Escape":
            self._stop()
            return "break"
        key = self._event_key(event)
        pending_release = self._release_jobs.pop(key, None)
        if pending_release is not None:
            release_job, release_time = pending_release
            self.after_cancel(release_job)
            if event.time == release_time:
                return "break"
            self.mode.handle_key_up(key)
        completed = self.mode.handle_key_down(key)
        if completed and getattr(self.winfo_toplevel(), "sound_enabled", True):
            sound_player.play_chord(completed.expected_chord)
        if self.mode.is_finished():
            self.on_finish(self.mode.session)
            return "break"
        self._render()
        return None

    def _key_up(self, event: tk.Event) -> None:
        key = self._event_key(event)
        if not key or key in self._release_jobs:
            return
        job = self.after_idle(self._finish_release, key)
        self._release_jobs[key] = (job, event.time)

    def _finish_release(self, key: str) -> None:
        self._release_jobs.pop(key, None)
        completed = self.mode.handle_key_up(key)
        if completed and getattr(self.winfo_toplevel(), "sound_enabled", True):
            sound_player.play_chord(completed.expected_chord)
        if self.mode.is_finished():
            self.on_finish(self.mode.session)
            return
        self._render()

    @staticmethod
    def _event_key(event: tk.Event) -> str:
        char = event.char.lower()
        if char:
            return char
        keysym = event.keysym.lower()
        return keysym if len(keysym) == 1 else ""

    def _focus_out(self, event: tk.Event) -> None:
        for job, _ in self._release_jobs.values():
            self.after_cancel(job)
        self._release_jobs.clear()
        self.mode.clear_pressed_keys()
        self._render()

    def _render(self) -> None:
        chord = self.mode.get_target()
        if chord is None:
            return
        self.title_label.configure(text=f"{chord.name}  /  {tr(self, chord.full_name)}")
        self.diagram.set_chord(chord)
        expected = self.mode.expected_keys
        for key, cap in self.keycaps.items():
            pressed = key in self.mode.pressed_keys
            wanted = key in expected
            cap.configure(
                bg=GOOD if pressed and wanted else BAD if pressed else PANEL,
                fg=BG if pressed else ACCENT if wanted else MUTED,
                highlightbackground=ACCENT if wanted else BORDER,
            )
        target = " + ".join(key.upper() for key in sorted(expected))
        self.feedback.configure(text=tr(self, "Hold together: {keys}", keys=target))
        self.progress.set(self.mode.progress)

    def _tick(self) -> None:
        metrics = LaptopChordMetrics.from_session(self.mode.session)
        values = {
            "Timer": f"{self.mode.session.elapsed_time:.1f}s",
            "Changes": str(metrics.completed),
            "Avg. change": f"{metrics.average_change:.2f}s",
            "Accuracy": f"{metrics.accuracy:.1f}%",
            "Errors": str(metrics.errors),
        }
        for title, value in values.items():
            self.cards[title].set(value)
        self._timer = self.after(150, self._tick)

    def _stop(self) -> None:
        self.mode.session.finish()
        if self.mode.session.events:
            self.on_finish(self.mode.session)
        else:
            self.on_cancel()

    def destroy(self) -> None:
        for sequence, identifier in self._bindings:
            self.winfo_toplevel().unbind(sequence, identifier)
        if self._timer:
            self.after_cancel(self._timer)
        for job, _ in self._release_jobs.values():
            self.after_cancel(job)
        self._release_jobs.clear()
        self.mode.session.finish()
        super().destroy()
