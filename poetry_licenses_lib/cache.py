from __future__ import annotations

import functools
from typing import TYPE_CHECKING

if TYPE_CHECKING:

    from collections.abc import Generator
    from typing import Any
    from typing import Callable
    from typing import Protocol
    from typing import TypeVar

    from piplicenses_lib import PackageInfo

    class CachedPackageInfo(Protocol):
        def __call__(self, *args: Any, **kwargs: Any) -> dict[str, PackageInfo]: ...
        def cache_info(self) -> functools._CacheInfo: ...
        def cache_clear(self) -> None: ...

    R = TypeVar("R", bound=Generator[tuple[str, PackageInfo], None, None])


def cache_packageinfo(
    maxsize: int = 1,
    typed: bool = False,
) -> Callable[[Callable[..., R]], CachedPackageInfo]:
    """Decorator to cache the package information as a dictionary."""

    def decorator(func: Callable[..., R]) -> CachedPackageInfo:

        cached_func = functools.lru_cache(maxsize=maxsize, typed=typed)(
            lambda *args, **kwargs: dict(func(*args, **kwargs))
        )

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> dict[str, PackageInfo]:
            """The wrapper function that calls the cached function."""
            return cached_func(*args, **kwargs)

        setattr(wrapper, "cache_info", cached_func.cache_info)
        setattr(wrapper, "cache_clear", cached_func.cache_clear)

        return wrapper  # type: ignore[return-value]

    return decorator
