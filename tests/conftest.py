from __future__ import annotations

import os
import subprocess

import pytest
from pathlibutil import Path


def create_pyproject(cwd: str | os.PathLike | None = None) -> Path:
    """ "Create a pyproject.toml file using Poetry."""

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
        "--directory",
        cwd,
    ]
    subprocess.check_call(add, cwd=cwd)

    return Path(cwd).joinpath("pyproject.toml").resolve(True)


@pytest.fixture(scope="session")
def poetry_toml(tmp_path_factory: pytest.TempPathFactory):
    """Fixture to create a pyproject.toml file using Poetry."""

    tmp_path = tmp_path_factory.mktemp("poetry_project")

    toml = create_pyproject(tmp_path)

    try:
        yield toml
    finally:
        Path(tmp_path).delete(recursive=True)


@pytest.fixture(scope="session")
def poetry_venv(poetry_toml: Path):
    """Fixture to create a Poetry virtual environment for testing."""

    cwd = str(poetry_toml.parent)
    env = os.environ.copy()
    env.pop("VIRTUAL_ENV", None)
    env["POETRY_VIRTUALENVS_IN_PROJECT"] = "true"

    setup = [
        "poetry",
        "install",
        "--no-interaction",
        "--quiet",
        "--no-root",
        "--directory",
        cwd,
    ]

    assert subprocess.check_call(setup, env=env, cwd=cwd) == 0, "creating .venv failed"
    assert Path(cwd).joinpath(".venv").is_dir(), f".venv not found in {cwd=}"

    try:
        yield poetry_toml
    finally:
        teardown = [
            "poetry",
            "env",
            "remove",
            "--all",
            "--quiet",
            "--directory",
            cwd,
        ]
        subprocess.run(teardown, env=env, cwd=cwd, check=False)
