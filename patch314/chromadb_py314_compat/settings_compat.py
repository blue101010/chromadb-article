"""
Pydantic v2 Settings adapter for ChromaDB.

Provides BaseSettings and a validator shim that bridges the pydantic v1
@validator API to pydantic v2's @field_validator, so existing chromadb
Settings code works without modification.
"""

from pydantic_settings import BaseSettings  # noqa: F401
from pydantic import field_validator


def validator(
    field: str,
    *,
    pre: bool = False,
    always: bool = False,
    allow_reuse: bool = False,
):
    """
    Compatibility wrapper: translates pydantic v1 @validator kwargs
    to pydantic v2 @field_validator.

    Maps:
        pre=True  -> mode="before"
        pre=False -> mode="after"

    The `always` and `allow_reuse` params are accepted but ignored
    (they have no direct equivalent in v2 and are safe to drop for
    ChromaDB's usage).
    """
    mode = "before" if pre else "after"
    return field_validator(field, mode=mode)


__all__ = ["BaseSettings", "validator"]
