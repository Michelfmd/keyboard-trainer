from abc import ABC, abstractmethod
from random import Random

from app.core.events import InputEvent
from app.core.session import Session


class BaseMode(ABC):
    name: str
    label: str
    show_keyboard = False

    def __init__(self, count: int, rng: Random | None = None) -> None:
        if count < 1:
            raise ValueError("Count must be positive")
        self.count = count
        self.rng = rng if rng is not None else Random()
        self.target = ""
        self.position = 0
        self.outcomes: list[bool] = []
        self.session = Session(self.name)

    @abstractmethod
    def generate_target(self) -> str:
        pass

    def start(self, session: Session | None = None) -> None:
        self.target = self.generate_target()
        self.position = 0
        self.outcomes.clear()
        self.session = session if session is not None else Session(self.name)
        self.session.start()

    def reset(self) -> None:
        self.start()

    def handle_input(self, key: str) -> InputEvent | None:
        if self.is_finished() or len(key) != 1 or not key.isprintable():
            return None
        event = self.session.record(self.get_target(), key)
        if self.should_advance(event):
            self.outcomes.append(event.correct)
            self.position += 1
        if self.is_finished():
            self.session.finish()
        return event

    @abstractmethod
    def should_advance(self, event: InputEvent) -> bool:
        pass

    def get_target(self) -> str:
        return self.target[self.position] if not self.is_finished() else ""

    def is_finished(self) -> bool:
        return self.position >= len(self.target)

    @property
    def progress(self) -> float:
        return self.position / len(self.target) if self.target else 0.0
