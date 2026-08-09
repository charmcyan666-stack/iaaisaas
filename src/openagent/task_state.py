from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json

from .runtime import Task, TaskStatus


class TaskStateStore:
    """
    Simple JSON-based persistent task state storage.

    This allows the runtime to remember task execution state
    between process restarts.
    """

    def __init__(self, state_file: str = ".openagent/state.json"):
        self.state_file = Path(state_file)
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

    def save(self, task: Task) -> None:
        data = {
            "name": task.name,
            "status": task.status.value,
            "attempts": task.attempts,
            "result": self._safe_value(task.result),
            "error": task.error,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        state = self._load_all()
        state[task.name] = data

        self.state_file.write_text(
            json.dumps(state, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def get(self, task_name: str) -> dict[str, Any] | None:
        state = self._load_all()
        return state.get(task_name)

    def list_tasks(self) -> dict[str, Any]:
        return self._load_all()

    def delete(self, task_name: str) -> None:
        state = self._load_all()

        if task_name in state:
            del state[task_name]

            self.state_file.write_text(
                json.dumps(state, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

    def clear(self) -> None:
        if self.state_file.exists():
            self.state_file.unlink()

    def _load_all(self) -> dict[str, Any]:
        if not self.state_file.exists():
            return {}

        try:
            return json.loads(
                self.state_file.read_text(encoding="utf-8")
            )
        except (json.JSONDecodeError, OSError):
            return {}

    @staticmethod
    def _safe_value(value: Any) -> Any:
        try:
            json.dumps(value)
            return value
        except (TypeError, ValueError):
            return repr(value)
