import tkinter as tk
from collections.abc import Callable
from time import perf_counter


def blend(start: str, end: str, amount: float) -> str:
    channels = (
        round(
            int(start[index : index + 2], 16) * (1 - amount)
            + int(end[index : index + 2], 16) * amount
        )
        for index in (1, 3, 5)
    )
    return "#" + "".join(f"{channel:02x}" for channel in channels)


class Motion:
    """Own interruptible Tk animations and cancel callbacks with their widget."""

    def __init__(self, owner: tk.Misc) -> None:
        self.owner = owner
        self.jobs: dict[str, str] = {}
        owner.bind("<Destroy>", self._on_destroy, add="+")

    def cancel(self, name: str) -> None:
        job = self.jobs.pop(name, None)
        if job is not None:
            self.owner.after_cancel(job)

    def animate(
        self, name: str, update: Callable[[float], None], duration: int = 160
    ) -> None:
        self.cancel(name)
        if getattr(self.owner.winfo_toplevel(), "reduced_motion", False):
            update(1.0)
            return
        started = perf_counter()

        def step() -> None:
            self.jobs.pop(name, None)
            fraction = min(1.0, (perf_counter() - started) * 1000 / duration)
            update(1 - (1 - fraction) ** 3)
            if fraction < 1:
                self.jobs[name] = self.owner.after(16, step)

        step()

    def _on_destroy(self, event: tk.Event) -> None:
        if event.widget == self.owner:
            for name in tuple(self.jobs):
                self.cancel(name)
