from pathlib import Path

from .scanner import analyze_repo, scan_dependencies, scan_security


def _append_findings(lines: list[str], title: str, findings: list) -> None:
    lines.extend(["", f"## {title}", ""])
    if not findings:
        lines.append("No findings were detected.")
        return

    lines.append("| Severity | Rule | File | Line | Message |")
    lines.append("|---|---|---|---:|---|")
    for item in findings:
        lines.append(
            f"| {item.severity} | `{item.rule}` | `{item.path}` | "
            f"{item.line or '-'} | {item.message} |"
        )


def build_report(root: Path) -> str:
    summary = analyze_repo(root)
    security_findings = scan_security(root)
    dependency_findings = scan_dependencies(root)

    lines = [
        "# OpenDevKit Maintenance Report",
        "",
        f"- Repository: `{root}`",
        f"- Files: {summary.files}",
        f"- Directories: {summary.directories}",
        f"- Total size: {summary.total_bytes:,} bytes",
        f"- Languages: {', '.join(summary.languages) or 'Unknown'}",
        f"- Entry points: {', '.join(summary.entry_points) or 'None detected'}",
    ]

    _append_findings(lines, "Security findings", security_findings)
    _append_findings(lines, "Dependency findings", dependency_findings)

    lines.extend([
        "",
        "## Review note",
        "",
        "This report is a heuristic static analysis result. It is not a proof that the repository is secure.",
    ])
    return "\n".join(lines) + "\n"
