from __future__ import annotations

import os
import shutil
import subprocess
from collections.abc import Generator
from contextlib import ExitStack
from tempfile import TemporaryDirectory
from venv import EnvBuilder

import pytest
from packaging.version import Version
from pathlibutil import Path
from poetry.__version__ import __version__

from poetry_licenses_lib.activate import activate


def zip_dir(dir_path: Path, zip_path: Path) -> Path:
    """Create a zip archive of the specified directory."""

    dir = dir_path.resolve(True)

    shutil.make_archive(
        base_name=zip_path.with_suffix("").as_posix(),
        format="zip",
        root_dir=dir.as_posix(),
    )
    return zip_path


def setup_poetry(
    *poetry_versions: str,
    install: bool = False,
) -> Generator[str]:
    """
    Create a pyproject.toml file with the given poetry versions in a temp directory,
    optional it will install the dependencies in a virtual environment.
    """

    for version in poetry_versions:
        with TemporaryDirectory(prefix="pip_") as venv:

            # create venv to install poetry into
            builder = EnvBuilder(with_pip=True, clear=True)
            builder.create(venv)

            with activate(venv):
                # install poetry in venv
                subprocess.check_call(
                    [
                        "pip",
                        "install",
                        "--disable-pip-version-check",
                        "--no-input",
                        "--quiet",
                        f"poetry=={version}",
                    ]
                )

                # from venv create a poetry package with an .venv in a temp directory
                with TemporaryDirectory(prefix="poetry_", dir=venv) as poetry_venv:
                    subprocess.check_call(
                        [
                            "poetry",
                            "init",
                            "--no-interaction",
                            "--quiet",
                            "--python",
                            "^3.9",
                            "--dependency",
                            "pathlibutil==0.3.5",
                            "--dev-dependency",
                            "unicode-charset==0.0.0",
                        ],
                        cwd=poetry_venv,
                    )

                    add = [
                        "poetry",
                        "add",
                        "--no-interaction",
                        "--quiet",
                        "pytest-doctestplus",
                        "--lock",
                        "--optional",
                    ]

                    if Version(__version__) >= Version("2.0"):
                        add.append("pt")

                    subprocess.check_call(
                        add,
                        cwd=poetry_venv,
                    )

                    with ExitStack() as stack:
                        if install:
                            env = os.environ.copy()
                            env["POETRY_VIRTUALENVS_IN_PROJECT"] = "true"

                            subprocess.check_call(
                                [
                                    "poetry",
                                    "install",
                                    "--quiet",
                                    "--no-root",
                                ],
                                cwd=poetry_venv,
                                env=env,
                            )

                            stack.enter_context(activate(poetry_venv + "/.venv"))

                        yield poetry_venv


def setup_test_environment(tmp_dir: str) -> Path:
    """Set up a test environment using Poetry."""

    # create hash filename
    cache_dir = os.environ.get("PYTEST_VENV_CACHE", ".pytest_cache")
    hash = Path(__file__).hexdigest("sha1")[:7]
    cache = Path(cache_dir).joinpath(f"venv-{hash}.zip")

    # if cached file exists restore cached files into tempdir
    if cache.is_file():
        try:
            return cache.unpack_archive(tmp_dir)
        except Exception:
            cache.unlink(missing_ok=True)

    # else create pyproject.toml and install dependencies

    for venv in setup_poetry(__version__, install=True):
        tmp_dir = Path(venv).copy(tmp_dir)

    # create cache zip
    try:
        zip_dir(tmp_dir, cache)
    except Exception:
        cache.unlink(missing_ok=True)

    return tmp_dir


@pytest.fixture(scope="session")
def poetry_venv(tmp_path_factory: pytest.TempPathFactory):
    """Fixture to create a pyproject.toml file using Poetry."""

    tmp_path = tmp_path_factory.mktemp("poetry_project")

    try:
        yield setup_test_environment(tmp_path)
    finally:
        shutil.rmtree(tmp_path, ignore_errors=True)


@pytest.fixture(scope="session")
def poetry_toml(poetry_venv: Path) -> Path:
    """Fixture to create a pyproject.toml file using Poetry."""

    return poetry_venv / "pyproject.toml"
