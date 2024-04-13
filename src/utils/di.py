from functools import wraps
from typing import Any, Callable, Dict, TypeVar


P = TypeVar('P')
R = TypeVar('R')


def di_singleton(fnc: Callable[..., R]) -> Callable[..., R]:
    setattr(fnc, 'singleton', True)  # noqa

    @wraps(fnc)
    def wrapper(*args: P, **kwargs: Any) -> R:
        return fnc(*args, **kwargs)

    return wrapper


class DIContainer:
    _register: Dict[str, Callable[..., Any]]

    def __init__(self) -> None:
        self._register = {}

    def __getattribute__(self, name: str) -> Any:
        ret = None
        if name == '_register' or name.startswith('__'):
            return super().__getattribute__(name)

        if name not in self._register:
            fnc = super().__getattribute__(f'_get_{name}')
            ret = fnc()
            if getattr(fnc, 'singleton', False):
                self._register[name] = ret
            return ret

        return self._register[name]
