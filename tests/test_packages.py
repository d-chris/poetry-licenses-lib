from pathlib import Path

import pytest

from poetry_licenses_lib import PoetryDependencyError
from poetry_licenses_lib import get_poetry_package_group
from poetry_licenses_lib import get_poetry_packages


def test_get_poetry_packages(poetry_venv: Path) -> None:
    """Test the get_poetry_packages function."""

    packages = dict(get_poetry_packages(poetry_venv))

    assert "pip" in packages.keys()
    assert packages["pip"].license == "MIT"


@pytest.mark.parametrize(
    "group,package",
    [
        ("main", "pathlibutil"),
        ("dev", "unicode-charset"),
    ],
    ids=lambda x: repr(x),
)
def test_get_poetry_package_group(poetry_venv: Path, group: str, package: str) -> None:
    """Test the get_poetry_package_group function."""

    packages = dict(get_poetry_package_group(poetry_venv, group))

    assert package in packages.keys()


def test_get_poetry_package_group_optional_strict(poetry_venv: Path) -> None:
    """Test the get_poetry_package_group function."""

    with pytest.raises(PoetryDependencyError):
        _ = dict(get_poetry_package_group(poetry_venv, "test", strict=True))


def test_get_poetry_package_group_optional(poetry_venv: Path) -> None:
    """Test the get_poetry_package_group function."""

    packages = dict(get_poetry_package_group(poetry_venv, "test"))

    assert packages["pytest-doctestplus"] is None


def test_get_poetry_package_group_raises(poetry_venv: Path) -> None:
    """Test the get_poetry_package_group function with an empty group."""

    with pytest.raises(ValueError):
        _ = dict(get_poetry_package_group(poetry_venv, "missing_group"))
