import unittest
from random import Random

from app.core.chord_metrics import ChordMetrics
from app.core.chords import Chord
from app.core.events import ChordAssessment
from app.core.session import Session
from app.data.chords import CHORDS
from app.modes.chord import ChordMode, generate_chord
from app.modes.laptop_chord import LaptopChordMode, laptop_keys


class GuitarTests(unittest.TestCase):
    def test_laptop_mapping_represents_shapes_and_barres(self):
        expected = {
            "Em": frozenset("sd"),
            "C": frozenset("xdy"),
            "F": frozenset("qfxc"),
            "Bm": frozenset(("s", "3", "4", "b")),
        }
        for name, keys in expected.items():
            chord = next(chord for chord in CHORDS if chord.name == name)
            self.assertEqual(laptop_keys(chord), keys)

    def test_t_and_i_are_aliases_for_the_y_position(self):
        chord = next(chord for chord in CHORDS if chord.name == "Am")
        self.assertNotIn("t", laptop_keys(chord))
        self.assertNotIn("i", laptop_keys(chord))
        self.assertEqual(laptop_keys(chord), frozenset("dfy"))
        for alias in ("t", "i"):
            mode = LaptopChordMode(1, Random(1), difficulty="easy")
            mode.start()
            mode._target = chord
            for key in ("d", "f", alias):
                event = mode.handle_key_down(key)
            self.assertTrue(mode.is_finished())
            self.assertEqual(event.expected_keys, frozenset("dfy"))

    def test_laptop_mode_requires_simultaneous_keys_and_measures_change(self):
        now = [2.0]
        mode = LaptopChordMode(1, Random(1), difficulty="easy")
        mode.start(Session("chord_changes", clock=lambda: now[0]))
        keys = list(mode.expected_keys)
        now[0] = 3.5
        for key in keys[:-1]:
            self.assertIsNone(mode.handle_key_down(key))
        self.assertFalse(mode.is_finished())
        event = mode.handle_key_down(keys[-1])
        self.assertTrue(mode.is_finished())
        self.assertEqual(event.response_time, 1.5)
        self.assertTrue(event.correct)

    def test_laptop_mode_records_corrected_shape_and_waits_for_release(self):
        mode = LaptopChordMode(2, Random(2), difficulty="medium")
        mode.start()
        first_chord = mode.get_target()
        mode.handle_key_down("q")
        for key in mode.expected_keys:
            mode.handle_key_down(key)
        self.assertEqual(mode.position, 0)
        event = mode.handle_key_up("q")
        self.assertFalse(event.correct)
        self.assertEqual(event.error_count, 1)
        self.assertTrue(mode.waiting_for_release)
        self.assertNotEqual(mode.get_target(), first_chord)
        self.assertFalse(mode.pressed_keys)
        repeated_key = next(iter(mode.release_pending))
        self.assertIsNone(mode.handle_key_down(repeated_key))
        self.assertFalse(mode.pressed_keys)
        self.assertEqual(mode.error_count, 0)
        for key in tuple(mode.release_pending):
            mode.handle_key_up(key)
        self.assertFalse(mode.waiting_for_release)
        self.assertEqual(mode.position, 1)

    def test_laptop_mode_cycles_all_chords_before_reusing_one(self):
        mode = LaptopChordMode(4, Random(4), difficulty="easy")
        mode.start()
        targets = []
        for _ in range(4):
            targets.append(mode.get_target().name)
            for key in tuple(mode.expected_keys):
                mode.handle_key_down(key)
            for key in tuple(mode.release_pending):
                mode.handle_key_up(key)
        self.assertEqual(len(set(targets[:3])), 3)
        self.assertNotEqual(targets[2], targets[3])

    def test_change_time_starts_at_previous_success(self):
        now = [10.0]
        mode = LaptopChordMode(2, Random(3), difficulty="easy")
        mode.start(Session("chord_changes", clock=lambda: now[0]))
        now[0] = 12.0
        for key in tuple(mode.expected_keys):
            mode.handle_key_down(key)
        now[0] = 13.0
        for key in tuple(mode.release_pending):
            mode.handle_key_up(key)
        now[0] = 16.0
        event = None
        for key in tuple(mode.expected_keys):
            event = mode.handle_key_down(key) or event
        self.assertEqual(event.response_time, 4.0)

    def test_laptop_mode_rejects_unknown_difficulty(self):
        with self.assertRaises(ValueError):
            LaptopChordMode(difficulty="unknown")

    def test_voicings_form_the_named_triads(self):
        pitch_classes = {
            "Em": {4, 7, 11},
            "E": {4, 8, 11},
            "Am": {9, 0, 4},
            "A": {9, 1, 4},
            "D": {2, 6, 9},
            "Dm": {2, 5, 9},
            "C": {0, 4, 7},
            "G": {7, 11, 2},
            "F": {5, 9, 0},
            "Bm": {11, 2, 6},
        }
        self.assertEqual(len(CHORDS), 10)
        for chord in CHORDS:
            self.assertEqual(
                {note % 12 for note in chord.midi_notes}, pitch_classes[chord.name]
            )

    def test_invalid_voicing(self):
        with self.assertRaises(ValueError):
            Chord("bad", "bad", "easy", (0,), (0,), "")
        with self.assertRaises(ValueError):
            Chord("bad", "bad", "easy", (0,) * 6, (1,) * 6, "")

    def test_generation_and_no_consecutive_repeats(self):
        for difficulty in ("easy", "medium", "hard"):
            previous = None
            for _ in range(60):
                chord = generate_chord(difficulty, Random(_), previous)
                self.assertEqual(chord.difficulty, difficulty)
                self.assertNotEqual(chord, previous)
                previous = chord
        with self.assertRaises(ValueError):
            ChordMode(difficulty="unknown")

    def test_manual_progress_and_timing(self):
        now = [10.0]
        mode = ChordMode(2)
        mode.start(Session("chords", clock=lambda: now[0]))
        now[0] = 14.0
        event = mode.mark_practiced()
        self.assertTrue(event.practiced)
        self.assertIsNone(event.assessment.correct)
        self.assertEqual(event.assessment.source, "manual")
        self.assertEqual(event.response_time, 4)
        self.assertEqual(mode.progress, 0.5)
        now[0] = 17.0
        self.assertFalse(mode.skip().practiced)
        self.assertTrue(mode.is_finished())
        self.assertIsNone(mode.mark_practiced())
        self.assertEqual(len(mode.session.events), 2)
        self.assertEqual(mode.session.elapsed_time, 7)

    def test_stop_and_reset(self):
        mode = ChordMode(2)
        self.assertIsNone(mode.mark_practiced())
        mode.start()
        mode.mark_practiced()
        mode.session.finish()
        self.assertIsNone(mode.skip())
        mode.reset()
        self.assertEqual(mode.position, 0)
        self.assertEqual(mode.session.events, [])
        self.assertIsNone(mode.session.ended_at)

    def test_assessment_boundary(self):
        mode = ChordMode(1)
        mode.start()
        assessment = ChordAssessment(source="test-evaluator", correct=False)
        event = mode.submit_assessment(assessment)
        self.assertEqual(event.assessment, assessment)
        self.assertTrue(mode.is_finished())

    def test_aggregate_metrics(self):
        sessions = []
        for _ in range(2):
            mode = ChordMode(2, Random(5))
            mode.start()
            mode.mark_practiced()
            mode.skip()
            sessions.append(mode.session)
        metrics = ChordMetrics.from_sessions(sessions)
        self.assertEqual(
            (metrics.practiced, metrics.skipped, metrics.unique_chords), (2, 2, 1)
        )
        empty = ChordMetrics.from_sessions([])
        self.assertEqual(
            (empty.practiced, empty.skipped, empty.elapsed_time), (0, 0, 0)
        )


if __name__ == "__main__":
    unittest.main()
