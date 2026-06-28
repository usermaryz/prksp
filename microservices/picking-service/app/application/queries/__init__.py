from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class GetTaskQuery:
    task_id: int


@dataclass(frozen=True)
class ListTasksQuery:
    status: Optional[str] = None


@dataclass(frozen=True)
class GetStatsQuery:
    pass


__all__ = ["GetTaskQuery", "ListTasksQuery", "GetStatsQuery"]
