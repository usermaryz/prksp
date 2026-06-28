from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class MovementTypeEnum(str, Enum):
    inbound = "inbound"
    outbound = "outbound"
    transfer = "transfer"
    adjustment = "adjustment"


@dataclass(frozen=True)
class MovementType:
    value: MovementTypeEnum

    @classmethod
    def inbound(cls) -> MovementType:
        return cls(MovementTypeEnum.inbound)

    @classmethod
    def outbound(cls) -> MovementType:
        return cls(MovementTypeEnum.outbound)

    @classmethod
    def transfer(cls) -> MovementType:
        return cls(MovementTypeEnum.transfer)

    @classmethod
    def adjustment(cls) -> MovementType:
        return cls(MovementTypeEnum.adjustment)

    def __str__(self) -> str:
        return self.value.value
