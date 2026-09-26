from random import Random

from app.core.chords import Chord
from app.core.events import ChordAssessment, ChordAttempt
from app.core.session import Session
from app.data.chords import CHORDS
from app.modes.base import BaseMode


def generate_chord(
    difficulty: str, rng: Random, previous: Chord | None = None
) -> Chord:
    choices = [
        chord
        for chord in CHORDS
        if chord.difficulty == difficulty and chord != previous
    ]
    if not choices:
        raise ValueError("Unknown or empty chord difficulty")
    return rng.choice(choices)


class ChordMode(BaseMode[Chord | None, ChordAttempt]):
    name = "chords"
    label = "Guitar chords"

    def __init__(
        self, count: int = 20, rng: Random | None = None, *, difficulty: str = "easy"
    ) -> None:
        super().__init__(count, rng)
        if difficulty not in {chord.difficulty for chord in CHORDS}:
            raise ValueError("Unknown chord difficulty")
        self.difficulty = difficulty
        self._target: Chord | None = None
        self._target_started_at = 0.0

    def start(self, session: Session[ChordAttempt] | None = None) -> None:
        self.position = 0
        self.session = session if session is not None else Session(self.name)
        self.session.start()
        self._target = generate_chord(self.difficulty, self.rng)
        assert self.session.started_at is not None
        self._target_started_at = self.session.started_at

    def get_target(self) -> Chord | None:
        return self._target

    def is_finished(self) -> bool:
        return self.position >= self.count

    @property
    def progress(self) -> float:
        return self.position / self.count

    def mark_practiced(self) -> ChordAttempt | None:
        return self.submit_assessment(ChordAssessment())

    def skip(self) -> ChordAttempt | None:
        return self._advance(False, ChordAssessment())

    def submit_assessment(self, assessment: ChordAssessment) -> ChordAttempt | None:
        """Shared entry point for manual confirmation and future evaluators."""
        return self._advance(True, assessment)

    def _advance(
        self, practiced: bool, assessment: ChordAssessment
    ) -> ChordAttempt | None:
        if (
            self._target is None
            or self.is_finished()
            or self.session.ended_at is not None
        ):
            return None
        now = self.session.clock()
        event = ChordAttempt(
            self._target,
            self.position,
            practiced,
            assessment,
            now,
            max(0.0, now - self._target_started_at),
            self.name,
        )
        self.session.add_event(event)
        self.position += 1
        if self.is_finished():
            self.session.finish()
        else:
            self._target = generate_chord(self.difficulty, self.rng, self._target)
            self._target_started_at = now
        return event
