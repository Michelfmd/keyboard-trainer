from app.core.chords import Chord

# Original diagrams are rendered from these factual standard-tuning voicings.
# Tuple order: low E (string 6) to high e (string 1); None = muted, 0 = open.
CHORDS = (
    Chord("Em", "E minor", "easy", (0, 2, 2, 0, 0, 0), (0, 2, 3, 0, 0, 0), "e-minor"),
    Chord("E", "E major", "easy", (0, 2, 2, 1, 0, 0), (0, 2, 3, 1, 0, 0), "e-major"),
    Chord(
        "Am", "A minor", "easy", (None, 0, 2, 2, 1, 0), (None, 0, 2, 3, 1, 0), "a-minor"
    ),
    Chord(
        "A",
        "A major",
        "medium",
        (None, 0, 2, 2, 2, 0),
        (None, 0, 1, 2, 3, 0),
        "a-major",
    ),
    Chord(
        "D",
        "D major",
        "medium",
        (None, None, 0, 2, 3, 2),
        (None, None, 0, 1, 3, 2),
        "d-major",
    ),
    Chord(
        "Dm",
        "D minor",
        "medium",
        (None, None, 0, 2, 3, 1),
        (None, None, 0, 2, 3, 1),
        "d-minor",
    ),
    Chord(
        "C",
        "C major",
        "medium",
        (None, 3, 2, 0, 1, 0),
        (None, 3, 2, 0, 1, 0),
        "c-major",
    ),
    Chord("G", "G major", "medium", (3, 2, 0, 0, 0, 3), (2, 1, 0, 0, 0, 3), "g-major"),
    Chord(
        "F",
        "F major",
        "hard",
        (1, 3, 3, 2, 1, 1),
        (1, 3, 4, 2, 1, 1),
        "f-major",
        (1, 6, 1),
    ),
    Chord(
        "Bm",
        "B minor",
        "hard",
        (None, 2, 4, 4, 3, 2),
        (None, 1, 3, 4, 2, 1),
        "b-minor",
        (2, 5, 1),
    ),
)
