import tkinter as tk
from tkinter import ttk

from app.core.metrics import Metrics
from app.core.session import Session
from app.ui.components.widgets import ACCENT, BG, MUTED, MetricCard, label
from app.ui.i18n import tr


class StatisticsView(tk.Frame):
    def __init__(
        self, parent: tk.Misc, sessions: list[Session], mode_labels: dict[str, str]
    ) -> None:
        super().__init__(parent, bg=BG)
        label(self, "Statistics", 26, ACCENT).pack(anchor="w", pady=(12, 16))
        label(
            self,
            "Completed sessions from this application run. History is kept in memory.",
            10,
            MUTED,
        ).pack(anchor="w", pady=(0, 16))
        metrics = Metrics.from_sessions(sessions)
        seconds = int(metrics.elapsed_time)
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        values = {
            "Sessions": str(len(sessions)),
            "Total time": f"{hours:02}:{minutes:02}:{seconds:02}",
            "Total inputs": str(metrics.total_inputs),
            "Correct": str(metrics.correct_inputs),
            "Errors": str(metrics.incorrect_inputs),
            "Overall accuracy": f"{metrics.accuracy:.1f}%",
            "Overall WPM": f"{metrics.words_per_minute:.1f}",
            "Overall CPM": f"{metrics.characters_per_minute:.1f}",
        }
        grid = tk.Frame(self, bg=BG)
        grid.pack(fill="x")
        self.cards: dict[str, MetricCard] = {}
        for index, (title, value) in enumerate(values.items()):
            grid.columnconfigure(index % 4, weight=1, uniform="totals")
            card = MetricCard(grid, title)
            card.grid(
                row=index // 4, column=index % 4, sticky="nsew", padx=(0, 8), pady=4
            )
            card.set(value)
            self.cards[title] = card
        label(
            self,
            tr(
                self,
                "Average response: {response:.0f} ms    Keys / second: {rate:.2f}",
                response=metrics.average_response_time * 1000,
                rate=metrics.keys_per_second,
            ),
            10,
            MUTED,
        ).pack(anchor="w", pady=(12, 6))
        note = label(
            self,
            "Overall rates use total inputs and practice time, not averages of session percentages.",
            9,
            MUTED,
        )
        note.pack(fill="x")
        note.bind("<Configure>", lambda event: note.configure(wraplength=event.width))
        label(self, "Session history", 14).pack(anchor="w", pady=(18, 10))
        if not sessions:
            label(
                self, "Complete a practice session to see your progress.", 11, MUTED
            ).pack(anchor="w")
            return
        table_frame = tk.Frame(self, bg=BG)
        table_frame.pack(fill="both", expand=True)
        columns = ("session", "mode", "time", "wpm", "accuracy", "errors")
        table = ttk.Treeview(table_frame, columns=columns, show="headings", height=4)
        for column in columns:
            table.heading(column, text=tr(self, column.title()))
            table.column(column, width=110, minwidth=65)
        scrollbar = ttk.Scrollbar(table_frame, command=table.yview)
        table.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        table.pack(fill="both", expand=True)
        for index, session in enumerate(sessions, 1):
            result = Metrics.from_session(session)
            table.insert(
                "",
                "end",
                values=(
                    index,
                    tr(self, mode_labels.get(session.mode, session.mode)),
                    f"{result.elapsed_time:.1f}s",
                    f"{result.words_per_minute:.1f}",
                    f"{result.accuracy:.1f}%",
                    result.incorrect_inputs,
                ),
            )
