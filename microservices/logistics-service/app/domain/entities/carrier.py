from dataclasses import dataclass


@dataclass
class Carrier:
    id: int
    code: str
    name: str
    is_active: bool
