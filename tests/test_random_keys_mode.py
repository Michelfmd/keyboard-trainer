import unittest
from random import Random
from string import ascii_lowercase

from app.core.session import Session
from app.modes.random_keys import RandomKeysMode


class RandomKeysTests(unittest.TestCase):
    def test_letters_and_no_immediate_repeat(self) -> None:
        mode = RandomKeysMode(200, Random(3))
        mode.start()
        self.assertEqual(len(mode.target), 200)
        self.assertTrue(set(mode.target) <= set(ascii_lowercase))
        self.assertTrue(all(a != b for a, b in zip(mode.target, mode.target[1:])))

    def test_error_keeps_target_and_attempt_times(self) -> None:
        now = 0.0
        session = Session("random_keys", lambda: now)
        mode = RandomKeysMode(2, Random(3))
        mode.start(session)
        target = mode.get_target()
        now = 0.5
        wrong = mode.handle_input("?")
        self.assertEqual(mode.get_target(), target)
        self.assertEqual(mode.position, 0)
        self.assertFalse(wrong.correct)
        self.assertEqual(wrong.response_time, 0.5)
        now = 0.75
        right = mode.handle_input(target)
        self.assertEqual(right.response_time, 0.25)
        self.assertEqual(mode.position, 1)
        self.assertEqual(len(session.events), 2)
        self.assertNotEqual(mode.get_target(), target)

    def test_finish_and_reset(self) -> None:
        mode = RandomKeysMode(1)
        mode.start()
        mode.handle_input(mode.get_target())
        self.assertTrue(mode.is_finished())
        self.assertIsNone(mode.handle_input("a"))
        mode.reset()
        self.assertFalse(mode.is_finished())
        self.assertEqual(mode.session.events, [])

    def test_uppercase_is_incorrect(self) -> None:
        mode = RandomKeysMode(1)
        mode.start()
        event = mode.handle_input(mode.get_target().upper())
        self.assertFalse(event.correct)
        self.assertEqual(mode.position, 0)

    def test_invalid_length(self) -> None:
        with self.assertRaises(ValueError):
            RandomKeysMode(-1)
