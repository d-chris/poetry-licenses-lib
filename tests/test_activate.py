import pytest
from pytest_mock import MockerFixture

from poetry_licenses_lib.activate import activate


def test_activate_raises(mocker: MockerFixture) -> None:

    mock_path = mocker.patch("poetry_licenses_lib.activate.Path.__new__")
    mock_path.return_value.joinpath.return_value.is_dir.return_value = False

    mocker.patch("os.name", return_value="posix")

    with pytest.raises(NotADirectoryError):
        with activate("not_a_directory"):
            pass
