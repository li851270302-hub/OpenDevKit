from pathlib import Path
from .scanner import analyze_repo, scan_security


def build_report(root: Path) -> str:
    summary = analyze_repo(root)
    findings = scan_security(root)

    lines = [
        "# OpenDevKit Maintenance Report",
        "",
        f"- Repository: `{root}`",
        f"- Files: {summary.files}",
        f"- Directories: {summary.directories}",
        f"- Total size: {summary.total_bytes:,} bytes",
        f"- Languages: {', '.join(summary.languages) or 'Unknown'}",
        f"- Entry points: {', '.join(summary.entry_points) or 'None detected'}",
        "",
        "## Security findings",
        "",
    ]

    if not findings:
        lines.append("No findings were detected by the conservative local ruleset.")
    else:
        lines.append("| Severity | Rule | File | Line | Message |")
        lines.append("|---|---|---|---:|---|")
        for item in findings:
            lines.append(
                f"| {item.severity} | `{item.rule}` | `{item.path}` | "
                f"{item.line or '-'} | {item.message} |"
            )

    lines.extend([
        "",
        "## Review note",
        "",
        "This report is a heuristic static analysis result. It is not a proof that the repository is secure.",
    ])
    return "\n".join(lines) + "\n"
