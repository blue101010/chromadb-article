#!/usr/bin/env bash
# ==============================================================================
# patch.sh - Apply Python 3.14 compatibility fix for ChromaDB (issue #5996)
#
# Replaces lines 15-24 of chromadb/config.py with the pydantic-settings
# import block, and installs the pydantic-settings dependency.
#
# Usage:
#   chmod +x patch.sh
#   ./patch.sh
#
# Options:
#   --dry-run     Show what would be changed without modifying anything
#   --no-pip      Skip pip install of pydantic-settings
#   --config-path Override auto-detected config.py path
# ==============================================================================

set -euo pipefail

# ── Detect Python binary ────────────────────────────────────────────────────
# On Windows/MINGW64 the command is "python", not "python3".
# Also prefer an active virtualenv's python if available.
PYTHON=""
if [[ -n "${VIRTUAL_ENV:-}" ]]; then
    # Virtualenv is active — use its python
    for candidate in "$VIRTUAL_ENV/bin/python" "$VIRTUAL_ENV/Scripts/python.exe" \
                     "$VIRTUAL_ENV/bin/python3" "$VIRTUAL_ENV/Scripts/python3.exe"; do
        if [[ -x "$candidate" ]]; then
            PYTHON="$candidate"
            break
        fi
    done
fi
if [[ -z "$PYTHON" ]]; then
    # Try common names in PATH
    for candidate in python3 python python3.14 python3.13 python3.12; do
        if command -v "$candidate" &>/dev/null; then
            # Verify it's a real CPython, not the Windows Store stub
            if "$candidate" -c "import sys; sys.exit(0)" 2>/dev/null; then
                PYTHON="$candidate"
                break
            fi
        fi
    done
fi
if [[ -z "$PYTHON" ]]; then
    echo "ERROR: No usable python interpreter found in PATH or VIRTUAL_ENV."
    exit 1
fi
echo "Using Python: $PYTHON ($($PYTHON --version 2>&1))"

# Also resolve pip relative to the same interpreter
PIP="$PYTHON -m pip"

# ── Colours ──────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Colour

# ── Defaults ─────────────────────────────────────────────────────────────────
DRY_RUN=false
SKIP_PIP=false
CONFIG_PATH=""

# ── Parse arguments ──────────────────────────────────────────────────────────
for arg in "$@"; do
    case "$arg" in
        --dry-run)   DRY_RUN=true ;;
        --no-pip)    SKIP_PIP=true ;;
        --config-path=*) CONFIG_PATH="${arg#*=}" ;;
        -h|--help)
            echo "Usage: $0 [--dry-run] [--no-pip] [--config-path=/path/to/config.py]"
            exit 0
            ;;
        *) echo -e "${RED}Unknown option: $arg${NC}"; exit 1 ;;
    esac
done

# ── Locate config.py ────────────────────────────────────────────────────────
if [[ -z "$CONFIG_PATH" ]]; then
    echo -e "${CYAN}[1/4] Locating chromadb/config.py ...${NC}"
    CONFIG_PATH=$($PYTHON -c "
import importlib.util, os
spec = importlib.util.find_spec('chromadb.config')
if spec and spec.origin:
    print(spec.origin)
else:
    raise SystemExit('chromadb.config not found')
" 2>/dev/null) || true

    # Fallback: search site-packages
    if [[ -z "$CONFIG_PATH" || ! -f "$CONFIG_PATH" ]]; then
        CONFIG_PATH=$($PYTHON -c "
import site, os
for sp in site.getsitepackages() + [site.getusersitepackages()]:
    p = os.path.join(sp, 'chromadb', 'config.py')
    if os.path.isfile(p):
        print(p)
        break
" 2>/dev/null) || true
    fi
fi

if [[ -z "$CONFIG_PATH" || ! -f "$CONFIG_PATH" ]]; then
    echo -e "${RED}ERROR: Could not find chromadb/config.py${NC}"
    echo "       Is chromadb installed?  Try: pip install chromadb"
    echo "       Or specify manually:    $0 --config-path=/path/to/config.py"
    exit 1
fi

echo -e "${GREEN}  Found: ${CONFIG_PATH}${NC}"

# ── Verify the file contains the original import block ──────────────────────
echo -e "${CYAN}[2/4] Verifying original import block ...${NC}"

# The 10 lines we expect at lines 15-24 (verbatim)
read -r -d '' OLD_BLOCK << 'OLDEOF' || true
in_pydantic_v2 = False
try:
    from pydantic import BaseSettings
except ImportError:
    in_pydantic_v2 = True
    from pydantic.v1 import BaseSettings
    from pydantic.v1 import validator

if not in_pydantic_v2:
    from pydantic import validator  # type: ignore # noqa
OLDEOF

if ! grep -qF "in_pydantic_v2 = False" "$CONFIG_PATH"; then
    echo -e "${YELLOW}WARNING: config.py does not contain the expected import block.${NC}"
    echo "         It may have already been patched or the version differs."
    echo "         Checking for existing patch marker ..."
    if grep -qF "from pydantic_settings import BaseSettings" "$CONFIG_PATH"; then
        echo -e "${GREEN}  Already patched! Nothing to do.${NC}"
        # Still install pydantic-settings if needed
        if [[ "$SKIP_PIP" == false && "$DRY_RUN" == false ]]; then
            echo -e "${CYAN}[3/4] Ensuring pydantic-settings is installed ...${NC}"
            $PIP install "pydantic-settings>=2.0" --quiet
            echo -e "${GREEN}  Done.${NC}"
        fi
        echo -e "${GREEN}[4/4] Patch already applied. Exiting.${NC}"
        exit 0
    fi
    echo -e "${RED}ERROR: Unrecognised config.py contents. Manual review needed.${NC}"
    exit 1
fi

echo -e "${GREEN}  Original import block found.${NC}"

# ── The replacement block ────────────────────────────────────────────────────
read -r -d '' NEW_BLOCK << 'NEWEOF' || true
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
NEWEOF

# ── Dry-run mode ─────────────────────────────────────────────────────────────
if [[ "$DRY_RUN" == true ]]; then
    echo ""
    echo -e "${YELLOW}=== DRY RUN — no changes will be made ===${NC}"
    echo ""
    echo -e "${RED}--- REMOVE (lines 15-24):${NC}"
    echo "$OLD_BLOCK"
    echo ""
    echo -e "${GREEN}+++ INSERT replacement:${NC}"
    echo "$NEW_BLOCK"
    echo ""
    echo -e "${YELLOW}Would also run: pip install \"pydantic-settings>=2.0\"${NC}"
    exit 0
fi

# ── Create backup ────────────────────────────────────────────────────────────
BACKUP="${CONFIG_PATH}.bak.$(date +%Y%m%d%H%M%S)"
cp "$CONFIG_PATH" "$BACKUP"
echo -e "${GREEN}  Backup saved: ${BACKUP}${NC}"

# ── Apply the patch via Python (robust multiline replace) ────────────────────
echo -e "${CYAN}[3/4] Patching config.py ...${NC}"

$PYTHON << PYEOF
import sys
import re

config_path = r"""${CONFIG_PATH}"""

with open(config_path, "r", encoding="utf-8") as f:
    content = f.read()

patches_applied = []

# ── Patch 1: Replace the pydantic import block (lines 15-24) ────────────────
old_import = '''in_pydantic_v2 = False
try:
    from pydantic import BaseSettings
except ImportError:
    in_pydantic_v2 = True
    from pydantic.v1 import BaseSettings
    from pydantic.v1 import validator

if not in_pydantic_v2:
    from pydantic import validator  # type: ignore # noqa'''

new_import = '''import sys

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
                "ChromaDB requires pydantic-settings on Python 3.14+. "
                "Install it with: pip install pydantic-settings>=2.0"
            )
        from pydantic.v1 import BaseSettings  # type: ignore[no-redef]
        from pydantic.v1 import validator  # type: ignore[no-redef]
        in_pydantic_v2 = True  # still pydantic v2 runtime, just using v1 shim'''

if old_import in content:
    content = content.replace(old_import, new_import, 1)
    patches_applied.append("pydantic import block")
else:
    print("ERROR: Could not find the original import block in config.py", file=sys.stderr)
    sys.exit(1)

# ── Patch 2: Add type annotations to un-annotated fields ────────────────────
# These 3 fields lack type annotations, which pydantic v2 BaseSettings rejects.
annotation_fixes = [
    ('    chroma_coordinator_host = "localhost"',
     '    chroma_coordinator_host: str = "localhost"'),
    ('    chroma_logservice_host = "localhost"',
     '    chroma_logservice_host: str = "localhost"'),
    ('    chroma_logservice_port = 50052',
     '    chroma_logservice_port: int = 50052'),
]

for old_line, new_line in annotation_fixes:
    if old_line in content:
        content = content.replace(old_line, new_line, 1)
        field_name = old_line.strip().split('=')[0].strip()
        patches_applied.append(f"type annotation for {field_name}")

# ── Patch 3: Convert inner class Config -> model_config for pydantic v2 ─────
# pydantic-settings v2 BaseSettings uses model_config dict instead of inner Config class.
# We make it work with both by replacing the inner class with a conditional block.
old_config_class = '''    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"'''

new_config_class = '''    # pydantic v2 (pydantic-settings) uses model_config; v1 uses inner Config class
    if in_pydantic_v2:
        model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}
    else:
        class Config:
            env_file = ".env"
            env_file_encoding = "utf-8"'''

if old_config_class in content:
    content = content.replace(old_config_class, new_config_class, 1)
    patches_applied.append("Config class -> model_config")

# ── Write result ─────────────────────────────────────────────────────────────
with open(config_path, "w", encoding="utf-8") as f:
    f.write(content)

for p in patches_applied:
    print(f"  Applied: {p}")
print(f"  config.py patched successfully ({len(patches_applied)} changes).")
PYEOF

# ── Install pydantic-settings ────────────────────────────────────────────────
if [[ "$SKIP_PIP" == false ]]; then
    echo -e "${CYAN}[4/4] Installing pydantic-settings ...${NC}"
    $PIP install "pydantic-settings>=2.0"
else
    echo -e "${YELLOW}[4/4] Skipping pip install (--no-pip).${NC}"
fi

# ── Verify ───────────────────────────────────────────────────────────────────
echo ""
echo -e "${CYAN}Verifying patch ...${NC}"
$PYTHON -c "
from chromadb.config import Settings
s = Settings()
print('  chromadb.config.Settings() — OK')
" && echo -e "${GREEN}✓ Patch applied and verified successfully!${NC}" \
  || echo -e "${RED}✗ Verification failed. Restoring backup ...${NC}" \
  && { if ! $PYTHON -c "from chromadb.config import Settings; Settings()" 2>/dev/null; then
         cp "$BACKUP" "$CONFIG_PATH"
         echo -e "${YELLOW}  Backup restored: ${CONFIG_PATH}${NC}"
       fi; }

echo ""
echo -e "${GREEN}Done.${NC}"
echo "  Backup:  ${BACKUP}"
echo "  Patched: ${CONFIG_PATH}"
echo ""
echo "To undo:  cp \"${BACKUP}\" \"${CONFIG_PATH}\""
