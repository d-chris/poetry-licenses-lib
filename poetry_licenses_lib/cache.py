from __future__ import annotations

import functools
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Generator
    from typing import Any
    from typing import Callable
    from typing import Protocol
    from typing import TypeVar

    T = TypeVar("T")
    R = Generator[tuple[str, T], None, None]
    F = TypeVar("F", bound=Callable[..., R])

    class CachedPackageInfo(Protocol[T]):
        def __call__(self, *args: Any, **kwargs: Any) -> dict[str, T]: ...
        def cache_info(self) -> functools._CacheInfo: ...
        def cache_clear(self) -> None: ...


def cache_packageinfo(
    maxsize: int = 1,
    typed: bool = False,
) -> Callable[[F], CachedPackageInfo[T]]:
    """
    A decorator to cache the results of a generator function that yields tuples[str, T],
    converting the output into a dict[str, T].
    """

    def decorator(func: F) -> CachedPackageInfo[T]:
        # The lambda calls func, which returns a generator yielding (str, T) tuples.
        # dict() collects them into a dict
        cached_func = functools.lru_cache(maxsize=maxsize, typed=typed)(
            lambda *args, **kwargs: dict(func(*args, **kwargs))
        )

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> dict[str, T]:
            """The wrapper function that calls the cached function."""
            return cached_func(*args, **kwargs)

        # Attach cache_info and cache_clear methods to the wrapper
        setattr(wrapper, "cache_info", cached_func.cache_info)
        setattr(wrapper, "cache_clear", cached_func.cache_clear)

        return wrapper  # type: ignore[return-value]

    return decorator
