"""Guitar navigation, manual practice and lifecycle checks; requires a display."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.ui.app import KeyboardTrainer
from app.ui.chord_view import ChordView
from app.ui.guitar_home import GuitarHomeView
from app.ui.home import HomeView
from app.ui.laptop_chord_view import LaptopChordView
from app.ui.results_view import ResultsView
from app.ui.statistics_view import StatisticsView

app = KeyboardTrainer()
app.geometry("800x740+0+0")
app.reduced_motion = True
app.sound_enabled = False
app.language = "es"
app.counts["chords"] = 2
app.counts["chord_changes"] = 2
errors = []
app.report_callback_exception = lambda *args: errors.append(args)


def settle():
    app.update()
    app.lift()
    app.focus_force()
    app.after(180, app.quit)
    app.mainloop()
    app.update()


def enter():
    app.event_generate("<KeyPress-Return>", state=0)
    app.event_generate("<KeyRelease-Return>", state=0)
    app.update()


try:
    app.open_activity("guitar")
    assert isinstance(app.view, GuitarHomeView)
    app.start_mode("chords", "hard")
    settle()
    view = app.view
    assert isinstance(view, ChordView)
    assert view.diagram.chord.barre is not None
    assert view.diagram.find_all()
    for _ in range(4):
        app.event_generate("<KeyPress-Return>", state=0)
    assert view.mode.position == 0
    app.event_generate("<KeyRelease-Return>", state=0)
    app.update()
    assert view.mode.position == 1
    view.skip_button.invoke()
    app.update()
    assert isinstance(app.view, ResultsView)
    assert len(app.history) == 1
    assert [e.practiced for e in app.history[0].events] == [True, False]
    settle()
    enter()
    assert isinstance(app.view, ChordView)
    assert app.view.mode.difficulty == "hard"
    app.view.stop_button.invoke()
    assert isinstance(app.view, GuitarHomeView)
    assert len(app.history) == 1
    app.start_mode("chords", "easy")
    app.view.practice_button.invoke()
    app.view.stop_button.invoke()
    assert isinstance(app.view, ResultsView)
    assert len(app.history) == 2
    app.show_guitar_home()
    app.start_mode("chord_changes", "easy")
    settle()
    assert isinstance(app.view, LaptopChordView)
    first_chord = app.view.mode.get_target()
    keys = tuple(app.view.mode.expected_keys)
    for key in keys:
        app.event_generate(f"<KeyPress-{key}>", state=0)
        app.update()
    assert isinstance(app.view, LaptopChordView)
    assert app.view.mode.get_target() != first_chord
    assert not app.view.mode.pressed_keys
    assert app.view.mode.waiting_for_release
    for key in keys:
        app.view.mode.handle_key_up(key)
    app.view._render()
    assert not app.view.mode.waiting_for_release
    keys = tuple(app.view.mode.expected_keys)
    for key in keys:
        app.event_generate(f"<KeyPress-{key}>", state=0)
        app.update()
    assert isinstance(app.view, ResultsView)
    assert app.history[-1].mode == "chord_changes"
    assert app.history[-1].events[0].correct
    app.show_statistics()
    assert isinstance(app.view, StatisticsView)
    app.show_home()
    assert isinstance(app.view, HomeView)
    app.update()
    assert "Guitar" not in app.nav_buttons
    app.start_mode("random_keys")
    settle()
    app.event_generate("<Escape>", state=0)
    app.update()
    assert isinstance(app.view, HomeView)
    assert not errors, errors
    print("Guitar UI smoke passed")
finally:
    app.destroy()
