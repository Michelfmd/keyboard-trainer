from collections.abc import Iterable
from dataclasses import dataclass

from app.core.events import LaptopChordAttempt
from app.core.session import Session


@dataclass(frozen=True)
class LaptopChordMetrics:
    completed: int
    clean: int
    errors: int
    average_change: float
    fastest_change: float | None
    elapsed_time: float

    @property
    def accuracy(self) -> float:
        return self.clean / self.completed * 100 if self.completed else 0.0

    @classmethod
    def from_sessions(
        cls, sessions: Iterable[Session[LaptopChordAttempt]]
    ) -> "LaptopChordMetrics":
        sessions = list(sessions)
        events = [event for session in sessions for event in session.events]
        times = [event.response_time for event in events]
        return cls(
            len(events),
            sum(event.correct for event in events),
            sum(event.error_count for event in events),
            sum(times) / len(times) if times else 0.0,
            min(times) if times else None,
            sum(session.elapsed_time for session in sessions),
        )

    @classmethod
    def from_session(cls, session: Session[LaptopChordAttempt]) -> "LaptopChordMetrics":
        return cls.from_sessions((session,))
