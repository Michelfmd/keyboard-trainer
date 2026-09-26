import tkinter as tk
import webbrowser
from collections.abc import Callable

from app.core.events import ChordAttempt
from app.core.session import Session
from app.core.sound import sound_player
from app.modes.chord import ChordMode
from app.ui.components.guitar_diagram import GuitarDiagram
from app.ui.components.widgets import (
    ACCENT,
    BG,
    MUTED,
    PANEL,
    ProgressBar,
    button,
    label,
)
from app.ui.i18n import tr


class ChordView(tk.Frame):
    def __init__(
        self,
        parent: tk.Misc,
        mode: ChordMode,
        on_finish: Callable[[Session[ChordAttempt]], None],
        on_cancel: Callable[[], None],
    ) -> None:
        super().__init__(parent, bg=BG)
        self.mode, self.on_finish, self.on_cancel = mode, on_finish, on_cancel
        self._bindings: list[tuple[str, str]] = []
        self._enter_held = False
        self._release_job: str | None = None
        self._timer: str | None = None
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", pady=(10, 8))
        label(header, "Guitar chords", 22, ACCENT).pack(side="left")
        self.stop_button = button(header, "Stop / Esc", self._stop)
        self.stop_button.pack(side="right")
        label(self, "Manual practice: sound is not evaluated.", 10, MUTED).pack(
            anchor="w"
        )
        self.progress = ProgressBar(self)
        self.progress.pack(fill="x", pady=(12, 6))
        self.status = label(self, "", 10, MUTED)
        self.status.pack(anchor="w")
        body = tk.Frame(self, bg=PANEL, padx=18, pady=10)
        body.pack(fill="both", expand=True, pady=12)
        self.chord_title = label(body, "", 25, ACCENT)
        self.chord_title.pack()
        label(body, "Standard tuning · E A D G B e", 10, MUTED).pack(pady=3)
        middle = tk.Frame(body, bg=PANEL)
        middle.pack(fill="both", expand=True)
        self.diagram = GuitarDiagram(middle)
        self.diagram.pack(side="left", fill="both", expand=True)
        self.instructions = label(middle, "", 11)
        self.instructions.configure(justify="left", anchor="w")
        self.instructions.pack(side="right", padx=(12, 8))
        label(body, "Left: string 6 (thick) · Right: string 1 (thin)", 10, MUTED).pack()
        label(self, "O: open string   X: do not play   Bar: barre", 10, MUTED).pack(
            anchor="w"
        )
        label(self, "Fingers: 1 index · 2 middle · 3 ring · 4 little", 10, MUTED).pack(
            anchor="w", pady=(4, 10)
        )
        actions = tk.Frame(self, bg=BG)
        actions.pack(fill="x", pady=(0, 8))
        self.practice_button = button(
            actions, "Practiced / Enter", self._practice, primary=True
        )
        self.practice_button.pack(side="left")
        self.skip_button = button(actions, "Skip", self._skip)
        self.skip_button.pack(side="left", padx=10)
        button(actions, "View lesson", self._open_lesson, quiet=True).pack(side="right")
        button(actions, "Play chord", self._play_chord, quiet=True).pack(
            side="right", padx=8
        )
        self.mode.start()
        self._render()
        root = self.winfo_toplevel()
        for sequence, callback in (
            ("<KeyPress-Return>", self._enter_down),
            ("<KeyPress-KP_Enter>", self._enter_down),
            ("<KeyRelease-Return>", self._enter_up),
            ("<KeyRelease-KP_Enter>", self._enter_up),
            ("<Escape>", lambda event: self._stop()),
            ("<FocusOut>", self._focus_out),
        ):
            self._bindings.append((sequence, root.bind(sequence, callback, add="+")))
        self._tick()

    def _enter_down(self, event: tk.Event) -> str:
        # Coalesce X11's synthetic release/press pairs while a key is held.
        if self._release_job:
            self.after_cancel(self._release_job)
            self._release_job = None
        self._enter_held = True
        return "break"

    def _enter_up(self, event: tk.Event) -> str:
        if self._enter_held and self._release_job is None:
            self._release_job = self.after_idle(self._finish_enter)
        return "break"

    def _finish_enter(self) -> None:
        self._release_job = None
        self._enter_held = False
        self._practice()

    def _focus_out(self, event: tk.Event) -> None:
        self._enter_held = False
        if self._release_job:
            self.after_cancel(self._release_job)
            self._release_job = None

    def _practice(self) -> None:
        self._play_chord()
        self.mode.mark_practiced()
        self._after_action()

    def _skip(self) -> None:
        self.mode.skip()
        self._after_action()

    def _after_action(self) -> None:
        if self.mode.is_finished():
            self.on_finish(self.mode.session)
        else:
            self._render()

    def _render(self) -> None:
        chord = self.mode.get_target()
        if chord is None:
            return
        self.chord_title.configure(text=f"{chord.name}  /  {tr(self, chord.full_name)}")
        self.diagram.set_chord(chord)
        lines = []
        for index, (fret, finger) in enumerate(zip(chord.frets, chord.fingers)):
            detail = (
                tr(self, "Do not play")
                if fret is None
                else tr(self, "Open")
                if fret == 0
                else tr(self, "Fret {fret} · finger {finger}", fret=fret, finger=finger)
            )
            lines.append(f"{6 - index}  |  {detail}")
        if chord.barre:
            fret, first, last = chord.barre
            lines.extend(
                (
                    "",
                    tr(
                        self,
                        "Barre: fret {fret}, strings {first}–{last}",
                        fret=fret,
                        first=first,
                        last=last,
                    ),
                )
            )
        self.instructions.configure(text="\n".join(lines))
        self.progress.set(self.mode.progress)

    def _tick(self) -> None:
        self.status.configure(
            text=tr(
                self,
                "Reviewed: {done} / {total}    Time: {time}s",
                done=self.mode.position,
                total=self.mode.count,
                time=f"{self.mode.session.elapsed_time:.0f}",
            )
        )
        self._timer = self.after(200, self._tick)

    def _open_lesson(self) -> None:
        chord = self.mode.get_target()
        if chord:
            webbrowser.open(f"https://chordbank.com/chords/{chord.source}/")

    def _play_chord(self) -> None:
        chord = self.mode.get_target()
        if chord and getattr(self.winfo_toplevel(), "sound_enabled", True):
            sound_player.play_chord(chord)

    def _stop(self) -> None:
        self.mode.session.finish()
        if self.mode.session.events:
            self.on_finish(self.mode.session)
        else:
            self.on_cancel()

    def destroy(self) -> None:
        for sequence, identifier in self._bindings:
            self.winfo_toplevel().unbind(sequence, identifier)
        for job in (self._timer, self._release_job):
            if job:
                self.after_cancel(job)
        self.mode.session.finish()
        super().destroy()
