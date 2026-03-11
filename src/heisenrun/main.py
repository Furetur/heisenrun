from datetime import timedelta
import re
from pathlib import Path
from typing import Annotated, List, Optional

import typer
from rich.console import Console

from heisenrun.app import HeisenrunApp


app = typer.Typer()
console = Console()


def parse_timeout(text: str) -> timedelta:
    match = re.fullmatch(r"(\d+)([smh]?)", text.strip())
    if not match:
        raise typer.BadParameter("Invalid duration format (examples: 10s, 5m, 1h)")

    value = int(match.group(1))
    unit = match.group(2)

    seconds = (
        value
        * {
            "": 1,
            "s": 1,
            "m": 60,
            "h": 3600,
        }[unit]
    )
    return timedelta(seconds=seconds)


@app.command()
def main(
    command: Annotated[List[str], typer.Argument(help="Command to run (use {#} as index)")],
    n_runs: Annotated[
        int, typer.Option("-n", "--num-runs", help="Total number of runs")
    ] = 1,
    max_parallel: Annotated[
        Optional[int],
        typer.Option(
            "-m", "--max-parallel", help="Maximum number of tasks running in parallel"
        ),
    ] = None,
    timeout: Annotated[
        Optional[timedelta],
        typer.Option(
            "-t", "--timeout", help="Timeout per run", parser=parse_timeout
        ),
    ] = None,
    output: Annotated[
        Optional[Path],
        typer.Option(
            "--output-dir",
            "-o",
            help="Output directory",
            resolve_path=True,
            file_okay=False,
        ),
    ] = None,
) -> None:
    HeisenrunApp(
        n_tasks=n_runs,
        max_parallel=max_parallel,
        cmd_template=command,
        task_timeout=timeout,
        outdir=output,
        console=console,
    ).run()
