from typing import Any, Callable, List, NoReturn, Union

from reactive_reference.event.data.Domain import Domain
from reactive_reference.event.data.Event import Event
from reactive_reference.event.data.LifecycleEvent import LifecycleEvent
from reactive_reference.event.data.ReplayStrategy import ReplayStrategy


class IEventProducer:
    __name__ = "EventProducer"

    domain: Domain

    def emit(self, data: Any, exclusive: bool = False) -> NoReturn:
        """
        Sends data to the Event Stream
        :param data: Structured payload for the Event Stream
        :param exclusive: Set the mode of the message to exclusive. If True, will only notify those of the same domain
        :return: None
        """
        ...
    
    def unregister(self) -> bool:
        """
        Unregisters the class from the Stream, therefore won't be able to provide updates
        :return: True if unregistered successfully, False otherwise
        """
        ...
