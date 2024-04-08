from abc import ABCMeta, abstractmethod
from typing import Callable, List, NoReturn, Union

from reactive_reference.event.Constants import Constants
from reactive_reference.event.data.Domain import Domain
from reactive_reference.event.data.Event import Event
from reactive_reference.event.data.LifecycleEvent import LifecycleEvent
from reactive_reference.event.data.ReplayStrategy import ReplayStrategy
from reactive_reference.event.interfaces.IEventStream import IEventStream
from reactive_reference.event.interfaces.IEventSubscriber import IEventSubscriber
from reactive_reference.utils import md5_hash, random_string


class EventSubscriber(IEventSubscriber, metaclass=ABCMeta):
    def __init__(
        self,
        stream: IEventStream,
        domain: Domain = Constants.DefaultDomain,
        replay_strategy: ReplayStrategy = ReplayStrategy.DISABLED,
    ) -> None:
        self.__id = md5_hash(random_string(15))
        self.__stream = stream
        self.__domain = domain
        self.__replay_strategy = replay_strategy
        self.__entity = self.__stream.register(self, domain)

    def __repr__(self):
        return f"EventSubscriber(id: {self.__id}, domain: {self.__domain})"

    @property
    def latest(self) -> Event:
        return self.__stream.latest

    @property
    def domain(self) -> Domain:
        return self.__domain

    @property
    def strategy(self) -> ReplayStrategy:
        return self.__replay_strategy

    @abstractmethod
    async def on_event_receive(self, data: Event) -> NoReturn:
        ...

    async def on_lifecycle_event(self, event: LifecycleEvent) -> NoReturn:
        ...

    def get(self, _filter: Union[Callable[[Event], bool], None] = None) -> List[Event]:
        return self.__stream.get(_filter)

    def unregister(self) -> bool:
        return self.__stream.unregister(self.__entity)

    def follow(self, domain: Domain) -> bool:
        return self.__stream.follow(self.__entity, domain)

    def unfollow(self, domain: Domain) -> bool:
        return self.__stream.unfollow(self.__entity, domain)

    def __eq__(self, other):
        if not isinstance(other, EventSubscriber):
            return False
        if self.__id != other.__id:
            return False
        return True


__all__ = ["EventSubscriber"]
