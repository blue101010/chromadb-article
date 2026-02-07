# ChromaDB Notes, Scripts, and Python 3.14 Patch

This repository groups educational material and practical tooling around ChromaDB.

## Repository Content

### 1. Articles

- `article_chromadb.tex`: full technical article in English (LaTeX source).
- `article_chromadb_fr.tex`: French LaTeX version.
- `article_chromadb.md`: simplified French markdown summary.

### 2. Example Scripts

- `main.py`: minimal ChromaDB indexing example using `policies.txt`.
- `chatbot.py`: small retrieval demo (index + query loop over policy text).
- `main_fr_polices.py`: French-focused demo using a multilingual sentence-transformer model.
- `spip_checker.py`: package security checker (PyPI metadata, typosquatting signals, risk scoring).

Supporting data files:
- `policies.txt`, `polices.txt`, `menu_items.csv`, and generated outputs such as `resu1.md`, `resu2.md`.

### 3. Tests

Tests are in `patch314/tests/` and validate ChromaDB behavior for Python 3.14 compatibility:

- `test_import.py`: import and client creation smoke tests.
- `test_settings.py`: `Settings` field/type validation, including issue-specific fields.
- `conftest.py`: pytest fixtures for Python and dependency checks.

Run tests from repository root:

```bash
pytest patch314/tests -q
```

### 4. Patch (Python 3.14 Compatibility)

The `patch314/` folder contains a fix for ChromaDB issue `#5996` (Pydantic compatibility on Python 3.14+):

- `patch314/patches/config_pydantic_fix.py`: replacement import logic for `chromadb/config.py`.
- `patch314/patches/config_pydantic_fix.patch`: unified diff patch.
- `patch314/patch.sh`: helper script to apply the fix and install required dependency.
- `patch314/chromadb_py314_compat/`: installable compatibility shim package.
- `patch314/README.md`: detailed patch documentation and rationale.

## Notes

- `myvenv/` and `my_vectordb/` are local environment/runtime artifacts.
- `.gitignore` should be updated as needed to avoid committing local generated data.
