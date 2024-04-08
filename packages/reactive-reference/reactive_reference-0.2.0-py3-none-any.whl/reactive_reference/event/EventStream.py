import asyncio
import inspect
from threading import Thread
from time import time
from typing import Any, Callable, Dict, List, NoReturn, Union

from reactive_reference.event.Constants import Constants
from reactive_reference.event.data.Domain import Domain
from reactive_reference.event.data.Entity import Entity
from reactive_reference.event.data.Event import Event
from reactive_reference.event.data.EventType import EventType
from reactive_reference.event.data.LifecycleEvent import LifecycleEvent
from reactive_reference.event.data.Payload import Payload
from reactive_reference.event.data.ReplayStrategy import ReplayStrategy
from reactive_reference.event.interfaces.IEventProducer import IEventProducer
from reactive_reference.event.interfaces.IEventStream import IEventStream
from reactive_reference.event.interfaces.IEventSubscriber import IEventSubscriber
from reactive_reference.utils import Singleton, md5_hash, random_string


class EventStream(IEventStream, Singleton):
    def __init__(
        self,
        exclusive: bool = False,
        limit: Union[int, None] = Constants.StreamMaxLimit,
    ):
        """
        Create a single stream of data for event based systems.
        :param exclusive: Set the mode of the stream to exclusive. If True, will only notify those of the same domain
        :param limit: If not set stream has no limit for how many values to store. Otherwise, oldest are dropped
        """
        self.__id = md5_hash("Stream")
        self.__values: List[Event] = []
        self.__lifecycle_events: List[LifecycleEvent] = []
        self.__subscribers: Dict[str, Entity] = {}
        self.__producers: Dict[str, Entity] = {}
        self.__exclusive = exclusive
        self.__notifications: Dict[str, dict] = {}
        self.__limit = limit
        self.__emit_lifecycle_event(EventType.ON_START, Payload("Stream Started"), None)
        self.__alive = True

    @property
    def latest(self) -> Event | None:
        if self.__exclusive:
            domain = self.__get_domain_from_stack()
            return self.__get_latest(lambda x: x.domain == domain)
        return self.__get_latest()

    @property
    def subscribers(self) -> int:
        """Number of connected subscribers"""
        return len(self.__subscribers)

    def emit(
        self,
        entity: Entity,
        data: Any,
        domain: Domain = Constants.DefaultDomain,
        exclusive: bool = False,
    ) -> NoReturn:
        async def runner(runners: List[Callable]) -> NoReturn:
            await asyncio.gather(*runners)

        if not self.__alive:
            return
        if not isinstance(entity.instance, IEventProducer):
            return
        if entity.id not in self.__producers.keys():
            return
        if isinstance(data, EventType):
            if data.KILL:
                self.__alive = False
                self.__emit_lifecycle_event(EventType.KILL, Payload("Stream Kill"), entity)
                return
        e = Event(
            md5_hash(data),
            Payload(data),
            time(),
            domain,
        )
        self.__emit_lifecycle_event(EventType.ON_EMIT, e, entity)
        if self.__limit and len(self.__values) + 1 > self.__limit:
            self.__values.pop(0)
        self.__values.append(e)
        coroutines = []
        if domain == Constants.DefaultDomain:
            for sub in self.__get_other_instances(entity):
                coroutines.append(sub.instance.on_event_receive(e))
        else:
            for sub in self.__get_instances_for_domain(entity, domain, exclusive):
                coroutines.append(sub.instance.on_event_receive(e))
        asyncio.run(runner(coroutines))

    def get(self, _filter: Union[Callable[[Event], bool], None] = None) -> List[Event]:
        if _filter:
            return [_ for _ in self.__values if _filter(_)]
        return self.__values

    def follow(self, entity: Entity, domain: Domain) -> bool:
        if entity.domain == domain:
            self.__emit_lifecycle_event(
                EventType.ON_FOLLOW, Payload("Failed to follow"), entity
            )
            return False
        if entity.id in self.__notifications:
            if domain not in self.__notifications[entity.id]["domains"]:
                self.__notifications[entity.id]["domains"].append(domain)
                self.__emit_lifecycle_event(
                    EventType.ON_FOLLOW, Payload("Followed successfully"), entity
                )
                return True
            self.__emit_lifecycle_event(
                EventType.ON_FOLLOW, Payload("Failed to follow"), entity
            )
            return False
        self.__notifications[entity.id] = {"domains": [domain], "entity": entity}
        self.__emit_lifecycle_event(
            EventType.ON_FOLLOW, Payload("Followed successfully"), entity
        )
        return True

    def unfollow(self, entity: Entity, domain: Domain) -> bool:
        if entity.domain == domain:
            self.__emit_lifecycle_event(
                EventType.ON_UNFOLLOW, Payload("Failed to unfollow"), entity
            )
            return False
        if entity.id in self.__notifications:
            if domain in self.__notifications[entity.id]["domains"]:
                self.__notifications[entity.id]["domains"] = [
                    _ for _ in self.__notifications[entity.id]["domains"] if _ != domain
                ]
                self.__emit_lifecycle_event(
                    EventType.ON_UNFOLLOW, Payload("Unfollowed successfully"), entity
                )
                return True
            self.__emit_lifecycle_event(
                EventType.ON_UNFOLLOW, Payload("Failed to unfollow"), entity
            )
            return False
        self.__emit_lifecycle_event(
            EventType.ON_UNFOLLOW, Payload("Failed to unfollow"), entity
        )
        return False

    def register(
        self,
        instance: IEventSubscriber | IEventProducer,
        domain: Domain = Constants.DefaultDomain,
    ) -> Entity:
        _entity = Entity(md5_hash(random_string(15)), instance, domain)
        if self.__alive:
            if isinstance(instance, IEventSubscriber):
                self.__subscribers[_entity.id] = _entity
                self.__emit_lifecycle_event(
                    EventType.ON_SUBSCRIBE, Payload("New entity subscribed"), _entity
                )
                self.__replay_events_on_subscribe(instance)
                self.__emit_lifecycle_event(
                    EventType.ON_SUBSCRIBE,
                    Payload(
                        f"Executed {_entity.instance.strategy.name} ReplayStrategy on {_entity.id}"
                    ),
                    _entity,
                )
            elif isinstance(instance, IEventProducer):
                self.__producers[_entity.id] = _entity
        return _entity

    def unregister(self, entity: Entity) -> bool:
        _ = (
            self.__subscribers.get(entity.id, None)
            if isinstance(entity.instance, IEventSubscriber)
            else self.__producers.get(entity.id)
        )
        if _:
            if isinstance(entity.instance, IEventSubscriber):
                del self.__subscribers[entity.id]
            else:
                del self.__producers[entity.id]
            self.__emit_lifecycle_event(
                EventType.ON_UNSUBSCRIBE,
                Payload(f"Entity {entity.id} unsubscribed"),
                entity,
            )
            return True
        self.__emit_lifecycle_event(
            EventType.ON_UNSUBSCRIBE,
            Payload(f"Entity {entity.id} failed to unsubscribe"),
            entity,
        )
        return False

    def restart(self) -> NoReturn:
        self.__values = []
        self.__emit_lifecycle_event(
            EventType.ON_START, Payload("EventStream restarted"), None
        )

    def __get_latest(self, _filter: Callable = None) -> Event | None:
        """
        Retrieves the latest Event sent to the stream
        :param _filter: Callable function to filter the data
        :return: Latest Event if values in the stream, otherwise None
        """
        if _filter:
            data = [_ for _ in self.__values if _filter(_)]
            return data[-1] if len(data) > 0 else None
        return self.__values[-1] if len(self.__values) > 0 else None

    def __get_instances_for_domain(
        self, entity: Entity, domain: Domain, force_exclusive: bool = False
    ) -> List[Entity]:
        normal_domains = (
            [domain, Constants.DefaultDomain] if not force_exclusive else [domain]
        )
        for _ in self.__subscribers.values():
            if (
                _.domain in normal_domains
                or domain in self.__get_domains_from_notifications(_, force_exclusive)
            ) and _ != entity:
                yield _

    def __get_other_instances(self, entity: Entity) -> List[Entity]:
        for _ in self.__subscribers.values():
            if _ != entity:
                yield _

    def __get_domains_from_notifications(
        self, entity: Entity, force_exclusive: bool = False
    ) -> List[Domain]:
        _ = self.__notifications.get(entity.id, None)
        if _ and (not self.__exclusive or not force_exclusive):
            return _["domains"]
        return []

    @staticmethod
    def __get_domain_from_stack() -> Domain:
        stack = inspect.stack()
        try:
            for _ in stack:
                _locals = _[0].f_locals.get("self", None)
                if (
                    _locals
                    and _locals.__name__
                    and _locals.__name__ == "EventSubscriber"
                ):
                    return _locals.domain
        except Exception:
            return stack[2][0].f_locals["self"].domain

    def __emit_lifecycle_event(
        self, event_type: EventType, event: Event | Payload, entity: Entity | None
    ) -> NoReturn:
        async def runner(runners: List[Callable]):
            await asyncio.gather(*runners)

        id_hash = md5_hash(f"{event_type.value}_{entity.id if entity else entity}")
        e = LifecycleEvent(
            id=f"LIFECYCLE_{id_hash}",
            payload=event if isinstance(event, Payload) else event.payload,
            timestamp=time(),
            domain=Constants.LifecycleDomain,
            event_type=event_type,
            entity=entity,
        )
        self.__lifecycle_events.append(e)
        coroutines = [
            self.__subscribers[_].instance.on_lifecycle_event(e)
            for _ in self.__subscribers
        ]
        asyncio.run(runner(coroutines))

    def __replay_events_on_subscribe(self, instance: IEventSubscriber) -> NoReturn:
        strat = instance.strategy
        if strat == ReplayStrategy.DISABLED:
            return

        if strat == ReplayStrategy.LATEST:
            instance.on_event_receive(self.__get_latest())
        elif strat == ReplayStrategy.LATEST_EXCLUSIVE:
            instance.on_event_receive(
                self.__get_latest(lambda x: x.domain == instance.domain)
            )
        elif strat == ReplayStrategy.EXCLUSIVE:
            values = [_ for _ in self.__values if _.domain == instance.domain]
            for _ in values:
                instance.on_event_receive(_)
        else:
            for _ in self.__values:
                instance.on_event_receive(_)

    def __eq__(self, other):
        if not isinstance(other, EventStream):
            return False
        if self.__id != other.__id:
            return False
        return True


class EventStreamThreaded(Thread):
    def __init__(
        self,
        exclusive: bool = False,
        limit: Union[int, None] = Constants.StreamMaxLimit,
    ):
        self.stream = EventStream(exclusive, limit)
        self.__alive = True
        Thread.__init__(self)
        Thread.daemon = True
        Thread.start(self)

    def run(self):
        while self.__alive:
            pass

    def kill_stream(self):
        self.__alive = False
        self.stream.emit(None, EventType.KILL)


__all__ = ["EventStream", "EventStreamThreaded"]
