from dataclasses import dataclass

from app.core.chords import Chord


@dataclass(frozen=True, slots=True)
class InputEvent:
    expected_key: str
    pressed_key: str
    correct: bool
    timestamp: float
    response_time: float
    mode: str


@dataclass(frozen=True, slots=True)
class ChordAssessment:
    """Evaluation boundary: manual practice has no measured correctness.

    A future microphone adapter can provide its source and measured result here.
    Audio capture and analysis do not belong in the mode or diagram widget.
    """

    source: str = "manual"
    correct: bool | None = None


@dataclass(frozen=True, slots=True)
class ChordAttempt:
    expected_chord: Chord
    target_index: int
    practiced: bool
    assessment: ChordAssessment
    timestamp: float
    response_time: float
    mode: str


@dataclass(frozen=True, slots=True)
class LaptopChordAttempt:
    expected_chord: Chord
    expected_keys: frozenset[str]
    response_time: float
    correct: bool
    error_count: int
    timestamp: float
    mode: str
