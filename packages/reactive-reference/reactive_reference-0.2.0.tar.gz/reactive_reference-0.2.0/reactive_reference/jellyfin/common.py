from typing import overload

from reactive_reference.jellyfin.data.Link import Link
from reactive_reference.jellyfin.data.Server import Server


class Jellyfin:
    def __init__(self, server: Server):
        self.__server = server

    @property
    def api_keys(self) -> str:
        return Link("Auth/Keys", self.__server).value

    @property
    def users(self) -> str:
        return Link("Users", self.__server).value

    @property
    def artists(self) -> str:
        return Link("Artists", self.__server).value

    def artists_by_name(self, name: str) -> str:
        return Link(f"Artists/{name}", self.__server).value
