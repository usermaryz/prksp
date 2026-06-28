"""
Application Layer — use-case orchestration.

Structure:
- commands/   immutable value objects representing write intentions
- queries/    immutable value objects representing read intentions
- handlers/   one handler per command/query, holds the logic
- bus.py      CommandBus / QueryBus — dispatch by type
- services/   OrderApplicationService (used by handlers)
"""

from .bus import CommandBus, QueryBus

__all__ = ["CommandBus", "QueryBus"]
