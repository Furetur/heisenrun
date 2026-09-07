import asyncio
from collections import Counter
from datetime import timedelta
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    ProgressColumn,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.text import Text

from heisenrun.report import print_report
from heisenrun.status import Status
from heisenrun.task import Task
from heisenrun.runner import Runner

REPORT_FILENAME = "report.txt"


class _TaskStatusColumn(ProgressColumn):
    def __init__(self, tasks: Sequence[Task]):
        super().__init__()
        self._tasks = tasks

    def render(self, task: Any):
        counts = Counter(t.status for t in self._tasks)
        failed = counts[Status.FAIL]
        success = counts[Status.SUCCESS]
        return Text(f"[fail:{failed} ok:{success}]")


class HeisenrunApp:
    def __init__(
        self,
        *,
        n_tasks: int,
        cmd_template: Sequence[str],
        max_parallel: Optional[int] = None,
        task_timeout: Optional[timedelta],
        outdir: Optional[Path],
        console: Console,
    ) -> None:
        self._cmd_template = cmd_template
        self._tasks = [
            Task(
                idx=idx,
                cmd=HeisenrunApp._get_task_cmd(idx, cmd_template),
                timeout=task_timeout,
                outfile=outdir / f"{idx}_output.log" if outdir else None,
            )
            for idx in range(n_tasks)
        ]
        self._max_parallel = max_parallel or n_tasks
        self._task_timeout = task_timeout
        self._outdir = outdir
        self._console = console

    @staticmethod
    def _get_task_cmd(idx: int, cmd_template: Sequence[str]) -> Sequence[str]:
        return [part.replace("{#}", str(idx)) for part in cmd_template]

    def _get_current_task_statuses(self) -> Mapping[int, Status]:
        return {task.idx: task.status for task in self._tasks}

    async def _run_with_progress_bar(self) -> None:
        runner = Runner(self._tasks, max_parallel=self._max_parallel)
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TextColumn("{task.completed}/{task.total}"),
            _TaskStatusColumn(self._tasks),
            TimeElapsedColumn(),
            console=self._console,
        ) as progress:
            rich_task = progress.add_task("Running commands", total=len(self._tasks))
            for future in runner.run_tasks():
                completed_task = await future
                progress.advance(rich_task)
                self._console.log(
                    f"[bold]{completed_task.idx}[/] finished → [yellow]{completed_task.status}[/]"
                )

    def _print_args(self) -> None:
        self._console.print(f"[bold]Command template:[/] {self._cmd_template}")
        self._console.print(f"[bold]Runs:[/] {len(self._tasks)}")
        if self._max_parallel < len(self._tasks):
            self._console.print(f"[bold]Max parallel tasks:[/] {self._max_parallel}")
        if self._task_timeout:
            self._console.print(f"[bold]Timeout:[/] {self._task_timeout}")
        if self._outdir:
            self._console.print(f"[bold]Output dir:[/] {self._outdir}")
        else:
            self._console.print(
                "[yellow]NOTE: all command output is discarded, use -o to capture output[/]"
            )
        self._console.print()

    @staticmethod
    def _format_path_with_size(path: Path) -> str:
        if path.exists():
            return f"{path} ({path.stat().st_size} bytes)"
        return f"{path} (missing)"

    def _save_report(self, statuses: Mapping[int, Status]) -> Optional[Path]:
        if not self._outdir:
            return None

        report_path = self._outdir / REPORT_FILENAME
        with report_path.open("w", encoding="utf-8") as report_file:
            file_console = Console(file=report_file, force_terminal=False, width=120)
            print_report(file_console, statuses)
        return report_path

    def _print_saved_outputs(self, report_path: Optional[Path]) -> None:
        if not self._outdir:
            return

        self._console.print("\n[bold]Saved outputs[/bold]")
        if report_path is not None:
            self._console.print(f" - {self._format_path_with_size(report_path)}")
        for task in self._tasks:
            outfile = task.outfile
            if outfile is None:
                continue
            self._console.print(f" - {self._format_path_with_size(outfile)}")

    def run(self) -> None:
        if self._outdir:
            self._outdir.mkdir(exist_ok=True, parents=True)

        self._print_args()
        try:
            asyncio.run(self._run_with_progress_bar())
        except KeyboardInterrupt:
            self._console.print("\n[bold red]Keyboard interrupt[/]")

        statuses = self._get_current_task_statuses()
        print_report(self._console, statuses)
        report_path = self._save_report(statuses)
        self._print_saved_outputs(report_path)
