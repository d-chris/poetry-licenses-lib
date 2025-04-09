from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import os

    from poetry.core.packages.dependency import Dependency


class PoetryError(RuntimeError):
    """Base class for Poetry-related errors."""

    ...


class PoetryVenvError(PoetryError):
    """no venv found for the given pyproject.toml file."""

    def __init__(self, pyproject: str | os.PathLike) -> None:
        self.pyproject = Path(pyproject)
        super().__init__(f"No '.venv' found for {pyproject=}")


class PoetryDependencyError(PoetryError):
    """dependency not installed in venv."""

    def __init__(self, dependency: Dependency) -> None:
        self.dependency = dependency
        package = dependency.name

        if dependency.is_optional():
            extras = dependency.in_extras

            if extras:
                message = f"optional {package=} missing, installed as {extras=}"
            else:
                message = f"optional {package=} must be installed"
        else:
            groups = dependency.groups

            if groups:
                groups = list(groups)
                message = f"{package=} missing, install with {groups=}"
            else:
                message = f"{package=} not installed in '.venv'"

        super().__init__(message)
