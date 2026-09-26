import tempfile
import unittest
import wave
from pathlib import Path

from app.core.sound import SAMPLE_RATE, SoundPlayer
from app.data.chords import CHORDS


class SoundTests(unittest.TestCase):
    def test_generated_click_and_chord_are_valid_wav_files(self):
        player = SoundPlayer()
        with tempfile.TemporaryDirectory() as directory:
            click = Path(directory) / "click.wav"
            chord = Path(directory) / "chord.wav"
            player._write_click(click)
            player._write_chord(chord, CHORDS[0])
            with wave.open(str(click), "rb") as audio:
                self.assertEqual(audio.getframerate(), SAMPLE_RATE)
                self.assertEqual(audio.getnchannels(), 1)
                self.assertGreater(audio.getnframes(), 500)
            with wave.open(str(chord), "rb") as audio:
                self.assertEqual(audio.getframerate(), SAMPLE_RATE)
                self.assertGreater(audio.getnframes(), SAMPLE_RATE)
        player.close()

    def test_all_chords_have_playable_reference_notes(self):
        for chord in CHORDS:
            self.assertGreaterEqual(len(chord.midi_notes), 3)


if __name__ == "__main__":
    unittest.main()
