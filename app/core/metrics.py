from collections import Counter
from dataclasses import dataclass

from app.core.events import InputEvent
from app.core.session import Session


@dataclass(frozen=True)
class Metrics:
    total_inputs: int
    correct_inputs: int
    incorrect_inputs: int
    accuracy: float
    elapsed_time: float
    characters_per_minute: float
    characters_per_second: float
    words_per_minute: float
    keys_per_second: float
    average_response_time: float

    @classmethod
    def from_session(cls, session: Session) -> "Metrics":
        total = len(session.events)
        correct = sum(event.correct for event in session.events)
        elapsed = session.elapsed_time
        cps = correct / elapsed if elapsed else 0.0
        return cls(
            total,
            correct,
            total - correct,
            correct / total * 100 if total else 0.0,
            elapsed,
            cps * 60,
            cps,
            cps * 12,
            total / elapsed if elapsed else 0.0,
            sum(event.response_time for event in session.events) / total
            if total
            else 0.0,
        )


def error_counts(events: list[InputEvent]) -> Counter[str]:
    return Counter(event.expected_key for event in events if not event.correct)
