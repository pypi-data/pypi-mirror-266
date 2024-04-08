from dataclasses import dataclass

from reactive_reference.event.data.Domain import Domain
from reactive_reference.event.interfaces.IEventSubscriber import IEventSubscriber


@dataclass(frozen=True)
class Entity:
    id: str
    instance: IEventSubscriber
    domain: Domain

    def __eq__(self, other):
        if not isinstance(other, Entity):
            return False
        if other.id != self.id:
            return False
        return True


__all__ = ["Entity"]
