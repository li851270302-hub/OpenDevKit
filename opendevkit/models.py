from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Finding:
    rule: str
    severity: str
    path: str
    line: int | None
    message: str
    evidence: str = ""


@dataclass
class RepoSummary:
    root: str
    files: int
    by_extension: dict[str, int] = field(default_factory=dict)
    directories: int = 0
    entry_points: list[str] = field(default_factory=list)
    total_bytes: int = 0

    @property
    def languages(self) -> list[str]:
        mapping = {
            ".py": "Python",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".tsx": "TypeScript/React",
            ".jsx": "JavaScript/React",
            ".go": "Go",
            ".rs": "Rust",
            ".java": "Java",
            ".cs": "C#",
            ".cpp": "C++",
            ".c": "C",
            ".md": "Markdown",
            ".json": "JSON",
            ".yaml": "YAML",
            ".yml": "YAML",
        }
        return sorted({mapping[e] for e in self.by_extension if e in mapping})
