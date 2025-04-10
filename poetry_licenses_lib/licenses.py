from __future__ import annotations

from typing import TYPE_CHECKING

import piplicenses_lib as piplicenses

if TYPE_CHECKING:
    import os
    from collections.abc import Generator


def get_packages(
    python_path: str | os.PathLike | None = None,
    **kwargs,
) -> Generator[tuple[str, piplicenses.PackageInfo]]:
    """Retrieve the relevant information for the given package."""

    from_source = kwargs.pop("from_source", piplicenses.FromArg.MIXED)

    for license in piplicenses.get_packages(
        from_source=from_source,
        python_path=python_path,
        **kwargs,
    ):
        yield license.name, license
