from pathlib import Path
from typing import TYPE_CHECKING
from typing import Callable

import pytest

from poetry_licenses_lib import cache_packageinfo
from poetry_licenses_lib import get_poetry_package_group
from poetry_licenses_lib import get_poetry_packages

if TYPE_CHECKING:
    from typing import Any

    from poetry_licenses_lib.cache import CachedPackageInfo


@pytest.mark.parametrize(
    "func",
    [
        get_poetry_package_group,
        get_poetry_packages,
    ],
)
def test_cache_packageinfo(poetry_venv: Path, func: Callable) -> None:
    """Test the get_poetry_packages function."""

    pyproject_toml = poetry_venv / "pyproject.toml"

    cached_func: CachedPackageInfo[Any] = cache_packageinfo()(func)

    result = cached_func(pyproject_toml)
    assert isinstance(result, dict)
    assert cached_func.cache_info().hits == 0
    assert cached_func.cache_info().misses == 1

    _ = cached_func(pyproject_toml)
    assert cached_func.cache_info().hits == 1
    assert cached_func.cache_info().misses == 1
