"""
chromadb_py314_compat - Monkey-patch shim for ChromaDB on Python 3.14+

Install this package alongside chromadb to fix the Pydantic import failure
on Python 3.14. It patches chromadb.config at import time.

Usage:
    pip install pydantic-settings>=2.0
    pip install -e ./chromadb_py314_compat
    import chromadb  # works on Python 3.14 now
"""

import sys
import importlib


def _patch_chromadb_config():
    """Patch chromadb.config to use pydantic-settings instead of pydantic.v1."""

    # Only needed on Python 3.14+
    if sys.version_info < (3, 14):
        return

    try:
        import pydantic_settings  # noqa: F401
    except ImportError:
        raise ImportError(
            "chromadb_py314_compat requires 'pydantic-settings>=2.0'. "
            "Install it with: pip install pydantic-settings>=2.0"
        )

    # Pre-populate the pydantic import path so chromadb.config finds
    # BaseSettings in the right place before it tries pydantic.v1
    from chromadb_py314_compat.settings_compat import (
        BaseSettings,
        validator,
    )

    # Intercept chromadb.config import via sys.modules manipulation
    import types

    config_shim = types.ModuleType("chromadb._py314_pydantic_shim")
    config_shim.BaseSettings = BaseSettings
    config_shim.validator = validator
    config_shim.in_pydantic_v2 = True
    sys.modules["chromadb._py314_pydantic_shim"] = config_shim


# Auto-apply patch on import of this package
_patch_chromadb_config()
