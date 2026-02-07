# ChromaDB Python 3.14 Compatibility Patch

**Issue:** [chroma-core/chroma#5996](https://github.com/chroma-core/chroma/issues/5996)
**Problem:** ChromaDB import fails on Python 3.14+ with Pydantic 2.12+ due to broken v1 compatibility detection in `config.py`.

## Root Cause

In `chromadb/config.py`, the Pydantic version detection uses:

```python
try:
    from pydantic import BaseSettings  # removed in pydantic 2.x
except ImportError:
    in_pydantic_v2 = True
    from pydantic.v1 import BaseSettings  # v1 compat shim
```

With Pydantic 2.12+, `BaseSettings` was moved to the `pydantic-settings` package. The `ImportError` fallback then loads `pydantic.v1`, whose metaclass introspection is incompatible with Python 3.14's type annotation changes (PEP 749 / lazy annotations). This causes:

```
pydantic.v1.errors.ConfigError: unable to infer type for attribute 'chroma_server_nofile'
```

## Patch Strategy

1. **`patches/config_pydantic_fix.py`** - Drop-in replacement for the import block in `config.py`. Uses `pydantic-settings` directly when available, avoids the broken `pydantic.v1` shim entirely.
2. **`chromadb_py314_compat/`** - Installable shim package that monkey-patches ChromaDB at import time (for users who cannot modify site-packages).
3. **`rust/`** - Notes on Rust `pyo3` ABI compatibility with CPython 3.14 stable ABI.
4. **`clients/js/`** - TypeScript/JS client is unaffected (no Pydantic dependency), but includes a version-gate utility for CI.
5. **`tests/`** - Validation tests for the patch.
6. **`.github/workflows/`** - CI workflow to test against Python 3.14.

## Quick Apply (manual patch)

Replace lines 15-24 of `chromadb/config.py` with the contents of `patches/config_pydantic_fix.py`.

## Quick Apply (shim package)

```bash
pip install -e ./chromadb_py314_compat
# Then import as usual:
python -c "import chromadb"
```

## Files

```
patch314/
├── README.md                          # This file
├── pyproject.toml                     # Patch package metadata
├── patches/
│   ├── config_pydantic_fix.py         # Direct replacement for config.py import block
│   └── config_pydantic_fix.patch      # Unified diff for config.py
├── chromadb_py314_compat/
│   ├── __init__.py                    # Monkey-patch shim (auto-applied on import)
│   ├── settings_compat.py             # Pydantic v2 Settings adapter
│   └── pyproject.toml                 # Shim package build config
├── rust/
│   ├── abi_compat_notes.md            # CPython 3.14 stable ABI notes for pyo3
│   └── build_check.rs                 # Compile-time Python version gate
├── clients/js/
│   └── version_gate.ts                # CI helper: skip JS client tests if server <3.14
├── tests/
│   ├── test_import.py                 # Validates chromadb imports on 3.14
│   ├── test_settings.py               # Validates Settings class instantiation
│   └── conftest.py                    # Pytest fixtures
└── .github/workflows/
    └── python314_ci.yml               # GitHub Actions workflow for 3.14
```

## Affected Components

| Component | Impact | Action |
|-----------|--------|--------|
| `chromadb/config.py` | **Critical** - import fails | Rewrite Pydantic import block |
| `pydantic.v1` shim | Broken on 3.14 | Stop using; require `pydantic-settings>=2.0` |
| Rust bindings (`chromadb_rust_bindings`) | Low risk - uses stable ABI (`cp39-abi3`) | Verify `pyo3` >=0.22 for 3.14 support |
| TypeScript client | No impact | No changes needed |
| gRPC / protobuf | Low risk | Verify `grpcio` wheel availability for 3.14 |

## Dependencies Added

```
pydantic-settings>=2.0
```

## Dependencies Removed (from compat path)

```
pydantic.v1 (compatibility shim no longer used)
```
