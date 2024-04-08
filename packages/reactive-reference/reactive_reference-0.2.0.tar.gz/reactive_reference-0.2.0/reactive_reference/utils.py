import random
from string import ascii_uppercase, digits
from hashlib import md5
from threading import Lock
from time import time


class Singleton:
    _instance = None

    def __new__(cls, *args, **kwargs) -> "Singleton":
        if cls._instance is None:
            cls._instance = super(Singleton, cls).__new__(cls)
        return cls._instance


class ThreadSafeSingleton:
    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs) -> "ThreadSafeSingleton":
        if not cls._instance:
            with cls._lock:
                cls._instance = super(ThreadSafeSingleton, cls).__new__(cls)
        return cls._instance


def random_string(n: int) -> str:
    return "".join(random.choices(ascii_uppercase + digits, k=n))


def create_hash(value: str, length: int = 7) -> str:
    return md5(value.encode("UTF-8")).hexdigest()[:length]


def md5_hash(data: str | object) -> str:
    salt = create_hash(random_string(15), 10)
    h = ""
    if isinstance(data, str):
        h = create_hash(data)
    else:
        h = f"{hash(data)}"
    return f"{salt}_{h}_{create_hash(f'{time()}', 6)}"
