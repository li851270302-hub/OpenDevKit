from pathlib import Path
import re

from .models import Finding, RepoSummary

IGNORED_DIRS = {
    ".git", ".venv", "venv", "node_modules", "__pycache__",
    ".pytest_cache", "dist", "build", ".mypy_cache", ".ruff_cache"
}
TEXT_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java",
    ".cs", ".cpp", ".c", ".h", ".hpp", ".sh", ".ps1", ".yaml",
    ".yml", ".json", ".toml", ".ini", ".cfg", ".env", ".md"
}
SECRET_PATTERNS = [
    ("possible-api-key", re.compile(r"(?i)(api[_-]?key|secret|token)\s*[:=]\s*['\"][^'\"]{12,}['\"]")),
    ("possible-private-key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("possible-cloud-key", re.compile(r"AKIA[0-9A-Z]{16}")),
]
DANGEROUS_PATTERNS = [
    ("shell-true", re.compile(r"\bsubprocess\.(?:run|Popen|call|check_call|check_output)\s*\([^)]*shell\s*=\s*True", re.S)),
    ("os-system", re.compile(r"\bos\.system\s*\(")),
    ("eval", re.compile(r"\beval\s*\(")),
    ("exec", re.compile(r"\bexec\s*\(")),
]
PATH_PATTERNS = [
    ("path-from-input", re.compile(r"(?:request|query|param|argv|input)\b[^\\n]{0,100}(?:open|Path|read_text|write_text)", re.I)),
]


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

    dep_files = [
        root / "requirements.txt",
        root / "requirements-dev.txt",
        root / "pyproject.toml",
        root / "package.json",
    ]
    for dep in dep_files:
        if dep.exists():
            text = dep.read_text(encoding="utf-8", errors="replace")
            if dep.name.startswith("requirements") and re.search(r"^[A-Za-z0-9_.-]+\s*$", text, re.M):
                findings.append(Finding(
                    "unpinned-dependency", "low", str(dep.relative_to(root)), None,
                    "One or more dependencies appear unpinned; consider reproducible version constraints."
                ))

    return findings
