import tkinter as tk
from collections.abc import Callable
from tkinter import ttk

from app.core.keyboard_layout import KeyboardLayout
from app.core.metrics import Metrics, error_counts
from app.core.session import Session
from app.ui.components.widgets import ACCENT, BG, MUTED, MetricCard, button, label
from app.ui.i18n import tr


class ResultsView(tk.Frame):
    def __init__(
        self, parent: tk.Misc, session: Session, on_retry: Callable[[], None]
    ) -> None:
        super().__init__(parent, bg=BG)
        self.on_retry = on_retry
        actions = tk.Frame(self, bg=BG)
        actions.pack(side="bottom", fill="x", pady=(14, 0))
        button(actions, "Practice again", on_retry, primary=True).pack(side="left")
        label(actions, "Enter for the next exercise", 10, MUTED).pack(
            side="left", padx=16
        )
        metrics = Metrics.from_session(session)
        label(self, "Results", 26, ACCENT).pack(anchor="w", pady=(12, 16))
        grid = tk.Frame(self, bg=BG)
        grid.pack(fill="x")
        values = {
            "Time": f"{metrics.elapsed_time:.1f}s",
            "Accuracy": f"{metrics.accuracy:.1f}%",
            "WPM": f"{metrics.words_per_minute:.1f}",
            "CPM": f"{metrics.characters_per_minute:.1f}",
            "Correct": str(metrics.correct_inputs),
            "Errors": str(metrics.incorrect_inputs),
            "Average response": f"{metrics.average_response_time * 1000:.0f} ms",
            "Keys / second": f"{metrics.keys_per_second:.2f}",
        }
        for index, (title, value) in enumerate(values.items()):
            grid.columnconfigure(index % 4, weight=1, uniform="results")
            card = MetricCard(grid, title)
            card.grid(
                row=index // 4, column=index % 4, sticky="nsew", padx=(0, 8), pady=4
            )
            card.set(value)
        label(
            self,
            tr(
                self,
                "Total inputs: {total}    Correct characters / second: {rate:.2f}",
                total=metrics.total_inputs,
                rate=metrics.characters_per_second,
            ),
            10,
            MUTED,
        ).pack(anchor="w", pady=(10, 0))
        errors = error_counts(session.events)
        summary = ", ".join(
            f"{tr(self, 'SPACE') if key == ' ' else key}: {count}"
            for key, count in errors.most_common(6)
        )
        label(
            self,
            tr(
                self,
                "Most missed keys: {summary}",
                summary=summary or tr(self, "No errors"),
            ),
            12,
        ).pack(anchor="w", pady=(16, 6))
        layout = KeyboardLayout()
        fingers = ", ".join(
            f"{tr(self, finger)}: {count}"
            for finger, count in layout.finger_errors(session.events).most_common()
        )
        finger_label = label(
            self,
            tr(
                self,
                "Approximate finger errors: {summary}",
                summary=fingers or tr(self, "None"),
            ),
            10,
            MUTED,
        )
        finger_label.pack(fill="x", pady=(0, 10))
        finger_label.bind(
            "<Configure>", lambda event: finger_label.config(wraplength=event.width)
        )
        label(self, "Error history", 14).pack(anchor="w", pady=6)
        table_frame = tk.Frame(self, bg=BG)
        table_frame.pack(fill="both", expand=True)
        columns = ("expected", "pressed", "time", "response", "nearby")
        table = ttk.Treeview(table_frame, columns=columns, show="headings", height=5)
        for key, title in zip(
            columns, ("Expected", "Pressed", "Elapsed", "Response", "Nearby key")
        ):
            table.heading(key, text=tr(self, title))
            table.column(key, width=100, minwidth=65, stretch=True)
        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=table.yview)
        table.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        table.pack(side="left", fill="both", expand=True)
        for event in session.events:
            if event.correct:
                continue
            table.insert(
                "",
                "end",
                values=(
                    tr(self, "SPACE")
                    if event.expected_key == " "
                    else event.expected_key,
                    tr(self, "SPACE")
                    if event.pressed_key == " "
                    else event.pressed_key,
                    f"{event.timestamp - (session.started_at or 0):.2f}s",
                    f"{event.response_time * 1000:.0f} ms",
                    tr(self, "Yes")
                    if layout.are_neighbors(event.expected_key, event.pressed_key)
                    else tr(self, "No"),
                ),
            )

        self._bindings = {
            key: self.winfo_toplevel().bind(key, self._on_retry_key, add="+")
            for key in ("<Return>", "<KP_Enter>")
        }
        self.focus_set()

    def _on_retry_key(self, event: tk.Event) -> str:
        if not event.state & (0x4 | 0x8 | 0x40 | 0x80 | 0x20000):
            self.on_retry()
        return "break"

    def destroy(self) -> None:
        for key, binding in self._bindings.items():
            self.winfo_toplevel().unbind(key, binding)
        super().destroy()
