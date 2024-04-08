from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Payload:
    value: Any

    def __repr__(self):
        return f"Payload(value: {self.value})"

    def __eq__(self, other):
        if not isinstance(other, Payload):
            return False
        if self.value != other.value:
            return False
        return True


__all__ = ["Payload"]
