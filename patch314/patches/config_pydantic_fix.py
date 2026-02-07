"""
Replacement for chromadb/config.py lines 15-24.

This fixes the Pydantic import logic to work with:
  - Pydantic v1 (standalone BaseSettings)
  - Pydantic v2 < 2.12 (pydantic.v1 compat shim)
  - Pydantic v2 >= 2.12 + pydantic-settings (Python 3.14 compatible)

Apply by replacing lines 15-24 of chromadb/config.py with this block.
"""

# --- BEGIN REPLACEMENT BLOCK (config.py lines 15-24) ---

import sys

in_pydantic_v1 = False
in_pydantic_v2 = False

# Strategy:
#   1. Try pydantic-settings (the correct location for pydantic v2)
#   2. Fall back to pydantic<2 direct import (pydantic v1 standalone)
#   3. Last resort: pydantic.v1 compat shim (only if Python < 3.14)

try:
    # Pydantic v2 with pydantic-settings installed (recommended path)
    from pydantic_settings import BaseSettings
    from pydantic import field_validator  # pydantic v2 API

    in_pydantic_v2 = True

    # Provide a 'validator' compatible wrapper for existing @validator usage
    # in the Settings class. This avoids rewriting all validators at once.
    def validator(field: str, *, pre: bool = False, always: bool = False,
                  allow_reuse: bool = False):
        """Shim: wraps pydantic v2 field_validator to match v1 @validator signature."""
        mode = "before" if pre else "after"
        return field_validator(field, mode=mode)

except ImportError:
    try:
        # Pydantic v1 (BaseSettings lived in pydantic directly)
        from pydantic import BaseSettings  # type: ignore[no-redef]
        from pydantic import validator  # type: ignore[no-redef]
        in_pydantic_v1 = True
    except ImportError:
        # Pydantic v2 without pydantic-settings: use v1 compat shim
        # WARNING: This path is broken on Python 3.14+ (PEP 749)
        if sys.version_info >= (3, 14):
            raise ImportError(
                "ChromaDB requires 'pydantic-settings' on Python 3.14+. "
                "Install it with: pip install pydantic-settings>=2.0"
            )
        from pydantic.v1 import BaseSettings  # type: ignore[no-redef]
        from pydantic.v1 import validator  # type: ignore[no-redef]
        in_pydantic_v2 = True  # still pydantic v2 runtime, just using v1 shim

# --- END REPLACEMENT BLOCK ---
