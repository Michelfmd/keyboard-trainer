import unittest

from app.core.events import InputEvent
from app.core.keyboard_layout import KeyboardLayout


class KeyboardLayoutTests(unittest.TestCase):
    def setUp(self) -> None:
        self.layout = KeyboardLayout()

    def test_neighboring_keys(self) -> None:
        self.assertTrue(self.layout.are_neighbors("f", "g"))
        self.assertTrue(self.layout.are_neighbors("f", "r"))
        self.assertFalse(self.layout.are_neighbors("a", "p"))
        self.assertFalse(self.layout.are_neighbors("f", "f"))

    def test_unknown_key(self) -> None:
        self.assertIsNone(self.layout.distance("f", "Return"))
        self.assertFalse(self.layout.are_neighbors("f", "Return"))

    def test_physical_key_normalization(self) -> None:
        self.assertEqual(self.layout.normalize("F"), "f")
        self.assertEqual(self.layout.normalize("!"), "1")
        self.assertTrue(self.layout.are_neighbors("F", "G"))

    def test_required_rows(self) -> None:
        self.assertTrue(
            set("1234567890qwertyuiopasdfghjklzxcvbnm ") <= self.layout.positions.keys()
        )

    def test_expected_finger_errors(self) -> None:
        events = [
            InputEvent("f", "g", False, 1, 1, "random_keys"),
            InputEvent("f", "f", True, 2, 1, "random_keys"),
            InputEvent(" ", "x", False, 3, 1, "words"),
        ]
        self.assertEqual(
            self.layout.finger_errors(events), {"left index": 1, "thumb": 1}
        )
