from __future__ import annotations

from rich.progress import BarColumn, Progress, ProgressColumn, Task, TextColumn, TimeRemainingColumn
from rich.text import Text

__all__ = [
    'BarColumn',
    'FPSColumn',
    'Progress',
    'TextColumn',
    'TimeRemainingColumn',
    'get_render_progress'
]


class FPSColumn(ProgressColumn):
    """Progress rendering."""

    def render(self, task: Task) -> Text:
        """Render bar."""
        return Text(f"{task.speed or 0:.02f} fps")


def get_render_progress() -> Progress:
    """Return render progress."""
    return Progress(
        TextColumn("{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
        TextColumn("{task.percentage:>3.02f}%"),
        FPSColumn(),
        TimeRemainingColumn(),
    )
