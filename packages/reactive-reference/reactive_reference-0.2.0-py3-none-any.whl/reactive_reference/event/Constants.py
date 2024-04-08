from dataclasses import dataclass

from reactive_reference.event.data.Domain import Domain


@dataclass
class Constants:
    DefaultDomain = Domain("Default")
    LifecycleDomain = Domain("Lifecycle")
    StreamMaxLimit: int | None = None
