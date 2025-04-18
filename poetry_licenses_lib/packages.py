from __future__ import annotations

from typing import TYPE_CHECKING

from pathlibutil import Path
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

    pyproject = Path(pyproject_toml).resolve()

    if not pyproject.is_file():
        raise FileNotFoundError(f"{pyproject_toml=} is not a file.")

    with activate_poetry(pyproject_toml) as poetry:
        yield from get_packages(
            python_path=poetry.python,
            **kwargs,
        )


class PoetryPackageInfo:
    _cache: dict[Path, tuple[str, PoetryPackageInfo]] = {}

    def __new__(
        cls,
        pyproject_toml: str | os.PathLike,
        cache: bool = True,
    ) -> PoetryPackageInfo:
        pyproject = Path(pyproject_toml).resolve()

        if not pyproject.is_file() or pyproject.name.lower() != "pyproject.toml":
            raise FileNotFoundError(f"{pyproject_toml=} is not a file.")

        hash = pyproject.with_name("poetry.lock").hexdigest()

        if cache is True:
            lock, instance = cls._cache.get(pyproject, ("", None))
        else:
            lock, _ = cls._cache.pop(pyproject, ("", None))
            instance = None

        if instance is None or lock != hash:
            instance = super().__new__(cls)

            if cache is True:
                cls._cache[pyproject] = (hash, instance)

        return instance

    def __init__(
        self,
        pyproject_toml: str | os.PathLike,
        cache: bool = True,
    ) -> None:
        self.pyproject = str(pyproject_toml)
        self._dependencies = get_poetry_dependencies(self.pyproject)
        self._packages = dict(get_poetry_packages(self.pyproject))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.pyproject}')"

    @property
    def dependencies(self):
        """Get the dependencies of the poetry project."""

        return self._dependencies

    @property
    def packages(self):
        """Get all packages of venv."""

        return self._packages

    @property
    def groups(self) -> set[str]:
        """Get all the groups from the poetry venv."""
        return set(self._dependencies.keys())

    def licenses(
        self,
        dependgency_group: str = "main",
        strict: bool = False,
    ) -> Generator[tuple[str, PackageInfo]]:
        """Get the licenses of the packages in the poetry venv."""

        grouped_dependencies = self.dependencies.get(dependgency_group, None)
        if grouped_dependencies is None:
            raise ValueError(
                f"Group '{dependgency_group}' not found in '{self.pyproject}'"
            )

        for dependency in grouped_dependencies:

            license = self.packages.get(dependency.name, None)

            if license is not None:
                setattr(license, "dependency", dependency)
            elif strict is True:
                raise PoetryDependencyError(dependency)

            yield dependency.name, license


def get_poetry_package_group(
    pyproject_toml: str | os.PathLike,
    dependency_group: str = "main",
    *,
    strict: bool = False,
    cache: bool = True,
) -> Generator[tuple[str, PackageInfo | None]]:

    p = PoetryPackageInfo(pyproject_toml, cache=cache)

    yield from p.licenses(
        dependgency_group=dependency_group,
        strict=strict,
    )
