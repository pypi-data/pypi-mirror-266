from typing import Any, Callable


class IReference:
    value: Any

    def __init__(
        self, value: Any, readonly: bool = False, read_from: "IReference | None" = None
    ) -> None:
        ...

    def add_hook(self, name: str, hook: Callable) -> bool:
        """
        Add a function to be executed on value update.
        If the same hook is added with different names, or the name is already present, the hook won't be added
        :param name: Unique name for the hook
        :param hook: Callable function that accepts 1 input
        :return: True if added. False if not.
        """
        ...

    def as_readonly(self) -> "IReference":
        """
        Creates a Readonly object and shares the same values
        :return: Immutable copy of reference
        """
        ...

    def reset(self) -> None:
        """
        Resets the value to the original value
        :return: None
        """
        ...

    def clear(self) -> None:
        """
        Clears everything from the internals and sets the value to `None`
        :return: None
        """
        ...

    def logs(self) -> None:
        """
        Prints all changes to the reference.
        :return: None
        """
        ...
