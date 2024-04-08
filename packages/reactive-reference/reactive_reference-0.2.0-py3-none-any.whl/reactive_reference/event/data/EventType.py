from enum import Enum


class EventType(Enum):
    ON_EMIT = "on_emit"
    ON_FOLLOW = "on_follow"
    ON_START = "on_start"
    ON_SUBSCRIBE = "on_subscribe"
    ON_UNFOLLOW = "on_unfollow"
    ON_UNSUBSCRIBE = "on_unsubscribe"
    ON_UPDATE = "on_update"
    KILL = "kill"


__all__ = ["EventType"]
