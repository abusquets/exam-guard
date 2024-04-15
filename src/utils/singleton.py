# With changes from: https://github.com/Kemaweyan/singleton_decorator/blob/master/singleton_decorator/decorator.py # noqa
import threading
from typing import Any, Type, TypeVar, cast


InstanceT = TypeVar('InstanceT')
WrappedT = TypeVar('WrappedT')


DecoratedT = TypeVar('DecoratedT', bound=Type[Any])
ResultT = Any


class _SingletonWrapper:
    """
    A singleton wrapper class. Its instances would be created
    for each decorated class.
    """

    def __init__(self, cls: DecoratedT) -> None:
        self.__wrapped__: DecoratedT = cls
        self._instance: ResultT = None
        self._lock = threading.Lock()

    def __call__(self, *args: Any, **kwargs: Any) -> ResultT:
        """Returns a single instance of decorated class"""
        if self._instance is None:
            with self._lock:
                if self._instance is None:
                    self._instance = self.__wrapped__(*args, **kwargs)
        return self._instance


def singleton(cls: DecoratedT) -> DecoratedT:
    """
    A singleton decorator. Returns a wrapper objects. A call on that object
    returns a single instance object of decorated class. Use the __wrapped__
    attribute to access decorated class directly in unit tests
    """
    return cast(DecoratedT, _SingletonWrapper(cls))
