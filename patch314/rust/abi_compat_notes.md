# Rust / pyo3 ABI Compatibility with CPython 3.14

## Current State

ChromaDB ships `chromadb_rust_bindings` as a compiled wheel tagged `cp39-abi3-win_amd64`
(and equivalent tags for Linux/macOS). The `abi3` tag means it uses the **CPython Stable ABI**,
which is forward-compatible across minor Python versions.

## CPython 3.14 Stable ABI Changes

CPython 3.14 introduces changes relevant to native extensions:

1. **PEP 749 (Deferred Evaluation of Annotations)** - Affects type introspection at runtime.
   Rust bindings using `pyo3` are not affected because they define types via the C API,
   not Python annotations.

2. **Free-threaded (no-GIL) builds** - CPython 3.13+ offers experimental free-threaded builds.
   3.14 continues this. `pyo3` >=0.22 supports `Py_GIL_DISABLED` but requires the `abi3`
   feature to be disabled for free-threaded builds (they use `cp314-cp314t` tags).

3. **Stable ABI additions** - No breaking changes to existing stable ABI functions.

## Action Items

| Item | Status | Notes |
|------|--------|-------|
| Verify `pyo3` version >= 0.22 | Required | Adds CPython 3.14 support |
| Test wheel install on 3.14 | Required | `pip install chromadb` should find abi3 wheel |
| Free-threaded build support | Optional | Requires separate `cp314t` wheel, no abi3 |

## Build Verification

To verify the Rust bindings load correctly on Python 3.14:

```python
import sys
assert sys.version_info >= (3, 14)

from chromadb import chromadb_rust_bindings
print(f"Rust bindings loaded: {chromadb_rust_bindings.__file__}")
```

## Cargo.toml Changes (if rebuilding)

If the upstream project needs to rebuild for 3.14 explicitly:

```toml
[dependencies]
pyo3 = { version = ">=0.22", features = ["abi3-py39"] }
```

The `abi3-py39` feature ensures the built wheel works on Python 3.9 through 3.14+.

## Risk Assessment

**Low risk.** The `abi3` stable ABI contract guarantees forward compatibility. The primary
risk is if CPython 3.14 removes or changes a stable ABI function that `pyo3` depends on,
which has not happened. The existing wheel should load without recompilation.
