from openagent.runtime import AgentRuntime, Task
from openagent.tools import ToolRegistry
from openagent.retry import RetryPolicy, run_with_retry


def say_hello(name: str) -> str:
    return f"Hello, {name}!"


def main() -> None:
    registry = ToolRegistry()

    registry.register(
        name="say_hello",
        handler=say_hello,
        description="Return a greeting for a given name.",
    )

    runtime = AgentRuntime()

    task = Task(
        name="basic-example",
        action=lambda: run_with_retry(
            lambda: registry.execute("say_hello", "OpenAgent"),
            RetryPolicy(
                max_attempts=3,
                initial_delay=0.2,
                backoff_factor=2.0,
            ),
        ),
    )

    runtime.add_task(task)

    results = runtime.run()

    print("Task status:", task.status.value)
    print("Attempts:", task.attempts)
    print("Result:", results[0])


if __name__ == "__main__":
    main()
