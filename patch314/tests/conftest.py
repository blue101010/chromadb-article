"""Pytest fixtures for Python 3.14 compatibility tests."""

import sys
import pytest


@pytest.fixture
def python_version():
    """Return the current Python version tuple."""
    return sys.version_info


@pytest.fixture
def is_python_314():
    """True if running on Python 3.14+."""
    return sys.version_info >= (3, 14)


@pytest.fixture
def pydantic_version():
    """Return the installed pydantic version string."""
    import pydantic
    return pydantic.__version__


@pytest.fixture
def has_pydantic_settings():
    """True if pydantic-settings is installed."""
    try:
        import pydantic_settings  # noqa: F401
        return True
    except ImportError:
        return False
