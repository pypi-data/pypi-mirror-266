from typing import Callable, List, Any, NoReturn, Union

from reactive_reference.event.Constants import Constants
from reactive_reference.event.data.Domain import Domain
from reactive_reference.event.data.Entity import Entity
from reactive_reference.event.data.Event import Event
from reactive_reference.event.interfaces.IEventProducer import IEventProducer
from reactive_reference.event.interfaces.IEventSubscriber import IEventSubscriber


class IEventStream:
    __name__ = "EventStream"

    latest: Event
    subscribers: int

    def emit(
        self,
        entity: Entity,
        data: Any,
        domain: Domain = Constants.DefaultDomain,
        exclusive: bool = False,
    ) -> NoReturn:
        """
        Sends data to the Event Stream, triggering `on_event_receive` for all subscribers.
        :param entity: Entity from which the emit was called from
        :param data: Structured payload for the Event Stream
        :param domain: Domain to which the data is binded to
        :param exclusive: Set the mode of the message to exclusive. If True, will only notify those of the same domain
        :return: None
        """
        ...

    def get(self, _filter: Union[Callable[[Event], bool], None] = None) -> List[Event]:
        """
        Retrieve all events
        :param _filter: Function to allow filtering of events
        :return: List with all applicable Events
        """
        ...

    def follow(self, entity: Entity, domain: Domain) -> bool:
        """
        Adds the ability to Subscribers to receive notifications from other Domains
        :param entity: Entity object which specifies the subscriber
        :param domain: Domain to register to stream
        :return: True if was correctly subscribed, False otherwise or if already subscribed
        """
        ...

    def unfollow(self, entity: Entity, domain: Domain) -> bool:
        """
        Removes the Subscribers from receiving notifications from other Domains
        :param entity: Entity object which specifies the subscriber
        :param domain: Domain to unfollow from the stream
        :return: True if was correctly unfollowed, False otherwise or if already unfollowed
        """
        ...

    def register(
        self,
        instance: IEventSubscriber | IEventProducer,
        domain: Domain = Constants.DefaultDomain,
    ) -> Entity:
        """
        Register class for Event updates
        :param instance: Class instance that extends from EventSubscriber
        :param domain: Domain to subscribe for updates. If no domain is given class will subscribe to every update
        :return: Entity object
        """
        ...

    def unregister(self, entity: Entity) -> bool:
        """
        Unregisters the class from the Stream, therefore won't receive any other updates
        :param entity: Entity object created on register
        :return: True if unregistered successfully, False otherwise
        """
        ...
