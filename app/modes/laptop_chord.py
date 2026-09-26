from random import Random

from app.core.chords import Chord
from app.core.events import LaptopChordAttempt
from app.core.session import Session
from app.data.chords import CHORDS
from app.modes.base import BaseMode

FRET_KEYS = {
    # Y replaces T for string 2: it is close by and avoids a commonly ghosted shape.
    1: "qweryu",
    2: "asdfgh",
    3: "zxcvbn",
    4: "123456",
}
VALID_LAPTOP_KEYS = frozenset("".join(FRET_KEYS.values()))
KEY_ALIASES = {"t": "y", "i": "y"}


def laptop_keys(chord: Chord) -> frozenset[str]:
    """Map fretted positions to a four-fret laptop keyboard grid."""
    keys: set[str] = set()
    barre_fret = barre_first = barre_last = None
    if chord.barre:
        barre_fret, barre_first, barre_last = chord.barre
        keys.add(FRET_KEYS[barre_fret][6 - barre_first])
    for index, fret in enumerate(chord.frets):
        string = 6 - index
        if fret is None or fret == 0:
            continue
        if (
            barre_fret == fret
            and barre_first is not None
            and barre_last is not None
            and barre_first >= string >= barre_last
        ):
            continue
        keys.add(FRET_KEYS[fret][index])
    return frozenset(keys)


class LaptopChordMode(BaseMode[Chord | None, LaptopChordAttempt]):
    name = "chord_changes"
    label = "Laptop chord changes"

    def __init__(
        self, count: int = 20, rng: Random | None = None, *, difficulty: str = "easy"
    ) -> None:
        super().__init__(count, rng)
        if difficulty not in {chord.difficulty for chord in CHORDS}:
            raise ValueError("Unknown chord difficulty")
        self.difficulty = difficulty
        self._target: Chord | None = None
        self._target_started_at = 0.0
        self.pressed_keys: set[str] = set()
        self.release_pending: set[str] = set()
        self.waiting_for_release = False
        self.error_count = 0
        self._remaining: list[Chord] = []

    def start(self, session: Session[LaptopChordAttempt] | None = None) -> None:
        self.position = 0
        self.pressed_keys.clear()
        self.release_pending.clear()
        self.waiting_for_release = False
        self.error_count = 0
        self._remaining.clear()
        self.session = session if session is not None else Session(self.name)
        self.session.start()
        self._target = self._next_chord()
        assert self.session.started_at is not None
        self._target_started_at = self.session.started_at

    def get_target(self) -> Chord | None:
        return self._target

    @property
    def expected_keys(self) -> frozenset[str]:
        return laptop_keys(self._target) if self._target else frozenset()

    def is_finished(self) -> bool:
        return self.position >= self.count

    @property
    def progress(self) -> float:
        return self.position / self.count

    def handle_key_down(self, key: str) -> LaptopChordAttempt | None:
        key = self._normalize_key(key)
        if self.is_finished() or key not in VALID_LAPTOP_KEYS:
            return None
        if key in self.release_pending:
            return None
        if key in self.pressed_keys:
            return None
        self.pressed_keys.add(key)
        if key not in self.expected_keys:
            self.error_count += 1
        if self.pressed_keys == self.expected_keys:
            return self._complete()
        return None

    def handle_key_up(self, key: str) -> LaptopChordAttempt | None:
        key = self._normalize_key(key)
        self.pressed_keys.discard(key)
        self.release_pending.discard(key)
        self.waiting_for_release = bool(self.release_pending)
        if self.pressed_keys == self.expected_keys and not self.is_finished():
            return self._complete()
        return None

    def clear_pressed_keys(self) -> None:
        self.pressed_keys.clear()
        self.release_pending.clear()
        self.waiting_for_release = False

    def _complete(self) -> LaptopChordAttempt:
        assert self._target is not None
        now = self.session.clock()
        event = LaptopChordAttempt(
            self._target,
            self.expected_keys,
            max(0.0, now - self._target_started_at),
            self.error_count == 0,
            self.error_count,
            now,
            self.name,
        )
        self.session.add_event(event)
        self.position += 1
        self.release_pending = set(self.pressed_keys)
        self.pressed_keys.clear()
        self.waiting_for_release = bool(self.release_pending)
        self.error_count = 0
        if self.is_finished():
            self.session.finish()
        else:
            self._target = self._next_chord()
            self._target_started_at = now
        return event

    def _next_chord(self) -> Chord:
        if not self._remaining:
            self._remaining = [
                chord for chord in CHORDS if chord.difficulty == self.difficulty
            ]
            if self._target in self._remaining and len(self._remaining) > 1:
                self._remaining.remove(self._target)
        chord = self.rng.choice(self._remaining)
        self._remaining.remove(chord)
        return chord

    @staticmethod
    def _normalize_key(key: str) -> str:
        key = key.lower()
        return KEY_ALIASES.get(key, key)
