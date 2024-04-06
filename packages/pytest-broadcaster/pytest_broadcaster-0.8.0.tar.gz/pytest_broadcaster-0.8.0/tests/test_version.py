import pytest


@pytest.mark.buildmeta
def test_pytest_broadcaster_version():
    """Test pytest_broadcaster version is generated."""

    from pytest_broadcaster import __version__, __version_tuple__

    assert isinstance(__version__, str)
    assert isinstance(__version_tuple__, tuple)
