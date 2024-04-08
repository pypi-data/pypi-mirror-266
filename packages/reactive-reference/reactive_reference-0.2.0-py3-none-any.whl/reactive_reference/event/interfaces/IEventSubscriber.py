from typing import Callable, List, NoReturn, Union

from reactive_reference.event.data.Domain import Domain
from reactive_reference.event.data.Event import Event
from reactive_reference.event.data.LifecycleEvent import LifecycleEvent
from reactive_reference.event.data.ReplayStrategy import ReplayStrategy


class IEventSubscriber:
    __name__ = "EventSubscriber"

    latest: Event
    domain: Domain
    strategy: ReplayStrategy

    async def on_event_receive(self, data: Event) -> NoReturn:
        """
        Triggered by the event stream when new Events are posted in the Stream
        :param data: Event sent by the stream
        :return: None
        """
        ...

    async def on_lifecycle_event(self, event: LifecycleEvent) -> NoReturn:
        """
        Triggered by the event stream when new Events are posted in the Stream
        :param event: Lifecycle event sent by the stream
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

    def unregister(self) -> bool:
        """
        Unregisters the class from the Stream, therefore won't receive any other updates
        :return: True if unregistered successfully, False otherwhise
        """
        ...

    def follow(self, domain: Domain) -> bool:
        """
        Adds the ability to Subscribers to receive notifications from other Domains
        :param domain: Domain to register to stream
        :return: True if was correctly subscribed, False otherwise or if already subscribed
        """
        ...

    def unfollow(self, domain: Domain) -> bool:
        """
        Removes the Subscribers from receiving notifications from other Domains
        :param domain: Domain to register to stream
        :return: True if was correctly unfollowed, False otherwise or if already unfollowed
        """
        ...
