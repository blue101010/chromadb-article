"""
Tests that chromadb can be imported on Python 3.14+.

These tests validate the fix for https://github.com/chroma-core/chroma/issues/5996
"""

import sys
import importlib
import pytest


class TestChromaImport:
    """Verify that the chromadb package imports without error."""

    def test_import_chromadb(self):
        """Core test: chromadb must import without raising."""
        import chromadb  # noqa: F401

    def test_import_config(self):
        """The config module is where the Pydantic bug manifests."""
        from chromadb import config  # noqa: F401

    def test_import_base_settings(self):
        """BaseSettings must be resolvable from whatever path config.py uses."""
        from chromadb.config import Settings
        assert Settings is not None

    def test_settings_instantiation(self):
        """Settings() must instantiate without ConfigError."""
        from chromadb.config import Settings
        settings = Settings()
        assert settings is not None

    def test_import_client(self):
        """Client creation must work end-to-end."""
        import chromadb
        client = chromadb.Client()
        assert client is not None

    @pytest.mark.skipif(
        sys.version_info < (3, 14),
        reason="Only relevant on Python 3.14+"
    )
    def test_no_pydantic_v1_shim_on_314(self):
        """On Python 3.14+, we must NOT be using the pydantic.v1 compat layer."""
        from chromadb import config

        # If the patched config uses pydantic-settings, the in_pydantic_v2 flag
        # should be True and we should NOT have imported from pydantic.v1
        assert not getattr(config, "in_pydantic_v1", False), (
            "config.py is using pydantic.v1 shim on Python 3.14, which is broken"
        )

    def test_pydantic_settings_available(self, has_pydantic_settings, is_python_314):
        """On 3.14+, pydantic-settings MUST be installed."""
        if is_python_314:
            assert has_pydantic_settings, (
                "pydantic-settings is required on Python 3.14+ but not installed"
            )


class TestConfigReload:
    """Verify config can be reloaded (catches import-time side effects)."""

    def test_reload_config(self):
        """Reloading chromadb.config must not raise."""
        import chromadb.config
        importlib.reload(chromadb.config)

    def test_reload_preserves_settings(self):
        """Settings class must survive module reload."""
        import chromadb.config
        importlib.reload(chromadb.config)
        settings = chromadb.config.Settings()
        assert settings is not None
