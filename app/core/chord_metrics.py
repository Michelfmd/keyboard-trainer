from collections.abc import Iterable
from dataclasses import dataclass

from app.core.events import ChordAttempt
from app.core.session import Session


@dataclass(frozen=True)
class ChordMetrics:
    practiced: int
    skipped: int
    unique_chords: int
    elapsed_time: float

    @classmethod
    def from_session(cls, session: Session[ChordAttempt]) -> "ChordMetrics":
        return cls.from_sessions((session,))

    @classmethod
    def from_sessions(cls, sessions: Iterable[Session[ChordAttempt]]) -> "ChordMetrics":
        sessions = list(sessions)
        events = [event for session in sessions for event in session.events]
        return cls(
            sum(event.practiced for event in events),
            sum(not event.practiced for event in events),
            len({event.expected_chord.name for event in events if event.practiced}),
            sum(session.elapsed_time for session in sessions),
        )
