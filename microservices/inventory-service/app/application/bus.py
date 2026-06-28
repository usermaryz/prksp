from __future__ import annotations

from typing import Any, Callable, Type


class AsyncCommandBus:
    def __init__(self) -> None:
        self._handlers: dict[Type, Callable] = {}

    def register(self, command_type: Type, handler: Callable) -> None:
        self._handlers[command_type] = handler

    async def dispatch(self, cmd: Any) -> Any:
        handler = self._handlers.get(type(cmd))
        if handler is None:
            raise ValueError(f"No handler for {type(cmd).__name__}")

        return await handler(cmd)


class AsyncQueryBus:
    def __init__(self) -> None:
        self._handlers: dict[Type, Callable] = {}

    def register(self, query_type: Type, handler: Callable) -> None:
        self._handlers[query_type] = handler

    async def ask(self, query: Any) -> Any:
        handler = self._handlers.get(type(query))
        if handler is None:
            raise ValueError(f"No handler for {type(query).__name__}")

        return await handler(query)
