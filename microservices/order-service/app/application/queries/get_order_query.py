from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GetOrderQuery:
    order_id: int
