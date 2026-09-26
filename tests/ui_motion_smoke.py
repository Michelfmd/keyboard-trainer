"""Verify animation lifecycle and reduced motion with an available display."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.ui.app import KeyboardTrainer
from app.ui.components.widgets import ACCENT, BG, AnimatedButton, ProgressBar
from app.ui.keyboard_view import KeyboardView


def settle(app: KeyboardTrainer, milliseconds: int = 230) -> None:
    app.after(milliseconds, app.quit)
    app.mainloop()


def run() -> None:
    app = KeyboardTrainer()
    failures: list[object] = []
    app.report_callback_exception = lambda *error: failures.append(error)
    try:
        settle(app)
        progress = ProgressBar(app.content)
        progress.set(0.75)
        assert progress.motion.jobs
        settle(app)
        assert progress.value == 0.75
        assert not progress.motion.jobs
        progress.set(1.0)
        progress.destroy()
        assert not progress.motion.jobs

        button = AnimatedButton(app.content, "Test", lambda: None)
        button._fade(ACCENT)
        assert button.motion.jobs
        button.destroy()
        assert not button.motion.jobs

        keyboard = KeyboardView(app.content)
        keyboard.flash("f", True)
        settle(app, 210)
        assert keyboard.motion.jobs
        keyboard.destroy()
        assert not keyboard.motion.jobs

        app.reduced_motion = True
        progress = ProgressBar(app.content)
        progress.set(0.8)
        assert progress.value == 0.8
        assert not progress.motion.jobs
        progress.destroy()
        button = AnimatedButton(app.content, "Test", lambda: None)
        button._fade(ACCENT)
        assert button.cget("bg") == ACCENT
        assert not button.motion.jobs
        button.destroy()

        for language in ("en", "es"):
            app.language = language
            app._refresh_navigation()
            app._refresh_footer()
            app.reduced_motion = False
            for _ in range(3):
                app.show_home()
                app.show_settings()
                app.start_mode("random_keys")
                view = app.view
                view.mode.handle_input(view.mode.get_target())
                view._render_target()
                app.show_statistics()
            settle(app)
            assert app.view.cget("bg") == BG
        assert not failures, failures
        print(
            "Motion smoke passed: hover, progress, key fades, reduced motion, rapid navigation, cleanup."
        )
    finally:
        app.destroy()


if __name__ == "__main__":
    run()
