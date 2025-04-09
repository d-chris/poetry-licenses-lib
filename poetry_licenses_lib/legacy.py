from __future__ import annotations

import sys
from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING

from poetry.factory import Factory
from poetry.utils.env import EnvManager

from .errors import PoetryVenvError

if TYPE_CHECKING:
    from poetry.utils.env import VirtualEnv


def poetry_venv(pyproject_toml: str) -> VirtualEnv:
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
def activate_poetry(pyproject_toml: str):
    """Activate a virtual environment by modifying sys.path."""

    original_sys_path = sys.path[:]

    try:
        venv = poetry_venv(pyproject_toml)
        sys.path = venv.sys_path + sys.path

        yield venv
    except IndexError as e:
        raise PoetryVenvError(pyproject_toml) from e
    finally:
        sys.path = original_sys_path
