from __future__ import annotations

from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING

from poetry.factory import Factory
from poetry.utils.env import EnvManager

from poetry_licenses_lib.activate import activate
from poetry_licenses_lib.errors import PoetryVenvError

if TYPE_CHECKING:
    import os
    from collections.abc import Generator

    from poetry.utils.env import VirtualEnv


def poetry_venv(pyproject_toml: str | os.PathLike) -> VirtualEnv:
    """Retrieve the virtual environment for a Poetry project."""

    toml = Path(pyproject_toml).resolve(True)

    @lru_cache
    def venv(pyproject: Path) -> VirtualEnv:
        # Load the pyproject.toml file
        poetry = Factory().create_poetry(pyproject)

        # Get the virtual environment manager
        env_manager = EnvManager(poetry)

        return env_manager.list()[0]

    return venv(toml)


@contextmanager
def activate_poetry(pyproject_toml: str | os.PathLike) -> Generator[VirtualEnv]:
    """Activate a virtual environment by modifying sys.path."""

    try:
        venv = poetry_venv(pyproject_toml)
    except IndexError as e:
        raise PoetryVenvError(pyproject_toml) from e

    with activate(venv.path):
        yield venv
