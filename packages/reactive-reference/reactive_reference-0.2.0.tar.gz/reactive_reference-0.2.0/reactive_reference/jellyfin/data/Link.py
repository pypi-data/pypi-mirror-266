from dataclasses import dataclass

from reactive_reference.jellyfin.data.Server import Server


@dataclass
class Link:
    __path: str
    __server: Server

    @property
    def value(self):
        return (
            f"{self.__server.to_string()}/{self.__path}?ApiKey={self.__server.api_key}"
        )

    def __repr__(self):
        return f"Link(value: {self.value})"
