from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Generator


@contextmanager
def activate(venv_path: str | os.PathLike) -> Generator[Path]:

    if os.name == "nt":
        venv = Path(venv_path).joinpath("Scripts")
    else:
        venv = Path(venv_path).joinpath("bin")

    if not venv.is_dir():
        raise NotADirectoryError(f"{venv=} is not a directory.")

    original_env = os.environ.copy()
    _ = os.environ.pop("VIRTUAL_ENV", None)

    try:
        os.environ["PATH"] = os.pathsep.join([str(venv), os.environ["PATH"]])
        yield venv
    finally:
        os.environ.clear()
        os.environ.update(original_env)
