import os
import subprocess
from pathlib import Path
from shutil import rmtree

import pytest


@pytest.fixture(scope="session")
def poetry_toml(tmp_path_factory: pytest.TempPathFactory):
    """Fixture to create a pyproject.toml file using Poetry."""

    tmp_path = tmp_path_factory.mktemp("poetry_project")

    toml = tmp_path / "pyproject.toml"
    cwd = str(toml.parent)

    create = [
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
    assert subprocess.check_call(create, cwd=cwd) == 0, "creating pyproject.toml failed"
    assert toml.is_file(), f"{toml=} not found"

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

    assert subprocess.check_call(add, cwd=cwd) == 0, "adding optional tox failed"

    try:
        yield toml
    finally:
        rmtree(tmp_path, ignore_errors=True)


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
