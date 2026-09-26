import tkinter as tk
from tkinter import ttk

from app.core.events import LaptopChordAttempt
from app.core.laptop_chord_metrics import LaptopChordMetrics
from app.core.session import Session
from app.ui.components.widgets import BG, MetricCard, label
from app.ui.i18n import tr


def render_laptop_chord_results(
    parent: tk.Misc, session: Session[LaptopChordAttempt]
) -> None:
    metrics = LaptopChordMetrics.from_session(session)
    values = (
        ("Changes", str(metrics.completed)),
        ("Clean changes", str(metrics.clean)),
        ("Accuracy", f"{metrics.accuracy:.1f}%"),
        ("Average change", f"{metrics.average_change:.2f}s"),
        (
            "Fastest change",
            "—" if metrics.fastest_change is None else f"{metrics.fastest_change:.2f}s",
        ),
        ("Errors", str(metrics.errors)),
        ("Time", f"{metrics.elapsed_time:.1f}s"),
    )
    grid = tk.Frame(parent, bg=BG)
    grid.pack(fill="x")
    for index, (title, value) in enumerate(values):
        grid.columnconfigure(index % 4, weight=1, uniform="change_results")
        card = MetricCard(grid, title)
        card.grid(row=index // 4, column=index % 4, sticky="nsew", padx=(0, 8), pady=4)
        card.set(value)
    label(parent, "Chord change history", 14).pack(anchor="w", pady=(12, 6))
    table = ttk.Treeview(
        parent, columns=("chord", "keys", "time", "status"), show="headings", height=5
    )
    for column, title in zip(
        ("chord", "keys", "time", "status"),
        ("Chord", "Keys", "Change time", "Status"),
    ):
        table.heading(column, text=tr(parent, title))
        table.column(column, width=130, minwidth=70)
    table.pack(fill="both", expand=True)
    for event in session.events:
        table.insert(
            "",
            "end",
            values=(
                event.expected_chord.name,
                " + ".join(key.upper() for key in sorted(event.expected_keys)),
                f"{event.response_time:.2f}s",
                tr(parent, "Clean" if event.correct else "Corrected"),
            ),
        )
