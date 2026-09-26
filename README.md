# Keyboard Trainer

A Python 3.10+ desktop typing trainer using Tkinter and the standard library.

## Run

```sh
python3 main.py
```

Tkinter and a graphical desktop are required. On Debian/Ubuntu, install
`python3-tk` if your Python installation does not provide Tkinter.

## Practice

- **Words:** type the highlighted character, including spaces. Every printable
  input advances, even on an error. Backspace does not undo attempts.
  Choose **Easy** (1–2 words), **Medium** (3–4 words), or **Hard** (the configured
  length, 20 words by default) on the Practice screen. Easy and Medium choose
  their word count randomly each exercise. Practice again keeps the difficulty.
- **Random Keys:** type the displayed letter. Incorrect attempts are recorded;
  the target remains until the correct key is pressed.
- Timing starts when the exercise appears. Response time is the interval from
  exercise start to the first input, then between consecutive accepted inputs,
  including incorrect attempts. Time spent idle or unfocused is included.
- Shifted letters count as typed: uppercase is incorrect for a lowercase target.
  Modifier-only keys, controls, Backspace, and Ctrl/Alt/Super combinations are
  ignored. Escape cancels. Cancelled sessions do not enter Statistics.
- The keyboard outline marks the expected key. A brief green/pink fill marks
  the physical key pressed. Unknown keys still count as incorrect input.
- Settings offer English and Spanish for the interface and local practice words.
  Spanish exercises include accents and ñ; use a keyboard layout or input method
  that can type them. Random Keys continues to train the same QWERTY letters.
- Settings configure Hard word count and Random Keys length (1–200). Settings, completed sessions,
  and their individual events remain in memory until the app closes.

## Metrics

Accuracy = correct inputs / all inputs × 100. CPM = correct characters /
minutes. WPM = CPM / 5. Correct characters include spaces. Characters per
second counts correct inputs; keys per second counts all accepted attempts.
Empty sessions and zero-duration rates return zero. Each immutable event
contains expected/pressed keys, correctness, a `perf_counter` timestamp,
response time in seconds, and mode. Completed session time is frozen.

Results include missed keys, individual error history, nearby-key information,
and error counts grouped by the expected key's approximate QWERTY finger.
Finger assignments are conventional estimates, not measurements of hand motion.
Keyboard positions model a US QWERTY layout, not the OS keyboard configuration.

## Architecture

- `main.py`: entry point only.
- `app/core`: events, sessions, pure metric calculation, keyboard geometry.
- `app/modes`: common mode interface and exercise advancement rules.
- `app/data`: local English word list, shuffled in batches without repetition.
- `app/ui`: navigation, screens, reusable cards, text and keyboard components.

Modes consume normalized printable inputs independently of Tkinter. The UI
adapter filters raw events. A future simultaneous-key mode can extend the input
adapter and common mode interface without changing the event history or metric
engine. No chord mode is implemented.

## Tests

```sh
python3 -m unittest discover -s tests -v
python3 -m compileall -q app main.py
```

For the optional GUI smoke test on a headless Linux machine, install Xvfb:

```sh
xvfb-run -a python3 tests/ui_smoke.py
```
# keyboard-trainer
