from typing import Any, Callable, Dict, List

from reactive_reference.reference.IReference import IReference


class MutableReference(IReference):
    def __init__(
        self, value: Any, readonly: bool = False, read_from: IReference | None = None
    ) -> None:
        super().__init__(value)
        self.__import = read_from
        self.__readonly = readonly
        self.__value = value if not self.__import else self.__import.value
        self.__initial_value = value
        self.__update_registry: List[type(value)] = []
        self.__on_update: Dict[str, Dict[str, Callable | bool]] = {}

    def __repr__(self):
        print(self.__value)

    @property
    def value(self):
        return self.__value if not self.__import else self.__import.value

    @value.setter
    def value(self, value: Any):
        if self.__readonly:
            return
        if not isinstance(value, type(self.__value)):
            raise TypeError(
                f"Type mismatch between {type(self.__value).__name__} and {type(value).__name__}"
            )
        self.__update_registry.append(f"{self.__value} -> {value}")
        self.__value = value
        for hook in self.__on_update.values():
            try:
                if not hook["lock"]:
                    hook["lock"] = True
                    hook["callable"](self)
            except Exception as e:
                print(e)
        self.__release_locks()

    def add_hook(self, name: str, hook: Callable) -> bool:
        if self.__readonly:
            return False
        if name in self.__on_update or id(hook) in self.__get_hook_ids():
            return False
        self.__on_update[name] = {"callable": hook, "lock": False}
        return True

    def as_readonly(self) -> "IReference":
        return ReadonlyReference(self)

    def reset(self) -> None:
        if self.__readonly:
            return
        self.__update_registry.append(f"{self.__value} -> {self.__initial_value}")
        self.__value = self.__initial_value

    def clear(self) -> None:
        if self.__readonly:
            return
        self.__value = None
        self.__update_registry = []
        self.__on_update = {}

    def logs(self):
        print("\n".join(self.__update_registry))

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, IReference):
            print(f"Cannot compare {other.__name__} with Reference")
            return False
        if self.value == other.value:
            return True
        return False

    def __get_hook_ids(self) -> List[int]:
        """
        Returns a list of internal IDs for all hooks stored.
        :return: List of ids
        """
        return [id(_) for _ in self.__on_update.values()]

    def __release_locks(self):
        for hook in self.__on_update.values():
            hook["lock"] = False


class ReadonlyReference(MutableReference):
    def __init__(self, reference: IReference):
        super().__init__(reference.value, readonly=True, read_from=reference)


__all__ = ["MutableReference", "ReadonlyReference"]
