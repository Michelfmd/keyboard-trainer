import unittest
from itertools import pairwise
from random import Random

from app.data.words import WORDS
from app.modes.words import WordsMode


class WordsModeTests(unittest.TestCase):
    def test_local_words_without_repeats(self) -> None:
        mode = WordsMode(len(WORDS), Random(2))
        mode.start()
        self.assertEqual(set(mode.target.split()), set(WORDS))
        self.assertEqual(len(mode.target.split()), len(WORDS))

    def test_multiple_batches_no_adjacent_repetition(self) -> None:
        mode = WordsMode(200, Random(2))
        mode.start()
        words = mode.target.split()
        self.assertEqual(len(words), 200)
        self.assertTrue(all(a != b for a, b in pairwise(words)))

    def test_error_advances_and_is_recorded(self) -> None:
        mode = WordsMode(1, Random(2))
        mode.start()
        expected = mode.get_target()
        event = mode.handle_input("?")
        self.assertIsNotNone(event)
        self.assertEqual(event.expected_key, expected)
        self.assertFalse(event.correct)
        self.assertEqual(mode.position, 1)
        self.assertEqual(mode.outcomes, [False])
        self.assertEqual(mode.session.events, [event])

    def test_complete_and_ignore_further_input(self) -> None:
        mode = WordsMode(2, Random(2))
        mode.start()
        target = mode.target
        for key in target:
            mode.handle_input(key)
        self.assertTrue(mode.is_finished())
        self.assertEqual(mode.progress, 1)
        self.assertEqual(len(mode.session.events), len(target))
        self.assertIsNone(mode.handle_input("x"))
        self.assertIsNotNone(mode.session.ended_at)

    def test_control_inputs_do_not_advance(self) -> None:
        mode = WordsMode(1)
        mode.start()
        for key in ("", "\n", "\t", "\b", "Shift_L"):
            self.assertIsNone(mode.handle_input(key))
        self.assertEqual(mode.position, 0)

    def test_reset(self) -> None:
        mode = WordsMode(1)
        mode.start()
        mode.handle_input("x")
        mode.reset()
        self.assertEqual(mode.position, 0)
        self.assertEqual(mode.outcomes, [])
        self.assertEqual(mode.session.events, [])

    def test_invalid_length(self) -> None:
        with self.assertRaises(ValueError):
            WordsMode(0)

    def test_difficulty_lengths_and_reset(self) -> None:
        for difficulty, expected in (("easy", {1, 2}), ("medium", {3, 4})):
            with self.subTest(difficulty=difficulty):
                mode = WordsMode(20, Random(2), difficulty=difficulty)
                observed = set()
                for _ in range(20):
                    mode.reset()
                    words = mode.target.split()
                    observed.add(len(words))
                    self.assertEqual(len(words), len(set(words)))
                    for key in mode.target:
                        mode.handle_input(key)
                    self.assertTrue(mode.is_finished())
                self.assertEqual(observed, expected)
                self.assertEqual(mode.difficulty, difficulty)

    def test_hard_preserves_configured_length(self) -> None:
        for count in (20, 35):
            mode = WordsMode(count, difficulty="hard")
            mode.start()
            self.assertEqual(len(mode.target.split()), count)

    def test_unknown_difficulty(self) -> None:
        with self.assertRaises(ValueError):
            WordsMode(difficulty="unknown")
