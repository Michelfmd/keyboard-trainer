from dataclasses import dataclass

STANDARD_TUNING = (40, 45, 50, 55, 59, 64)  # MIDI, strings 6 through 1.


@dataclass(frozen=True, slots=True)
class Chord:
    name: str
    full_name: str
    difficulty: str
    frets: tuple[int | None, ...]
    fingers: tuple[int | None, ...]
    source: str
    barre: tuple[int, int, int] | None = None  # fret, first string, last string

    def __post_init__(self) -> None:
        if self.difficulty not in ("easy", "medium", "hard"):
            raise ValueError("Unknown chord difficulty")
        if len(self.frets) != 6 or len(self.fingers) != 6:
            raise ValueError("A guitar voicing must describe six strings")
        for fret, finger in zip(self.frets, self.fingers):
            if fret is None and finger is None:
                continue
            if fret == 0 and finger == 0:
                continue
            if fret is None or fret < 1 or finger not in (1, 2, 3, 4):
                raise ValueError("Invalid fret or fingering")
        if self.barre is not None:
            fret, first, last = self.barre
            if not (fret > 0 and 6 >= first > last >= 1):
                raise ValueError("Invalid barre")
            if any(
                value is None or value < fret
                for value in self.frets[6 - first : 7 - last]
            ):
                raise ValueError("Barre crosses an open or muted string")

    @property
    def midi_notes(self) -> tuple[int, ...]:
        """Reference pitches available to a future audio evaluator."""
        return tuple(
            note + fret
            for note, fret in zip(STANDARD_TUNING, self.frets)
            if fret is not None
        )
