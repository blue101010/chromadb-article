#!/usr/bin/env python
"""
spip_checker.py - Security checker module for spip
Performs comprehensive security analysis before pip install
"""

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from difflib import SequenceMatcher
import re
from typing import Optional, Dict, Set
import time
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

# Popular packages for typosquatting detection
POPULAR_PACKAGES = [
    "requests", "numpy", "pandas", "django", "flask", "tensorflow",
    "pytorch", "scikit-learn", "matplotlib", "scipy", "pillow",
    "beautifulsoup4", "selenium", "boto3", "sqlalchemy", "celery",
    "redis", "psycopg2", "pymongo", "cryptography", "pyyaml",
    "click", "fastapi", "uvicorn", "httpx", "aiohttp", "pytest",
    "black", "flake8", "mypy", "setuptools", "wheel", "pip",
    "chromadb", "langchain", "openai", "anthropic", "transformers",
]

class Colors:
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[0;34m"
    CYAN = "\033[0;36m"
    BOLD = "\033[1m"
    NC = "\033[0m"

@dataclass
class SecurityReport:
    package: str
    exists: bool = False
    version: str = ""
    downloads_last_month: int = 0
    first_release_date: Optional[datetime] = None
    version_release_date: Optional[datetime] = None
    age_days: int = 0
    author: str = ""
    maintainer_email: str = ""
    home_page: str = ""
    similar_packages: list = field(default_factory=list)
    vulnerabilities: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    errors: list = field(default_factory=list)
    risk_score: int = 0  # 0-100, higher = more risky
    dependency_tree: dict = field(default_factory=dict)

def fetch_pypi_info(package: str) -> Optional[dict]:
    """Fetch package info from PyPI JSON API."""
    url = f"https://pypi.org/pypi/{package}/json"
    try:
        with urlopen(url, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except HTTPError as e:
        if e.code == 404:
            return None
        raise
    except URLError:
        return None

def fetch_download_stats(package: str) -> int:
    """Fetch download stats from PyPI Stats API."""
    url = f"https://pypistats.org/api/packages/{package}/recent"
    try:
        with urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            return data.get("data", {}).get("last_month", 0)
    except (HTTPError, URLError, json.JSONDecodeError):
        return -1  # Unknown

def check_typosquatting(package: str, threshold: float = 0.85) -> list:
    """Check for similar package names (potential typosquatting)."""
    similar = []
    pkg_lower = package.lower()
    
    for popular in POPULAR_PACKAGES:
        if pkg_lower == popular.lower():
            continue
        ratio = SequenceMatcher(None, pkg_lower, popular.lower()).ratio()
        if ratio >= threshold:
            similar.append((popular, ratio))
    
    return sorted(similar, key=lambda x: x[1], reverse=True)

def check_vulnerabilities(package: str) -> list:
    """Check for known vulnerabilities using pip-audit if available."""
    vulns = []
    try:
        result = subprocess.run(
            ["pip-audit", "--require-hashes=false", "-r", "/dev/stdin"],
            input=f"{package}\n",
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode != 0 and "vulnerability" in result.stdout.lower():
            for line in result.stdout.split("\n"):
                if package.lower() in line.lower() and "vulnerability" in line.lower():
                    vulns.append(line.strip())
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass  # pip-audit not installed or timed out
    return vulns

def analyze_package(package: str, min_downloads: int = 1000, min_age_days: int = 30, check_deps: bool = False, progress: bool = False, debug: bool = False) -> SecurityReport:
    """Perform comprehensive security analysis on a package."""
    report = SecurityReport(package=package)
    
    total_steps = 6 if check_deps else 5
    
    # Fetch PyPI info
    print(f"{Colors.CYAN}[1/{total_steps}] Fetching package info from PyPI...{Colors.NC}")
    pypi_data = fetch_pypi_info(package)
    
    if not pypi_data:
        report.exists = False
        report.errors.append(f"Package '{package}' not found on PyPI")
        report.risk_score = 100
        return report
    
    report.exists = True
    info = pypi_data.get("info", {})
    report.version = info.get("version", "unknown")
    report.author = info.get("author", "unknown")
    report.maintainer_email = info.get("maintainer_email") or info.get("author_email", "unknown")
    report.home_page = info.get("home_page") or info.get("project_url", "")
    
    # Parse release dates
    releases = pypi_data.get("releases", {})
    if releases:
        dates = []
        for ver, files in releases.items():
            for f in files:
                if "upload_time" in f:
                    try:
                        dt = datetime.fromisoformat(f["upload_time"].replace("Z", "+00:00"))
                        dates.append(dt)
                    except ValueError:
                        pass
        if dates:
            first_release = min(dates)
            # ensure the datetime is timezone-aware so subtraction with
            # `datetime.now(timezone.utc)` doesn't raise a TypeError
            if first_release.tzinfo is None:
                first_release = first_release.replace(tzinfo=timezone.utc)
            report.first_release_date = first_release
            report.age_days = (datetime.now(timezone.utc) - first_release).days
        # determine release date for the current package version (if available)
        version_dates = []
        for f in releases.get(report.version, []):
            if "upload_time" in f:
                try:
                    dt = datetime.fromisoformat(f["upload_time"].replace("Z", "+00:00"))
                    version_dates.append(dt)
                except ValueError:
                    pass
        if version_dates:
            ver_dt = max(version_dates)
            if ver_dt.tzinfo is None:
                ver_dt = ver_dt.replace(tzinfo=timezone.utc)
            report.version_release_date = ver_dt
    
    # Fetch download stats
    print(f"{Colors.CYAN}[2/{total_steps}] Checking download statistics...{Colors.NC}")
    report.downloads_last_month = fetch_download_stats(package)
    
    # Check for typosquatting
    print(f"{Colors.CYAN}[3/{total_steps}] Checking for similar package names...{Colors.NC}")
    report.similar_packages = check_typosquatting(package)
    
    # Check vulnerabilities
    print(f"{Colors.CYAN}[4/{total_steps}] Scanning for known vulnerabilities...{Colors.NC}")
    report.vulnerabilities = check_vulnerabilities(package)

    # Dependency tree analysis and hash verification
    if check_deps:
        print(f"{Colors.CYAN}[5/{total_steps}] Building dependency tree and verifying file hashes...{Colors.NC}")
        tree = build_dependency_tree(package, progress=progress, debug=debug)
        report.dependency_tree = tree
        # walk tree to find missing hashes
        missing_hashes = 0
        def _walk(node):
            nonlocal missing_hashes
            for f in node.get("files", []):
                if not f.get("sha256"):
                    missing_hashes += 1
            for child in node.get("dependencies", {}).values():
                if child:
                    _walk(child)
        _walk(tree)
        if missing_hashes:
            report.warnings.append(f"{missing_hashes} distribution files missing SHA256 digests")
            report.risk_score += 10

    # Calculate risk score and warnings
    print(f"{Colors.CYAN}[{total_steps}/{total_steps}] Calculating risk assessment...{Colors.NC}")
    
    if report.downloads_last_month >= 0 and report.downloads_last_month < min_downloads:
        report.warnings.append(f"Low download count: {report.downloads_last_month:,} (threshold: {min_downloads:,})")
        report.risk_score += 25
    
    if report.age_days < min_age_days:
        report.warnings.append(f"Package is only {report.age_days} days old (threshold: {min_age_days})")
        report.risk_score += 30
    
    if report.similar_packages:
        top_similar = report.similar_packages[0]
        report.warnings.append(f"Similar to popular package '{top_similar[0]}' ({top_similar[1]*100:.0f}% match)")
        report.risk_score += 20
    
    if report.vulnerabilities:
        report.warnings.append(f"Found {len(report.vulnerabilities)} known vulnerabilities")
        report.risk_score += 40
    
    if not report.author or report.author == "unknown":
        report.warnings.append("No author information available")
        report.risk_score += 10
    
    report.risk_score = min(report.risk_score, 100)
    return report

def _parse_requirement_name(req: str) -> Optional[str]:
    # Examples: "requests (>=2.0)", "idna; python_version<'3'", "urllib3[secure] (>=1.21.1)"
    if not req:
        return None
    # strip extras and markers
    req = req.split(";", 1)[0].strip()
    m = re.match(r"^([A-Za-z0-9_.+-]+)", req)
    if m:
        return m.group(1)
    return None

def _get_release_files_with_hashes(package: str, version: Optional[str] = None) -> list:
    data = fetch_pypi_info(package)
    if not data:
        return []
    info = data.get("info", {})
    ver = version or info.get("version")
    releases = data.get("releases", {})
    files = []
    for f in releases.get(ver, []):
        filename = f.get("filename")
        sha256 = f.get("digests", {}).get("sha256") if isinstance(f.get("digests"), dict) else None
        url = f.get("url")
        files.append({"filename": filename, "sha256": sha256, "url": url})
    return files

def build_dependency_tree(package: str, seen: Optional[Set[str]] = None, depth: int = 0, max_depth: int = 4, progress: bool = False, debug: bool = False) -> Dict:
    start_time = time.time()
    counter = {"count": 0, "last_print": 0.0}

    spinner = ["|", "/", "-", "\\"]
    def _log_progress(pkg, depth_level, seen_set):
        # live one-line progress with spinner, throttle to ~5fps
        now = time.time()
        if now - counter["last_print"] > 0.18:
            idx = counter["count"] % len(spinner)
            msg = f"building deps {spinner[idx]} scanned={counter['count']} current={pkg} depth={depth_level} unique={len(seen_set)}"
            try:
                sys.stdout.write("\r" + msg)
                sys.stdout.flush()
            except Exception:
                print(msg)
            counter["last_print"] = now

    def _build(pkg: str, seen_local: Set[str], d: int) -> Dict:
        pkg_key = pkg.lower()
        if pkg_key in seen_local or d > max_depth:
            return {}
        seen_local.add(pkg_key)
        counter["count"] += 1
        if progress:
            _log_progress(pkg, d, seen_local)
        if debug:
            print(f"[debug] fetching metadata for {pkg} (depth={d})")
        data = fetch_pypi_info(pkg)
        if not data:
            if debug:
                print(f"[debug] no metadata for {pkg}")
            return {"version": None, "files": [], "dependencies": {}}
        info = data.get("info", {})
        version = info.get("version")
        files = _get_release_files_with_hashes(pkg, version)
        requires = info.get("requires_dist") or []
        deps = {}
        for req in requires:
            name = _parse_requirement_name(req)
            if not name:
                continue
            deps[name] = _build(name, seen_local, d + 1)
        return {"version": version, "files": files, "dependencies": deps}

    result = _build(package, set() if seen is None else set(seen), depth)
    if progress:
        elapsed = time.time() - start_time
        # clear progress line
        try:
            sys.stdout.write("\r")
            sys.stdout.flush()
        except Exception:
            pass
        print(f"[progress] done scanned={counter['count']} elapsed={elapsed:.1f}s")
    return result
    if seen is None:
        seen = set()
    pkg_key = package.lower()
    if pkg_key in seen or depth > max_depth:
        return {}
    seen.add(pkg_key)
    data = fetch_pypi_info(package)
    if not data:
        return {"version": None, "files": [], "dependencies": {}}
    info = data.get("info", {})
    version = info.get("version")
    files = _get_release_files_with_hashes(package, version)
    requires = info.get("requires_dist") or []
    deps = {}
    for req in requires:
        name = _parse_requirement_name(req)
        if not name:
            continue
        deps[name] = build_dependency_tree(name, seen=seen, depth=depth + 1, max_depth=max_depth)
    return {"version": version, "files": files, "dependencies": deps}

def print_report(report: SecurityReport):
    """Print formatted security report."""
    print()
    print(f"{Colors.BOLD}╔═══════════════════════════════════════╗{Colors.NC}")
    print(f"{Colors.BOLD}║         SECURITY REPORT               ║{Colors.NC}")
    print(f"{Colors.BOLD}╚═══════════════════════════════════════╝{Colors.NC}")
    
    if not report.exists:
        print(f"\n{Colors.RED}✗ PACKAGE NOT FOUND{Colors.NC}")
        for err in report.errors:
            print(f"  {err}")
        return
    
    # Package info
    print(f"\n{Colors.BLUE}Package:{Colors.NC} {report.package}")
    print(f"{Colors.BLUE}Version:{Colors.NC} {report.version}")
    print(f"{Colors.BLUE}Author:{Colors.NC} {report.author}")
    if report.home_page:
        print(f"{Colors.BLUE}Homepage:{Colors.NC} {report.home_page}")
    
    # Stats
    print(f"\n{Colors.BLUE}Downloads (last month):{Colors.NC} ", end="")
    if report.downloads_last_month >= 0:
        print(f"{report.downloads_last_month:,}")
    else:
        print("Unknown")
    
    print(f"{Colors.BLUE}Package age:{Colors.NC} {report.age_days} days")
    if report.first_release_date:
        print(f"{Colors.BLUE}First release:{Colors.NC} {report.first_release_date.strftime('%Y-%m-%d')}")
    if report.version_release_date:
        print(f"{Colors.BLUE}Release date (version {report.version}):{Colors.NC} {report.version_release_date.strftime('%Y-%m-%d')}")
    
    # Risk score
    print(f"\n{Colors.BOLD}Risk Score:{Colors.NC} ", end="")
    if report.risk_score <= 20:
        print(f"{Colors.GREEN}{report.risk_score}/100 (LOW){Colors.NC}")
    elif report.risk_score <= 50:
        print(f"{Colors.YELLOW}{report.risk_score}/100 (MEDIUM){Colors.NC}")
    else:
        print(f"{Colors.RED}{report.risk_score}/100 (HIGH){Colors.NC}")
    
    # Warnings
    if report.warnings:
        print(f"\n{Colors.YELLOW}⚠ Warnings:{Colors.NC}")
        for warn in report.warnings:
            print(f"  • {warn}")
    
    # Similar packages
    if report.similar_packages:
        print(f"\n{Colors.YELLOW}Similar packages (potential typosquatting):{Colors.NC}")
        for pkg, ratio in report.similar_packages[:3]:
            print(f"  • {pkg} ({ratio*100:.0f}% similar)")
    
    # Vulnerabilities
    if report.vulnerabilities:
        print(f"\n{Colors.RED}🛡 Known Vulnerabilities:{Colors.NC}")
        for vuln in report.vulnerabilities:
            print(f"  • {vuln}")

    # Dependency tree summary
    if report.dependency_tree:
        print(f"\n{Colors.BLUE}Dependency tree summary:{Colors.NC}")
        def _print_node(name, node, indent=2, max_display_depth=2, depth=0):
            prefix = " " * indent * depth
            ver = node.get("version") if isinstance(node, dict) else None
            print(f"{prefix}- {name} {f'({ver})' if ver else ''}")
            if depth >= max_display_depth:
                return
            for f in node.get("files", [])[:3]:
                sha = f.get("sha256") or "<no-sha256>"
                print(f"{prefix}  • {f.get('filename')} : {sha}")
            for child_name, child in sorted(node.get("dependencies", {}).items()):
                if child:
                    _print_node(child_name, child, indent, max_display_depth, depth + 1)

        # top-level package
        top = report.dependency_tree
        _print_node(report.package, top)
    
    # Final status
    print()
    if report.risk_score <= 20:
        print(f"{Colors.GREEN}✓ Package appears safe to install{Colors.NC}")
    elif report.risk_score <= 50:
        print(f"{Colors.YELLOW}⚠ Package has some concerns - review warnings above{Colors.NC}")
    else:
        print(f"{Colors.RED}✗ Package has significant security concerns{Colors.NC}")

def prompt_install(report: SecurityReport, auto_yes: bool = False) -> bool:
    """Prompt user for installation confirmation."""
    if not report.exists:
        return False
    
    if auto_yes and report.risk_score <= 50:
        return True
    
    print()
    if report.risk_score > 50:
        prompt = f"{Colors.RED}HIGH RISK:{Colors.NC} Proceed with installation? (yes/no): "
    elif report.risk_score > 20:
        prompt = f"{Colors.YELLOW}MEDIUM RISK:{Colors.NC} Proceed with installation? (yes/no): "
    else:
        prompt = "Proceed with installation? (yes/no): "
    
    try:
        response = input(prompt).strip().lower()
        return response in ("yes", "y")
    except (KeyboardInterrupt, EOFError):
        print()
        return False

def install_package(package: str) -> bool:
    """Install package using pip."""
    print(f"\n{Colors.BLUE}Installing {package}...{Colors.NC}\n")
    result = subprocess.run([sys.executable, "-m", "pip", "install", package])
    return result.returncode == 0

def audit_installed():
    """Audit all installed packages."""
    try:
        subprocess.run(["pip-audit"], check=False)
    except FileNotFoundError:
        print(f"{Colors.YELLOW}pip-audit not installed. Install with: pip install pip-audit{Colors.NC}")
        print(f"\n{Colors.BLUE}Checking for outdated packages instead...{Colors.NC}\n")
        subprocess.run([sys.executable, "-m", "pip", "list", "--outdated"])

def main():
    parser = argparse.ArgumentParser(description="Security checker for pip packages")
    parser.add_argument("package", nargs="?", help="Package name to check")
    parser.add_argument("--install", action="store_true", help="Install after checks pass")
    parser.add_argument("--check", action="store_true", help="Enable dependency/tree and hash checks")
    parser.add_argument("--checkfast", action="store_true", help="Fast metadata-only checks (skip deps/hashes)")
    parser.add_argument("--yes", "-y", action="store_true", help="Auto-confirm installation")
    parser.add_argument("--min-downloads", type=int, default=1000, help="Minimum download threshold")
    parser.add_argument("--min-age-days", type=int, default=30, help="Minimum package age")
    parser.add_argument("--audit", action="store_true", help="Audit installed packages")
    parser.add_argument("--progress", action="store_true", help="Show progress while building dependency tree")
    parser.add_argument("--debug", action="store_true", help="Show minimal debug logs")
    
    args = parser.parse_args()
    
    if args.audit:
        audit_installed()
        return 0
    
    if not args.package:
        parser.print_help()
        return 1
    
    # Determine check mode: --checkfast takes precedence, otherwise use --check
    check_deps = args.check and not args.checkfast
    
    report = analyze_package(
        args.package,
        min_downloads=args.min_downloads,
        min_age_days=args.min_age_days,
        check_deps=check_deps,
        progress=args.progress,
        debug=args.debug,
    )
    print_report(report)
    
    if args.install:
        if prompt_install(report, args.yes):
            success = install_package(args.package)
            return 0 if success else 1
        else:
            print(f"\n{Colors.YELLOW}Installation cancelled{Colors.NC}")
            return 1
    
    return 0 if report.risk_score <= 50 else 1

if __name__ == "__main__":
    sys.exit(main())