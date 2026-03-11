import asyncio
from datetime import timedelta
from pathlib import Path
from typing import Optional, Self, Sequence

from shellous import sh
import shellous

from heisenrun.status import Status


class Task:
    def __init__(
        self,
        idx: int,
        cmd: Sequence[str],
        timeout: Optional[timedelta],
        outfile: Optional[Path],
    ) -> None:
        assert cmd, "Command is empty"
        self._idx = idx
        self._cmd = cmd
        self._timeout = timeout
        self._outfile = outfile
        self._status = Status.NOT_STARTED

    @property
    def idx(self) -> int:
        return self._idx

    @property
    def status(self) -> Status:
        return self._status

    @property
    def outfile(self) -> Optional[Path]:
        return self._outfile

    async def run(self) -> Self:
        command = sh(self._cmd)
        if self._outfile:
            command = command.stdout(self._outfile).stderr(sh.STDOUT)
        else:
            command = command.stdout(sh.DEVNULL).stderr(sh.DEVNULL)
        if self._timeout:
            command = command.set(timeout=self._timeout.seconds)
        try:
            await command
            self._status = Status.SUCCESS
        except FileNotFoundError:
            self._status = Status.FAIL
            if self._outfile:
                self._outfile.write_text(f"Unknown command: {self._cmd[0]}\n")
        except shellous.ResultError:
            self._status = Status.FAIL
        except TimeoutError:
            self._status = Status.TIMEOUT
        except asyncio.CancelledError:
            self._status = Status.INTERRUPTED
        return self
