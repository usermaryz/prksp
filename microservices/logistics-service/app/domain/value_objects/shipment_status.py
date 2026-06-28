from dataclasses import dataclass
from enum import Enum
from typing import Set, FrozenSet


class ShipmentStatusEnum(str, Enum):
    PENDING = "pending"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETURNED = "returned"


ALLOWED_TRANSITIONS: dict[ShipmentStatusEnum, Set[ShipmentStatusEnum]] = {
    ShipmentStatusEnum.PENDING: {
        ShipmentStatusEnum.IN_TRANSIT,
        ShipmentStatusEnum.FAILED,
    },
    ShipmentStatusEnum.IN_TRANSIT: {
        ShipmentStatusEnum.DELIVERED,
        ShipmentStatusEnum.FAILED,
    },
    ShipmentStatusEnum.DELIVERED: {
        ShipmentStatusEnum.RETURNED,
    },
    ShipmentStatusEnum.FAILED: {
        ShipmentStatusEnum.IN_TRANSIT,
    },
    ShipmentStatusEnum.RETURNED: set(),
}


@dataclass(frozen=True)
class ShipmentStatus:
    value: ShipmentStatusEnum

    def can_transition_to(self, new_status: ShipmentStatusEnum) -> bool:
        return new_status in ALLOWED_TRANSITIONS.get(self.value, set())

    def transition_to(self, new_status: ShipmentStatusEnum) -> "ShipmentStatus":
        if not self.can_transition_to(new_status):
            allowed = ALLOWED_TRANSITIONS.get(self.value, set())
            allowed_str = ", ".join(s.value for s in allowed) or "none"
            raise ValueError(
                f"Invalid transition: {self.value.value} -> {new_status.value}. "
                f"Allowed: {allowed_str}"
            )

        return ShipmentStatus(new_status)

    def get_allowed_transitions(self) -> FrozenSet[ShipmentStatusEnum]:
        return frozenset(ALLOWED_TRANSITIONS.get(self.value, set()))

    def is_terminal(self) -> bool:
        return len(ALLOWED_TRANSITIONS.get(self.value, set())) == 0

    @classmethod
    def initial(cls) -> "ShipmentStatus":
        return cls(ShipmentStatusEnum.PENDING)

    @classmethod
    def from_string(cls, status_str: str) -> "ShipmentStatus":
        try:
            return cls(ShipmentStatusEnum(status_str))
        except ValueError:
            raise ValueError(f"Unknown status: {status_str}")

    def __str__(self) -> str:
        return self.value.value

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ShipmentStatus):
            return self.value == other.value
        if isinstance(other, ShipmentStatusEnum):
            return self.value == other
        if isinstance(other, str):
            return self.value.value == other

        return False

    def __hash__(self) -> int:
        return hash(self.value)
