from __future__ import annotations

from typing import Any, Callable, Type


class CommandBus:
    def __init__(self) -> None:
        self._handlers: dict[Type, Callable] = {}

    def register(self, command_type: Type, handler: Callable) -> None:
        self._handlers[command_type] = handler

    def dispatch(self, command: Any) -> Any:
        handler = self._handlers.get(type(command))
        if handler is None:
            raise ValueError(
                f"No handler registered for {type(command).__name__}"
            )

        return handler(command)


class QueryBus:
    def __init__(self) -> None:
        self._handlers: dict[Type, Callable] = {}

    def register(self, query_type: Type, handler: Callable) -> None:
        self._handlers[query_type] = handler

    def ask(self, query: Any) -> Any:
        handler = self._handlers.get(type(query))
        if handler is None:
            raise ValueError(
                f"No handler registered for {type(query).__name__}"
            )

        return handler(query)
