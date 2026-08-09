from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class Tool:
    name: str
    description: str
    handler: Callable[..., Any]

    def run(self, *args, **kwargs) -> Any:
        return self.handler(*args, **kwargs)


class ToolRegistry:
    """
    Registry for tools that can be executed by an agent.
    """

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(
        self,
        name: str,
        handler: Callable[..., Any],
        description: str = "",
    ) -> None:
        if name in self._tools:
            raise ValueError(f"Tool already registered: {name}")

        self._tools[name] = Tool(
            name=name,
            description=description,
            handler=handler,
        )

    def unregister(self, name: str) -> None:
        self._tools.pop(name, None)

    def get(self, name: str) -> Tool:
        if name not in self._tools:
            raise KeyError(f"Tool not found: {name}")

        return self._tools[name]

    def execute(self, name: str, *args, **kwargs) -> Any:
        tool = self.get(name)
        return tool.run(*args, **kwargs)

    def list_tools(self) -> list[dict[str, str]]:
        return [
            {
                "name": tool.name,
                "description": tool.description,
            }
            for tool in self._tools.values()
        ]
