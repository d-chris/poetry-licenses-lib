from __future__ import annotations

import os
import shutil
import subprocess
import sys
from collections.abc import Generator
from contextlib import ExitStack
from tempfile import TemporaryDirectory
from venv import EnvBuilder

from packaging.version import Version
from pathlibutil import Path
from poetry.__version__ import __version__

from poetry_licenses_lib.activate import activate


def zip_dir(dir_path: str | os.PathLike, zip_path: Path) -> Path:
    """Create a zip archive of the specified directory."""

    dir = Path(dir_path).resolve(True)

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


def cache_name() -> str:
    v = sys.version_info
    python = f"py{v.major}{v.minor}"

    v = Version(__version__)
    poetry = f"poetry{v.major}{v.minor}"

    hash = Path(__file__).hexdigest("sha1")[:7]

    return f"venv-{sys.platform}-{python}-{poetry}-{hash}.zip"
