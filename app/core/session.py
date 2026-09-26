from collections.abc import Callable
from time import perf_counter
from typing import Generic, TypeVar

from app.core.events import ChordAttempt, InputEvent, LaptopChordAttempt

EventT = TypeVar("EventT", InputEvent, ChordAttempt, LaptopChordAttempt)


class Session(Generic[EventT]):
    def __init__(self, mode: str, clock: Callable[[], float] = perf_counter) -> None:
        self.mode = mode
        self.clock = clock
        self.events: list[EventT] = []
        self.started_at: float | None = None
        self.ended_at: float | None = None
        self._last_input_at: float | None = None

    def start(self) -> None:
        self.events.clear()
        self.started_at = self.clock()
        self.ended_at = None
        self._last_input_at = self.started_at

    def record(
        self: "Session[InputEvent]", expected_key: str, pressed_key: str
    ) -> InputEvent:
        if self.started_at is None or self.ended_at is not None:
            raise RuntimeError("Session must be active to record input")
        now = self.clock()
        previous = self._last_input_at
        event = InputEvent(
            expected_key,
            pressed_key,
            expected_key == pressed_key,
            now,
            max(0.0, now - previous) if previous is not None else 0.0,
            self.mode,
        )
        self.add_event(event)
        self._last_input_at = now
        return event

    def add_event(self, event: EventT) -> None:
        if self.started_at is None or self.ended_at is not None:
            raise RuntimeError("Session must be active to record input")
        self.events.append(event)

    def finish(self) -> None:
        if self.started_at is not None and self.ended_at is None:
            self.ended_at = self.clock()

    @property
    def elapsed_time(self) -> float:
        if self.started_at is None:
            return 0.0
        end = self.ended_at if self.ended_at is not None else self.clock()
        return max(0.0, end - self.started_at)
