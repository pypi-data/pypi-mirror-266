from dataclasses import dataclass
from typing import Any

from reactive_reference.event.data.Event import Event
from reactive_reference.event.data.EventType import EventType


@dataclass(frozen=True)
class LifecycleEvent(Event):
    id: str
    timestamp: float
    event_type: EventType
    entity: Any | None

    def __repr__(self):
        return f"LifecycleEvent(id: {self.id}, data: {self.payload}, type: {self.event_type}, entity: {self.entity})"


__all__ = ["LifecycleEvent"]
