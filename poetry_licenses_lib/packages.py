from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from poetry.factory import Factory

from poetry_licenses_lib.errors import PoetryDependencyError
from poetry_licenses_lib.legacy import activate_poetry
from poetry_licenses_lib.licenses import get_packages

if TYPE_CHECKING:
    import os
    from collections.abc import Generator
    from typing import Protocol
    from typing import TypeVar

    import piplicenses_lib as piplicenses
    from poetry.core.packages.dependency import Dependency

    T = TypeVar("T", bound=piplicenses.PackageInfo, covariant=True)

    class PackageInfo(Protocol[T]):
        @property
        def dependency(self) -> Dependency:
            """The Poetry dependency associated with this package license."""
            ...


def get_poetry_dependencies(
    pyproject_toml: str | os.PathLike,
    *,
    all: bool = True,
) -> dict[str, list[Dependency]]:
    """Retrieve the grouped dependencies from a Poetry project."""

    toml = Path(pyproject_toml).resolve(True)

    poetry = Factory().create_poetry(toml)

    # Get the dependencies
    dependencies = poetry.package.all_requires if all else poetry.package.requires

    groups: dict[str, list[Dependency]] = dict()

    for dep in dependencies:
        for group in dep.groups:
            groups.setdefault(group, []).append(dep)

    return groups


def get_poetry_packages(
    pyproject_toml: str | os.PathLike,
    **kwargs,
) -> Generator[tuple[str, piplicenses.PackageInfo]]:
    """Retrieve the packages from a Poetry project."""

    with activate_poetry(pyproject_toml) as poetry:
        yield from get_packages(
            python_path=poetry.python,
            **kwargs,
        )


def get_poetry_package_group(
    pyproject_toml: str | os.PathLike,
    dependency_group: str = "main",
    *,
    strict: bool = False,
    **kwargs,
) -> Generator[tuple[str, PackageInfo | None]]:
    """Retrieve the relevant information for the given package group."""

    dependencies = get_poetry_dependencies(pyproject_toml)

    grouped_dependencies = dependencies.get(dependency_group, None)
    if grouped_dependencies is None:
        raise ValueError(f"{grouped_dependencies=} not found in {pyproject_toml=}")

    licenses = dict(get_poetry_packages(pyproject_toml, **kwargs))

    for dependency in grouped_dependencies:

        license = licenses.get(dependency.name, None)

        if license is not None:
            setattr(license, "dependency", dependency)
        elif strict is True:
            raise PoetryDependencyError(dependency)

        yield dependency.name, license
