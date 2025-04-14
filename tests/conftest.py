from __future__ import annotations

import os
import shutil
import subprocess

import pytest
from pathlibutil import Path


def create_pyproject(cwd: str | os.PathLike | None = None) -> Path:
    """Create a pyproject.toml file using Poetry."""

    cwd = str(cwd) if cwd else os.getcwd()

    init = [
        "poetry",
        "init",
        "--no-interaction",
        "--quiet",
        "--dependency",
        "git+https://github.com/d-chris/pathlibutil.git",
        "--dev-dependency",
        "git+https://github.com/d-chris/unicode-charset.git",
        "--directory",
        cwd,
    ]
    subprocess.check_call(init, cwd=cwd)

    add = [
        "poetry",
        "add",
        "--no-interaction",
        "--quiet",
        "--group",
        "test",
        "git+https://github.com/d-chris/pytest-doctestplus.git",
        "--optional",
        "--lock",
        "--directory",
        cwd,
    ]
    subprocess.check_call(add, cwd=cwd)

    return Path(cwd).joinpath("pyproject.toml").resolve(True)


def create_venv(pyproject_toml: str | os.PathLike) -> Path:
    """Create a virtual environment from pyproject.toml using Poetry."""

    toml = Path(pyproject_toml).resolve(True)
    cwd = str(toml.parent)

    env = os.environ.copy()
    env.pop("VIRTUAL_ENV", None)
    env["POETRY_VIRTUALENVS_IN_PROJECT"] = "true"

    install = [
        "poetry",
        "install",
        "--no-interaction",
        "--quiet",
        "--no-root",
        "--directory",
        cwd,
    ]

    subprocess.check_call(install, env=env, cwd=cwd)

    return Path(cwd).joinpath(".venv").resolve(True)


def zip_dir(dir_path: Path, zip_path: Path) -> Path:
    """Create a zip archive of the specified directory."""

    dir = dir_path.resolve(True)

    shutil.make_archive(
        base_name=zip_path.with_suffix("").as_posix(),
        format="zip",
        root_dir=dir.as_posix(),
    )
    return zip_path


def setup_test_environment(tmp_dir: str) -> Path:
    """Set up a test environment using Poetry."""

    # create hash filename
    cache_dir = os.environ.get("PYTEST_VENV_CACHE", ".pytest_cache")
    hash = Path(__file__).hexdigest("sha1")[:7]
    cache = Path(cache_dir).joinpath(f"venv-{hash}.zip")

    # if cached file exists restore cached files into tempdir
    if cache.is_file():
        return cache.unpack_archive(tmp_dir)

    # else create pyproject.toml and install dependencies
    toml = create_pyproject(tmp_dir)
    create_venv(toml)

    # create cache zip
    tmp_dir = Path(tmp_dir).resolve()
    zip_dir(tmp_dir, cache)

    return tmp_dir


@pytest.fixture(scope="session")
def poetry_venv(tmp_path_factory: pytest.TempPathFactory):
    """Fixture to create a pyproject.toml file using Poetry."""

    tmp_path = tmp_path_factory.mktemp("poetry_project")

    try:
        yield setup_test_environment(tmp_path)
    finally:
        Path(tmp_path).parent.delete(recursive=True)
