from enum import Enum


class ReplayStrategy(Enum):
    DISABLED = 0
    LATEST = 1
    LATEST_EXCLUSIVE = 2
    EXCLUSIVE = 3
    ALL = 4
