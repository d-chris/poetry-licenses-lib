from unittest.mock import MagicMock

import pytest

from poetry_licenses_lib.activate import Path
from poetry_licenses_lib.activate import activate


def test_activate_raises(mocker):

    mock_path = MagicMock(spec=Path)
    mock_path.joinpath.return_value.is_dir.return_value = False

    mocker.patch("poetry_licenses_lib.activate.Path.__new__", return_value=mock_path)
    mocker.patch("os.name", "posix")

    with pytest.raises(NotADirectoryError):
        with activate("not_a_directory"):
            pass
