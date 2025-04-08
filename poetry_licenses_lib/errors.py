import os
from pathlib import Path
from typing import Union

from poetry.core.packages.dependency import Dependency


class PoetryError(RuntimeError):
    """Base class for Poetry-related errors."""

    ...


class PoetryVenvError(PoetryError):
    """no venv found for the given pyproject.toml file."""

    def __init__(self, pyproject: Union[str, os.PathLike]) -> None:
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
                message = f"optional {package=} must be installed as {extras=}"
            else:
                message = f"optional {package=} must be installed"
        else:
            message = f"{package=} not installed in '.venv'"

        super().__init__(message)
