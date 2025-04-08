import os
import subprocess
import sys
from collections.abc import Generator
from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path
from typing import Union

import piplicenses_lib as piplicenses

from .errors import PoetryVenvError


@lru_cache(maxsize=16)
def get_python_sys_path(
    python_path: Path,
) -> list[str]:
    """Get the python sys.path."""

    return piplicenses.get_python_sys_path(python_path)


@lru_cache(maxsize=16)
def get_poetry_env_path(
    pyproject_toml: Path,
) -> tuple[str, str]:
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

    return python_exe, virtual_env


@contextmanager
def activate_venv(
    path: Union[str, os.PathLike],
) -> Generator[None, None, None]:
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
    *path: Union[str, os.PathLike],
) -> Generator[None, None, None]:
    """Activate the given path by modifying sys.path."""

    original_path = sys.path[:]

    try:
        sys.path = [str(p) for p in path] + original_path
        yield
    finally:
        sys.path = original_path


@contextmanager
def activate_python(
    python_exe: Union[str, os.PathLike],
) -> Generator[list[str], None, None]:
    """Activate the python environment."""

    python = Path(python_exe).resolve()

    if not python.is_file():
        raise ValueError(f"{python_exe=} is not a file.")

    path = get_python_sys_path(python)

    with activate(*path):
        yield path


@contextmanager
def activate_poetry(
    pyproject_toml: Union[str, os.PathLike],
) -> Generator[tuple[str, str], None, None]:
    """Activate the poetry environment."""

    pyproject = Path(pyproject_toml).resolve()

    if not pyproject.is_file():
        raise ValueError(f"{pyproject_toml=} is not a file.")

    python_exe, virtual_env = get_poetry_env_path(pyproject)

    if any(not Path(p).exists() for p in (python_exe, virtual_env)):
        raise PoetryVenvError(pyproject)

    with activate_python(python_exe):
        with activate_venv(virtual_env):
            yield python_exe, virtual_env
