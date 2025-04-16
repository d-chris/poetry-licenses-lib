import pytest
from pytest_mock import MockerFixture

from poetry_licenses_lib.errors import PoetryVenvError
from poetry_licenses_lib.legacy import activate_poetry


def test_activate_poetry_raises(mocker: MockerFixture) -> None:

    mock_env = mocker.patch("poetry_licenses_lib.legacy.EnvManager")
    mock_env.return_value.list.return_value = []

    with pytest.raises(PoetryVenvError):
        with activate_poetry("pyproject.toml"):
            pass
