import re
from pathlib import Path

from typer.testing import CliRunner

from opendevkit import cli as cli_module
from opendevkit.cli import app


runner = CliRunner()
ANSI_ESCAPE = re.compile(r"\x1b\[[0-9;]*m")


def plain_output(output: str) -> str:
    return ANSI_ESCAPE.sub("", output)


def test_review_passes_selected_file(tmp_path: Path, monkeypatch):
    target = tmp_path / "target.py"
    target.write_text("VALUE = 1\n", encoding="utf-8")
    captured = {}

    def fake_ask(root, task, selected_paths=None):
        captured["root"] = root
        captured["selected_paths"] = selected_paths
        return "review complete"

    monkeypatch.setattr(cli_module, "ask", fake_ask)
    result = runner.invoke(app, ["review", str(tmp_path), "--path", "target.py"])

    assert result.exit_code == 0
    assert "review complete" in result.output
    assert captured["root"] == tmp_path.resolve()
    assert captured["selected_paths"] == [target.resolve()]


def test_review_without_path_remains_repository_wide(tmp_path: Path, monkeypatch):
    captured = {}

    def fake_ask(root, task, selected_paths=None):
        captured["selected_paths"] = selected_paths
        return "review complete"

    monkeypatch.setattr(cli_module, "ask", fake_ask)
    result = runner.invoke(app, ["review", str(tmp_path)])

    assert result.exit_code == 0
    assert captured["selected_paths"] is None


def test_review_rejects_directory_path(tmp_path: Path):
    (tmp_path / "folder").mkdir()

    result = runner.invoke(app, ["review", str(tmp_path), "--path", "folder"])

    assert result.exit_code != 0
    assert "--path must point to an existing file" in plain_output(result.output)


def test_review_rejects_path_outside_repository(tmp_path: Path):
    outside = tmp_path.parent / "outside-review.py"
    outside.write_text("VALUE = 1\n", encoding="utf-8")

    result = runner.invoke(app, ["review", str(tmp_path), "--path", str(outside)])

    assert result.exit_code != 0
    assert "--path must stay inside the repository" in plain_output(result.output)
