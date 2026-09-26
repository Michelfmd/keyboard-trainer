"""Run explicitly with a graphical display or xvfb-run."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.ui.app import KeyboardTrainer
from app.ui.results_view import ResultsView
from app.ui.test_view import TestView


def run() -> None:
    app = KeyboardTrainer()
    failures: list[object] = []
    app.report_callback_exception = lambda *error: failures.append(error)
    try:
        app.update()
        app.counts = {"words": 1, "random_keys": 2}
        for mode_name in ("words", "random_keys"):
            app.start_mode(mode_name)
            app.update()
            app.focus_force()
            app.update()
            view = app.view
            assert isinstance(view, TestView)
            app.event_generate("<KeyPress>", keysym="question")
            app.update()
            assert len(view.mode.session.events) == 1
            for keysym, state in (("Shift_L", 0), ("BackSpace", 0), ("a", 4)):
                app.event_generate("<KeyPress>", keysym=keysym, state=state)
                app.update()
            assert len(view.mode.session.events) == 1
            while not view.mode.is_finished():
                key = view.mode.get_target()
                app.event_generate("<KeyPress>", keysym="space" if key == " " else key)
                app.update()
            assert isinstance(app.view, ResultsView)
            assert len(app.history[-1].events) > 0
        app.show_statistics()
        app.update()
        app.show_settings()
        app.update()
        app.start_mode("random_keys")
        app.update()
        app.focus_force()
        app.update()
        app.event_generate("<KeyPress>", keysym="Escape")
        app.update()
        assert not isinstance(app.view, TestView)
        assert len(app.history) == 2
        app.after(250, app.quit)
        app.mainloop()
        assert not failures, failures
        print(
            "GUI smoke passed: Words, Random Keys, input filtering, results, statistics, settings, cancellation."
        )
    finally:
        app.destroy()


if __name__ == "__main__":
    run()
