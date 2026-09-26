import atexit
import math
import shutil
import struct
import subprocess
import sys
import tempfile
import wave
from pathlib import Path
from time import monotonic

from app.core.chords import STANDARD_TUNING, Chord

SAMPLE_RATE = 22_050


class SoundPlayer:
    """Generate small local WAV files and play them without blocking Tk."""

    def __init__(self) -> None:
        self._directory = tempfile.TemporaryDirectory(prefix="keyboard-trainer-audio-")
        self._processes: list[subprocess.Popen] = []
        self._last_click = 0.0
        self._command = self._find_player()
        atexit.register(self.close)

    @property
    def available(self) -> bool:
        return sys.platform == "win32" or self._command is not None

    def play_correct(self) -> None:
        now = monotonic()
        if now - self._last_click < 0.025:
            return
        self._last_click = now
        path = Path(self._directory.name) / "correct.wav"
        if not path.exists():
            self._write_click(path)
        self._play(path)

    def play_chord(self, chord: Chord) -> None:
        path = Path(self._directory.name) / f"chord-{chord.name}.wav"
        if not path.exists():
            self._write_chord(path, chord)
        self._play(path)

    def _play(self, path: Path) -> None:
        self._processes = [
            process for process in self._processes if process.poll() is None
        ]
        if sys.platform == "win32":
            import winsound

            winsound.PlaySound(
                str(path),
                winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT,
            )
            return
        if self._command is None:
            return
        self._processes.append(
            subprocess.Popen(
                [*self._command, str(path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        )

    def _write_click(self, path: Path) -> None:
        duration = 0.065
        samples = []
        for index in range(round(SAMPLE_RATE * duration)):
            time = index / SAMPLE_RATE
            envelope = math.sin(math.pi * time / duration) ** 2
            value = envelope * (
                0.7 * math.sin(2 * math.pi * 880 * time)
                + 0.3 * math.sin(2 * math.pi * 1320 * time)
            )
            samples.append(value * 0.22)
        self._write_wave(path, samples)

    def _write_chord(self, path: Path, chord: Chord) -> None:
        duration = 1.55
        samples = [0.0] * round(SAMPLE_RATE * duration)
        strings = [
            tuning + fret
            for tuning, fret in zip(STANDARD_TUNING, chord.frets)
            if fret is not None
        ]
        for string_index, midi_note in enumerate(strings):
            start = round(string_index * 0.04 * SAMPLE_RATE)
            frequency = 440.0 * 2 ** ((midi_note - 69) / 12)
            for sample_index in range(start, len(samples)):
                time = (sample_index - start) / SAMPLE_RATE
                attack = min(1.0, time / 0.008)
                decay = math.exp(-2.8 * time)
                tone = (
                    math.sin(2 * math.pi * frequency * time)
                    + 0.34 * math.sin(2 * math.pi * frequency * 2 * time)
                    + 0.13 * math.sin(2 * math.pi * frequency * 3 * time)
                )
                samples[sample_index] += attack * decay * tone / max(4, len(strings))
        self._write_wave(path, samples)

    @staticmethod
    def _write_wave(path: Path, samples: list[float]) -> None:
        peak = max((abs(sample) for sample in samples), default=1.0)
        scale = 0.82 * 32767 / max(1.0, peak)
        frames = b"".join(
            struct.pack("<h", round(max(-32767, min(32767, sample * scale))))
            for sample in samples
        )
        with wave.open(str(path), "wb") as output:
            output.setnchannels(1)
            output.setsampwidth(2)
            output.setframerate(SAMPLE_RATE)
            output.writeframes(frames)

    @staticmethod
    def _find_player() -> tuple[str, ...] | None:
        for name, arguments in (
            ("paplay", ()),
            ("pw-play", ()),
            ("aplay", ("-q",)),
            ("afplay", ()),
        ):
            executable = shutil.which(name)
            if executable:
                return (executable, *arguments)
        return None

    def close(self) -> None:
        for process in self._processes:
            if process.poll() is None:
                process.terminate()
        self._processes.clear()


sound_player = SoundPlayer()
