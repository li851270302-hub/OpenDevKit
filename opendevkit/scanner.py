from pathlib import Path
import json
import re

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10 compatibility
    import tomli as tomllib

from .models import Finding, RepoSummary

IGNORED_DIRS = {
    ".git", ".venv", "venv", "node_modules", "__pycache__",
    ".pytest_cache", "dist", "build", ".mypy_cache", ".ruff_cache"
}
TEXT_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java",
    ".cs", ".cpp", ".c", ".h", ".hpp", ".sh", ".ps1", ".yaml",
    ".yml", ".json", ".toml", ".ini", ".cfg", ".env", ".md", ".txt"
}
SECRET_PATTERNS = [
    ("possible-api-key", re.compile(r"(?i)(api[_-]?key|secret|token)\s*[:=]\s*['\"][^'\"]{12,}['\"]")),
    ("possible-private-key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("possible-cloud-key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("possible-github-token", re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}")),
    ("possible-bearer-token", re.compile(r"(?i)authorization\s*[:=]\s*['\"]?bearer\s+[A-Za-z0-9._~+/-]{16,}")),
]
DANGEROUS_PATTERNS = [
    ("shell-true", re.compile(r"\bsubprocess\.(?:run|Popen|call|check_call|check_output)\s*\([^)]*shell\s*=\s*True", re.S)),
    ("os-system", re.compile(r"\bos\.system\s*\(")),
    ("eval", re.compile(r"\beval\s*\(")),
    ("exec", re.compile(r"\bexec\s*\(")),
    ("pipe-to-shell", re.compile(r"(?i)\b(?:curl|wget)\b[^\n|]*\|\s*(?:sh|bash|zsh)\b")),
]
PATH_PATTERNS = [
    ("path-from-input", re.compile(r"(?:request|query|param|argv|input)\b[^\\n]{0,100}(?:open|Path|read_text|write_text)", re.I)),
]
UNTRUSTED_INSTRUCTION_PATTERNS = [
    ("prompt-secret-exfiltration", re.compile(r"(?i)(ignore|override|bypass).{0,80}(previous|system|developer).{0,120}(secret|token|api key|credential)")),
    ("prompt-shell-execution", re.compile(r"(?i)(run|execute|launch).{0,80}(shell|terminal|powershell|bash|cmd|command).{0,120}(without asking|automatically|immediately|silently)")),
    ("prompt-sensitive-file-read", re.compile(r"(?i)(read|open|print|upload|send).{0,80}(\.env|id_rsa|credentials|secrets?\.json|ssh key)")),
    ("prompt-network-exfiltration", re.compile(r"(?i)(send|upload|post|exfiltrate).{0,100}(http|webhook|remote server|external endpoint)")),
]
DEPENDENCY_FILES = {"requirements.txt", "requirements-dev.txt", "pyproject.toml", "package.json"}


def iter_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in IGNORED_DIRS for part in path.parts):
            continue
        yield path


def analyze_repo(root: Path) -> RepoSummary:
    counts: dict[str, int] = {}
    total = 0
    files = 0
    dirs = 0
    entries = []

    for path in iter_files(root):
        files += 1
        total += path.stat().st_size
        ext = path.suffix.lower() or "[no extension]"
        counts[ext] = counts.get(ext, 0) + 1

        if path.name in {"main.py", "app.py", "cli.py", "manage.py", "__main__.py"}:
            entries.append(str(path.relative_to(root)))

    for path in root.rglob("*"):
        if path.is_dir() and not any(part in IGNORED_DIRS for part in path.parts):
            dirs += 1

    return RepoSummary(
        root=str(root),
        files=files,
        by_extension=dict(sorted(counts.items(), key=lambda x: (-x[1], x[0]))),
        directories=dirs,
        entry_points=sorted(entries),
        total_bytes=total,
    )


def scan_untrusted_instructions(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in iter_files(root):
        if path.suffix.lower() not in {".md", ".txt", ".yaml", ".yml", ".json", ".toml"}:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        rel = str(path.relative_to(root))
        for line_no, line in enumerate(text.splitlines(), 1):
            for rule, pattern in UNTRUSTED_INSTRUCTION_PATTERNS:
                if pattern.search(line):
                    findings.append(Finding(
                        rule, "medium", rel, line_no,
                        "Repository text contains an instruction pattern that could influence an AI-assisted workflow.",
                        evidence=line.strip()[:160],
                    ))
    return findings


def _version_is_pinned(spec: str) -> bool:
    spec = spec.strip()
    if not spec or spec.startswith(("#", "-e ", "git+", "http://", "https://")):
        return True
    return bool(re.search(r"(^|[^<>=!~])==[^=]", spec))


def scan_dependencies(root: Path) -> list[Finding]:
    findings: list[Finding] = []

    for name in ("requirements.txt", "requirements-dev.txt"):
        path = root / name
        if not path.exists():
            continue
        for line_no, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            spec = line.strip()
            if spec and not spec.startswith("#") and not _version_is_pinned(spec):
                findings.append(Finding(
                    "unpinned-dependency", "low", name, line_no,
                    "Dependency is not pinned with ==; review reproducibility and supply-chain exposure.",
                    evidence=spec[:120],
                ))

    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        try:
            data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
            deps = data.get("project", {}).get("dependencies", []) or []
            optional = data.get("project", {}).get("optional-dependencies", {}) or {}
            for group in optional.values():
                deps.extend(group)
            for spec in deps:
                if not _version_is_pinned(spec):
                    findings.append(Finding(
                        "unpinned-dependency", "low", "pyproject.toml", None,
                        "Dependency is not pinned with ==; review reproducibility and supply-chain exposure.",
                        evidence=str(spec)[:120],
                    ))
        except (OSError, tomllib.TOMLDecodeError):
            findings.append(Finding(
                "dependency-manifest-parse", "medium", "pyproject.toml", None,
                "Could not parse pyproject.toml for dependency analysis.",
            ))

    package_json = root / "package.json"
    if package_json.exists():
        try:
            data = json.loads(package_json.read_text(encoding="utf-8"))
            for section in ("dependencies", "devDependencies", "optionalDependencies"):
                for name, version in (data.get(section, {}) or {}).items():
                    if not re.fullmatch(r"\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?", str(version)):
                        findings.append(Finding(
                            "unpinned-dependency", "low", "package.json", None,
                            "Dependency range or non-exact version detected; review reproducibility and supply-chain exposure.",
                            evidence=f"{name}: {version}"[:120],
                        ))
        except (OSError, json.JSONDecodeError):
            findings.append(Finding(
                "dependency-manifest-parse", "medium", "package.json", None,
                "Could not parse package.json for dependency analysis.",
            ))

    return findings


def scan_security(root: Path) -> list[Finding]:
    findings: list[Finding] = []

    for path in iter_files(root):
        if path.suffix.lower() not in TEXT_EXTENSIONS and path.name not in {".env", "Dockerfile"}:
            continue

        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        lines = text.splitlines()
        rel = str(path.relative_to(root))

        for line_no, line in enumerate(lines, 1):
            for rule, pattern in SECRET_PATTERNS:
                if pattern.search(line):
                    findings.append(Finding(
                        rule, "high", rel, line_no,
                        "Possible credential or secret embedded in source.",
                        evidence=line.strip()[:120],
                    ))

            for rule, pattern in DANGEROUS_PATTERNS:
                if pattern.search(line):
                    findings.append(Finding(
                        rule, "medium", rel, line_no,
                        "Potentially dangerous dynamic or shell execution construct found.",
                        evidence=line.strip()[:120],
                    ))

        for rule, pattern in PATH_PATTERNS:
            if pattern.search(text):
                findings.append(Finding(
                    rule, "medium", rel, None,
                    "Possible flow from external input into file operations; review for path traversal.",
                ))

    findings.extend(scan_untrusted_instructions(root))
    return findings
