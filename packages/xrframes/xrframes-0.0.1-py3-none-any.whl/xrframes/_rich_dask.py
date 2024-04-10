from __future__ import annotations

from dask.diagnostics import Callback
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskID, TimeElapsedColumn


class RichProgressDaskCallback(Callback):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.progress: Progress | None = None
        self.task: TaskID | None = None

    def _start_state(self, _, state):
        self.progress = Progress(
            SpinnerColumn(finished_text="✔"),
            " [progress.description]{task.description}",
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.0f}%",
            TimeElapsedColumn(),
            auto_refresh=True,
        )
        self.progress.start()
        self.task = self.progress.add_task(
            description="Writing frames",
            total=sum(len(state[k]) for k in ["ready", "waiting", "running", "finished"]),
        )

    def _posttask(self, *_, **__):
        assert self.progress is not None
        assert self.task is not None
        self.progress.advance(self.task, 1)
        self.progress.refresh()

    def _finish(self, *_, **__):
        assert self.progress is not None
        self.progress.stop()
