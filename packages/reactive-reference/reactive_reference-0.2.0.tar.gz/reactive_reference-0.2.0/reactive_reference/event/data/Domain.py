from dataclasses import dataclass


@dataclass(frozen=True)
class Domain:
    name: str

    def __repr__(self):
        return f"Domain(name: {self.name})"

    def __eq__(self, other):
        if not isinstance(other, Domain):
            return False
        if other.name != self.name:
            return False
        return True


__all__ = ["Domain"]
