from poetry_licenses_lib import get_poetry_packages


def test_get_poetry_packages(poetry_venv: str) -> None:
    """Test the get_poetry_packages function."""

    packages = dict(get_poetry_packages(poetry_venv))
    assert "pathlibutil" in packages.keys()
