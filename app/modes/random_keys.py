from random import Random
from string import ascii_lowercase

from app.core.events import InputEvent
from app.modes.base import TypingMode


class RandomKeysMode(TypingMode):
    name = "random_keys"
    label = "Random Keys"
    show_keyboard = True

    def __init__(self, count: int = 40, rng: Random | None = None) -> None:
        super().__init__(count, rng)

    def generate_target(self) -> str:
        result: list[str] = []
        for _ in range(self.count):
            choices = (
                ascii_lowercase.replace(result[-1], "") if result else ascii_lowercase
            )
            result.append(self.rng.choice(choices))
        return "".join(result)

    def should_advance(self, event: InputEvent) -> bool:
        return event.correct
