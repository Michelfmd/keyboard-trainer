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
  On Results, press Enter (or keypad Enter) for the next exercise without the mouse.
  This shortcut preserves the mode, difficulty and language; it is inactive during practice.
- **Random Keys:** type the displayed letter. Incorrect attempts are recorded;
  the target remains until the correct key is pressed.
- Timing starts when the exercise appears. Response time is the interval from
  exercise start to the first input, then between consecutive accepted inputs,
  including incorrect attempts. Time spent idle or unfocused is included.
- Shifted letters count as typed: uppercase is incorrect for a lowercase target.
  Modifier-only keys, controls, Backspace, and Ctrl/Alt/Super combinations are
  ignored. The visible Stop / Esc button or Escape cancels immediately. Cancelled sessions do not enter Statistics.
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

## Interface and motion

The dark interface uses mint accents, a compact navigation bar, visible keyboard
focus, and consistent metric cards. Hover feedback (140 ms), screen entrances
(180 ms), progress updates (120 ms), and key feedback fades (160 ms) use Tk's
non-blocking `after` scheduler. Exercise screens appear immediately; animation
never gates input or changes session timing. Animations cancel when their widgets
are destroyed, and repeated interactions replace an animation instead of queuing it.

Enable **Reduce motion** in Settings and save to disable animated transitions.
Correct/incorrect key feedback remains visible. This preference, like the other
settings, lasts for the current application run.

Design references: [Monkeytype](https://monkeytype.com/) for the focused typing
experience and [Material Design motion](https://m1.material.io/motion/duration-easing.html)
for short, responsive desktop transitions. No web framework or animation dependency
is required.

Optional display-based animation verification:

```sh
python3 tests/ui_motion_smoke.py
```

Statistics includes a running summary of all completed sessions in the current
application run: session count, total practice time, inputs, correct inputs,
errors, overall accuracy, WPM and CPM, average response time and keys per second.
Accuracy is weighted by input count, speed uses summed practice duration (without
breaks between sessions), and response time is averaged across individual attempts.
The individual session history remains below the summary. Cancelled exercises
are excluded, and closing the application clears this in-memory history.

## Start menu and activities

The application opens on a menu with Keyboard, Guitar and access to Settings.
Keyboard opens the existing Words and Random Keys exercises. Guitar is a disabled
presentation card only: it has no route, exercise logic or session state.
The Menu navigation tab returns to this screen from the keyboard section.

`app/activities.py` defines the activity catalog independently of exercise modes.
`app/ui/menu_view.py` renders the catalog and emits selection callbacks; `app/ui/app.py`
owns navigation and routes available activities. Future guitar implementation can
add its own screens and modes without treating guitar as a typing `BaseMode`.
