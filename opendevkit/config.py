from dataclasses import dataclass
from fnmatch import fnmatchcase
from functools import lru_cache
from pathlib import Path, PurePosixPath
import re

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10 compatibility
    import tomli as tomllib


CONFIG_FILENAME = ".opendevkit.toml"
DEFAULT_IGNORED_DIRS = frozenset({
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    "dist",
    "build",
    ".mypy_cache",
    ".ruff_cache",
})


class ConfigurationError(ValueError):
    """Raised when a repository configuration cannot be used safely."""


@dataclass(frozen=True)
class ProjectConfig:
    exclude: tuple[str, ...] = ()


def _normalize_pattern(value: object, index: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ConfigurationError(
            f"{CONFIG_FILENAME}: scan.exclude[{index}] must be a non-empty string."
        )

    pattern = value.strip().replace("\\", "/")
    while pattern.startswith("./"):
        pattern = pattern[2:]
    if (
        PurePosixPath(pattern).is_absolute()
        or re.match(r"^[A-Za-z]:/", pattern)
        or ".." in PurePosixPath(pattern).parts
    ):
        raise ConfigurationError(
            f"{CONFIG_FILENAME}: scan.exclude[{index}] must stay relative to the repository."
        )
    if pattern.endswith("/"):
        pattern += "**"
    return pattern


def load_config(root: Path) -> ProjectConfig:
    path = root / CONFIG_FILENAME
    if not path.is_file():
        return ProjectConfig()
    if path.is_symlink():
        raise ConfigurationError(f"{CONFIG_FILENAME} must not be a symbolic link.")

    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        raise ConfigurationError(f"Could not parse {CONFIG_FILENAME}: {exc}") from exc

    scan = data.get("scan", {})
    if not isinstance(scan, dict):
        raise ConfigurationError(f"{CONFIG_FILENAME}: [scan] must be a table.")
    raw_exclude = scan.get("exclude", [])
    if not isinstance(raw_exclude, list):
        raise ConfigurationError(
            f"{CONFIG_FILENAME}: scan.exclude must be an array of repository-relative patterns."
        )

    return ProjectConfig(tuple(
        _normalize_pattern(value, index)
        for index, value in enumerate(raw_exclude)
    ))


def _matches_pattern(relative: PurePosixPath, pattern: str) -> bool:
    pattern_parts = PurePosixPath(pattern).parts
    path_parts = relative.parts

    if len(pattern_parts) == 1:
        return any(fnmatchcase(part, pattern) for part in path_parts)

    @lru_cache(maxsize=None)
    def matches(path_index: int, pattern_index: int) -> bool:
        if pattern_index == len(pattern_parts):
            return path_index == len(path_parts)
        part = pattern_parts[pattern_index]
        if part == "**":
            return matches(path_index, pattern_index + 1) or (
                path_index < len(path_parts)
                and matches(path_index + 1, pattern_index)
            )
        return (
            path_index < len(path_parts)
            and fnmatchcase(path_parts[path_index], part)
            and matches(path_index + 1, pattern_index + 1)
        )

    return matches(0, 0)


def is_excluded(root: Path, path: Path, config: ProjectConfig) -> bool:
    try:
        relative = path.relative_to(root)
    except ValueError:
        return True

    if relative.as_posix() == CONFIG_FILENAME:
        return False
    if path.is_symlink() or any(part in DEFAULT_IGNORED_DIRS for part in relative.parts):
        return True

    for pattern in config.exclude:
        if _matches_pattern(PurePosixPath(relative.as_posix()), pattern):
            return True
    return False
