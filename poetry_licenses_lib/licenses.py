from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING

import piplicenses_lib as piplicenses

if TYPE_CHECKING:
    import os


@lru_cache(maxsize=16)
def get_packages(
    python_path: str | os.PathLike | None = None,
    **kwargs,
) -> dict[str, piplicenses.PackageInfo]:
    """Retrieve the relevant information for the given package."""

    from_source = kwargs.pop("from_source", piplicenses.FromArg.MIXED)

    dists = piplicenses.get_packages(
        from_source=from_source,
        python_path=python_path,
        **kwargs,
    )

    return {d.name: d for d in dists}
