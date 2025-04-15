import pytest

from poetry_licenses_lib.errors import PoetryVenvError
from poetry_licenses_lib.legacy import activate_poetry


def test_activate_poetry_raises(mocker):

    mocker.patch("poetry_licenses_lib.legacy.poetry_venv", side_effect=IndexError)

    with pytest.raises(PoetryVenvError):
        with activate_poetry("pyproject.toml"):
            pass
