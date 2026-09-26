from dataclasses import dataclass


@dataclass(frozen=True)
class Activity:
    key: str
    title: str
    description: str
    available: bool


ACTIVITIES = (
    Activity("keyboard", "Keyboard", "Words and random keys.", True),
    Activity("guitar", "Guitar", "Learn guitar chords with diagrams.", True),
)
