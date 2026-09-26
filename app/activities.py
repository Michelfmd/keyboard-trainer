from dataclasses import dataclass


@dataclass(frozen=True)
class Activity:
    key: str
    title: str
    description: str
    available: bool


ACTIVITIES = (
    Activity("keyboard", "Keyboard", "Words, random keys and typing statistics.", True),
    Activity("guitar", "Guitar", "A future space for guitar practice.", False),
)
