from pathlib import Path
import json

import typer
from rich.console import Console
from rich.table import Table

from . import __version__
from .ai import ask
from .report import build_report
from .scanner import analyze_repo, scan_dependencies, scan_security, scan_untrusted_instructions

app = typer.Typer(help="OpenDevKit: local-first developer maintenance assistant.")
console = Console()


def _root(path: Path) -> Path:
    path = path.expanduser().resolve()
    if not path.exists() or not path.is_dir():
        raise typer.BadParameter(f"Not a directory: {path}")
    return path


def _show_findings(findings, title: str, as_json: bool = False):
    if as_json:
        typer.echo(json.dumps([{
            "rule": f.rule,
            "severity": f.severity,
            "path": f.path,
            "line": f.line,
            "message": f.message,
        } for f in findings], indent=2))
        return
    if not findings:
        console.print("[green]No findings detected.[/green]")
        return
    table = Table(title=f"{title} ({len(findings)})")
    table.add_column("Severity")
    table.add_column("Rule")
    table.add_column("Location")
    table.add_column("Message")
    for f in findings:
        table.add_row(f.severity, f.rule, f"{f.path}:{f.line or '-'}", f.message)
    console.print(table)


@app.command()
def version():
    """Show the installed version."""
    console.print(__version__)


@app.command()
def analyze(path: Path = typer.Argument(".", exists=True, file_okay=False), as_json: bool = typer.Option(False, "--json")):
    """Inspect repository structure without executing repository code."""
    root = _root(path)
    summary = analyze_repo(root)
    if as_json:
        typer.echo(json.dumps({"root": summary.root, "files": summary.files, "directories": summary.directories, "bytes": summary.total_bytes, "languages": summary.languages, "by_extension": summary.by_extension, "entry_points": summary.entry_points}, indent=2))
        return
    table = Table(title="Repository analysis")
    table.add_column("Metric")
    table.add_column("Value")
    table.add_row("Files", str(summary.files))
    table.add_row("Directories", str(summary.directories))
    table.add_row("Size", f"{summary.total_bytes:,} bytes")
    table.add_row("Languages", ", ".join(summary.languages) or "Unknown")
    table.add_row("Entry points", ", ".join(summary.entry_points) or "None detected")
    console.print(table)


@app.command()
def security(path: Path = typer.Argument(".", exists=True, file_okay=False), as_json: bool = typer.Option(False, "--json")):
    """Run conservative local security heuristics; never execute repository code."""
    _show_findings(scan_security(_root(path)), "Security findings", as_json)


@app.command()
def deps(path: Path = typer.Argument(".", exists=True, file_okay=False), as_json: bool = typer.Option(False, "--json")):
    """Inspect dependency manifests for non-exact versions and parse problems."""
    _show_findings(scan_dependencies(_root(path)), "Dependency findings", as_json)


@app.command("prompt-scan")
def prompt_scan(path: Path = typer.Argument(".", exists=True, file_okay=False), as_json: bool = typer.Option(False, "--json")):
    """Flag repository text that may try to manipulate an AI-assisted maintenance workflow."""
    _show_findings(scan_untrusted_instructions(_root(path)), "Untrusted-instruction findings", as_json)


@app.command()
def report(path: Path = typer.Argument(".", exists=True, file_okay=False), output: Path = typer.Option("opendevkit-report.md", "--output", "-o")):
    """Generate a Markdown maintenance report."""
    root = _root(path)
    output.write_text(build_report(root), encoding="utf-8")
    console.print(f"Wrote {output}")


@app.command()
def review(path: Path = typer.Argument(".", exists=True, file_okay=False), file_path: Path | None = typer.Option(None, "--path", "-p")):
    """Use the OpenAI API for an advisory code review."""
    root = _root(path)
    selected_paths = None
    if file_path:
        candidate = (root / file_path).resolve()
        if root not in candidate.parents:
            raise typer.BadParameter("--path must stay inside the repository.")
        if not candidate.is_file():
            raise typer.BadParameter("--path must point to an existing file.")
        selected_paths = [candidate]
    console.print(ask(
        root,
        "Perform a focused code review. Prioritize correctness, maintainability, security, and test gaps.",
        selected_paths=selected_paths,
    ))


@app.command()
def test(path: Path = typer.Argument(".", exists=True, file_okay=False)):
    """Generate a focused test plan using the OpenAI API."""
    console.print(ask(_root(path), "Create a prioritized test plan. Include unit, integration, regression, and security-relevant cases. Do not write files."))


@app.command()
def docs(path: Path = typer.Argument(".", exists=True, file_okay=False)):
    """Generate a README improvement draft using the OpenAI API."""
    console.print(ask(_root(path), "Draft concise README improvements covering purpose, installation, usage, architecture, security model, and contribution workflow. Do not claim facts not present in the repository."))


if __name__ == "__main__":
    app()
