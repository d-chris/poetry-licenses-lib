from __future__ import annotations

import os
import subprocess
import sys
from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, NamedTuple

import piplicenses_lib as piplicenses

from .errors import PoetryVenvError

if TYPE_CHECKING:
    from collections.abc import Generator


class PoetryEnv(NamedTuple):
    """Poetry environment."""

    python: str
    """path to the python executable."""
    path: str
    """location of the virtual environment."""

    def __call__(self) -> bool:
        """Check if the environment is valid."""
        for item in self:
            if not item or not Path(item).exists():
                return False

        return True


@lru_cache(maxsize=16)
def get_python_sys_path(
    python_path: Path,
) -> list[str]:
    """Get the python sys.path."""

    return piplicenses.get_python_sys_path(python_path)


@lru_cache(maxsize=16)
def get_poetry_env_path(
    pyproject_toml: Path,
) -> PoetryEnv:
    """Get the poetry environment."""

    command = ["poetry", "env", "info", "--directory", str(pyproject_toml.parent)]

    python_exe = subprocess.check_output(
        command + ["--executable"],
        text=True,
    ).strip()

    virtual_env = subprocess.check_output(
        command + ["--path"],
        text=True,
    ).strip()

    return PoetryEnv(python_exe, virtual_env)


@contextmanager
def activate_venv(
    path: str | os.PathLike,
) -> Generator[None]:
    """set environment variable for virtual environment."""

    venv = os.environ.get("VIRTUAL_ENV")

    try:
        os.environ["VIRTUAL_ENV"] = str(path)

        yield

    finally:
        if venv is None:
            del os.environ["VIRTUAL_ENV"]
        else:
            os.environ["VIRTUAL_ENV"] = venv


@contextmanager
def activate(
    *path: str | os.PathLike,
) -> Generator[None]:
    """Activate the given path by modifying sys.path."""

    original_path = sys.path[:]

    try:
        sys.path = [str(p) for p in path] + original_path
        yield
    finally:
        sys.path = original_path


@contextmanager
def activate_python(
    python_exe: str | os.PathLike,
) -> Generator[list[str]]:
    """Activate the python environment."""

    python = Path(python_exe).resolve()

    if not python.is_file():
        raise ValueError(f"{python_exe=} is not a file.")

    path = get_python_sys_path(python)

    with activate(*path):
        yield path


@contextmanager
def activate_poetry(
    pyproject_toml: str | os.PathLike,
) -> Generator[PoetryEnv]:
    """Activate the poetry environment."""

    pyproject = Path(pyproject_toml).resolve()

    if not pyproject.is_file():
        raise ValueError(f"{pyproject_toml=} is not a file.")

    poetry = get_poetry_env_path(pyproject)

    if poetry() is False:
        raise PoetryVenvError(pyproject)

    with activate_python(poetry.python):
        with activate_venv(poetry.path):
            yield poetry
