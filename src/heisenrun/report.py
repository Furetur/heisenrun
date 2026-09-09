from collections import Counter
from typing import Mapping, Optional

from rich.console import Console
from rich.table import Table

from heisenrun.status import Status


def _format_log_size(size: Optional[int]) -> str:
    if size is None:
        return "—"
    return f"{size} B"


def print_report(
    console: Console,
    statuses: Mapping[int, Status],
    log_sizes: Optional[Mapping[int, Optional[int]]] = None,
) -> None:
    table = Table(title="Execution Report")

    table.add_column("Instance", justify="right")
    table.add_column("Status")
    if log_sizes is not None:
        table.add_column("Log Size", justify="right")

    for i, status in sorted(statuses.items()):
        color = {
            Status.NOT_STARTED: "white",
            Status.SUCCESS: "green",
            Status.FAIL: "red",
            Status.TIMEOUT: "yellow",
            Status.INTERRUPTED: "magenta",
        }.get(status, "white")

        row = [str(i), f"[{color}]{status}[/{color}]"]
        if log_sizes is not None:
            row.append(_format_log_size(log_sizes.get(i)))
        table.add_row(*row)

    console.print()
    console.print(table)

    summary = Counter(statuses.values())
    console.print("\n[bold]Summary[/bold]")
    for status, count in summary.most_common():
        if count:
            console.print(f" - {status}: {count}")
