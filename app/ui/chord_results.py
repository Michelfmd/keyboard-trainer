import tkinter as tk
from tkinter import ttk

from app.core.chord_metrics import ChordMetrics
from app.core.events import ChordAttempt
from app.core.session import Session
from app.ui.components.widgets import BG, MUTED, MetricCard, label
from app.ui.i18n import tr


def render_chord_metrics(parent: tk.Misc, metrics: ChordMetrics) -> None:
    grid = tk.Frame(parent, bg=BG)
    grid.pack(fill="x")
    for index, (title, value) in enumerate(
        (
            ("Practiced", str(metrics.practiced)),
            ("Skipped", str(metrics.skipped)),
            ("Distinct chords", str(metrics.unique_chords)),
            ("Time", f"{metrics.elapsed_time:.1f}s"),
        )
    ):
        grid.columnconfigure(index, weight=1, uniform="guitar_metrics")
        card = MetricCard(grid, title)
        card.grid(row=0, column=index, sticky="nsew", padx=(0, 8), pady=4)
        card.set(value)


def render_chord_results(parent: tk.Misc, session: Session[ChordAttempt]) -> None:
    render_chord_metrics(parent, ChordMetrics.from_session(session))
    label(parent, "Manual practice: sound is not evaluated.", 10, MUTED).pack(
        anchor="w", pady=12
    )
    label(parent, "Chord history", 14).pack(anchor="w", pady=(10, 6))
    container = tk.Frame(parent, bg=BG)
    container.pack(fill="both", expand=True)
    columns = ("chord", "status", "time")
    table = ttk.Treeview(container, columns=columns, show="headings", height=4)
    for column, title in zip(columns, ("Chord", "Status", "Practice time")):
        table.heading(column, text=tr(parent, title))
        table.column(column, width=150, minwidth=70)
    scroll = ttk.Scrollbar(container, command=table.yview)
    table.configure(yscrollcommand=scroll.set)
    scroll.pack(side="right", fill="y")
    table.pack(fill="both", expand=True)
    for event in session.events:
        table.insert(
            "",
            "end",
            values=(
                event.expected_chord.name,
                tr(parent, "Practiced" if event.practiced else "Skipped"),
                f"{event.response_time:.1f}s",
            ),
        )
