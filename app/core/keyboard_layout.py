from collections import Counter
from dataclasses import dataclass
from math import hypot
from typing import ClassVar

from app.core.events import InputEvent


@dataclass(frozen=True)
class KeyPosition:
    x: float
    y: float
    finger: str


class KeyboardLayout:
    rows = ("1234567890-=", "qwertyuiop[]\\", "asdfghjkl;'", "zxcvbnm,./", " ")
    offsets = (0.0, 0.25, 0.5, 1.0, 3.0)
    fingers = (
        "left pinky",
        "left ring",
        "left middle",
        "left index",
        "left index",
        "right index",
        "right index",
        "right middle",
        "right ring",
        "right pinky",
    )
    shifted: ClassVar[dict[str, str]] = dict(
        zip('!@#$%^&*()_+{}|:"<>?', "1234567890-=[]\\;',./")
    )

    def __init__(self) -> None:
        self.positions = {
            key: KeyPosition(
                self.offsets[row] + column,
                float(row),
                "thumb" if key == " " else self.fingers[min(column, 9)],
            )
            for row, keys in enumerate(self.rows)
            for column, key in enumerate(keys)
        }

    def normalize(self, key: str) -> str:
        return self.shifted.get(key, key.lower())

    def distance(self, first: str, second: str) -> float | None:
        a = self.positions.get(self.normalize(first))
        b = self.positions.get(self.normalize(second))
        return hypot(a.x - b.x, a.y - b.y) if a and b else None

    def are_neighbors(self, first: str, second: str) -> bool:
        distance = self.distance(first, second)
        return distance is not None and 0 < distance <= 1.3

    def finger_errors(self, events: list[InputEvent]) -> Counter[str]:
        counts: Counter[str] = Counter()
        for event in events:
            position = self.positions.get(self.normalize(event.expected_key))
            if not event.correct and position:
                counts[position.finger] += 1
        return counts
