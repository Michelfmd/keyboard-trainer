# Keyboard Trainer

A Python 3.10+ desktop typing and guitar trainer using Tkinter and the standard library.

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
  This shortcut preserves the mode, difficulty and language; during guitar practice, Enter confirms the current chord.
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
- Settings configure Hard word count, Random Keys length and Chords per exercise (1–200). Settings, completed sessions,
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
- `app/data`: local English/Spanish word lists and standard guitar chord voicings.
- `app/ui`: navigation, screens, reusable cards, text and keyboard components.

`BaseMode` defines session lifecycle, targets and progress. `TypingMode` owns
character input for Words/Random Keys. `ChordMode` owns manual guitar progression.
`Session[EventT]` accepts typing `InputEvent` or guitar `ChordAttempt` records;
metrics stay independent of Tk and guitar attempts never contribute to WPM.

Guitar `Chord` data holds six frets and finger numbers (string 6 to 1), optional
barre geometry and a lesson reference. `GuitarDiagram` renders these as a canvas.
`ChordAssessment` is the evaluation boundary: manual input has `source="manual"`
and `correct=None`. A future microphone adapter can analyze captured audio against
`Chord.midi_notes` and deliver its assessment through `ChordMode.submit_assessment`.
Audio capture, permissions, analysis and measured-accuracy UI are not implemented.
The UI never interprets a manual confirmation as proof of a correctly played chord.

## Tests

```sh
python3 -m unittest discover -s tests -v
python3 -m compileall -q app main.py
```

For the optional GUI smoke test on a headless Linux machine, install Xvfb:

```sh
xvfb-run -a python3 tests/ui_smoke.py
```

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
The individual session history remains below the summary. Cancelled typing exercises
are excluded, and closing the application clears this in-memory history.

## Start menu and activities

The application opens on a menu with Keyboard, Guitar and Settings.
Keyboard contains Words and Random Keys. Guitar opens its own difficulty screen.
The navigation shows the current activity; Menu lets you switch activities.
`app/activities.py` is the activity catalog; `app/ui/app.py` owns routing.

## Guitar chords

Choose **Guitar → Easy, Medium or Hard**:

- Easy: Em, E, Am.
- Medium: A, D, Dm, C, G.
- Hard: F and Bm with full barres.

These are instructional groupings for this app. Settings control the number of
chords (default 20). Adjacent targets do not repeat.

Each level offers two exercises. **With guitar** keeps the diagram-based manual
practice. **Laptop keys** trains chord-change speed without requiring a guitar:
hold every highlighted key at the same time. As soon as the shape is correct, a
different chord appears; release the previous combination before forming it. The
timer starts at the previous success, so it includes releasing and repositioning.
A four-row grid maps laptop keys to guitar positions:
QWERYU is fret 1, ASDFGH fret 2, ZXCVBN fret 3, and 123456 fret 4; columns run
from string 6 to string 1. A barre uses one key at its starting position.
The second-string position on fret 1 uses Y instead of T because combinations such
as T+D+F are not reported reliably by some laptop keyboard matrices. T and I remain
input aliases for compatibility, while the interface displays the closer Y key.

Laptop sessions record completed and clean changes, extra-key errors, accuracy,
average change time and fastest change. A wrong key can be released and corrected;
that chord completes but is not marked clean. Held key repeats are ignored. The
Guitar statistics tab combines manual and laptop sessions without mixing either
one into typing WPM. Every chord in the selected level appears once before that
level's chord pool is reused, and the same chord never appears twice in a row.
The visual keyboard resets as soon as a chord is accepted. Keys from the previous
shape remain release-gated internally, so they cannot appear red or become errors
for the new chord. Each key unlocks independently when released, so one missing
release event cannot freeze the whole exercise; operating-system key-repeat pairs
are coalesced as well. A live timer shows total session time.

Read the diagram, place your fingers and play your guitar. Click **Practiced** or
press and release **Enter** to continue; **Skip** records an omitted target.
The diagram shows standard tuning, string numbers (6/thick on the left), fret
numbers, finger numbers, open strings (O), muted strings (X), and barres.
The side panel also describes every string. **View lesson** opens the reference
page in your browser; practice itself works offline.

**Stop / Esc** saves a partial guitar session if any targets were reviewed,
otherwise it returns to the guitar screen. Enter on Results starts another session
with the same difficulty. All history lasts until the application closes.
Statistics has separate Typing and Guitar tabs, plus combined session/time totals.
Guitar reports practiced, skipped, distinct practiced chords and elapsed time;
it does not report musical accuracy. Time includes idle and unfocused time.
No microphone access or additional Python dependency is used.

## Sound

Correct typing inputs play a short, quiet confirmation tone. Guitar practice plays
a locally synthesized strum using the standard-tuning pitches in each displayed
voicing; manual practice also includes a **Play chord** button. Audio files are
generated in a temporary directory and contain no downloaded samples. Playback is
non-blocking through the first available system player (`paplay`, `pw-play`,
`aplay`, or `afplay`; Windows uses `winsound`). Sound effects can be disabled in
Settings and the preference lasts for the current application run.

Voicing references: [ChordBank guitar lessons](https://chordbank.com/chords/),
including [C major](https://chordbank.com/chords/c-major/),
[F major](https://chordbank.com/chords/f-major/) and
[B minor](https://chordbank.com/chords/b-minor/). Each chord in
`app/data/chords.py` includes its lesson slug. Diagrams are drawn locally from
fret positions; website images, recordings and lesson text are not copied.

Additional GUI verification (requires a display):

```sh
python3 tests/ui_chord_smoke.py
```
