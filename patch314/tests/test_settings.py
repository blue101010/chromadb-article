"""
Tests for the Settings class fields that trigger the Pydantic v1 ConfigError.

The original issue reports that these specific fields fail type inference
on Python 3.14 with pydantic.v1:
  - chroma_server_nofile
  - chroma_coordinator_host
  - chroma_logservice_host
  - chroma_logservice_port
"""

import sys
import pytest


class TestSettingsFields:
    """Validate that all Settings fields resolve correctly."""

    def test_chroma_server_nofile_default(self):
        """chroma_server_nofile defaults to None (the field that triggers #5996)."""
        from chromadb.config import Settings
        s = Settings()
        assert s.chroma_server_nofile is None

    def test_chroma_server_nofile_set_int(self):
        """chroma_server_nofile accepts an integer."""
        from chromadb.config import Settings
        s = Settings(chroma_server_nofile=65536)
        assert s.chroma_server_nofile == 65536

    def test_chroma_server_nofile_empty_str_to_none(self):
        """The empty_str_to_none validator must coerce '' to None."""
        from chromadb.config import Settings
        s = Settings(chroma_server_nofile="")
        assert s.chroma_server_nofile is None

    def test_chroma_server_host_default(self):
        from chromadb.config import Settings
        s = Settings()
        assert s.chroma_server_host is None

    def test_chroma_server_host_set(self):
        from chromadb.config import Settings
        s = Settings(chroma_server_host="localhost")
        assert s.chroma_server_host == "localhost"

    def test_persist_directory_default(self):
        from chromadb.config import Settings
        s = Settings()
        assert s.persist_directory == "./chroma"

    def test_chroma_api_impl_default(self):
        from chromadb.config import Settings
        s = Settings()
        assert "RustBindingsAPI" in s.chroma_api_impl or "rust" in s.chroma_api_impl.lower()

    def test_environment_default(self):
        from chromadb.config import Settings
        s = Settings()
        assert s.environment == ""


class TestSettingsFieldTypes:
    """Verify type annotations are resolvable on all Python versions."""

    def test_optional_int_fields(self):
        """Optional[int] fields must not raise ConfigError."""
        from chromadb.config import Settings
        s = Settings()
        # These are the fields mentioned in issue #5996
        assert hasattr(s, "chroma_server_nofile")
        assert hasattr(s, "chroma_server_http_port")

    def test_optional_str_fields(self):
        """Optional[str] fields must not raise ConfigError."""
        from chromadb.config import Settings
        s = Settings()
        assert hasattr(s, "chroma_server_host")

    def test_bool_fields(self):
        from chromadb.config import Settings
        s = Settings()
        assert isinstance(s.is_persistent, bool)
        assert isinstance(s.allow_reset, bool)

    def test_list_fields(self):
        from chromadb.config import Settings
        s = Settings()
        assert isinstance(s.chroma_server_cors_allow_origins, list)

    @pytest.mark.skipif(
        sys.version_info < (3, 14),
        reason="Annotation evaluation behavior changed in 3.14"
    )
    def test_all_fields_resolvable_on_314(self):
        """Every field on Settings must have a resolvable type on 3.14."""
        from chromadb.config import Settings
        import typing

        hints = typing.get_type_hints(Settings)
        # If this doesn't raise, all annotations are valid
        assert len(hints) > 0, "Settings has no resolvable type hints"
