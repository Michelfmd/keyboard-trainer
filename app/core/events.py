from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class InputEvent:
    expected_key: str
    pressed_key: str
    correct: bool
    timestamp: float
    response_time: float
    mode: str
