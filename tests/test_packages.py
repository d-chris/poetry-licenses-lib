from pathlib import Path

import pytest

from poetry_licenses_lib import PoetryDependencyError
from poetry_licenses_lib import get_poetry_package_group
from poetry_licenses_lib import get_poetry_packages
from poetry_licenses_lib.packages import PoetryPackageInfo


def test_get_poetry_packages(poetry_toml: Path) -> None:
    """Test the get_poetry_packages function."""

    packages = dict(get_poetry_packages(poetry_toml))

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
def test_get_poetry_package_group(poetry_toml: Path, group: str, package: str) -> None:
    """Test the get_poetry_package_group function."""

    packages = dict(get_poetry_package_group(poetry_toml, group))

    assert package in packages.keys()


def test_get_poetry_package_group_optional_strict(poetry_toml: Path) -> None:
    """Test the get_poetry_package_group function."""

    with pytest.raises(PoetryDependencyError):
        _ = dict(get_poetry_package_group(poetry_toml, strict=True))


def test_get_poetry_package_group_optional(poetry_toml: Path) -> None:
    """Test the get_poetry_package_group function."""

    packages = dict(get_poetry_package_group(poetry_toml))

    assert packages["pytest-doctestplus"] is None


def test_get_poetry_package_group_raises(poetry_toml: Path) -> None:
    """Test the get_poetry_package_group function with an empty group."""

    with pytest.raises(ValueError):
        _ = dict(get_poetry_package_group(poetry_toml, "missing_group"))


@pytest.mark.parametrize(
    "func",
    [
        get_poetry_package_group,
        get_poetry_packages,
    ],
)
def test_get_poetry_notoml_raises(func, tmp_path):
    """Test the get_poetry_packages function."""

    with pytest.raises(FileNotFoundError):
        _ = dict(func(tmp_path))


def test_get_poetry_package_group_nolock_raises(tmp_path: Path):

    toml = tmp_path / "pyproject.toml"
    toml.touch()

    with pytest.raises(FileNotFoundError):
        _ = dict(get_poetry_package_group(toml))


@pytest.mark.parametrize(
    "attr, instance",
    [
        ("dependencies", dict),
        ("packages", dict),
        ("groups", set),
        ("pyproject", str),
    ],
)
def test_poetrypackageinfo_properties(poetry_toml, attr, instance):

    p = PoetryPackageInfo(poetry_toml)

    assert isinstance(getattr(p, attr), instance)


def test_propertypackageinfo_cache(poetry_toml):

    p1 = PoetryPackageInfo(poetry_toml, cache=True)
    p2 = PoetryPackageInfo(poetry_toml, cache=True)
    p3 = PoetryPackageInfo(poetry_toml, cache=False)

    assert p1 is p2
    assert p1 is not p3
