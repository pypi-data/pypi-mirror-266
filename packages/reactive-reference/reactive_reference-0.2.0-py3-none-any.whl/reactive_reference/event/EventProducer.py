from abc import ABCMeta
from typing import Any, NoReturn

from reactive_reference.event.Constants import Constants
from reactive_reference.event.data.Domain import Domain
from reactive_reference.event.interfaces.IEventProducer import IEventProducer
from reactive_reference.event.interfaces.IEventStream import IEventStream
from reactive_reference.utils import md5_hash, random_string


class EventProducer(IEventProducer, metaclass=ABCMeta):
    def __init__(
        self,
        stream: IEventStream,
        domain: Domain = Constants.DefaultDomain,
    ) -> None:
        self.__id = md5_hash(random_string(15))
        self.__stream = stream
        self.__domain = domain
        self.__entity = self.__stream.register(self, domain)

    def __repr__(self):
        return f"EventProducer(id: {self.__id}, domain: {self.__domain})"

    @property
    def domain(self) -> Domain:
        return self.__domain

    def emit(self, data: Any, exclusive: bool = False) -> NoReturn:
        self.__stream.emit(self.__entity, data, self.__domain, exclusive)

    def unregister(self) -> bool:
        return self.__stream.unregister(self.__entity)

    def __eq__(self, other):
        if not isinstance(other, EventProducer):
            return False
        if self.__id != other.__id:
            return False
        return True


__all__ = ["EventProducer"]
