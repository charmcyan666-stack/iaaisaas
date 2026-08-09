from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Any
import time


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Task:
    name: str
    action: Callable[[], Any]
    max_retries: int = 3
    status: TaskStatus = TaskStatus.PENDING
    attempts: int = 0
    result: Any = None
    error: str | None = None


class AgentRuntime:
    def __init__(self, retry_delay: float = 1.0):
        self.retry_delay = retry_delay
        self.tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def run_task(self, task: Task) -> Any:
        task.status = TaskStatus.RUNNING

        while task.attempts < task.max_retries:
            task.attempts += 1

            try:
                task.result = task.action()
                task.status = TaskStatus.COMPLETED
                task.error = None
                return task.result

            except Exception as exc:
                task.error = str(exc)

                if task.attempts >= task.max_retries:
                    task.status = TaskStatus.FAILED
                    raise

                time.sleep(self.retry_delay)

    def run(self) -> list[Any]:
        results = []

        for task in self.tasks:
            results.append(self.run_task(task))

        return results
