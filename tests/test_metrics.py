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

    def test_aggregate_weights_inputs_and_time_and_excludes_gaps(self) -> None:
        self.session.start()
        self.now = 2.0
        self.session.record("a", "a")
        self.now = 10.0
        self.session.finish()
        second = Session("random_keys", lambda: self.now)
        self.now = 100.0
        second.start()
        for timestamp, key in ((103.0, "a"), (107.0, "x"), (112.0, "x")):
            self.now = timestamp
            second.record("a", key)
        self.now = 130.0
        second.finish()
        combined = Metrics.from_sessions([self.session, second])
        self.assertEqual(combined.total_inputs, 4)
        self.assertEqual(combined.correct_inputs, 2)
        self.assertEqual(combined.incorrect_inputs, 2)
        self.assertEqual(combined.elapsed_time, 40)
        self.assertEqual(combined.accuracy, 50)
        self.assertEqual(combined.characters_per_minute, 3)
        self.assertAlmostEqual(combined.words_per_minute, 0.6)
        self.assertAlmostEqual(combined.characters_per_second, 0.05)
        self.assertEqual(combined.keys_per_second, 0.1)
        self.assertEqual(combined.average_response_time, 3.5)
        self.assertEqual(len(self.session.events), 1)
        self.assertEqual(len(second.events), 3)

    def test_aggregate_empty_history(self) -> None:
        combined = Metrics.from_sessions([])
        self.assertEqual(combined, Metrics.from_session(self.session))

    def test_aggregate_updates_when_session_is_added(self) -> None:
        history = []
        self.assertEqual(Metrics.from_sessions(history).total_inputs, 0)
        self.session.start()
        self.session.record("a", "x")
        self.session.finish()
        history.append(self.session)
        result = Metrics.from_sessions(history)
        self.assertEqual(result.total_inputs, 1)
        self.assertEqual(result.incorrect_inputs, 1)
        self.assertEqual(result.words_per_minute, 0)
