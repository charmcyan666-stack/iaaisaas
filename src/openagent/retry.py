import time
from dataclasses import dataclass
from typing import Callable, TypeVar, Any

T = TypeVar("T")


@dataclass
class RetryPolicy:
    max_attempts: int = 3
    initial_delay: float = 1.0
    backoff_factor: float = 2.0
    max_delay: float = 30.0


class RetryError(Exception):
    """Raised when an operation fails after all retry attempts."""


def run_with_retry(
    action: Callable[[], T],
    policy: RetryPolicy | None = None,
    on_retry: Callable[[int, Exception, float], Any] | None = None,
) -> T:
    """
    Execute an action with exponential backoff.

    Example delays:
    1s -> 2s -> 4s -> 8s
    """

    policy = policy or RetryPolicy()
    delay = policy.initial_delay
    last_error: Exception | None = None

    for attempt in range(1, policy.max_attempts + 1):
        try:
            return action()

        except Exception as exc:
            last_error = exc

            if attempt >= policy.max_attempts:
                break

            if on_retry:
                on_retry(attempt, exc, delay)

            time.sleep(delay)

            delay = min(
                delay * policy.backoff_factor,
                policy.max_delay,
            )

    raise RetryError(
        f"Operation failed after {policy.max_attempts} attempts"
    ) from last_error
