from __future__ import annotations

from joblib import Parallel
from rich.progress import MofNCompleteColumn, Progress, SpinnerColumn, TaskID, TimeElapsedColumn


class RichProgressJoblibParallel(Parallel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.progress: Progress | None = None
        self.task: TaskID | None = None

    # TODO: Rich spinner for startup ([...]: Using backend LokyBackend with X concurrent workers.)

    def __call__(self, *args, **kwargs):
        with Progress(
            SpinnerColumn(finished_text="✔"),
            " [progress.description]{task.description}",
            MofNCompleteColumn(),
            "[progress.percentage]{task.percentage:>3.0f}%",
            TimeElapsedColumn(),
            auto_refresh=True,
        ) as self.progress:
            return super().__call__(*args, **kwargs)

    def print_progress(self):
        assert self.progress is not None
        if self.task is None:
            self.task = self.progress.add_task(
                description="Writing frame",
                total=self.n_dispatched_tasks,
            )
        self.progress.update(
            self.task,
            completed=self.n_completed_tasks,
            total=self.n_dispatched_tasks,
        )
        self.progress.refresh()
