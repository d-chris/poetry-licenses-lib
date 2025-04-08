from collections.abc import Generator
from functools import lru_cache
from pathlib import Path

import piplicenses_lib as piplicenses
from poetry.core.packages.dependency import Dependency
from poetry.factory import Factory

from .activate import activate_poetry
from .errors import PoetryDependencyError
from .licenses import get_packages


def poetry_dependencies(pyproject_toml: str) -> dict[str, list[Dependency]]:
    """Retrieve the grouped dependencies from a Poetry project."""

    toml = Path(pyproject_toml).resolve(True)

    @lru_cache(maxsize=16)
    def dependencies(pyproject):
        # Load the pyproject.toml file
        poetry = Factory().create_poetry(pyproject)

        # Get the dependencies
        dependencies = poetry.package.all_requires

        groups = dict()

        for dep in dependencies:
            for group in dep.groups:
                groups.setdefault(group, []).append(dep)

        return groups

    return dependencies(toml)


def get_poetry_packages(
    pyproject_toml: str,
    **kwargs,
) -> dict[str, piplicenses.PackageInfo]:
    """Retrieve the packages from a Poetry project."""

    with activate_poetry(pyproject_toml) as poetry:
        return get_packages(
            python_path=poetry.python,
            **kwargs,
        )


def get_poetry_package_group(
    pyproject_toml: str,
    dependency_group: str = "main",
    strict: bool = True,
    **kwargs,
) -> Generator[tuple[Dependency, piplicenses.PackageInfo], None, None]:
    """Retrieve the relevant information for the given package group."""

    dependencies = poetry_dependencies(pyproject_toml)

    grouped_dependencies = dependencies.get(dependency_group, None)
    if grouped_dependencies is None:
        raise ValueError(f"{grouped_dependencies=} not found in {pyproject_toml=}")

    licenses = get_poetry_packages(pyproject_toml, **kwargs)

    for dependency in grouped_dependencies:

        license = licenses.get(dependency.name, None)

        if strict is True and license is None:
            raise PoetryDependencyError(dependency)

        yield dependency, license
