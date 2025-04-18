from __future__ import annotations

import functools
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Generator
    from collections.abc import Mapping
    from typing import Callable
    from typing import Protocol
    from typing import TypeVar

    T = TypeVar("T", covariant=True)

    class CachedDict(Protocol[T]):
        def __call__(self, *args, **kwargs) -> Mapping[str, T]: ...
        def cache_info(self) -> functools._CacheInfo: ...
        def cache_clear(self) -> None: ...


def cache_as_dict(
    maxsize: int,
    **kwargs,
) -> Callable[[Callable[..., Generator[tuple[str, T]]]], CachedDict[T]]:

    if type(maxsize) is not int or maxsize < 0:
        raise ValueError("maxsize must be a non-negative integer")

    def decorator(
        func: Callable[..., Generator[tuple[str, T]]],
    ) -> CachedDict[T]:

        @functools.lru_cache(maxsize=maxsize, **kwargs)
        def cached_as_dict(*fargs, **fkwargs) -> Mapping[str, T]:
            return dict(func(*fargs, **fkwargs))

        @functools.wraps(func)
        def wrapper(*fargs, **fkwargs) -> Mapping[str, T]:
            return cached_as_dict(*fargs, **fkwargs)

        # Attach cache methods
        setattr(wrapper, "cache_info", cached_as_dict.cache_info)
        setattr(wrapper, "cache_clear", cached_as_dict.cache_clear)

        return wrapper  # type: ignore[return-value]

    return decorator
