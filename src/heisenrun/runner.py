import asyncio
from typing import Iterable, List, Any

from heisenrun.task import Task

class Runner:
    def __init__(self, tasks: List[Any], max_parallel: int):
        assert max_parallel > 0, "max_parallel must be positive"
        self.tasks = tasks
        self.max_parallel = max_parallel
        self._semaphore = asyncio.Semaphore(max_parallel)

    async def _run_task(self, task: Task) -> Task:
        async with self._semaphore:
            return await task.run()

    def run_tasks(self) -> Iterable[asyncio.Future[Task]]:
        coros = [self._run_task(task) for task in self.tasks]
        return asyncio.as_completed(coros)
