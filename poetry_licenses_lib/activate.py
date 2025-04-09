from __future__ import annotations

import os
import sys
from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING

import piplicenses_lib as piplicenses

if TYPE_CHECKING:
    from collections.abc import Generator


@lru_cache(maxsize=16)
def get_python_sys_path(
    python_path: Path,
) -> list[str]:
    """Get the python sys.path."""

    return piplicenses.get_python_sys_path(python_path)


@contextmanager
def activate_venv(
    venv_path: str | os.PathLike,
) -> Generator[None]:
    """set environment variable for virtual environment."""

    venv = os.environ.get("VIRTUAL_ENV")

    try:
        os.environ["VIRTUAL_ENV"] = str(venv_path)

        yield

    finally:
        if venv is None:
            del os.environ["VIRTUAL_ENV"]
        else:
            os.environ["VIRTUAL_ENV"] = venv


@contextmanager
def activate(
    *sys_path: str | os.PathLike,
) -> Generator[None]:
    """Activate the given path by modifying sys.path."""

    original_path = sys.path[:]

    try:
        sys.path = [str(p) for p in sys_path] + original_path
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
