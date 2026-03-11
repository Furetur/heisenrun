from collections import Counter
from typing import Mapping

from rich.console import Console
from rich.table import Table

from heisenrun.status import Status


def print_report(console: Console, statuses: Mapping[int, Status]):
    table = Table(title="Execution Report")

    table.add_column("Instance", justify="right")
    table.add_column("Status")

    for i, status in sorted(statuses.items()):
        color = {
            Status.NOT_STARTED: "white",
            Status.SUCCESS: "green",
            Status.FAIL: "red",
            Status.TIMEOUT: "yellow",
            Status.INTERRUPTED: "magenta"
        }.get(status, "white")

        table.add_row(str(i), f"[{color}]{status}[/{color}]")

    console.print()
    console.print(table)

    summary = Counter(statuses.values())
    console.print("\n[bold]Summary[/bold]")
    for status, count in summary.most_common():
        if count:
            console.print(f" - {status}: {count}")
