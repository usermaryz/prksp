from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Price:
    amount: Decimal

    def __post_init__(self) -> None:
        if self.amount < Decimal("0"):
            raise ValueError("Price amount cannot be negative")

    def format(self) -> str:
        return f"{self.amount:.2f}"

    def __add__(self, other: Price) -> Price:
        return Price(self.amount + other.amount)

    def __mul__(self, factor: int | Decimal) -> Price:
        return Price(self.amount * Decimal(str(factor)))
