from random import Random

from app.core.events import InputEvent
from app.data.words import WORD_LISTS
from app.modes.base import BaseMode


class WordsMode(BaseMode):
    name = "words"
    label = "Words"

    def __init__(
        self,
        count: int = 20,
        rng: Random | None = None,
        *,
        difficulty: str = "hard",
        language: str = "en",
    ) -> None:
        if difficulty not in ("easy", "medium", "hard"):
            raise ValueError("Unknown difficulty")
        if language not in WORD_LISTS:
            raise ValueError("Unknown language")
        super().__init__(count, rng)
        self.language = language
        self.difficulty = difficulty
        self.label = f"Words / {difficulty.title()}"

    def generate_target(self) -> str:
        word_count = self.count
        if self.difficulty == "easy":
            word_count = self.rng.randint(1, 2)
        elif self.difficulty == "medium":
            word_count = self.rng.randint(3, 4)
        result: list[str] = []
        while len(result) < word_count:
            batch = list(WORD_LISTS[self.language])
            self.rng.shuffle(batch)
            if result and batch[0] == result[-1]:
                batch[0], batch[1] = batch[1], batch[0]
            result.extend(batch[: word_count - len(result)])
        return " ".join(result)

    def should_advance(self, event: InputEvent) -> bool:
        return True
