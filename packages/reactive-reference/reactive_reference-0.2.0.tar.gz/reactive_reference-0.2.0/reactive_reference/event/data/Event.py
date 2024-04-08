from dataclasses import dataclass

from reactive_reference.event.data.Domain import Domain
from reactive_reference.event.data.Payload import Payload


@dataclass(frozen=True)
class Event:
    id: str
    payload: Payload | None
    timestamp: float
    domain: Domain

    def __repr__(self):
        return f"Event(id: {self.id}, payload: {self.payload}, timestamp: {self.timestamp}, domain: {self.domain})"


__all__ = ["Event"]
