import unittest

from app.core.metrics import Metrics, error_counts
from app.core.session import Session


class MetricsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.now = 0.0
        self.session = Session("words", lambda: self.now)

    def test_empty_metrics(self) -> None:
        metrics = Metrics.from_session(self.session)
        self.assertEqual(metrics.total_inputs, 0)
        self.assertEqual(metrics.accuracy, 0)
        self.assertEqual(metrics.words_per_minute, 0)
        self.assertEqual(metrics.average_response_time, 0)

    def test_rates_accuracy_and_response_times(self) -> None:
        self.session.start()
        self.now = 1.0
        first = self.session.record("a", "a")
        self.now = 3.0
        second = self.session.record("b", "x")
        self.now = 4.0
        self.session.record(" ", " ")
        self.now = 6.0
        self.session.finish()
        metrics = Metrics.from_session(self.session)
        self.assertEqual(
            (metrics.total_inputs, metrics.correct_inputs, metrics.incorrect_inputs),
            (3, 2, 1),
        )
        self.assertAlmostEqual(metrics.accuracy, 200 / 3)
        self.assertEqual(metrics.characters_per_minute, 20)
        self.assertEqual(metrics.words_per_minute, 4)
        self.assertAlmostEqual(metrics.characters_per_second, 1 / 3)
        self.assertEqual(metrics.keys_per_second, 0.5)
        self.assertAlmostEqual(metrics.average_response_time, 4 / 3)
        self.assertEqual((first.response_time, second.response_time), (1, 2))
        self.assertEqual(second.timestamp, 3)
        self.assertEqual(second.mode, "words")
        self.assertEqual(error_counts(self.session.events), {"b": 1})

    def test_zero_elapsed_with_inputs(self) -> None:
        self.session.start()
        self.session.record("a", "a")
        self.assertEqual(Metrics.from_session(self.session).characters_per_minute, 0)

    def test_finish_freezes_duration(self) -> None:
        self.session.start()
        self.now = 10
        self.session.finish()
        self.now = 20
        self.session.finish()
        self.assertEqual(self.session.elapsed_time, 10)

    def test_invalid_recording(self) -> None:
        with self.assertRaises(RuntimeError):
            self.session.record("a", "a")
        self.session.start()
        self.session.finish()
        with self.assertRaises(RuntimeError):
            self.session.record("a", "a")

    def test_restart_clears_events_and_time(self) -> None:
        self.session.start()
        self.session.record("a", "b")
        self.session.finish()
        self.now = 10
        self.session.start()
        self.assertEqual(self.session.events, [])
        self.assertEqual(self.session.elapsed_time, 0)
        self.assertIsNone(self.session.ended_at)
