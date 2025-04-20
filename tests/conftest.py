import os
import shutil
from typing import TYPE_CHECKING

import pytest
from pathlibutil import Path
from poetry.__version__ import __version__

from .setup import cache_name
from .setup import setup_poetry
from .setup import zip_dir

if TYPE_CHECKING:
    from _pytest.terminal import TerminalReporter


def cached_venv() -> Path:
    """Return the cache directory."""
    ci = os.environ.get("CI", "false").lower() in ("true", "1")

    root = "." if ci else os.environ.get("PYTEST_VENV_CACHE", ".pytest_cache")

    return Path(root).joinpath(cache_name()).resolve()


@pytest.fixture(scope="session")
def poetry_venv(tmp_path_factory: pytest.TempPathFactory):
    """Fixture to create a pyproject.toml file using Poetry."""

    tmp_path = tmp_path_factory.mktemp("poetry_project")
    cache = cached_venv()

    try:
        yield cache.unpack_archive(tmp_path)
    finally:
        shutil.rmtree(tmp_path, ignore_errors=True)


@pytest.fixture(scope="session")
def poetry_toml(poetry_venv: Path) -> Path:
    """Fixture to create a pyproject.toml file using Poetry."""

    return poetry_venv / "pyproject.toml"


def pytest_sessionstart(session: pytest.Session) -> None:
    zip = cached_venv().resolve()

    log: TerminalReporter = session.config.pluginmanager.get_plugin("terminalreporter")

    log.write_sep("=", "prepare test cache", bold=True)

    try:
        if zip.is_file():
            log.write_line("cache found...")
        else:
            log.write_line("create cache... (this may take a while)", flush=True)

            for venv in setup_poetry(__version__, install=True):
                zip_dir(venv, zip)
    finally:
        log.write_line(f"{zip.size()}   {zip.as_posix()}", flush=True)
